// src/pages/Policy.jsx
import React, { useState, useEffect, useCallback, useMemo } from "react";
import styled, { css } from "styled-components";
import { useDropzone } from "react-dropzone";
import yaml from "js-yaml";
import Editor from "react-simple-code-editor";
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-yaml";
import "prismjs/themes/prism-tomorrow.css";
import {
  MdFileUpload,
  MdArrowUpward,
  MdArrowDownward,
  MdRemove,
  MdCloudUpload,
  MdCompareArrows,
  MdEdit,
  MdDelete,
} from "react-icons/md";

// API
import { getCurrentPolicies, applyNewPolicy, getPolicyHistory } from "../apis/policyApi";

/* =================== Styled =================== */

const hideScrollbar = css`
  &::-webkit-scrollbar { display: none; width: 0; height: 0; }
  scrollbar-width: none;
`;

const PageContainer = styled.div`
  box-sizing: border-box;
  width: 100%;
  min-height: 100vh;
  padding: 24px 28px 120px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  h1 {
    font-size: 24px; font-weight: 500; margin: 0;
    span { color: #a0aec0; font-weight: 400; }
  }
`;

const ApplyButton = styled.button`
  background: #0075ff; color: white; font-weight: 500; font-size: 14px;
  border: none; border-radius: 12px; padding: 10px 20px; cursor: pointer;
  display: flex; align-items: center; gap: 8px;
  transition: background-color .3s ease, opacity .3s ease;
  &:hover { background: #005ecc; }
  &:disabled { opacity: .5; cursor: not-allowed; }
`;

const ContentGrid = styled.div`
  display: grid; grid-template-columns: 1fr; gap: 24px; width: 100%;
  @media (min-width: 1024px) { grid-template-columns: 1fr 1fr; }
`;

const Card = styled.div`
  box-sizing: border-box; width: 100%;
  background: linear-gradient(128deg, rgba(36,41,79,.94) 0%, rgba(9,14,35,.49) 100%);
  border-radius: 20px; padding: 24px; backdrop-filter: blur(60px);
  border: 1px solid rgba(255,255,255,.1);
  display: flex; flex-direction: column;
  h2 { font-size: 18px; font-weight: 500; margin-bottom: 16px; }
`;

const TableScroll = styled.div`
  max-height: 60vh; overflow-y: auto; ${hideScrollbar}
`;

const PolicyTable = styled.table`
  width: 100%; font-size: 12px; border-collapse: collapse;
  th, td {
    padding: 10px 12px; text-align: left;
    border-bottom: 1px solid rgba(255,255,255,.08);
    white-space: nowrap;
  }
  th { color: #a0aec0; font-weight: 400; }
  td { color: #e2e8f0; vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  code {
    background: rgba(0,0,0,.2); padding: 2px 5px; border-radius: 4px;
    font-family: "Fira Code", monospace; white-space: pre-wrap; word-break: break-all;
  }
`;

const HistoryHeader = styled.div`
  display:flex; align-items:center; gap:12px; margin-bottom:14px;
`;

const Select = styled.select`
  background:#0F1535; border:1px solid #2D2E5F; color:#E2E8F0;
  border-radius:10px; padding:8px 10px; font-size:12px;
`;

const HistoryTable = styled.table`
  width:100%; border-collapse:collapse; font-size:12px;
  th, td { padding:10px 12px; border-bottom:1px solid rgba(255,255,255,.08); text-align:left; vertical-align:top; }
  th { color:#A0AEC0; font-weight:400; }
  tr:last-child td { border-bottom:none; }
  code { background: rgba(0,0,0,.2); padding:2px 5px; border-radius:4px; }
`;

const DiffBox = styled.pre`
  background:#0F1535; border:1px solid #2D3748; border-radius:8px;
  padding:12px; margin:8px 0 0; white-space:pre-wrap; word-break:break-word;
  font-family:"Fira Code", monospace; font-size:12px; color:#E2E8F0;
`;

const Tag = styled.span`
  display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px;
  color:#fff; margin-left:8px;
  ${({ $type }) => $type === 'added' && css` background:#01B574; `}
  ${({ $type }) => $type === 'deleted' && css` background:#E31A1A; `}
  ${({ $type }) => $type === 'modified' && css` background:#F6AD55; color:#1A1F37; `}
  ${({ $type }) => !$type && css` background:#4A5568; `}
