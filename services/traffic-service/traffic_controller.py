from datetime import datetime, timezone
import uuid

def calculate_local_decision(congestion_level: int) -> dict:
    decision_id = str(uuid.uuid4())
    leader_id = 'local-controller'
    timestamp = datetime.now(timezone.utc).isoformat()

    if congestion_level < 30:
        return {
            'decision_id': decision_id,
            'signal_state': 'GREEN',
            'durations': {'green': 30, 'yellow': 5, 'red': 25},
            'leader_id': leader_id,
            'timestamp': timestamp
        }
    elif congestion_level <= 70:
        return {
            'decision_id': decision_id,
            'signal_state': 'GREEN',
            'durations': {'green': 45, 'yellow': 5, 'red': 20},
            'leader_id': leader_id,
            'timestamp': timestamp
        }
    elif congestion_level <= 100:
        return {
            'decision_id': decision_id,
            'signal_state': 'GREEN',
            'durations': {'green': 60, 'yellow': 5, 'red': 15},
            'leader_id': leader_id,
            'timestamp': timestamp
        }
    else:
        return {
            'decision_id': decision_id,
            'signal_state': 'GREEN',
            'durations': {'green': 90, 'yellow': 5, 'red': 10},
            'leader_id': leader_id,
            'timestamp': timestamp
        }

def get_emergency_override() -> dict:
    return {
        'decision_id': str(uuid.uuid4()),
        'signal_state': 'EMERGENCY_OVERRIDE',
        'durations': {'green': 120, 'yellow': 3, 'red': 5},
        'leader_id': 'emergency-controller',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
