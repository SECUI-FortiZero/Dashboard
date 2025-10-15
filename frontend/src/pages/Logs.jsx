// src/pages/Logs.jsx
import React, { useState } from 'react';
import styled from 'styled-components';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { MdInfo } from 'react-icons/md';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

// --- axios 클라이언트 ---
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 20000,
});

// --- API 함수 ---
const fetchGeneralLogs = async (range) => {
  const { data } = await api.get('/api/logs', { params: { range } });
  if (data.status !== 'success') throw new Error(data.message);
  return data.data;
};

const fetchPolicyLogs = async (type, range) => {
  // 임시: 정책 로그도 /api/logs 로 가져오고 type 필터링한다고 가정
  const { data } = await api.get('/api/logs', { params: { range } });
  if (data.status !== 'success') throw new Error(data.message);
  // 정책 로그는 log_type으로 구분 (CLOUD/ONPREM)
  return data.data.filter((l) => l.log_type?.toLowerCase() === type);
};

// Threat Logs (항상 10분 단위)
const fetchThreatLogs = async () => {
  const { data } = await api.get('/api/logs/threats', { params: { range: '10min' } });
  if (data.status !== 'success') throw new Error(data.message);
  return data.threats;
};

// --- 목업 데이터 (로그 볼륨 차트만 유지) ---
const logVolumeData = [
  { name: 'Jan', volume: 4000 }, { name: 'Feb', volume: 3000 },
  { name: 'Mar', volume: 2000 }, { name: 'Apr', volume: 2780 },
  { name: 'May', volume: 1890 }, { name: 'Jun', volume: 2390 },
  { name: 'Jul', volume: 3490 }, { name: 'Aug', volume: 2800 },
  { name: 'Sep', volume: 3200 }, { name: 'Oct', volume: 3800 },
  { name: 'Nov', volume: 3500 }, { name: 'Dec', volume: 4100 },
];

// --- Styled Components ---
const PageContainer = styled.div`
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px 40px;
`;

const PageHeader = styled.div`
  margin: 24px 0 16px;
  h1 {
    font-size: 24px; font-weight: 500; margin: 0;
    span { color: #A0AEC0; font-weight: 400; }
  }
`;

const Card = styled.div`
  background: linear-gradient(175deg, rgba(6, 11, 38, 0.74) 0%, rgba(26, 31, 55, 0.50) 100%);
  border-radius: 20px;
  padding: 24px;
  backdrop-filter: blur(60px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 24px;
`;

const FilterBar = styled(Card)`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const Select = styled.select`
  background: #0F1535;
  border: 1px solid rgba(226, 232, 240, 0.3);
  border-radius: 12px;
  color: white;
  padding: 10px 15px;
  min-width: 200px;
`;

const Button = styled.button`
  background: #0075FF;
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 700;
  padding: 10px 20px;
  cursor: pointer;
  margin-left: auto;
