from prometheus_client import Counter, Histogram, Gauge

TRAFFIC_CONGESTION = Gauge('traffic_congestion_level', 'Current congestion level', ['zone_id'])
DECISION_COUNT = Counter('traffic_decisions_total', 'Total traffic decisions made', ['zone_id', 'signal_state'])
FOG_CALL_DURATION = Histogram('fog_grpc_call_duration_seconds', 'Duration of Fog gRPC calls')
CIRCUIT_BREAKER_STATE = Gauge('circuit_breaker_state', 'Circuit breaker state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)')
