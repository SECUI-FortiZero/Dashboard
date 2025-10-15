import React from 'react';
import styled from 'styled-components';
import { Card } from './common/Card';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const TrafficRegionStyled = styled(Card)`
  grid-column: span 4;
  h3 { margin: 0 0 5px 0; font-size: 18px; }
  p { color: #A0AEC0; font-size: 14px; margin: 0 0 10px 0; }
`;
const LegendContainer = styled.div`
  display: flex; justify-content: space-around; margin-top: 15px;
`;
const LegendItem = styled.div`
  text-align: center;
  p { font-size: 18px; color: white; font-weight: 700; margin: 0 0 5px 0; }
  span { font-size: 14px; color: #A0AEC0; display: flex; align-items: center; }
  div { width: 12px; height: 12px; border-radius: 4px; margin-right: 8px; }
`;

export const TrafficRegion = ({ data, colors }) => (
  <TrafficRegionStyled>
    <h3>Traffic Region</h3>
    <p>From this Policy</p>
    <ResponsiveContainer width="100%" height={150}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={50} outerRadius={70} fill="#8884d8" paddingAngle={5} dataKey="value">
          {data.map((entry, index) => <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />)}
        </Pie>
        <Tooltip contentStyle={{ backgroundColor: '#1A1F37', border: '1px solid #2D2E5F' }} />
      </PieChart>
    </ResponsiveContainer>
    <LegendContainer>
      {data.map((entry, index) => (
        <LegendItem key={`legend-${index}`}>
          <p>{entry.value}%</p>
          <span><div style={{backgroundColor: colors[index]}}></div>{entry.name}</span>
        </LegendItem>
      ))}
    </LegendContainer>
  </TrafficRegionStyled>
);