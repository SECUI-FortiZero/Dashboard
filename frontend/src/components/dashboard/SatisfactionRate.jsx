import React from 'react';
import styled from 'styled-components';
import { Card } from './common/Card';

const SatisfactionRateStyled = styled(Card)`
  grid-column: span 3;
  position: relative;
  overflow: hidden;
  h3 { margin: 0 0 5px 0; font-size: 18px; }
  p { color: #A0AEC0; font-size: 14px; margin: 0; }
`;
const CircleBg = styled.div`
    width: 200px; height: 200px;
    border-radius: 50%;
    position: absolute;
    top: 50px; right: -50px;
    background: conic-gradient(#0075FF 0% 95%, #22234B 95% 100%);
`;
const CenterTextCard = styled.div`
    position: absolute;
    bottom: 20px; left: 20px; right: 20px;
    background: linear-gradient(175deg, rgba(5.91, 11.17, 39.61, 0.74) 0%, rgba(9.54, 14, 35.36, 0.71) 100%);
    backdrop-filter: blur(60px);
    border-radius: 20px;
    padding: 15px;
    text-align: center;
    h2 { font-size: 28px; margin: 0; }
    span { font-size: 12px; color: #A0AEC0; }
`;

export const SatisfactionRate = () => (
  <SatisfactionRateStyled>
    <h3>Satisfaction Rate</h3>
    <p>From this Policy</p>
    <CircleBg />
    <CenterTextCard>
      <h2>95%</h2>
      <span>Based on Traffic</span>
    </CenterTextCard>
  </SatisfactionRateStyled>
);