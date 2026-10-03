import time
from enum import Enum
import structlog
from metrics import CIRCUIT_BREAKER_STATE

logger = structlog.get_logger()

class CBState(Enum):
    CLOSED = 0
    HALF_OPEN = 1
    OPEN = 2

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CBState.CLOSED
        self.failures = 0
        self.last_failure_time = 0

    def _update_metric(self):
        CIRCUIT_BREAKER_STATE.set(self.state.value)

    def record_success(self):
        if self.state == CBState.HALF_OPEN:
            logger.info('circuit_breaker_recovered')
            self.state = CBState.CLOSED
            self.failures = 0
            self._update_metric()
        elif self.state == CBState.CLOSED:
            self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.state == CBState.HALF_OPEN or (self.state == CBState.CLOSED and self.failures >= self.failure_threshold):
            logger.warning('circuit_breaker_opened')
            self.state = CBState.OPEN
            self._update_metric()

    def can_execute(self) -> bool:
        if self.state == CBState.CLOSED:
            return True
        if self.state == CBState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CBState.HALF_OPEN
                self._update_metric()
                logger.info('circuit_breaker_half_open')
                return True
            return False
        if self.state == CBState.HALF_OPEN:
            return True
        return False

    async def call(self, func, *args, **kwargs):
        if not self.can_execute():
            raise CircuitBreakerOpenException('Circuit breaker is OPEN')
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

fog_circuit_breaker = CircuitBreaker()
