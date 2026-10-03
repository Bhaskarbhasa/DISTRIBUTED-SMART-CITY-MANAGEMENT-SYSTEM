import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface TrafficChartProps {
  data: any[];
  height?: number;
}

export const TrafficChart: React.FC<TrafficChartProps> = ({ data, height = 300 }) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
        <XAxis dataKey="timestamp" stroke="#888" />
        <YAxis stroke="#888" />
        <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
        <Legend />
        <Line type="monotone" dataKey="zone_1" stroke="#8884d8" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="zone_2" stroke="#82ca9d" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
};