`;

const Table = styled.div``;

const TableHeader = styled.div`
  display: grid;
  grid-template-columns: ${(p) => p.cols || '1fr 1fr 1fr 1fr 2fr'};
  padding: 16px;
  border-bottom: 1px solid #2D2E5F;
  span { color: #A0AEC0; font-size: 10px; font-weight: 500; text-transform: uppercase; }
`;

const TableRow = styled.div`
  position: relative;
  display: grid;
  grid-template-columns: ${(p) => p.cols || '1fr 1fr 1fr 1fr 2fr'};
  align-items: center;
  padding: 16px;
  font-size: 14px;
  &:not(:last-child) { border-bottom: 1px solid #2D2E5F; }

  &:hover .tooltip {
    visibility: visible;
    opacity: 1;
  }
`;

const TooltipStyled = styled.div`
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s;
  position: absolute;
  top: -40px;
  right: 20px;
  background-color: #1A1F37;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #2D2E5F;
  font-size: 12px;
  z-index: 10;
  white-space: nowrap;

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    right: 30px;
    border-width: 5px;
    border-style: solid;
    border-color: #1A1F37 transparent transparent transparent;
  }
`;

// --- Logs 페이지 메인 컴포넌트 ---
const Logs = () => {
  const [logType, setLogType] = useState('general');
  const [timeRange, setTimeRange] = useState('daily');

  // General Logs
  const { data: generalLogs = [], isLoading: loadingGeneral } = useQuery({
    queryKey: ['generalLogs', timeRange],
    queryFn: () => fetchGeneralLogs(timeRange),
    enabled: logType === 'general',
  });

  // Policy Logs
  const { data: policyLogs = [], isLoading: loadingPolicy } = useQuery({
    queryKey: ['policyLogs', logType, timeRange],
    queryFn: () => fetchPolicyLogs(logType, timeRange),
    enabled: logType === 'onprem' || logType === 'cloud',
  });

  // Threat Logs (항상 10분 단위 — 차트 아래 Full width로 표시)
  const { data: threatLogs = [], isLoading: loadingThreats } = useQuery({
    queryKey: ['threatLogs', '10min'],
    queryFn: fetchThreatLogs,
  });

  // 현재 선택된 로그 데이터
  let displayedLogs = [];
  if (logType === 'general') displayedLogs = generalLogs;
  if (logType === 'onprem') displayedLogs = policyLogs;
  if (logType === 'cloud') displayedLogs = policyLogs;

  return (
    <PageContainer>
      <PageHeader>
        <h1><span>Pages /</span> Logs</h1>
      </PageHeader>

      {/* 필터 바 */}
      <FilterBar>
        <Select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
          <option value="10min">Last 10 minutes</option>
          <option value="hourly">Hourly</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
        </Select>
        <Select value={logType} onChange={(e) => setLogType(e.target.value)}>
          <option value="general">General Logs</option>
          <option value="onprem">Policy On-Prem Logs</option>
          <option value="cloud">Policy Cloud Logs</option>
        </Select>
        <Button>Search</Button>
      </FilterBar>

      {/* 차트 */}
      <Card>
        <h3 style={{ marginTop: 0 }}>Log Data Volume</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={logVolumeData}>
            <defs>
              <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#01B574" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#01B574" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis dataKey="name" stroke="#56577A" fontSize="12px" />
            <YAxis stroke="#56577A" fontSize="12px" />
            <Tooltip contentStyle={{ backgroundColor: '#1A1F37', border: '1px solid #2D2E5F' }} />
            <Area type="monotone" dataKey="volume" stroke="#01B574" fillOpacity={1} fill="url(#colorVolume)" />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* ⬇️ 트리튼: 차트 바로 아래, 전체 폭 */}
      <Card>
        <h3 style={{ marginTop: 0 }}>AI Threat Detections</h3>
        {loadingThreats ? (
          <p>Loading threats...</p>
        ) : (
          <>
            <p style={{ color: '#A0AEC0', fontSize: '14px', marginBottom: '12px', display: 'flex', alignItems: 'center' }}>
              <MdInfo style={{ color: '#E31A1A', marginRight: '8px' }} />
              AI has detected {threatLogs.length} suspicious logs.
            </p>
            <Table>
              <TableHeader cols="1.6fr 1.2fr 1.2fr .8fr .8fr">
                <span>TIME</span>
                <span>SRC IP</span>
                <span>DST IP</span>
                <span>PORT</span>
                <span>PROTOCOL</span>
              </TableHeader>
              {threatLogs.map((t, idx) => (
                <TableRow key={idx} cols="1.6fr 1.2fr 1.2fr .8fr .8fr">
                  <div>{t.timestamp}</div>
                  <div>{t.src_ip}</div>
                  <div>{t.dst_ip}</div>
                  <div>{t.dst_port}</div>
                  <div>{t.protocol}</div>
                  <TooltipStyled className="tooltip">{t.reason}</TooltipStyled>
                </TableRow>
              ))}
            </Table>
          </>
        )}
      </Card>

      {/* Streaming Area */}
      <Card>
        <h3 style={{ marginTop: 0 }}>Streaming Area ({logType})</h3>
        {loadingGeneral || loadingPolicy ? (
          <p>Loading logs...</p>
        ) : (
          <Table>
            <TableHeader>
              <span>TIMESTAMP</span>
              <span>SRC IP</span>
              <span>DST IP</span>
              <span>PROTOCOL</span>
              <span>ACTION</span>
            </TableHeader>
            {displayedLogs.map((log, idx) => (
              <TableRow key={idx}>
                <div>{log.timestamp}</div>
                <div>{log.srcip}</div>
                <div>{log.dstip}</div>
                <div>{log.protocol}</div>
                <div>{log.action ?? '-'}</div>
              </TableRow>
            ))}
          </Table>
        )}
      </Card>
    </PageContainer>
  );
};

export default Logs;
