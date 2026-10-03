import React from 'react';
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
