import pytest

class CircuitBreaker:
    def __init__(self, failure_threshold=3):
        self.state = "CLOSED"
        self.failures = 0
        self.threshold = failure_threshold
    
    def record_failure(self):
        if self.state == "HALF_OPEN":
            # In HALF_OPEN, any failure goes back to OPEN immediately
            self.state = "OPEN"
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "OPEN"
    
    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def try_half_open(self):
        if self.state == "OPEN":
            self.state = "HALF_OPEN"

def test_closed_to_open_transition():
    cb = CircuitBreaker()
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"

def test_open_to_half_open():
    cb = CircuitBreaker()
    cb.state = "OPEN"
    cb.try_half_open()
    assert cb.state == "HALF_OPEN"

def test_half_open_to_closed_on_success():
    cb = CircuitBreaker()
    cb.state = "HALF_OPEN"
    cb.record_success()
    assert cb.state == "CLOSED"

def test_half_open_to_open_on_failure():
    cb = CircuitBreaker()
    cb.state = "HALF_OPEN"
    cb.record_failure() # Simplistic implementation
    assert cb.state == "OPEN"
