from models import EmergencyEvent

def process_emergency(data: dict) -> EmergencyEvent:
    event = EmergencyEvent(**data)
    
    priority_map = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }
    
    base_priority = priority_map.get(event.severity.upper(), 1)
    if event.emergency_type.upper() in ["FIRE", "MEDICAL"]:
        base_priority += 1
        
    event.priority = min(base_priority, 5)
    return event
