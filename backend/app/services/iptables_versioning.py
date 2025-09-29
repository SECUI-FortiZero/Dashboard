import os, json, hashlib, yaml, re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from app.connector_db import get_connection

REQUIRED_RULE_FIELDS = ["chain", "target"]
VALID_STATES = {"present", "absent"}

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _normalize_rule(rule: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """필드 정규화 + 기본값 채움 + 소팅된 raw_match 생성"""
    table = (rule.get("table") or defaults.get("table") or "filter").lower()
    chain = rule["chain"].upper().strip()
    target = rule["target"].upper().strip()
    priority = int(rule.get("priority", 100))

    norm = {
        "table": table,
        "chain": chain,
        "priority": priority,
        "target": target,
        "proto": (rule.get("proto") or None),
        "src": (rule.get("src") or None),
        "dst": (rule.get("dst") or None),
        "sport": (str(rule.get("sport")) if rule.get("sport") is not None else None),
        "dport": (str(rule.get("dport")) if rule.get("dport") is not None else None),
        "in_iface": (rule.get("in_iface") or None),
        "out_iface": (rule.get("out_iface") or None),
        "state_match": (rule.get("state_match") or None),
        "comment": (rule.get("comment") or None),
        "state": (rule.get("state") or "present").lower()
    }

    # 나머지 매치 옵션은 raw_match로
    known = set(["table","chain","priority","target","proto","src","dst","sport","dport",
                 "in_iface","out_iface","state_match","comment","state"])
    extra = {k: rule[k] for k in rule.keys() - known}
    # raw_match는 dict key 소팅하여 결정적
    norm["raw_match"] = json.dumps(extra, sort_keys=True, ensure_ascii=False)

    # 간단한 유효성
    if norm["state"] not in VALID_STATES:
        raise ValueError(f"Invalid state: {norm['state']}")
    return norm

def _rule_key(norm: Dict[str, Any]) -> str:
    """규칙 동등성 판정용 키. (idempotent)"""
    parts = [
        norm["table"], norm["chain"], str(norm["priority"]), norm["target"],
        norm.get("proto") or "-", norm.get("src") or "-", norm.get("dst") or "-",
        norm.get("sport") or "-", norm.get("dport") or "-",
        norm.get("in_iface") or "-", norm.get("out_iface") or "-",
        norm.get("state_match") or "-", norm["raw_match"]
    ]
    return _sha256("|".join(parts))

def _load_yaml(yaml_text: str) -> Dict[str, Any]:
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict):
        raise ValueError("잘못된 YAML 형식입니다. 최상위는 dict 이어야 합니다.")
    if "rules" in data and not isinstance(data["rules"], list):
        raise ValueError("rules 는 list 여야 합니다.")
    return data

def create_or_get_policy_id(name: str, scope: str = "onprem", description: str = None) -> int:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM policies WHERE name=%s", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute("INSERT INTO policies (name, scope, description) VALUES (%s,%s,%s)",
                    (name, scope, description))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()

def get_next_version(policy_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT COALESCE(MAX(version),0)+1 AS v FROM policy_versions WHERE policy_id=%s", (policy_id,))
        return cur.fetchone()["v"]
    finally:
        cur.close(); conn.close()

def save_policy_version(yaml_text: str) -> Tuple[int, int]:
    """
    YAML 저장 + 규칙 스냅샷 저장
    return (policy_id, version_id)
    """
    data = _load_yaml(yaml_text)
    policy_meta = data.get("policy", {}) or {}
    name = policy_meta.get("name")
    if not name:
        raise ValueError("policy.name 이 필요합니다.")
    description = policy_meta.get("description")
    author = policy_meta.get("author")
    message = policy_meta.get("message")

    defaults = data.get("defaults", {}) or {}
    rules = data.get("rules", []) or []

    # 정규화 + 키 생성
    norm_rules = []
    for r in rules:
        if not isinstance(r, dict):
            raise ValueError("각 rule은 dict 이어야 합니다.")
        for f in REQUIRED_RULE_FIELDS:
            if f not in r:
                raise ValueError(f"rule 필수필드 누락: {f}")
        nr = _normalize_rule(r, defaults)
        nr["rule_key"] = _rule_key(nr)
        norm_rules.append(nr)

    # 체크섬(원본 기준)
    checksum = _sha256(yaml_text)

    # DB 저장 트랜잭션
    policy_id = create_or_get_policy_id(name=name, description=description)
    version = get_next_version(policy_id)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            INSERT INTO policy_versions (policy_id, version, author, message, source_yaml, checksum)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (policy_id, version, author, message, yaml_text, checksum))
        conn.commit()
        version_id = cur.lastrowid

        # 규칙 저장
        ins_sql = """
        INSERT INTO policy_rules
        (version_id, rule_key, `table`, `chain`, priority, target, proto, src, dst, sport, dport,
         in_iface, out_iface, state_match, comment, raw_match, state)
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        for nr in norm_rules:
            cur.execute(ins_sql, (
                version_id, nr["rule_key"], nr["table"], nr["chain"], nr["priority"], nr["target"],
                nr["proto"], nr["src"], nr["dst"], nr["sport"], nr["dport"],
                nr["in_iface"], nr["out_iface"], nr["state_match"], nr["comment"],
                nr["raw_match"], nr["state"]
            ))
        conn.commit()
        return policy_id, version_id
    finally:
        cur.close(); conn.close()

def _get_rules_by_version(version_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM policy_rules WHERE version_id=%s ORDER BY priority ASC, id ASC", (version_id,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()

def diff_versions(base_version_id: int, new_version_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    base 대비 new의 차이.
    - present 규칙: 새로 추가된 키 → added
    - absent 규칙: new에 absent가 있으면 → removed(명시적 삭제)
    - 동일 키 존재하나 내용이 일부 바뀐 경우 → changed
    (단, 'YAML에 없음'은 삭제로 취급하지 않음)
    """
    base = _get_rules_by_version(base_version_id)
    new  = _get_rules_by_version(new_version_id)

    base_map = {r["rule_key"]: r for r in base}
    new_map  = {r["rule_key"]: r for r in new}

    added, removed, changed, kept = [], [], [], []

    # 새 버전 기준 스캔
    for k, nr in new_map.items():
        if nr["state"] == "absent":
            # 삭제 명령은 removed로
            removed.append(nr)
            continue
        if k not in base_map:
            added.append(nr)
        else:
            br = base_map[k]
            # 상태 present & 키 동일 → 세부 비교
            keys_to_check = ["priority","target","proto","src","dst","sport","dport","in_iface","out_iface","state_match","comment","raw_match"]
            changed_flag = any((br.get(x) or "") != (nr.get(x) or "") for x in keys_to_check)
            if changed_flag:
                changed.append({"before": br, "after": nr})
            else:
                kept.append(nr)

    # base에만 있고 new에 (present로) 나타나지 않은 키는 ‘유지’로 간주 (삭제 아님)
    # (사용자 요구사항 반영: YAML 미기재 = 유지)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "kept": kept
    }

def get_version_header(version_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT pv.*, p.name AS policy_name
            FROM policy_versions pv JOIN policies p ON p.id=pv.policy_id
            WHERE pv.id=%s
        """, (version_id,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()
