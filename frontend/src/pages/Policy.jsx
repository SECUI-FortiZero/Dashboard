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

// API 호출 함수
import { getCurrentPolicies, applyNewPolicy } from "../apis/policyApi";

/* =================== Styled =================== */

// 공통 스크롤바 숨김 믹스인
const hideScrollbar = css`
  /* Chrome, Safari, Edge */
  &::-webkit-scrollbar {
    display: none;
    width: 0;
    height: 0;
  }
  /* Firefox */
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
    font-size: 24px;
    font-weight: 500;
    margin: 0;
    span {
      color: #a0aec0;
      font-weight: 400;
    }
  }
`;

const ApplyButton = styled.button`
  background: #0075ff;
  color: white;
  font-weight: 500;
  font-size: 14px;
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s ease, opacity 0.3s ease;
  &:hover {
    background: #005ecc;
  }
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  width: 100%;
  @media (min-width: 1024px) {
    grid-template-columns: 1fr 1fr;
  }
`;

const Card = styled.div`
  box-sizing: border-box;
  width: 100%;
  background: linear-gradient(
    128deg,
    rgba(36, 41, 79, 0.94) 0%,
    rgba(9, 14, 35, 0.49) 100%
  );
  border-radius: 20px;
  padding: 24px;
  backdrop-filter: blur(60px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  h2 {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 16px;
  }
`;

const TableScroll = styled.div`
  max-height: 60vh;
  overflow-y: auto;
  ${hideScrollbar}
`;

const PolicyTable = styled.table`
  width: 100%;
  font-size: 12px;
  border-collapse: collapse;
  th,
  td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    white-space: nowrap;
  }
  th {
    color: #a0aec0;
    font-weight: 400;
  }
  td {
    color: #e2e8f0;
    vertical-align: top;
  }
  tr:last-child td {
    border-bottom: none;
  }
  code {
    background: rgba(0, 0, 0, 0.2);
    padding: 2px 5px;
    border-radius: 4px;
    font-family: "Fira Code", monospace;
    white-space: pre-wrap;
    word-break: break-all;
  }
`;

const ModalOverlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  width: 94%;
  max-width: 1080px;
  height: 92vh; /* 고정 높이 */
  background: #1a202c;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 28px;
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 20px;
  position: relative;
  overflow: hidden;
  h2 {
    font-size: 20px;
    margin: 0 0 6px 0;
    grid-column: 1 / -1;
  }
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
  .close-btn {
    position: absolute;
    top: 16px;
    right: 16px;
    background: none;
    border: none;
    color: #a0aec0;
    font-size: 24px;
    cursor: pointer;
  }
`;

const Dropzone = styled.div`
  border: 2px dashed #4a5568;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s ease;
  &:hover {
    border-color: #0075ff;
  }
  p {
    color: #a0aec0;
  }
  grid-column: 1 / -1;
`;

const ResultDisplay = styled.pre`
  background: #0f1535;
  border-radius: 8px;
  padding: 16px;
  font-family: "Fira Code", monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 250px;
  overflow-y: auto;
  ${hideScrollbar}
  border: 1px solid #2d3748;
  grid-column: 1 / -1;
`;

const PolicyItemCard = styled(Card)`
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  opacity: ${({ status }) => (status === "deleted" ? 0.6 : 1)};
  border-left: 5px solid;
  border-color: transparent;
  ${({ status }) => {
    switch (status) {
      case "added":
        return css`
          border-left-color: #01b574;
        `;
      case "deleted":
        return css`
          border-left-color: #e31a1a;
        `;
      case "modified":
        return css`
          border-left-color: #f6ad55;
        `;
      default:
        return css``;
    }
  }}
