import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from 'recharts';
import { Box, Typography } from '@mui/material';

export const EnvironmentGauge: React.FC<{ value: number, max: number, label: string }> = ({ value, max, label }) => {
  const data = [{ name: label, value, fill: value > max * 0.8 ? '#f44336' : value > max * 0.5 ? '#ff9800' : '#4caf50' }];
  
  return (
    <Box position="relative" height={200} display="flex" alignItems="center" justifyContent="center" flexDirection="column">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%" barSize={10} data={data} startAngle={180} endAngle={0}>
          <RadialBar background dataKey="value" cornerRadius={5} />
        </RadialBarChart>
      </ResponsiveContainer>
      <Box position="absolute" bottom={40} textAlign="center">
        <Typography variant="h4">{value}</Typography>
        <Typography variant="caption" color="textSecondary">{label}</Typography>
      </Box>
    </Box>
  );
};
