from models import TrafficEvent

def process_traffic(data: dict) -> TrafficEvent:
    event = TrafficEvent(**data)
    
    if event.vehicle_count < 30:
        event.congestion_level = "LOW"
    elif 30 <= event.vehicle_count <= 70:
        event.congestion_level = "MEDIUM"
    elif 71 <= event.vehicle_count <= 100:
        event.congestion_level = "HIGH"
    else:
        event.congestion_level = "CRITICAL"
        
    event.density = event.vehicle_count / (event.lane_count * 1000.0) if event.lane_count else 0.0
    
    event.anomaly_score = 0.0
    if event.vehicle_count > 80 and event.average_speed > 60:
        event.anomaly_score = 0.8
    elif event.vehicle_count < 10 and event.average_speed < 10:
        event.anomaly_score = 0.6
        
    return event
