from models import EnvironmentEvent

def process_environment(data: dict) -> EnvironmentEvent:
    event = EnvironmentEvent(**data)
    
    if event.aqi <= 100:
        event.air_quality_category = "GOOD" if event.aqi <= 50 else "MODERATE"
    elif event.aqi <= 150:
        event.air_quality_category = "UNHEALTHY_SENSITIVE"
    elif event.aqi <= 200:
        event.air_quality_category = "UNHEALTHY"
    elif event.aqi <= 300:
        event.air_quality_category = "VERY_UNHEALTHY"
    else:
        event.air_quality_category = "HAZARDOUS"
        
    event.temperature_alert = event.temperature > 40 or event.temperature < -5
    
    return event
