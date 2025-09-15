// src/components/Sidebar.jsx

import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';

// Google Material Design 아이콘들을 react-icons 라이브러리에서 가져옵니다.
import {
  MdDashboard,
  MdPolicy,
  MdArticle,
  MdAssessment,
  MdPerson,
  MdLogin,
  MdRocketLaunch,
  MdHelp,
} from 'react-icons/md';

import sidebarImage from '../assets/sidebarImage.jpg'; // 사이드바 배경 이미지

// --- Styled Components 정의 ---

const SidebarContainer = styled.nav`
  width: 280px;
  min-width: 280px;
  height: calc(100vh - 20px);
  background: linear-gradient(157deg, rgba(6, 11, 38, 0.94) 0%, rgba(26, 31, 55, 0.4) 100%);
  backdrop-filter: blur(60px);
  padding: 20px;
  border-radius: 20px;
  margin: 10px;
  display: flex;
  flex-direction: column; /* 아이템들을 세로로 정렬 */
`;

const SidebarHeader = styled.div`
  padding: 10px 15px;
  margin-bottom: 30px;
  h2 {
    font-size: 20px;
    line-height: 1.3;
    margin: 0;
  }
`;

const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const NavItem = styled.li`
  margin: 8px 0;
`;

const StyledNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  color: #A0AEC0;
  text-decoration: none;
  padding: 14px 20px;
  border-radius: 15px;
  font-weight: 500;
  transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;

  &.active {
    background-color: #0075FF;
    color: white;
    box-shadow: 0px 3.5px 5.5px rgba(0, 0, 0, 0.02);
  }

  &:hover:not(.active) {
    background-color: rgba(255, 255, 255, 0.05);
  }
`;

const DisabledNavItem = styled.div`
  display: flex;
  align-items: center;
  color: #A0AEC0;
  padding: 14px 20px;
  border-radius: 15px;
  font-weight: 500;
  opacity: 0.6; /* 비활성화된 느낌을 주기 위해 투명도 조절 */
  cursor: not-allowed; /* 커서 모양 변경 */
`;

const IconWrapper = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
`;

const SectionTitle = styled.h3`
  font-size: 12px;
  font-weight: 500;
  color: white;
  padding: 0 20px;
  margin: 30px 0 10px 0;
`;

const Spacer = styled.div`
  flex-grow: 1; /* 남은 공간을 모두 차지하여 HelpCard를 아래로 밀어냄 */
`;

const HelpCard = styled.div`
  background: url(${sidebarImage}) center/cover;
  border-radius: 15px;
  padding: 20px;
  text-align: center;
`;

const HelpIconWrapper = styled.div`
  width: 35px;
  height: 35px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  color: #0075FF;
  font-size: 20px;
`;

const HelpTitle = styled.h4`
  color: white;
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 5px 0;
`;

const HelpText = styled.p`
  color: white;
  font-size: 12px;
  font-weight: 400;
  margin: 0 0 15px 0;
`;

const DocumentationButton = styled.button`
  width: 100%;
  background: linear-gradient(175deg, rgba(5, 11, 38, 0.74) 0%, rgba(9, 14, 35, 0.71) 100%);
  backdrop-filter: blur(5px);
  border: none;
  border-radius: 12px;
  color: white;
  padding: 10px;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  
  &:hover {
    background: linear-gradient(175deg, rgba(15, 21, 48, 0.8) 0%, rgba(19, 24, 45, 0.8) 100%);
  }
`;

// --- Sidebar 컴포넌트 ---

const Sidebar = () => {
  return (
    <SidebarContainer>
      <div>
        <SidebarHeader>
          <h2>Hybrid Policy<br/>Management</h2>
        </SidebarHeader>

        <NavList>
          {/* --- 메인 네비게이션 --- */}
          <NavItem><StyledNavLink to="/"><IconWrapper><MdDashboard /></IconWrapper>Dashboard</StyledNavLink></NavItem>
          <NavItem><StyledNavLink to="/policy"><IconWrapper><MdPolicy /></IconWrapper>Policy</StyledNavLink></NavItem>
          <NavItem><StyledNavLink to="/logs"><IconWrapper><MdArticle /></IconWrapper>Logs</StyledNavLink></NavItem>
          <NavItem><StyledNavLink to="/reports"><IconWrapper><MdAssessment /></IconWrapper>Reports</StyledNavLink></NavItem>
        </NavList>

        {/* --- 계정 페이지 섹션 (비활성) --- */}
        <SectionTitle>ACCOUNT PAGES</SectionTitle>
        <NavList>
          <NavItem><DisabledNavItem><IconWrapper><MdPerson /></IconWrapper>Profile</DisabledNavItem></NavItem>
          <NavItem><DisabledNavItem><IconWrapper><MdLogin /></IconWrapper>Sign In</DisabledNavItem></NavItem>
          <NavItem><DisabledNavItem><IconWrapper><MdRocketLaunch /></IconWrapper>Sign Up</DisabledNavItem></NavItem>
        </NavList>
      </div>

      <Spacer />

      {/* --- 도움말 카드 --- */}
      <HelpCard>
        <HelpIconWrapper><MdHelp /></HelpIconWrapper>
        <HelpTitle>Need help?</HelpTitle>
        <HelpText>Please check our docs</HelpText>
        <DocumentationButton>DOCUMENTATION</DocumentationButton>
      </HelpCard>
    </SidebarContainer>
  );
};

export default Sidebar;