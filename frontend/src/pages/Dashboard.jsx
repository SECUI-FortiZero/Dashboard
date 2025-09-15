// src/pages/Dashboard.jsx
import React from 'react';
import styled, { css } from 'styled-components';
import { 
  MdFileCopy, MdEqualizer, MdOutlineSecurity, MdShowChart,
  MdLockOpen, MdScanner, MdBugReport, MdError, MdTravelExplore
} from 'react-icons/md';

// 분리된 컴포넌트들을 import 합니다.
import { StatCard } from '../components/dashboard/StatCard';
import { WelcomeCard } from '../components/dashboard/WelcomeCard';
import { SatisfactionRate } from '../components/dashboard/SatisfactionRate';
import { RecentChanges } from '../components/dashboard/RecentChanges';
import { TrafficTimeline } from '../components/dashboard/TrafficTimeline';
import { TrafficRegion } from '../components/dashboard/TrafficRegion';
import { SecurityEventsTable } from '../components/dashboard/SecurityEventsTable';

// --- 데이터 목업(Mock Data) ---
const timelineData = [
  { name: 'Jan', allowed: 400, anomaly: 240 }, { name: 'Feb', allowed: 300, anomaly: 139 },
  { name: 'Mar', allowed: 200, anomaly: 380 }, { name: 'Apr', allowed: 278, anomaly: 390 },
  { name: 'May', allowed: 189, anomaly: 480 }, { name: 'Jun', allowed: 239, anomaly: 380 },
  { name: 'Jul', allowed: 349, anomaly: 430 }, { name: 'Aug', allowed: 300, anomaly: 220 },
  { name: 'Sep', allowed: 450, anomaly: 300 }, { name: 'Oct', allowed: 380, anomaly: 400 },
  { name: 'Nov', allowed: 420, anomaly: 250 }, { name: 'Dec', allowed: 400, anomaly: 310 },
];

const regionData = [ { name: 'US', value: 70 }, { name: 'Kor', value: 20 }, { name: 'China', value: 10 } ];
const REGION_COLORS = ['#0052CC', '#582CFF', '#1E1B39'];

const securityEvents = [
  { risk: 'Critical', icon: <MdLockOpen />, details: 'Unusual login from new device', sourceIP: '118.34.56.78', time: '2 min ago', status: 'New' },
  { risk: 'High', icon: <MdScanner />, details: 'Excessive port scanning detected', sourceIP: '192.168.1.89', time: '15 min ago', status: 'Investigating' },
  { risk: 'Critical', icon: <MdBugReport />, details: 'Malware signature detected in file upload', sourceIP: '203.0.113.45', time: '1 hour ago', status: 'New' },
  { risk: 'Medium', icon: <MdError />, details: 'Potential XSS attempt on /login page', sourceIP: '172.16.0.10', time: '3 hours ago', status: 'Resolved' },
  { risk: 'High', icon: <MdTravelExplore />, details: 'Anomalous traffic from a Tor exit node', sourceIP: '211.23.45.67', time: '5 hours ago', status: 'Investigating' },
];

// --- 페이지 레이아웃 스타일 ---
const PageHeader = styled.div`
  margin-bottom: 2rem;
  h1 {
    font-size: 24px; font-weight: 500; margin: 0;
    span { color: #A0AEC0; font-weight: 400; }
  }
`;

const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: auto;
  gap: 24px;
`;

// --- Dashboard 페이지 메인 컴포넌트 ---
const Dashboard = () => {
  return (
    <>
      <PageHeader>
        <h1><span>Pages /</span> Dashboard</h1>
      </PageHeader>
      
      <DashboardGrid>
        {/* Row 1: Stat Cards */}
        <StatCard icon={<MdFileCopy />} title="Total Policies" value="542" subValue="On-prem | 788 cloud" />
        <StatCard icon={<MdEqualizer />} title="Active Sessions" value="12" change="5%" increase />
        <StatCard icon={<MdOutlineSecurity />} title="24h Detected Threats" value="28" change="+1 Critical" />
        <StatCard icon={<MdShowChart />} title="24h Blocked Traffic" value="1.2M" />

        {/* Row 2: Welcome, Satisfaction, Recent Changes */}
        <WelcomeCard />
        <SatisfactionRate />
        <RecentChanges />

        {/* Row 3: Charts */}
        <TrafficTimeline data={timelineData} />
        <TrafficRegion data={regionData} colors={REGION_COLORS} />

        {/* Row 4: Security Events Table */}
        <SecurityEventsTable events={securityEvents} />
      </DashboardGrid>
    </>
  );
};

export default Dashboard;