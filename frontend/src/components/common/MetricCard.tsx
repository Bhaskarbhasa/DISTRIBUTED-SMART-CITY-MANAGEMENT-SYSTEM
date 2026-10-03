import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: string;
  trend?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, icon, color = 'primary.main', trend }) => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography color="textSecondary" gutterBottom variant="overline">
            {title}
          </Typography>
          {icon && <Box sx={{ color }}>{icon}</Box>}
        </Box>
        <Typography variant="h4" component="h2" sx={{ color }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="textSecondary">
            {subtitle} {trend && <span style={{ marginLeft: 8 }}>{trend}</span>}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};