`;

const ModalOverlay = styled.div`
  position: fixed; inset: 0; background: rgba(0,0,0,.7); backdrop-filter: blur(5px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
`;

const ModalContent = styled.div`
  width: 94%; max-width: 1080px; height: 92vh;
  background: #1a202c; border-radius: 20px; border: 1px solid rgba(255,255,255,.1);
  padding: 28px; display: grid; grid-template-columns: 1.3fr 1fr; gap: 20px;
  position: relative; overflow: hidden;
  h2 { font-size: 20px; margin: 0 0 6px 0; grid-column: 1 / -1; }
  @media (max-width: 1024px) { grid-template-columns: 1fr; }
  .close-btn {
    position: absolute; top: 16px; right: 16px; background: none; border: none;
    color: #a0aec0; font-size: 24px; cursor: pointer;
  }
`;

const Dropzone = styled.div`
  border: 2px dashed #4a5568; border-radius: 12px; padding: 40px 20px; text-align: center;
  cursor: pointer; transition: border-color .3s ease; grid-column: 1 / -1;
  &:hover { border-color: #0075ff; }
  p { color: #a0aec0; }
`;

const ResultDisplay = styled.pre`
  background: #0f1535; border-radius: 8px; padding: 16px;
  font-family: "Fira Code", monospace; font-size: 12px;
  white-space: pre-wrap; word-break: break-all; max-height: 250px; overflow-y: auto;
  ${hideScrollbar}; border: 1px solid #2d3748; grid-column: 1 / -1;
`;

const PolicyItemCard = styled(Card)`
  display: flex; flex-direction: row; align-items: flex-start; gap: 16px; padding: 16px;
  opacity: ${({ status }) => (status === "deleted" ? 0.6 : 1)};
  border-left: 5px solid; border-color: transparent;
  ${({ status }) => {
    switch (status) {
      case "added": return css`border-left-color: #01b574;`;
      case "deleted": return css`border-left-color: #e31a1a;`;
      case "modified": return css`border-left-color: #f6ad55;`;
      default: return css``;
    }
  }}
`;

const StatusIcon = styled.div`
  width: 32px; height: 32px; min-width: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 16px;
  ${({ status }) => {
    switch (status) {
      case "added": return css`background: rgba(1,181,116,.1); color: #01b574;`;
      case "deleted": return css`background: rgba(227,26,26,.1); color: #e31a1a;`;
      case "modified": return css`background: rgba(246,173,85,.1); color: #f6ad55;`;
      default: return css`background: rgba(160,174,192,.1); color: #a0aec0;`;
    }
  }}
`;

const PolicyContent = styled.div` flex: 1 1 auto; min-width: 0; `;
const PolicyHeader = styled.div`
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
  h4 { font-size: 14px; font-weight: 600; margin: 0; }
`;

const ActionButtons = styled.div`
  display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500;
  button {
    background: none; border: none; color: #a0aec0; display: inline-flex; align-items: center;
    cursor: pointer; padding: 6px 10px; border-radius: 8px;
    &:hover { color: white; background: rgba(255,255,255,.06); }
    svg { margin-right: 4px; }
  }
  .delete-btn:hover { color: #e31a1a; background: rgba(227,26,26,.08); }
`;

const PolicyDetails = styled.div`
  color: #a0aec0; font-size: 12px; line-height: 1.8; white-space: pre-wrap; word-break: break-word;
`;

const CodeEditorWrapper = styled.div`
  width: 100%; ${hideScrollbar}
  .npm__react-simple-code-editor__textarea { outline: none !important; }
`;

const LeftScroll = styled.div`
  overflow: auto; ${hideScrollbar}
  max-height: calc(92vh - 28px - 28px - 32px);
  display: flex; flex-direction: column; gap: 12px;
`;

const RightPanel = styled(Card)`
  padding: 14px; display: grid; grid-template-rows: auto 1fr auto; gap: 10px; height: 100%; overflow: hidden;
`;

const SectionTitle = styled.h3` margin: 0 0 6px 0; font-weight: 600; font-size: 14px; `;
const EditorScrollBox = styled.div`
  overflow: auto; ${hideScrollbar}; border-radius: 8px; border: 1px solid #2d3748; background: #0f1535; max-height: 100%;
`;

/* =================== Diff helpers =================== */

const idOnPrem = (r) =>
  [r.chain ?? "", r.protocol ?? "", String(r.port ?? ""), r.source_ip ?? "", r.destination_ip ?? ""].join("|");

const idAws = (r) =>
  [
    r.target_sg ?? "",
    r.protocol ?? "",
    String(r.port ?? ""),
    r.source_ip ? `srcip:${r.source_ip}` : "",
    r.source_sg ? `srcsg:${r.source_sg}` : "",
  ].join("|");

const equalMeta = (a, b) =>
  (a?.action ?? "") === (b?.action ?? "") && (a?.comment ?? "") === (b?.comment ?? "");

const isDeleteOp = (r) => String(r?.operation || "").toLowerCase() === "delete";

function makeDiff(currentArr, newArr, platform) {
  // 방어: 배열 보장
  const curList = Array.isArray(currentArr) ? currentArr : [];
  const newList = Array.isArray(newArr) ? newArr : [];

  const idFn = platform === "on-premise" ? idOnPrem : idAws;

  const curMap = new Map(curList.map((r) => [idFn(r), r]));
  const newMap = new Map(newList.map((r) => [idFn(r), r]));

  const out = [];

  for (const [id, cur] of curMap.entries()) {
    if (!newMap.has(id)) {
      out.push({ platform, status: "unchanged", rule: cur, previous: cur });
    } else {
      const up = newMap.get(id);
      if (isDeleteOp(up)) {
        out.push({ platform, status: "deleted", rule: cur, previous: cur });
      } else if (equalMeta(cur, up)) {
        out.push({ platform, status: "unchanged", rule: up, previous: cur });
      } else {
        out.push({ platform, status: "modified", rule: up, previous: cur });
      }
    }
  }

  for (const [id, up] of newMap.entries()) {
    if (!curMap.has(id)) {
      if (isDeleteOp(up)) continue;
      out.push({ platform, status: "added", rule: up });
    }
  }

  return out;
}

/* =================== Component =================== */

const Policy = () => {
  // 현재 정책
  const [onpremPolicies, setOnpremPolicies] = useState([]);
  const [awsPolicies, setAwsPolicies] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 변경 이력 (온프레)
  const [historyRange, setHistoryRange] = useState("daily"); // 10min | hourly | daily | weekly
  const [onpremHistory, setOnpremHistory] = useState([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState(null);

  // 모달/업로드/적용
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [rawYamlText, setRawYamlText] = useState("");
  const [applyResult, setApplyResult] = useState(null);
  const [isApplying, setIsApplying] = useState(false);

  // 작업중 규칙들
  const [workingOnp, setWorkingOnp] = useState([]);
  const [workingAws, setWorkingAws] = useState([]);

  // per-item 편집
  const [editingId, setEditingId] = useState(null);
  const [editingYaml, setEditingYaml] = useState("");

  // 현재 정책 로딩
  const fetchPolicies = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCurrentPolicies();
      if (data?.status === "success") {
        setOnpremPolicies(Array.isArray(data?.data?.on_premise) ? data.data.on_premise : []);
        // aws는 객체 → security_group_rules 배열만 사용
        setAwsPolicies(Array.isArray(data?.data?.aws?.security_group_rules) ? data.data.aws.security_group_rules : []);
      } else {
        throw new Error(data?.message || "Failed to fetch current policies");
      }
    } catch (err) {
      setError(err.message || "Failed to fetch");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchPolicies(); }, [fetchPolicies]);

  // 변경 이력 로딩
  const fetchOnpremHistory = useCallback(async () => {
    setIsHistoryLoading(true);
    setHistoryError(null);
    try {
      const data = await getPolicyHistory("onprem", historyRange);
      if (data?.status === "success") {
        setOnpremHistory(Array.isArray(data?.data) ? data.data : []);
      } else {
        throw new Error(data?.message || "Failed to load history");
      }
    } catch (e) {
      setHistoryError(e.message || "Failed to load history");
    } finally {
      setIsHistoryLoading(false);
    }
  }, [historyRange]);

  useEffect(() => { fetchOnpremHistory(); }, [fetchOnpremHistory]);

  // 모달 열릴 때 배경 스크롤 잠금
  useEffect(() => {
    if (!isModalOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = prev; };
  }, [isModalOpen]);

  // 드롭존
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result || "");
      try {
        const doc = yaml.load(text);
        if (!doc || !Array.isArray(doc?.rules)) {
          throw new Error("YAML에 rules 리스트가 없습니다.");
        }
        const onp = (doc.rules || []).filter((r) => r.platform === "on-premise");
        const aws = (doc.rules || []).filter((r) => r.platform === "aws");
        setRawYamlText(text);
        setWorkingOnp(onp);
        setWorkingAws(aws);
        setEditingId(null);
        setEditingYaml("");
      } catch (e) {
        alert("YAML 파싱 오류: " + e.message);
      }
    };
    reader.readAsText(file);
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { "application/x-yaml": [".yaml", ".yml"] },
    maxFiles: 1,
  });

  // diff
  const diffs = useMemo(() => ({
    onp: makeDiff(onpremPolicies, workingOnp, "on-premise"),
    aws: makeDiff(awsPolicies, workingAws, "aws"),
  }), [onpremPolicies, workingOnp, awsPolicies, workingAws]);

  // 라벨/디테일
  const ruleTitle = (r, platform) => {
    const del = isDeleteOp(r) ? " [DELETE]" : "";
    if (platform === "on-premise") {
      return `[On-prem] ${r.chain} ${r.protocol}/${r.port} ${r.source_ip ?? ""} → ${r.destination_ip ?? ""} (${r.action})${del}`;
    }
    const src = r.source_ip || r.source_sg || "-";
    return `[AWS] ${r.target_sg} ← ${src} ${r.protocol}/${r.port} (${r.action || "allow"})${del}`;
  };

  const ruleDetails = (r, platform) => {
    const keys = platform === "on-premise"
      ? ["platform", "chain", "protocol", "port", "source_ip", "destination_ip", "action", "comment", "operation"]
      : ["platform", "target_sg", "protocol", "port", "source_ip", "source_sg", "action", "comment", "operation"];
    return (
      <PolicyDetails>
        {keys.map((k) => (
          <div key={k}><strong>{k}:</strong> {String(r?.[k] ?? "")}</div>
        ))}
      </PolicyDetails>
    );
  };

  // per-item 편집
  const onEdit = (platform, index, item) => {
    const idStr = `${platform}:${index}:${platform === "on-premise" ? idOnPrem(item.rule) : idAws(item.rule)}`;
    setEditingId(idStr);
    setEditingYaml(yaml.dump(item.rule));
  };

  const onSave = (platform, index) => {
    try {
      const obj = yaml.load(editingYaml);
      if (!obj || typeof obj !== "object") throw new Error("올바른 YAML 객체가 아닙니다.");
      if (!obj.platform) obj.platform = platform === "on-premise" ? "on-premise" : "aws";
      if (platform === "on-premise") {
        const next = [...workingOnp]; next[index] = obj; setWorkingOnp(next);
      } else {
        const next = [...workingAws]; next[index] = obj; setWorkingAws(next);
      }
      setEditingId(null); setEditingYaml("");
    } catch (e) { alert("YAML 형식 오류: " + e.message); }
  };

  const onDelete = (platform, index) => {
    if (!confirm("Remove this rule from the proposed policy?")) return;
    if (platform === "on-premise") {
      const next = [...workingOnp]; next.splice(index, 1); setWorkingOnp(next);
    } else {
      const next = [...workingAws]; next.splice(index, 1); setWorkingAws(next);
    }
  };

  // 렌더 대상(working 기준)
  const listForRender = useMemo(() => {
    const onpList = workingOnp.map((r, i) => {
      const found = diffs.onp.find((d) => idOnPrem(d.rule) === idOnPrem(r));
      return {
        platform: "on-premise",
        index: i,
        status: found?.status || (isDeleteOp(r) ? "deleted" : "added"),
        rule: r,
        previous: found?.previous,
      };
    });
    const awsList = workingAws.map((r, i) => {
      const found = diffs.aws.find((d) => idAws(d.rule) === idAws(r));
      return {
        platform: "aws",
        index: i,
        status: found?.status || (isDeleteOp(r) ? "deleted" : "added"),
        rule: r,
        previous: found?.previous,
      };
    });
    return { onp: onpList, aws: awsList };
  }, [workingOnp, workingAws, diffs]);

  // 적용
  const handleApplyPolicy = async () => {
    let mode = "overwrite";
    try { const d = yaml.load(rawYamlText); if (typeof d?.mode === "string") mode = d.mode; } catch {}
    const merged = { mode, rules: [...workingOnp, ...workingAws] };
    const finalYaml = yaml.dump(merged);
    const blob = new Blob([finalYaml], { type: "application/x-yaml" });
    const file = new File([blob], "policy_edited.yaml", { type: "application/x-yaml" });

    const formData = new FormData();
    formData.append("policy_file", file);

    setIsApplying(true);
    setApplyResult(null);
    try {
      const res = await applyNewPolicy(formData);
      setApplyResult(res);
      if (res?.status === "success") {
        setTimeout(async () => {
          setIsModalOpen(false);
          await fetchPolicies();
        }, 800);
      }
    } catch (err) {
      setApplyResult({ status: "error", message: err.message || "Apply failed" });
    } finally {
      setIsApplying(false);
    }
  };

  const openModal = () => {
    setIsModalOpen(true);
    setRawYamlText("");
    setApplyResult(null);
    setWorkingOnp([]);
    setWorkingAws([]);
    setEditingId(null);
    setEditingYaml("");
  };

  const getStatusIcon = (status) => {
    if (status === "added") return <MdArrowUpward />;
    if (status === "deleted") return <MdArrowDownward />;
    return <MdRemove />;
  };

  // 이력 details → 사람이 보기 좋게
  const buildEventDiff = (details) => {
    const before = details?.before ?? null;
    const after = details?.after ?? null;
    if (before && after && typeof before === "object" && typeof after === "object") {
      const keys = Array.from(new Set([...Object.keys(before), ...Object.keys(after)]));
      const lines = [];
      keys.forEach((k) => {
        const b = before[k]; const a = after[k];
        if (JSON.stringify(b) !== JSON.stringify(a)) {
          lines.push(`- ${k}:`);
          lines.push(`    old: ${JSON.stringify(b)}`);
          lines.push(`    new: ${JSON.stringify(a)}`);
        }
      });
      return lines.length ? lines.join("\n") : "No field-level changes.";
    }
    return JSON.stringify(details ?? {}, null, 2);
  };

  /* =================== Render =================== */

  if (isLoading) return <PageContainer><h1>Loading...</h1></PageContainer>;
  if (error) return <PageContainer><h1>Error: {error}</h1></PageContainer>;

  return (
    <PageContainer>
      <PageHeader>
        <h1><span>Pages /</span> Policy Management</h1>
        <ApplyButton onClick={openModal}><MdCloudUpload /> Apply New Policy</ApplyButton>
      </PageHeader>

      {/* 현재 정책 */}
      <ContentGrid>
        <Card>
          <h2>🏢 On-Premise Policies (iptables)</h2>
          <TableScroll>
            <PolicyTable>
              <thead>
                <tr><th>Chain</th><th>Source/Dest</th><th>Port</th><th>Action</th><th>Comment</th></tr>
              </thead>
              <tbody>
                {onpremPolicies.map((p, i) => (
                  <tr key={i}>
                    <td><code>{p.chain || "INPUT"}</code></td>
                    <td><code>{p.source_ip || p.destination_ip || "any"}</code></td>
                    <td><code>{p.port || "any"}</code></td>
                    <td>{p.action}</td>
                    <td>{p.comment}</td>
                  </tr>
                ))}
              </tbody>
            </PolicyTable>
          </TableScroll>
        </Card>

        <Card>
          <h2>☁️ Cloud Policies (AWS Security Group)</h2>
          <TableScroll>
            <PolicyTable>
              <thead>
                <tr><th>Target SG</th><th>Source</th><th>Port</th><th>Protocol</th><th>Comment</th></tr>
              </thead>
              <tbody>
                {awsPolicies.map((p, i) => (
                  <tr key={i}>
                    <td><code>{p.target_sg}</code></td>
                    <td><code>{p.source_ip || p.source_sg || "-"}</code></td>
                    <td><code>{p.port}</code></td>
                    <td>{p.protocol}</td>
                    <td>{p.comment}</td>
                  </tr>
                ))}
              </tbody>
            </PolicyTable>
          </TableScroll>
        </Card>
      </ContentGrid>

      {/* 온프레 변경 이력 */}
      <Card>
        <h2>🕒 On-Premise Policy Change History</h2>
        <HistoryHeader>
          <div style={{ color:'#A0AEC0', fontSize:12 }}>Range</div>
          <Select value={historyRange} onChange={(e)=>setHistoryRange(e.target.value)}>
            <option value="10min">Last 10 minutes</option>
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </Select>
        </HistoryHeader>

        {isHistoryLoading ? (
          <div style={{ color:'#A0AEC0' }}>Loading history…</div>
        ) : historyError ? (
          <div style={{ color:'#E31A1A' }}>Error: {historyError}</div>
        ) : (
          <TableScroll>
            <HistoryTable>
              <thead>
                <tr>
                  <th style={{width:180}}>Timestamp</th>
                  <th style={{width:220}}>Event</th>
                  <th style={{width:120}}>User</th>
                  <th>Details / Diff</th>
                </tr>
              </thead>
              <tbody>
                {onpremHistory.length === 0 && (
                  <tr><td colSpan={4} style={{color:'#A0AEC0'}}>No history in selected range.</td></tr>
                )}
                {onpremHistory.map((ev, idx) => {
                  const op = String(ev?.details?.operation || '').toLowerCase();
                  let tagType;
                  if (op.includes('delete') || ev?.event_name?.toLowerCase().includes('delete')) tagType = 'deleted';
                  else if (op.includes('create') || ev?.event_name?.toLowerCase().includes('create')) tagType = 'added';
                  else if (op.includes('update') || ev?.event_name?.toLowerCase().includes('update')) tagType = 'modified';

                  return (
                    <tr key={idx}>
                      <td>{ev.timestamp}</td>
                      <td>
                        <code>{ev.event_name || '-'}</code>
                        {tagType && <Tag $type={tagType}>{tagType}</Tag>}
                      </td>
                      <td>{ev.user || '-'}</td>
                      <td><DiffBox>{buildEventDiff(ev.details)}</DiffBox></td>
                    </tr>
                  );
                })}
              </tbody>
            </HistoryTable>
          </TableScroll>
        )}
      </Card>

      {/* 모달 */}
      {isModalOpen && (
        <ModalOverlay>
          <ModalContent>
            <button className="close-btn" onClick={() => setIsModalOpen(false)}>&times;</button>
            <h2>Apply New Policy</h2>

            {workingOnp.length === 0 && workingAws.length === 0 ? (
              <Dropzone {...getRootProps()}>
                <input {...getInputProps()} />
                <MdFileUpload size={40} style={{ margin: "0 auto 1rem" }} />
                <p>비교할 YAML 파일을 드래그하거나 클릭하여 선택하세요.</p>
              </Dropzone>
            ) : (
              <>
                <LeftScroll>
                  <SectionTitle>
                    <MdCompareArrows style={{ display: "inline-block", marginRight: 8 }} />
                    Diff Preview — On-Premise
                  </SectionTitle>

                  {listForRender.onp.length === 0 && <PolicyDetails>Empty.</PolicyDetails>}
                  {listForRender.onp.map((item, i) => {
                    const idStr = `on-premise:${item.index}:${idOnPrem(item.rule)}`;
                    const isEditing = editingId === idStr;
                    return (
                      <PolicyItemCard key={`onp-${i}-${idStr}`} status={item.status}>
                        <StatusIcon status={item.status}>{getStatusIcon(item.status)}</StatusIcon>
                        <PolicyContent>
                          <PolicyHeader>
                            <h4>{ruleTitle(item.rule, "on-premise")}</h4>
                            <ActionButtons>
                              {!isEditing ? (
                                <>
                                  <button onClick={() => onEdit("on-premise", item.index, item)}>
                                    <MdEdit /> EDIT
                                  </button>
                                  <button className="delete-btn" onClick={() => onDelete("on-premise", item.index)}>
                                    <MdDelete /> DELETE
                                  </button>
                                </>
                              ) : (
                                <>
                                  <button onClick={() => onSave("on-premise", item.index)}>Save</button>
                                  <button onClick={() => setEditingId(null)}>Cancel</button>
                                </>
                              )}
                            </ActionButtons>
                          </PolicyHeader>

                          {!isEditing ? (
                            ruleDetails(item.rule, "on-premise")
                          ) : (
                            <CodeEditorWrapper>
                              <Editor
                                value={editingYaml}
                                onValueChange={(code) => setEditingYaml(code)}
                                highlight={(code) => highlight(code, languages.yaml)}
                                padding={12}
                                style={{
                                  fontFamily: '"Fira Code","Fira Mono",monospace',
                                  fontSize: 12,
                                  backgroundColor: "#0F1535",
                                  borderRadius: 8,
                                  minHeight: 200,
                                  width: "100%",
                                }}
                              />
                            </CodeEditorWrapper>
                          )}
                        </PolicyContent>
                      </PolicyItemCard>
                    );
                  })}

                  <SectionTitle style={{ marginTop: 16 }}>Diff Preview — AWS</SectionTitle>

                  {listForRender.aws.length === 0 && <PolicyDetails>Empty.</PolicyDetails>}
                  {listForRender.aws.map((item, i) => {
                    const idStr = `aws:${item.index}:${idAws(item.rule)}`;
                    const isEditing = editingId === idStr;
                    return (
                      <PolicyItemCard key={`aws-${i}-${idStr}`} status={item.status}>
                        <StatusIcon status={item.status}>{getStatusIcon(item.status)}</StatusIcon>
                        <PolicyContent>
                          <PolicyHeader>
                            <h4>{ruleTitle(item.rule, "aws")}</h4>
                            <ActionButtons>
                              {!isEditing ? (
                                <>
                                  <button onClick={() => onEdit("aws", item.index, item)}>
                                    <MdEdit /> EDIT
                                  </button>
                                  <button className="delete-btn" onClick={() => onDelete("aws", item.index)}>
                                    <MdDelete /> DELETE
                                  </button>
                                </>
                              ) : (
                                <>
                                  <button onClick={() => onSave("aws", item.index)}>Save</button>
                                  <button onClick={() => setEditingId(null)}>Cancel</button>
                                </>
                              )}
                            </ActionButtons>
                          </PolicyHeader>

                          {!isEditing ? (
                            ruleDetails(item.rule, "aws")
                          ) : (
                            <CodeEditorWrapper>
                              <Editor
                                value={editingYaml}
                                onValueChange={(code) => setEditingYaml(code)}
                                highlight={(code) => highlight(code, languages.yaml)}
                                padding={12}
                                style={{
                                  fontFamily: '"Fira Code","Fira Mono",monospace',
                                  fontSize: 12,
                                  backgroundColor: "#0F1535",
                                  borderRadius: 8,
                                  minHeight: 200,
                                  width: "100%",
                                }}
                              />
                            </CodeEditorWrapper>
                          )}
                        </PolicyContent>
                      </PolicyItemCard>
                    );
                  })}
                </LeftScroll>

                <RightPanel>
                  <SectionTitle>YAML Editor (Whole Policy)</SectionTitle>
                  <EditorScrollBox>
                    <CodeEditorWrapper>
                      <Editor
                        value={yaml.dump({
                          mode: (() => { try { return yaml.load(rawYamlText)?.mode || "overwrite"; } catch { return "overwrite"; } })(),
                          rules: [...workingOnp, ...workingAws],
                        })}
                        onValueChange={(txt) => {
                          setRawYamlText(txt);
                          try {
                            const parsed = yaml.load(txt);
                            const onp = (parsed?.rules || []).filter((r) => r.platform === "on-premise");
                            const aws = (parsed?.rules || []).filter((r) => r.platform === "aws");
                            setWorkingOnp(onp);
                            setWorkingAws(aws);
                            setEditingId(null);
                          } catch { /* 최종 적용 시 검증 */ }
                        }}
                        highlight={(code) => highlight(code, languages.yaml)}
                        padding={12}
                        style={{ fontFamily: '"Fira Code","Fira Mono",monospace', fontSize: 12, backgroundColor: "transparent", minHeight: 400, width: "100%" }}
                      />
                    </CodeEditorWrapper>
                  </EditorScrollBox>

                  {applyResult && (
                    <ResultDisplay style={{ color: applyResult.status === "success" ? "#68D391" : "#FC8181" }}>
                      <strong>{applyResult.status?.toUpperCase()}:</strong> {applyResult.message}
                    </ResultDisplay>
                  )}

                  <ApplyButton
                    onClick={handleApplyPolicy}
                    disabled={
                      isApplying ||
                      (makeDiff(onpremPolicies, workingOnp, "on-premise")
                        .concat(makeDiff(awsPolicies, workingAws, "aws"))
                        .filter((d) => d.status !== "unchanged").length === 0)
                    }
                  >
                    {isApplying ? "Applying..." : "Confirm & Apply"}
                  </ApplyButton>
                </RightPanel>
              </>
            )}
          </ModalContent>
        </ModalOverlay>
      )}
    </PageContainer>
  );
};

export default Policy;
