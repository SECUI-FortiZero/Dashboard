// src/layouts/MainLayout.jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import styled from 'styled-components';
import Sidebar from '../components/Sidebar';

const LayoutContainer = styled.div`
  display: flex;
  width: 100%;
  min-height: 100vh;
`;

const ContentArea = styled.main`
  flex-grow: 1;
  padding: 2.5rem;
  overflow-y: auto; /* 콘텐츠가 길어지면 스크롤 생성 */
`;

const MainLayout = () => {
  return (
    <LayoutContainer>
      <Sidebar />
      <ContentArea>
        <Outlet />
      </ContentArea>
    </LayoutContainer>
  );
};

export default MainLayout;