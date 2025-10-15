// src/pages/Reports.jsx
import React, { useState } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { MdDateRange, MdTopic, MdFileCopy, MdAddAlert, MdNotificationsOff, MdAdd } from 'react-icons/md';
import axios from 'axios';

// --- axios ---
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 20000,
});

// --- Styled Components ---
const PageContainer = styled.div`
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px;
  box-sizing: border-box;
`;

const PageHeader = styled.div`
  margin-bottom: 2rem;
  h1 {
    font-size: 24px; font-weight: 500; margin: 0;
    span { color: #A0AEC0; font-weight: 400; }
  }
`;

const ReportsGrid = styled.div`
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 24px;
  align-items: start;
`;

const Card = styled.div`
  background: linear-gradient(128deg, rgba(36, 41, 79, 0.94) 0%, rgba(9, 14, 35, 0.49) 100%);
  border-radius: 20px;
  padding: 24px;
  backdrop-filter: blur(60px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 내부 요소가 넘치지 않도록 */
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
`;

const TitleGroup = styled.div``;

const CardTitle = styled.h3`
  font-size: 18px;
  margin: 0 0 8px 0;
`;

const CardSubtitle = styled.p`
  font-size: 14px;
  color: #A0AEC0;
  margin: 0;
`;

const InputGroup = styled.div`
  display: flex;
  gap: 16px;
`;

const SelectWrapper = styled.div`
  position: relative;
  flex: 1;
  svg {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #A0AEC0;
  }
`;

const Select = styled.select`
  width: 100%;
  background: #0F1535;
  border: 1px solid #2D2E5F;
  border-radius: 12px;
  color: white;
  padding: 12px 12px 12px 45px;
  font-size: 14px;
`;

const Button = styled.button`
  background: ${({ disabled }) => (disabled ? '#2D2E5F' : '#0075FF')};
  border: none;
  border-radius: 12px;
  color: ${({ disabled }) => (disabled ? '#A0AEC0' : 'white')};
  font-weight: 700;
  padding: 12px;
  cursor: ${({ disabled }) => (disabled ? 'not-allowed' : 'pointer')};
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SmallButton = styled(Button)`
  padding: 8px 16px;
  font-size: 12px;
  width: auto;
`;

const ReportDisplayCard = styled(Card)`
  margin-top: 24px;
  min-height: 400px;
  flex-grow: 1;
