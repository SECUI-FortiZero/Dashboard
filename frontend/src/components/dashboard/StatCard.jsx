import React from 'react';
import styled from 'styled-components';
import { Card } from './common/Card'; // 재사용을 위해 Card 스타일을 분리할 수 있습니다. (여기선 간단히 정의)

const StatCardStyled = styled(Card)`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;
const StatInfo = styled.div``;
const StatTitle = styled.p`
  color: #A0AEC0; font-size: 12px; font-weight: 500; margin: 0 0 8px 0;
`;
const StatValue = styled.h3`
  color: white; font-size: 18px; font-weight: 700; margin: 0;
  span { font-size: 12px; font-weight: 700; color: #A0AEC0; }
`;
const StatChange = styled.span`
  font-size: 14px; font-weight: 700; margin-left: 8px;
  color: ${props => (props.increase ? '#01B574' : '#E31A1A')};
`;
const StatIconWrapper = styled.div`
  width: 45px; height: 45px; background: #0075FF; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; color: white;
`;

export const StatCard = ({ icon, title, value, subValue, change, increase }) => (
  <StatCardStyled style={{ gridColumn: 'span 3' }}>
    <StatInfo>
      <StatTitle>{title}</StatTitle>
      <StatValue>{value} {subValue && <span>{subValue}</span>}
        {change && <StatChange increase={increase}>{increase ? '+' : ''}{change}</StatChange>}
      </StatValue>
    </StatInfo>
    <StatIconWrapper>{icon}</StatIconWrapper>
  </StatCardStyled>
);