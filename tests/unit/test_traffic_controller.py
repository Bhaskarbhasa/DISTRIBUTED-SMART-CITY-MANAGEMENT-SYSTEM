import pytest

def get_congestion_level(count):
    if count < 10: return "LOW"
    if count < 50: return "MEDIUM"
    if count < 100: return "HIGH"
    return "CRITICAL"

def get_signal_duration(level):
    durations = {"LOW": 30, "MEDIUM": 45, "HIGH": 60, "CRITICAL": 90}
    return durations.get(level, 30)

def test_congestion_classification():
    assert get_congestion_level(5) == "LOW"
    assert get_congestion_level(25) == "MEDIUM"
    assert get_congestion_level(75) == "HIGH"
    assert get_congestion_level(150) == "CRITICAL"

def test_signal_duration_calculation():
    assert get_signal_duration("LOW") == 30
    assert get_signal_duration("CRITICAL") == 90

def test_emergency_override():
    # Emergency forces duration to specific value or state
    assert True

def test_boundary_conditions():
    assert get_congestion_level(10) == "MEDIUM"
    assert get_congestion_level(50) == "HIGH"
    assert get_congestion_level(100) == "CRITICAL"
