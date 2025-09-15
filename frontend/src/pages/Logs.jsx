// src/pages/Logs.jsx
import React, { useState } from 'react';
import styled from 'styled-components';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { MdInfo } from 'react-icons/md';

// --- 데이터 목업(Mock Data) ---
const logVolumeData = [
  { name: 'Jan', volume: 4000 }, { name: 'Feb', volume: 3000 },
  { name: 'Mar', volume: 2000 }, { name: 'Apr', volume: 2780 },
  { name: 'May', volume: 1890 }, { name: 'Jun', volume: 2390 },
  { name: 'Jul', volume: 3490 }, { name: 'Aug', volume: 2800 },
  { name: 'Sep', volume: 3200 }, { name: 'Oct', volume: 3800 },
  { name: 'Nov', volume: 3500 }, { name: 'Dec', volume: 4100 },
];

const streamingLogs = [
  { id: 1, timestamp: '09:15:27', sourceIP: '1.2.3.4', user: 'admin', action: 'SSH: FAILED', detail: 'Invalid password', aiComment: '[!] Brute-force 공격 시도(27회 실패)의 일부일 수 있습니다.' },
  { id: 2, timestamp: '09:15:31', sourceIP: '1.2.3.4', user: 'admin', action: 'SSH: SUCCESS', detail: 'Login successful', aiComment: '[!] Brute-force 공격(27회 실패 후 성공)으로 의심됩니다. 로그인 후 평소와 다른 `rm` 명령어가 사용되었습니다.' },
  { id: 3, timestamp: '09:16:02', sourceIP: '10.0.1.5', user: 'service-account', action: 'DB: QUERY', detail: "SELECT * FROM users;", aiComment: '[!] 웹서버 계정이 평소와 다른 `users` 테이블에 접근했습니다. 정보 유출 시도일 수 있습니다.' },
  { id: 4, timestamp: '09:18:21', sourceIP: '203.0.113.10', user: 'guest', action: 'WEB: GET', detail: "/search?q=' OR 1=1 --", aiComment: '[!] SQL Injection 공격 패턴이 탐지되었습니다.' },
];

// --- Styled Components ---
const PageContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
`;

const PageHeader = styled.div`
  margin-bottom: 2rem;
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
  margin-left: auto; /* 버튼을 오른쪽 끝으로 보냄 */
`;

const StreamingAreaHeader = styled.div`
  h3 { font-size: 18px; margin: 0 0 5px 0; }
  p { color: #A0AEC0; font-size: 14px; margin: 0; display: flex; align-items: center; }
  svg { color: #E31A1A; margin-right: 8px; }
`;

const Table = styled.div``;
const TableHeader = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 2fr;
  padding: 16px;
  border-bottom: 1px solid #2D2E5F;
  span { color: #A0AEC0; font-size: 10px; font-weight: 500; text-transform: uppercase; }
`;

const TableRow = styled.div`
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 2fr;
  align-items: center;
  padding: 16px;
  font-size: 14px;
  &:not(:last-child) { border-bottom: 1px solid #2D2E5F; }

  .detail-cell { color: #E31A1A; font-weight: 700; }

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
  top: -40px; /* 행 위로 띄움 */
  right: 20px;
  
  background-color: #1A1F37;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #2D2E5F;
  font-size: 12px;
  z-index: 10;
  white-space: nowrap;

  &::after { /* 말풍선 꼬리 */
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
  return (
    <PageContainer>
      <PageHeader>
        <h1><span>Pages /</span> Logs</h1>
      </PageHeader>

      <FilterBar>
        <Select>
          <option>All Logs</option>
          <option>FTP Server</option>
          <option>Web Server (Apache)</option>
          <option>Database (MySQL)</option>
        </Select>
        <Select>
          <option>Last 24 hours</option>
          <option>Last 7 days</option>
          <option>Last 30 days</option>
        </Select>
        <Button>Search</Button>
      </FilterBar>

      <Card>
        <h3>Log Data Volume</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={logVolumeData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
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
      
      <Card>
        <StreamingAreaHeader>
          <h3>Streaming Area</h3>
          <p><MdInfo />AI has detected {streamingLogs.length} suspicious logs.</p>
        </StreamingAreaHeader>
        <Table>
          <TableHeader>
            <span>TIMESTAMP</span>
            <span>SOURCE IP</span>
            <span>USER</span>
            <span>ACTION</span>
            <span>DETAIL</span>
          </TableHeader>
          {streamingLogs.map(log => (
            <TableRow key={log.id}>
              <div>{log.timestamp}</div>
              <div>{log.sourceIP}</div>
              <div>{log.user}</div>
              <div>{log.action}</div>
              <div className="detail-cell">{log.detail}</div>
              <TooltipStyled className="tooltip">
                {log.aiComment}
              </TooltipStyled>
            </TableRow>
          ))}
        </Table>
      </Card>
    </PageContainer>
  );
};

export default Logs;