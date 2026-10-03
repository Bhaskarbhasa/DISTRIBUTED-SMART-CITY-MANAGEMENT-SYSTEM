export interface TrafficZone {
  zone_id: string;
  zone_name: string;
  vehicle_count: number;
  average_speed: number;
  congestion_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  signal_state: 'GREEN' | 'YELLOW' | 'RED';
  green_duration: number;
  yellow_duration: number;
  red_duration: number;
  fog_leader: string;
  last_update: string;
}

export interface FogNode {
  node_id: string;
  state: 'FOLLOWER' | 'CANDIDATE' | 'LEADER';
  term: number;
  leader_id: string;
  commit_index: number;
  log_length: number;
  cpu_percent: number;
  memory_mb: number;
  is_healthy: boolean;
  last_heartbeat: string;
  messages_processed: number;
}

export interface EmergencyAlert {
  alert_id: string;
  alert_type: 'ACCIDENT' | 'FIRE' | 'MEDICAL' | 'SECURITY' | 'INFRASTRUCTURE';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  zone_id: string;
  location: { lat: number; lon: number };
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  reported_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

export interface EnvironmentData {
  zone_id: string;
  temperature: number;
  humidity: number;
  aqi: number;
  pm25: number;
  pm10: number;
  co2: number;
  no2: number;
  wind_speed: number;
  timestamp: string;
}

export interface SystemMetrics {
  kafka_throughput: number;
  events_processed: number;
  events_failed: number;
  active_sensors: number;
  total_sensors: number;
  fog_nodes_online: number;
  fog_nodes_total: number;
  raft_leader: string;
  raft_term: number;
  system_uptime: number;
}

export interface User {
  id: string;
  email: string;
  role: 'ADMIN' | 'OPERATOR' | 'ANALYST' | 'VIEWER';
  last_login: string;
}

export interface AuditLog {
  id: string;
  actor_email: string;
  action: string;
  resource: string;
  timestamp: string;
  result: 'SUCCESS' | 'FAILURE';
  ip_address: string;
}
