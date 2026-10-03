from prometheus_client import Gauge, Counter, Histogram

raft_current_term = Gauge('raft_current_term', 'Current term of the Raft node')
raft_is_leader = Gauge('raft_is_leader', '1 if node is leader, 0 otherwise')
raft_commit_index = Gauge('raft_commit_index', 'Current commit index of the Raft node')
raft_log_length = Gauge('raft_log_length', 'Length of the Raft log')
raft_leader_changes_total = Counter('raft_leader_changes_total', 'Total number of leader changes')

fog_decisions_total = Counter('fog_decisions_total', 'Total number of fog decisions made')
fog_decision_latency_seconds = Histogram('fog_decision_latency_seconds', 'Latency of fog decisions')