`;

const StatusIcon = styled.div`
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  ${({ status }) => {
    switch (status) {
      case "added":
        return css`
          background: rgba(1, 181, 116, 0.1);
          color: #01b574;
        `;
      case "deleted":
        return css`
          background: rgba(227, 26, 26, 0.1);
          color: #e31a1a;
        `;
      case "modified":
        return css`
          background: rgba(246, 173, 85, 0.1);
          color: #f6ad55;
        `;
      default:
        return css`
          background: rgba(160, 174, 192, 0.1);
          color: #a0aec0;
        `;
    }
  }}
`;

const PolicyContent = styled.div`
  flex: 1 1 auto;
  min-width: 0;
`;

const PolicyHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  h4 {
    font-size: 14px;
    font-weight: 600;
    margin: 0;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  button {
    background: none;
    border: none;
    color: #a0aec0;
    display: inline-flex;
    align-items: center;
    cursor: pointer;
    padding: 6px 10px;
    border-radius: 8px;
    &:hover {
      color: white;
      background: rgba(255, 255, 255, 0.06);
    }
    svg {
      margin-right: 4px;
    }
  }
  .delete-btn:hover {
    color: #e31a1a;
    background: rgba(227, 26, 26, 0.08);
  }
`;

const PolicyDetails = styled.div`
  color: #a0aec0;
  font-size: 12px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
`;

const CodeEditorWrapper = styled.div`
  width: 100%;
  ${hideScrollbar}
  .npm__react-simple-code-editor__textarea {
    outline: none !important;
  }
`;

const LeftScroll = styled.div`
  overflow: auto;
  ${hideScrollbar}
  max-height: calc(92vh - 28px - 28px - 32px); /* 모달 패딩/타이틀 여백 감안 */
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const RightPanel = styled(Card)`
  padding: 14px;
  display: grid;
  grid-template-rows: auto 1fr auto; /* 타이틀/에디터/버튼 */
  gap: 10px;
  height: 100%; /* 모달 셀 높이 꽉 채움 */
  overflow: hidden;
`;

const SectionTitle = styled.h3`
  margin: 0 0 6px 0;
  font-weight: 600;
  font-size: 14px;
`;

const EditorScrollBox = styled.div`
  overflow: auto;
  ${hideScrollbar}
  border-radius: 8px;
  border: 1px solid #2d3748;
  background: #0f1535;
  max-height: 100%;
