import React from 'react';
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
