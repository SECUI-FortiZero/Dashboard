import React from 'react';
import styled from 'styled-components';
import { Card } from './common/Card';
import { MdCheckCircle, MdError, MdWarning } from 'react-icons/md';

const RecentChangesStyled = styled(Card)`
  grid-column: span 3;
  h3 { margin: 0 0 5px 0; font-size: 18px; }
  p { color: #A0AEC0; font-size: 14px; margin: 0 0 20px 0; }
`;
const ChangeList = styled.ul` list-style: none; padding: 0; margin: 0; `;
const ChangeItem = styled.li`
  display: flex; align-items: flex-start; margin-bottom: 20px;
  &:last-child { margin-bottom: 0; }
  div { 
      p:first-child { font-size: 14px; font-weight: 500; margin: 0 0 4px 0; color: white; }
      p:last-child { font-size: 12px; margin: 0; color: #A0AEC0; }
  }
`;
const ChangeIcon = styled.div`
  font-size: 16px; margin-right: 15px; margin-top: 2px;
  color: ${props => props.color || '#4299E1'};
`;

export const RecentChanges = () => (
  <RecentChangesStyled>
    <h3>Recent Policy Changes</h3>
    <p>+30 this month</p>
    <ChangeList>
      <ChangeItem>
        <ChangeIcon color="#0075FF"><MdCheckCircle /></ChangeIcon>
        <div><p>PM-01: Modified SSH rule</p><p>22 DEC 7:20 PM</p></div>
      </ChangeItem>
      <ChangeItem>
        <ChangeIcon color="#E31A1A"><MdError /></ChangeIcon>
        <div><p>PM-01: Modified SSH rule</p><p>21 DEC 11:21 PM</p></div>
      </ChangeItem>
      <ChangeItem>
        <ChangeIcon color="#F6AD55"><MdWarning /></ChangeIcon>
        <div><p>PM-02: Deactivated SSH rule</p><p>21 DEC 9:28 PM</p></div>
      </ChangeItem>
    </ChangeList>
  </RecentChangesStyled>
);