`;

const MarkdownWrapper = styled.div`
  flex-grow: 1;
  color: #E2E8F0;
  max-width: 100%;
  overflow-x: hidden;
  word-break: break-word;

  h1, h2, h3 { margin: 1.2rem 0 .6rem; }
  h2 { font-size: 20px; border-bottom: 1px solid #2D2E5F; padding-bottom: 8px; }
  p { line-height: 1.7; margin: .4rem 0; }
  ul, ol { padding-left: 1.2rem; }
  code { background-color: #0F1535; padding: 2px 6px; border-radius: 4px; font-family: 'Fira Code', monospace; }
  pre { background: #0B1230; padding: 12px; border-radius: 10px; border: 1px solid #2D2E5F; overflow-x: auto; white-space: pre-wrap; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #2D2E5F; padding: 6px 8px; }
`;

const AlarmList = styled.ul`
  list-style: none; padding: 0; margin: 0;
`;

const AlarmItem = styled.li`
  display: flex;
  align-items: center;
  padding: 12px 0;
  font-size: 14px;
  border-bottom: 1px solid #2D2E5F;
  &:last-child { border-bottom: none; }
  
  svg {
    margin-right: 12px; font-size: 18px;
    color: ${({ $type }) => ($type === 'added' ? '#01B574' : '#E31A1A')};
  }
  
  span { color: #A0AEC0; margin-left: auto; }
`;

// --- 헬퍼: 서버가 ```로 감싼 MD를 보내면 벗겨주기 ---
const normalizeMarkdown = (md) => {
  if (!md) return '';
  const trimmed = md.trim();
  if (trimmed.startsWith('```')) {
    // 첫 줄의 ```lang 제거
    const withoutOpen = trimmed.replace(/^```[a-zA-Z0-9-]*\n?/, '');
    // 마지막 ``` 제거
    return withoutOpen.replace(/```$/, '').trim();
  }
  return md;
};

// --- Reports 페이지 ---
const Reports = () => {
  const [range, setRange] = useState('daily'); // 10min|hourly|daily|weekly
  const [topic, setTopic] = useState('general'); // general|onprem|cloud
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportContent, setReportContent] = useState('');

  const canGenerate = !!range && !!topic;

  const fetchReport = async () => {
    if (!canGenerate || isGenerating) return;

    try {
      setIsGenerating(true);
      setReportContent('AI generating a report... 🤖');

      let res;
      if (topic === 'general') {
        res = await api.get('/api/logs/analysis-report', { params: { range } });
      } else if (topic === 'onprem') {
        res = await api.get('/api/policy/analysis-report', { params: { type: 'onprem', range } });
      } else if (topic === 'cloud') {
        res = await api.get('/api/policy/analysis-report', { params: { type: 'cloud', range } });
      }

      if (res?.data?.status === 'success') {
        setReportContent(normalizeMarkdown(res.data.report));
      } else {
        setReportContent('❌ Failed to generate report. Please try again.');
      }
    } catch (e) {
      console.error(e);
      setReportContent('❌ Error while generating report.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(reportContent || '')
      .then(() => alert('리포트 내용이 클립보드에 복사되었습니다.'))
      .catch(err => console.error('복사 실패:', err));
  };

  return (
    <PageContainer>
      <PageHeader>
        <h1><span>Pages /</span> Reports</h1>
      </PageHeader>
      
      <ReportsGrid>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Card>
            <CardHeader>
              <TitleGroup>
                <CardTitle>Generate Reports</CardTitle>
                <CardSubtitle>Select period and topic to generate AI-powered reports.</CardSubtitle>
              </TitleGroup>
              <SmallButton onClick={fetchReport} disabled={!canGenerate || isGenerating}>
                {isGenerating ? 'Generating...' : 'Generate'}
              </SmallButton>
            </CardHeader>

            <InputGroup>
              <SelectWrapper>
                <MdDateRange />
                {/* 기간: 로그 페이지와 동일 옵션 */}
                <Select value={range} onChange={e => setRange(e.target.value)}>
                  <option value="10min">Last 10 minutes</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </Select>
              </SelectWrapper>

              <SelectWrapper>
                <MdTopic />
                {/* 토픽: 세 가지로 통일 */}
                <Select value={topic} onChange={e => setTopic(e.target.value)}>
                  <option value="general">General Logs</option>
                  <option value="onprem">Policy On-Prem Logs</option>
                  <option value="cloud">Policy Cloud Logs</option>
                </Select>
              </SelectWrapper>
            </InputGroup>
          </Card>

          <ReportDisplayCard>
            <CardHeader>
              <TitleGroup>
                <CardTitle>Report</CardTitle>
                <CardSubtitle>This is an AI-generated report based on your selection.</CardSubtitle>
              </TitleGroup>
            </CardHeader>

            <MarkdownWrapper>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
              >
                {reportContent || 'Please generate a report to see the content.'}
              </ReactMarkdown>
            </MarkdownWrapper>

            <Button
              style={{ marginTop: '24px', alignSelf: 'flex-start', width: 'auto', padding: '8px 16px' }}
              onClick={handleCopy}
              disabled={!reportContent || isGenerating}
            >
              <MdFileCopy style={{marginRight: '8px'}} />
              Copy to Clipboard
            </Button>
          </ReportDisplayCard>
        </div>

        {/* 알람은 목업 유지 */}
        <Card>
          <CardHeader>
            <TitleGroup>
              <CardTitle>Existing Alarms List</CardTitle>
              <CardSubtitle>Manage alarms that trigger on specific conditions.</CardSubtitle>
            </TitleGroup>
            <SmallButton><MdAdd /> Add Alarm</SmallButton>
          </CardHeader>
          <AlarmList>
            <AlarmItem $type="added">
              <MdAddAlert /> DB Server Access Fail <span>Slack</span>
            </AlarmItem>
            <AlarmItem $type="deleted">
              <MdNotificationsOff /> Deprecated FTP Traffic <span>Email</span>
            </AlarmItem>
            <AlarmItem $type="added">
              <MdAddAlert /> Web Server Auth Bypass <span>Slack</span>
            </AlarmItem>
          </AlarmList>
        </Card>
      </ReportsGrid>
    </PageContainer>
  );
};

export default Reports;
