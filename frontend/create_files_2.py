import os

base_dir = r"d:\Distributed_system\Smart_DS_Project\distributed-smart-city\frontend\src"

files = {
    "components/common/CongestionBadge.tsx": """import React from 'react';
import { Chip } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';

type CongestionLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export const CongestionBadge: React.FC<{ level: CongestionLevel }> = ({ level }) => {
  switch (level) {
    case 'LOW':
      return <Chip icon={<CheckCircleIcon />} label="Low" color="success" size="small" />;
    case 'MEDIUM':
      return <Chip icon={<WarningIcon />} label="Medium" color="warning" size="small" />;
    case 'HIGH':
      return <Chip icon={<ErrorIcon />} label="High" color="error" size="small" />;
    case 'CRITICAL':
      return <Chip icon={<ReportProblemIcon />} label="Critical" color="error" size="small" sx={{ bgcolor: 'darkred', color: 'white' }} />;
    default:
      return null;
  }
};
""",
    "components/common/SeverityBadge.tsx": """import React from 'react';
import { Chip } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';

type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export const SeverityBadge: React.FC<{ severity: Severity }> = ({ severity }) => {
  switch (severity) {
    case 'LOW':
      return <Chip icon={<InfoIcon />} label="Low" color="info" size="small" />;
    case 'MEDIUM':
      return <Chip icon={<WarningIcon />} label="Medium" color="warning" size="small" />;
    case 'HIGH':
      return <Chip icon={<ErrorIcon />} label="High" color="error" size="small" />;
    case 'CRITICAL':
      return <Chip icon={<ReportProblemIcon />} label="Critical" color="error" size="small" sx={{ bgcolor: 'darkred', color: 'white' }} />;
    default:
      return null;
  }
};
""",
    "components/common/NodeStateBadge.tsx": """import React from 'react';
import { Chip } from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import GroupIcon from '@mui/icons-material/Group';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

type NodeState = 'LEADER' | 'FOLLOWER' | 'CANDIDATE';

export const NodeStateBadge: React.FC<{ state: NodeState }> = ({ state }) => {
  switch (state) {
    case 'LEADER':
      return <Chip icon={<StarIcon />} label="Leader" size="small" sx={{ bgcolor: 'gold', color: 'black' }} />;
    case 'FOLLOWER':
      return <Chip icon={<GroupIcon />} label="Follower" color="info" size="small" />;
    case 'CANDIDATE':
      return <Chip icon={<AccessTimeIcon />} label="Candidate" color="warning" size="small" />;
    default:
      return null;
  }
};
""",
    "components/common/TrafficSignal.tsx": """import React from 'react';
import { Box } from '@mui/material';

type SignalState = 'GREEN' | 'YELLOW' | 'RED';

export const TrafficSignal: React.FC<{ signal: SignalState, animated?: boolean }> = ({ signal, animated = true }) => {
  const getGlow = (color: string) => animated ? `0 0 10px ${color}` : 'none';

  return (
    <Box sx={{ 
      display: 'inline-flex', flexDirection: 'column', bgcolor: '#333', 
      p: 1, borderRadius: 2, gap: 1 
    }}>
      <Box sx={{ 
        width: 20, height: 20, borderRadius: '50%', 
        bgcolor: signal === 'RED' ? '#ff0000' : '#440000',
        boxShadow: signal === 'RED' ? getGlow('#ff0000') : 'none'
      }} />
      <Box sx={{ 
        width: 20, height: 20, borderRadius: '50%', 
        bgcolor: signal === 'YELLOW' ? '#ffff00' : '#444400',
        boxShadow: signal === 'YELLOW' ? getGlow('#ffff00') : 'none'
      }} />
      <Box sx={{ 
        width: 20, height: 20, borderRadius: '50%', 
        bgcolor: signal === 'GREEN' ? '#00ff00' : '#004400',
        boxShadow: signal === 'GREEN' ? getGlow('#00ff00') : 'none'
      }} />
    </Box>
  );
};
""",
    "components/common/MetricCard.tsx": """import React from 'react';
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
""",
    "components/charts/TrafficChart.tsx": """import React from 'react';
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
""",
    "components/charts/CongestionPieChart.tsx": """import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#8b0000'];

export const CongestionPieChart: React.FC<{ data: any[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};
""",
    "components/charts/EnvironmentGauge.tsx": """import React from 'react';
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
""",
    "components/charts/ThroughputChart.tsx": """import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const ThroughputChart: React.FC<{ data: any[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <XAxis dataKey="time" stroke="#888" />
        <YAxis stroke="#888" />
        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
        <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
        <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorValue)" />
      </AreaChart>
    </ResponsiveContainer>
  );
};
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', '\\'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding='utf-8') as f:
        f.write(content)

print("Created components and charts.")
