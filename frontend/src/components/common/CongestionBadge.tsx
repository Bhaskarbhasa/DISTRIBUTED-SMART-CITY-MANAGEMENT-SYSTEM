import React from 'react';
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
