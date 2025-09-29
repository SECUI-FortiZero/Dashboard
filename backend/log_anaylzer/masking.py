import os
import re
import json
import hmac
import hashlib
import ipaddress

MASKING_SECRET = os.getenv("MASKING_SECRET", "change_this_secret")

def hmac_hash(value: str, length: int = 12) -> str:
    if not value:
        return None
    mac = hmac.new(MASKING_SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()
    return mac[:length]

def mask_ipv4_last_octet(ip: str) -> str:
    if not ip:
        return None
    try:
        if "/" in ip:
            net = ipaddress.ip_network(ip, strict=False)
            return f"{net.network_address}/{net.prefixlen}"
        addr = ipaddress.ip_address(ip)
        if addr.version == 4:
            parts = str(addr).split(".")
            parts[-1] = "*"
            return ".".join(parts)
        else:
            return str(addr).split(":")[0] + ":*"
    except Exception:
        return hmac_hash(ip, 8)

EMAIL_RE = re.compile(r'([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
PHONE_RE = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\d{2,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})')

def mask_raw_log(raw_text: str) -> str:
    if not raw_text:
        return raw_text

    def emsub(m):
        user, domain = m.group(1), m.group(2)
        return user[0] + "***@" + domain.split(".")[0] + ".***"
    text = EMAIL_RE.sub(emsub, raw_text)

    def phsub(m):
        full = "".join(g or "" for g in m.groups())
        return "***-***-" + full[-4:]
    text = PHONE_RE.sub(phsub, text)

    text = re.sub(r"\b\d{6}-\d{7}\b", "******-*******", text)
    return text

def mask_common(row: dict) -> dict:
    out = row.copy()
    if "raw_log" in out and out["raw_log"]:
        try:
            raw_data = json.loads(out["raw_log"])
            out["raw_log"] = mask_raw_log(json.dumps(raw_data))
        except (json.JSONDecodeError, TypeError):
            out["raw_log"] = mask_raw_log(out["raw_log"])
    return out
