// src/pages/Policy.jsx
import React, { useState, useCallback } from 'react';
import styled, { css } from 'styled-components';
import { useDropzone } from 'react-dropzone';
import yaml from 'js-yaml';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-yaml';
import 'prismjs/themes/prism-tomorrow.css';
import { MdFileUpload, MdArrowUpward, MdArrowDownward, MdRemove, MdEdit, MdDelete } from 'react-icons/md';

// --- Styled Components ---

/** 페이지 전체 영역: 사이드바 옆 가용폭을 꽉 채우고, 세로로도 꽉 차게 */
const PageContainer = styled.div`
  box-sizing: border-box;
  width: 100%;
  min-height: 100vh;          /* 화면 세로 꽉 채움 */
  padding: 24px 28px 120px;   /* 하단 여유를 넉넉히 줘서 '깨짐' 방지 */
  margin: 0;                  /* 중앙정렬 대신 가용폭 전체 사용 */
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const PageHeader = styled.div`
  h1 {
    font-size: 24px;
    font-weight: 500;
    margin: 0;
    span { color: #A0AEC0; font-weight: 400; }
  }
`;

/** 공통 카드: 가로 100%로 꽉 채움 */
const Card = styled.div`
  box-sizing: border-box;
  width: 100%;
  background: linear-gradient(128deg, rgba(36, 41, 79, 0.94) 0%, rgba(9, 14, 35, 0.49) 100%);
  border-radius: 20px;
  padding: 24px;
  backdrop-filter: blur(60px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

/** 업로드 드롭존: 가운데 정렬 + 세로 충분한 높이 */
const DropzoneContainer = styled(Card)`
  display: flex;
  flex-direction: column;
  align-items: center;    /* 내부 아이콘/텍스트 중앙정렬 */
  justify-content: center;
  min-height: 60vh;       /* 화면의 절반 이상 차지해서 '깨짐' 방지 */
  border: 2px dashed #2D2E5F;
  cursor: pointer;
  transition: border-color 0.3s ease;

  &:hover { border-color: #0075FF; }
  p { color: #A0AEC0; font-size: 14px; margin-top: 1rem; }
`;

const PolicyItemCard = styled(Card)`
  display: flex;
  align-items: flex-start;
  gap: 16px;
`;

const StatusIcon = styled.div`
  width: 40px; height: 40px; min-width: 40px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;

  ${({ status }) => {
    switch (status) {
      case 'added':    return css` border: 1px solid #01B574; color: #01B574; `;
      case 'deleted':  return css` border: 1px solid #E31A1A; color: #E31A1A; `;
      case 'modified': return css` border: 1px solid #F6AD55; color: #F6AD55; `;
      default:         return css` border: 1px solid #A0AEC0; color: #A0AEC0; `;
    }
  }}
`;

const PolicyContent = styled.div`
  flex: 1 1 auto;        /* 가용 공간을 모두 차지 */
  min-width: 0;          /* 긴 내용 줄바꿈 허용 */
`;

const PolicyHeader = styled.div`
  display: flex;
  justify-content: space-between; /* 좌제목-우버튼 */
  align-items: center;
  margin-bottom: 16px;

  h4 { font-size: 14px; font-weight: 500; margin: 0; }
`;

const ActionButtons = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;

  button {
    background: none; border: none; color: #A0AEC0;
    display: inline-flex; align-items: center;
    cursor: pointer; padding: 6px 10px; border-radius: 8px;

    &:hover { color: white; background: rgba(255,255,255,0.06); }
    svg { margin-right: 4px; }
  }

  .delete-btn { &:hover { color: #E31A1A; background: rgba(227,26,26,0.08); } }
`;

const PolicyDetails = styled.div`
  color: #A0AEC0;
  font-size: 12px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
`;

const CodeEditorWrapper = styled.div`
  width: 100%;
  .npm__react-simple-code-editor__textarea { outline: none !important; }
`;

