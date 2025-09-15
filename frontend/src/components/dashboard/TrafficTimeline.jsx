import React from 'react';
import styled from 'styled-components';
import { Card } from './common/Card';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const TimelineStyled = styled(Card)`
  grid-column: span 8;
  h3 { margin: 0 0 5px 0; font-size: 18px; }
  div > span { 
      font-size: 14px;
      &:first-child { color: #01B574; font-weight: 700; }
      &:last-child { color: #E31A1A; font-weight: 700; }
  }
`;

export const TrafficTimeline = ({ data }) => (
  <TimelineStyled>
    <h3>Traffic & Event Timeline</h3>
    <div>
      <span>Allowed</span> | <span>Anomaly Detected</span>
    </div>
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorAllowed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#01B574" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#01B574" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorAnomaly" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#E31A1A" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#E31A1A" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <XAxis dataKey="name" stroke="#56577A" fontSize="12px" />
        <YAxis stroke="#56577A" fontSize="12px" />
        <Tooltip contentStyle={{ backgroundColor: '#1A1F37', border: '1px solid #2D2E5F' }} />
        <Area type="monotone" dataKey="anomaly" stroke="#E31A1A" fillOpacity={1} fill="url(#colorAnomaly)" />
        <Area type="monotone" dataKey="allowed" stroke="#01B574" fillOpacity={1} fill="url(#colorAllowed)" />
      </AreaChart>
    </ResponsiveContainer>
  </TimelineStyled>
);