// src/pages/Reports.jsx
import React, { useState } from 'react'; // [수정됨] useState를 import에 추가했습니다.
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { MdDateRange, MdTopic, MdFileCopy, MdAddAlert, MdNotificationsOff, MdAdd } from 'react-icons/md';

// --- Styled Components ---
const PageContainer = styled.div`
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
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
  h2 { font-size: 20px; border-bottom: 1px solid #2D2E5F; padding-bottom: 8px; margin-top: 0; }
  p { line-height: 1.6; }
  ul { padding-left: 20px; }
  code {
    background-color: #0F1535; padding: 2px 6px; border-radius: 4px;
    font-family: 'Fira Code', monospace;
  }
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
    color: ${({ type }) => (type === 'added' ? '#01B574' : '#E31A1A')};
  }
  
  span { color: #A0AEC0; margin-left: auto; }
`;

// --- Reports 페이지 메인 컴포넌트 ---
const Reports = () => {
  const [dateRange, setDateRange] = useState('');
  const [reportTopic, setReportTopic] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportContent, setReportContent] = useState('');

  const canGenerate = dateRange && reportTopic;

  const handleGenerateReport = () => {
    if (!canGenerate) return;

    setIsGenerating(true);
    setReportContent('AI generating a report... 🤖');
    
    setTimeout(() => {
      const generatedReport = `
## ${reportTopic} 분석 리포트 (${dateRange})

지난 선택된 기간 동안 **${reportTopic}** 데이터를 분석한 결과, 몇 가지 주요 동향과 이상 징후가 발견되었습니다.

### 주요 발견 사항
- **총 ${Math.floor(Math.random() * 100 + 50)}개의 정책 변경**이 감지되었으며, 이 중 ${Math.floor(Math.random() * 10 + 1)}개가 긴급 조치가 필요한 것으로 확인되었습니다.
- 특정 IP 대역(\`192.168.1.0/24\`)에서의 비정상적인 트래픽이 **${Math.floor(Math.random() * 30 + 10)}% 증가**했습니다.
- \`Allow-Public-Web-Traffic\` 정책에 대한 접근 시도가 평소보다 **${Math.floor(Math.random() * 200)}% 급증**했습니다.

### AI 추천 조치
1. '긴급'으로 분류된 정책 변경 사항에 대해 즉시 검토가 필요합니다.
2. \`192.168.1.0/24\` 대역에 대한 모니터링 강화를 권장합니다.
`;
      setReportContent(generatedReport);
      setIsGenerating(false);
    }, 2000);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(reportContent)
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
              <SmallButton onClick={handleGenerateReport} disabled={!canGenerate || isGenerating}>
                {isGenerating ? 'Generating...' : 'Generate'}
              </SmallButton>
            </CardHeader>
            <InputGroup>
              <SelectWrapper>
                <MdDateRange />
                <Select value={dateRange} onChange={e => setDateRange(e.target.value)}>
                  <option value="">Select Date Range</option>
                  <option value="Last 7 days">Last 7 days</option>
                  <option value="Last 30 days">Last 30 days</option>
                </Select>
              </SelectWrapper>
              <SelectWrapper>
                <MdTopic />
                <Select value={reportTopic} onChange={e => setReportTopic(e.target.value)}>
                  <option value="">Select Topic</option>
                  <option value="Policy Changes">Policy Changes</option>
                  <option value="Suspicious Logs">Suspicious Logs</option>
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
              <ReactMarkdown>{reportContent || 'Please generate a report to see the content.'}</ReactMarkdown>
            </MarkdownWrapper>
            <Button style={{ marginTop: '24px', alignSelf: 'flex-start', width: 'auto', padding: '8px 16px' }} onClick={handleCopy} disabled={!reportContent || isGenerating}>
              <MdFileCopy style={{marginRight: '8px'}} />
              Copy to Clipboard
            </Button>
          </ReportDisplayCard>
        </div>

        <Card>
          <CardHeader>
            <TitleGroup>
              <CardTitle>Existing Alarms List</CardTitle>
              <CardSubtitle>Manage alarms that trigger on specific conditions.</CardSubtitle>
            </TitleGroup>
            <SmallButton><MdAdd /> Add Alarm</SmallButton>
          </CardHeader>
          <AlarmList>
            <AlarmItem type="added">
              <MdAddAlert /> DB Server Access Fail <span>Slack</span>
            </AlarmItem>
            <AlarmItem type="deleted">
              <MdNotificationsOff /> Deprecated FTP Traffic <span>Email</span>
            </AlarmItem>
            <AlarmItem type="added">
              <MdAddAlert /> Web Server Auth Bypass <span>Slack</span>
            </AlarmItem>
          </AlarmList>
        </Card>
      </ReportsGrid>
    </PageContainer>
  );
};

export default Reports;