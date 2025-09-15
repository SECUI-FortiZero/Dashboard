import React from 'react';
import styled, { css } from 'styled-components';
import { Card } from './common/Card';
import { MdMoreVert } from 'react-icons/md';

const SecurityEventsStyled = styled(Card)` grid-column: span 12; `;
const Table = styled.div``;
const TableHeader = styled.div`
  display: grid;
  grid-template-columns: 0.8fr 3fr 1.5fr 1.5fr 1fr;
  padding: 0 16px 10px 16px;
  border-bottom: 1px solid #2D2E5F;
  span { color: #A0AEC0; font-size: 10px; font-weight: 500; text-transform: uppercase; }
`;
const TableRow = styled.div`
  display: grid;
  grid-template-columns: 0.8fr 3fr 1.5fr 1.5fr 1fr;
  align-items: center;
  padding: 16px;
  font-size: 14px;
  font-weight: 500;
  &:not(:last-child) { border-bottom: 1px solid #2D2E5F; }
`;
const EventDetailCell = styled.div` display: flex; align-items: center; font-weight: 700; `;
const EventIcon = styled.div`
  width: 28px; height: 28px; border-radius: 8px; background-color: #2D2E5F;
  color: #A0AEC0; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  margin-right: 12px;
`;
const RiskCell = styled.div`
  font-weight: 700; padding: 4px 8px; border-radius: 6px;
  text-align: center; font-size: 12px;
  ${({ risk }) => risk === 'Critical' && css` color: #E31A1A; background-color: rgba(227, 26, 26, 0.1); `}
  ${({ risk }) => risk === 'High' && css` color: #F6AD55; background-color: rgba(246, 173, 85, 0.1); `}
  ${({ risk }) => risk === 'Medium' && css` color: #4299E1; background-color: rgba(66, 153, 225, 0.1); `}
`;
const StatusCell = styled.div` color: #A0AEC0; font-weight: 400; `;

export const SecurityEventsTable = ({ events }) => (
  <SecurityEventsStyled>
    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
      <h3>Latest Security Events</h3>
      <MdMoreVert color="#A0AEC0" />
    </div>
    <Table>
      <TableHeader>
        <span>RISK</span>
        <span>EVENT DETAILS</span>
        <span>SOURCE IP</span>
        <span>TIMESTAMP</span>
        <span>STATUS</span>
      </TableHeader>
      {events.map((event, index) => (
        <TableRow key={index}>
          <RiskCell risk={event.risk}>{event.risk}</RiskCell>
          <EventDetailCell><EventIcon>{event.icon}</EventIcon>{event.details}</EventDetailCell>
          <div>{event.sourceIP}</div>
          <StatusCell>{event.time}</StatusCell>
          <StatusCell>{event.status}</StatusCell>
        </TableRow>
      ))}
    </Table>
  </SecurityEventsStyled>
);