`;

/* =================== Diff helpers =================== */

// 핵심키 정의
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

const equalMeta = (a, b) => (a?.action ?? "") === (b?.action ?? "") && (a?.comment ?? "") === (b?.comment ?? "");

const isDeleteOp = (r) => String(r?.operation || "").toLowerCase() === "delete";

/**
 * Diff 정책:
 * - 업로드(YAML)에 없는 규칙: 유지(unchanged)
 * - 업로드에 있고 operation: delete: deleted
 * - 업로드에 있고 메타(action/comment)만 변경: modified
 * - 업로드에만 있고 delete가 아님: added
 * - 업로드에 delete인데 현재에 없는 규칙: 무시
 */
function makeDiff(currentArr, newArr, platform) {
  const idFn = platform === "on-premise" ? idOnPrem : idAws;

  const curMap = new Map(currentArr.map((r) => [idFn(r), r]));
  const newMap = new Map(newArr.map((r) => [idFn(r), r]));

  const out = [];

  // 현재 기준 평가
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

  // 신규 추가 탐지
  for (const [id, up] of newMap.entries()) {
    if (!curMap.has(id)) {
      if (isDeleteOp(up)) continue; // 현재에 없는데 delete면 무시
      out.push({ platform, status: "added", rule: up });
    }
  }

  return out;
}

/* =================== Component =================== */
const Policy = () => {
  // 현재(서버) 정책
  const [onpremPolicies, setOnpremPolicies] = useState([]);
  const [awsPolicies, setAwsPolicies] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 모달 / 업로드 / 적용
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [rawYamlText, setRawYamlText] = useState("");
  const [applyResult, setApplyResult] = useState(null);
  const [isApplying, setIsApplying] = useState(false);

  // 작업중 제안안(working) 규칙 세트
  const [workingOnp, setWorkingOnp] = useState([]);
  const [workingAws, setWorkingAws] = useState([]);

  // per-item 편집 상태
  const [editingId, setEditingId] = useState(null);
  const [editingYaml, setEditingYaml] = useState("");

  // 초기 로드
  const fetchPolicies = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCurrentPolicies();
      if (data.status === "success") {
        setOnpremPolicies(data.data.on_premise || []);
        setAwsPolicies(data.data.aws || []);
      } else {
        throw new Error(data.message);
      }
    } catch (err) {
      setError(err.message || "Failed to fetch");
    } finally {
      setIsLoading(false);
    }
  }, []);
  useEffect(() => {
    fetchPolicies();
  }, [fetchPolicies]);

  // 모달 열릴 때 배경 스크롤 잠금
  useEffect(() => {
    if (isModalOpen) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = prev;
      };
    }
  }, [isModalOpen]);

  // YAML 드롭/업로드 → working 세팅
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
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

        setUploadedFile(file);
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

  // 현재 vs working diff
  const diffs = useMemo(() => {
    return {
      onp: makeDiff(onpremPolicies, workingOnp, "on-premise"),
      aws: makeDiff(awsPolicies, workingAws, "aws"),
    };
  }, [onpremPolicies, workingOnp, awsPolicies, workingAws]);

  // 카드 타이틀/디테일
  const ruleTitle = (r, platform) => {
    const del = isDeleteOp(r) ? " [DELETE]" : "";
    if (platform === "on-premise") {
      return `[On-prem] ${r.chain} ${r.protocol}/${r.port} ${r.source_ip ?? ""} → ${
        r.destination_ip ?? ""
      } (${r.action})${del}`;
    } else {
      const src = r.source_ip || r.source_sg || "-";
      return `[AWS] ${r.target_sg} ← ${src} ${r.protocol}/${r.port} (${r.action || "allow"})${del}`;
    }
  };
  const ruleDetails = (r, platform) => {
    const keys =
      platform === "on-premise"
        ? ["platform", "chain", "protocol", "port", "source_ip", "destination_ip", "action", "comment", "operation"]
        : ["platform", "target_sg", "protocol", "port", "source_ip", "source_sg", "action", "comment", "operation"];
    return (
      <PolicyDetails>
        {keys.map((k) => (
          <div key={k}>
            <strong>{k}:</strong> {String(r?.[k] ?? "")}
          </div>
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
        const next = [...workingOnp];
        next[index] = obj;
        setWorkingOnp(next);
      } else {
        const next = [...workingAws];
        next[index] = obj;
        setWorkingAws(next);
      }
      setEditingId(null);
      setEditingYaml("");
    } catch (e) {
      alert("YAML 형식 오류: " + e.message);
    }
  };
  const onDelete = (platform, index) => {
    if (!confirm("Remove this rule from the proposed policy?")) return;
    if (platform === "on-premise") {
      const next = [...workingOnp];
      next.splice(index, 1);
      setWorkingOnp(next);
    } else {
      const next = [...workingAws];
      next.splice(index, 1);
      setWorkingAws(next);
    }
  };

  // 렌더 리스트: working 기준(업로드/편집본만)
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

  // 적용: 편집 반영본으로 YAML 재생성 후 전송(삭제 플래그 포함)
  const handleApplyPolicy = async () => {
    // 기존 YAML의 mode 유지(없으면 overwrite)
    let mode = "overwrite";
    try {
      const d = yaml.load(rawYamlText);
      if (typeof d?.mode === "string") mode = d.mode;
    } catch {}

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
      if (res.status === "success") {
        setTimeout(async () => {
          setIsModalOpen(false);
          await fetchPolicies();
        }, 1000);
      }
    } catch (err) {
      setApplyResult({ status: "error", message: err.message || "Apply failed" });
    } finally {
      setIsApplying(false);
    }
  };

  const openModal = () => {
    setIsModalOpen(true);
    setUploadedFile(null);
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

  /* =================== Render =================== */

  if (isLoading) return <PageContainer><h1>Loading...</h1></PageContainer>;
  if (error) return <PageContainer><h1>Error: {error}</h1></PageContainer>;

  return (
    <PageContainer>
      <PageHeader>
        <h1>
          <span>Pages /</span> Policy Management
        </h1>
        <ApplyButton onClick={openModal}>
          <MdCloudUpload /> Apply New Policy
        </ApplyButton>
      </PageHeader>

      {/* 현재 정책 테이블(초기 화면 유지) */}
      <ContentGrid>
        <Card>
          <h2>🏢 On-Premise Policies (iptables)</h2>
          <TableScroll>
            <PolicyTable>
              <thead>
                <tr>
                  <th>Chain</th>
                  <th>Source/Dest</th>
                  <th>Port</th>
                  <th>Action</th>
                  <th>Comment</th>
                </tr>
              </thead>
              <tbody>
                {onpremPolicies.map((p, i) => (
                  <tr key={i}>
                    <td>
                      <code>{p.chain || "INPUT"}</code>
                    </td>
                    <td>
                      <code>{p.source_ip || p.destination_ip || "any"}</code>
                    </td>
                    <td>
                      <code>{p.port || "any"}</code>
                    </td>
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
                <tr>
                  <th>Target SG</th>
                  <th>Source</th>
                  <th>Port</th>
                  <th>Protocol</th>
                  <th>Comment</th>
                </tr>
              </thead>
              <tbody>
                {awsPolicies.map((p, i) => (
                  <tr key={i}>
                    <td>
                      <code>{p.target_sg}</code>
                    </td>
                    <td>
                      <code>{p.source_ip || p.source_sg}</code>
                    </td>
                    <td>
                      <code>{p.port}</code>
                    </td>
                    <td>{p.protocol}</td>
                    <td>{p.comment}</td>
                  </tr>
                ))}
              </tbody>
            </PolicyTable>
          </TableScroll>
        </Card>
      </ContentGrid>

      {/* 모달: 업로드 → 기존 카드형 UI + 에디터 유지 */}
      {isModalOpen && (
        <ModalOverlay>
          <ModalContent>
            <button className="close-btn" onClick={() => setIsModalOpen(false)}>
              &times;
            </button>
            <h2>Apply New Policy</h2>

            {/* 업로드 전 */}
            {workingOnp.length === 0 && workingAws.length === 0 ? (
              <Dropzone {...getRootProps()}>
                <input {...getInputProps()} />
                <MdFileUpload size={40} style={{ margin: "0 auto 1rem" }} />
                <p>비교할 YAML 파일을 드래그하거나 클릭하여 선택하세요.</p>
              </Dropzone>
            ) : (
              <>
                {/* 좌: 기존 카드 리스트 + Diff 표시 (사이드바 없이, 내부 스크롤만) */}
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
                              {item.index >= 0 && (
                                <>
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
                              {item.index >= 0 && (
                                <>
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

                {/* 우: Whole YAML 에디터(고정 박스 + 내부 스크롤) + Apply 버튼 고정 */}
                <RightPanel>
                  <SectionTitle>YAML Editor (Whole Policy)</SectionTitle>

                  <EditorScrollBox>
                    <CodeEditorWrapper>
                      <Editor
                        value={yaml.dump({
                          mode: (() => {
                            try {
                              return yaml.load(rawYamlText)?.mode || "overwrite";
                            } catch {
                              return "overwrite";
                            }
                          })(),
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
                          } catch {
                            // 적용 시점에 검증
                          }
                        }}
                        highlight={(code) => highlight(code, languages.yaml)}
                        padding={12}
                        style={{
                          fontFamily: '"Fira Code","Fira Mono",monospace',
                          fontSize: 12,
                          backgroundColor: "transparent",
                          minHeight: 400,
                          width: "100%",
                        }}
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