// --- Policy 페이지 메인 컴포넌트 ---
const Policy = () => {
  const [policies, setPolicies] = useState(null);
  const [editingPolicy, setEditingPolicy] = useState(null);
  const [currentCode, setCurrentCode] = useState('');

  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0];
    const reader = new FileReader();
    reader.onload = () => {
      const fileContent = reader.result;
      try {
        const parsedYaml = yaml.load(fileContent);
        const policiesWithStatus = parsedYaml.policies.map((p, index) => {
          const statuses = ['added', 'modified', 'deleted', 'unchanged'];
          return { ...p, id: index, status: statuses[index % statuses.length] };
        });
        setPolicies(policiesWithStatus);
      } catch (e) {
        console.error("YAML 파싱 오류:", e);
        alert("올바른 YAML 파일이 아닙니다.");
      }
    };
    reader.readAsText(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/x-yaml': ['.yaml', '.yml'] }
  });

  const handleEdit = (policy) => {
    setEditingPolicy(policy.id);
    setCurrentCode(yaml.dump(policy));
  };

  const handleSave = (policyId) => {
    try {
      const updatedPolicy = yaml.load(currentCode);
      setPolicies(policies.map(p => (p.id === policyId ? { ...updatedPolicy, id: policyId } : p)));
      setEditingPolicy(null);
      setCurrentCode('');
    } catch(e) {
      alert("YAML 형식이 올바르지 않습니다.");
    }
  };

  const getStatusIcon = (status) => {
    if (status === 'added') return <MdArrowUpward />;
    if (status === 'deleted') return <MdArrowDownward />;
    return <MdRemove />;
  };

  return (
    <PageContainer>
      <PageHeader>
        <h1><span>Pages /</span> Policy</h1>
      </PageHeader>

      {!policies ? (
        <DropzoneContainer {...getRootProps()}>
          <input {...getInputProps()} />
          <MdFileUpload size={56} color="#A0AEC0" />
          {isDragActive ? (
            <p>파일을 이곳에 드롭하세요...</p>
          ) : (
            <p>분석할 YAML 파일을 드래그 앤 드롭하거나 클릭하여 선택하세요.</p>
          )}
        </DropzoneContainer>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, width: '100%' }}>
          {policies.map(policy => (
            <PolicyItemCard key={policy.id}>
              <StatusIcon status={policy.status}>{getStatusIcon(policy.status)}</StatusIcon>
              <PolicyContent>
                <PolicyHeader>
                  <h4>{policy.name}</h4>
                  <ActionButtons>
                    {editingPolicy === policy.id ? (
                      <>
                        <button onClick={() => handleSave(policy.id)}>Save</button>
                        <button onClick={() => setEditingPolicy(null)}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => handleEdit(policy)}><MdEdit /> EDIT</button>
                        <button className="delete-btn"><MdDelete /> DELETE</button>
                      </>
                    )}
                  </ActionButtons>
                </PolicyHeader>

                {editingPolicy === policy.id ? (
                  <CodeEditorWrapper>
                    <Editor
                      value={currentCode}
                      onValueChange={code => setCurrentCode(code)}
                      highlight={code => highlight(code, languages.yaml)}
                      padding={12}
                      style={{
                        fontFamily: '"Fira Code","Fira Mono",monospace',
                        fontSize: 12,
                        backgroundColor: '#0F1535',
                        borderRadius: 8,
                        minHeight: 240,
                        width: '100%'
                      }}
                    />
                  </CodeEditorWrapper>
                ) : (
                  <PolicyDetails>
                    {policy?.spec
                      ? Object.entries(policy.spec).map(([key, value]) => (
                          <div key={key}><strong>{key}:</strong> {JSON.stringify(value)}</div>
                        ))
                      : <div>내용이 없습니다.</div>
                    }
                  </PolicyDetails>
                )}
              </PolicyContent>
            </PolicyItemCard>
          ))}
        </div>
      )}
    </PageContainer>
  );
};

export default Policy;
