// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Policy from './pages/Policy';
import Logs from './pages/Logs';
import Reports from './pages/Reports';
import GlobalStyle from './styles/GlobalStyle'; // GlobalStyle 가져오기

function App() {
  return (
    <>
      <GlobalStyle /> {/* 전역 스타일을 여기에 추가 */}
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/policy" element={<Policy />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/reports" element={<Reports />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;