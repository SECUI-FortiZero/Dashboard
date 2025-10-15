import React from 'react';
import styled from 'styled-components';
import { Card } from './common/Card';
import jellyfishImage from '../../assets/jellyfishImage.jpg';

const WelcomeCardStyled = styled(Card)`
  grid-column: span 6;
  background: linear-gradient(85deg, rgba(14, 13, 57, 0.4) 0%, #1A1F37 100%),
              url(${jellyfishImage}) no-repeat center center / cover;
  padding-top: 40px;
  h4 { color: #A0AEC0; font-size: 14px; margin: 0 0 5px 0; font-weight: 500; }
  h2 { font-size: 28px; margin: 0 0 10px 0; }
  p { color: #A0AEC0; font-size: 16px; line-height: 1.5; }
`;

export const WelcomeCard = () => (
  <WelcomeCardStyled>
    <h4>Welcome back,</h4>
    <h2>Mark Johnson</h2>
    <p>Glad to see you again!<br/>Ask me anything.</p>
  </WelcomeCardStyled>
);