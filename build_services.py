import os
import textwrap

base_dir = r'd:\Distributed_system\Smart_DS_Project\distributed-smart-city'
traffic_dir = os.path.join(base_dir, 'services', 'traffic-service')
emergency_dir = os.path.join(base_dir, 'services', 'emergency-service')

os.makedirs(traffic_dir, exist_ok=True)
os.makedirs(emergency_dir, exist_ok=True)

# ----------------- TRAFFIC SERVICE -----------------
with open(os.path.join(traffic_dir, '__init__.py'), 'w') as f: f.write('')

with open(os.path.join(traffic_dir, 'config.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import os
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        KAFKA_BROKERS: str = os.getenv('KAFKA_BROKERS', 'localhost:9092')
        REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
        DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/traffic')
        FOG_SERVICE_URL: str = os.getenv('FOG_SERVICE_URL', 'localhost:50051')
        PORT: int = int(os.getenv('PORT', '8002'))

    settings = Settings()
    '''))

with open(os.path.join(traffic_dir, 'metrics.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    from prometheus_client import Counter, Histogram, Gauge

    TRAFFIC_CONGESTION = Gauge('traffic_congestion_level', 'Current congestion level', ['zone_id'])
    DECISION_COUNT = Counter('traffic_decisions_total', 'Total traffic decisions made', ['zone_id', 'signal_state'])
    FOG_CALL_DURATION = Histogram('fog_grpc_call_duration_seconds', 'Duration of Fog gRPC calls')
    CIRCUIT_BREAKER_STATE = Gauge('circuit_breaker_state', 'Circuit breaker state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)')
    '''))

with open(os.path.join(traffic_dir, 'models.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
    from sqlalchemy.orm import declarative_base
    from datetime import datetime, timezone

    Base = declarative_base()

    class TrafficTelemetry(Base):
        __tablename__ = 'traffic_telemetry'
        id = Column(Integer, primary_key=True, index=True)
        sensor_id = Column(String, index=True)
        zone_id = Column(String, index=True)
        vehicle_count = Column(Integer)
        avg_speed = Column(Float)
        congestion_level = Column(String)
        timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    class TrafficDecision(Base):
        __tablename__ = 'traffic_decision'
        decision_id = Column(String, primary_key=True, index=True)
        zone_id = Column(String, index=True)
        signal_state = Column(String)
        green_duration = Column(Integer)
        yellow_duration = Column(Integer)
        red_duration = Column(Integer)
        leader_id = Column(String)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    class TrafficSignalState(Base):
        __tablename__ = 'traffic_signal_state'
        zone_id = Column(String, primary_key=True, index=True)
        current_signal = Column(String)
        duration_remaining = Column(Integer)
        last_decision_id = Column(String)
        updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    '''))

with open(os.path.join(traffic_dir, 'websocket_manager.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import asyncio
    from fastapi import WebSocket
    import structlog

    logger = structlog.get_logger()

    class ConnectionManager:
        def __init__(self):
            self.active_connections: list[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

        async def broadcast(self, message: str):
            for connection in list(self.active_connections):
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error('websocket_broadcast_error', error=str(e))
                    self.disconnect(connection)

    manager = ConnectionManager()
    '''))

with open(os.path.join(traffic_dir, 'redis_cache.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import redis.asyncio as redis
    import json
    from .config import settings

    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def set_traffic_state(zone_id: str, state: dict):
        await redis_client.setex(f"traffic:state:{zone_id}", 300, json.dumps(state))

    async def get_traffic_state(zone_id: str):
        data = await redis_client.get(f"traffic:state:{zone_id}")
        return json.loads(data) if data else None

    async def get_all_zones_state():
        keys = await redis_client.keys("traffic:state:*")
        states = []
        for key in keys:
            data = await redis_client.get(key)
            if data:
                states.append(json.loads(data))
        return states

    async def set_signal_state(zone_id: str, state: dict):
        await redis_client.setex(f"traffic:signal:{zone_id}", 300, json.dumps(state))

    async def get_signal_state(zone_id: str):
        data = await redis_client.get(f"traffic:signal:{zone_id}")
        return json.loads(data) if data else None

    async def get_all_signals_state():
        keys = await redis_client.keys("traffic:signal:*")
        states = []
        for key in keys:
            data = await redis_client.get(key)
            if data:
                states.append(json.loads(data))
        return states
    '''))

with open(os.path.join(traffic_dir, 'circuit_breaker.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import time
    from enum import Enum
    import structlog
    from .metrics import CIRCUIT_BREAKER_STATE

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
    '''))

with open(os.path.join(traffic_dir, 'traffic_controller.py'), 'w') as f:
    f.write(textwrap.dedent('''\
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
    '''))

with open(os.path.join(traffic_dir, 'fog_client.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import grpc
    import structlog
    from .config import settings
    from .circuit_breaker import fog_circuit_breaker
    from .traffic_controller import calculate_local_decision
    from .metrics import FOG_CALL_DURATION
    import time

    logger = structlog.get_logger()

    async def _call_fog_grpc(zone_id: str, congestion_level: int):
        # Stub for gRPC call to Fog Coordinator
        raise Exception('gRPC client to Fog Coordinator not implemented')

    async def get_traffic_decision(zone_id: str, congestion_level: int) -> dict:
        start_time = time.time()
        try:
            decision = await fog_circuit_breaker.call(_call_fog_grpc, zone_id, congestion_level)
            FOG_CALL_DURATION.observe(time.time() - start_time)
            return decision
        except Exception as e:
            logger.warning('fog_call_failed_using_local_fallback', error=str(e), zone_id=zone_id)
            return calculate_local_decision(congestion_level)
    '''))

with open(os.path.join(traffic_dir, 'database.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from .config import settings
    from .models import Base

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session
    '''))

with open(os.path.join(traffic_dir, 'kafka_consumer.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import asyncio
    import json
    import structlog
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
    from .config import settings
    from .fog_client import get_traffic_decision
    from .redis_cache import set_traffic_state, set_signal_state
    from .websocket_manager import manager
    from .database import AsyncSessionLocal
    from .models import TrafficTelemetry, TrafficDecision
    from .metrics import TRAFFIC_CONGESTION, DECISION_COUNT

    logger = structlog.get_logger()

    class TrafficKafkaManager:
        def __init__(self):
            self.consumer = AIOKafkaConsumer(
                'traffic.telemetry',
                bootstrap_servers=settings.KAFKA_BROKERS,
                group_id='traffic-service',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )

        async def start(self):
            await self.consumer.start()
            await self.producer.start()
            asyncio.create_task(self.consume())

        async def stop(self):
            await self.consumer.stop()
            await self.producer.stop()

        async def consume(self):
            try:
                async for msg in self.consumer:
                    data = msg.value
                    logger.info('received_telemetry', data=data)
                    await self.process_telemetry(data)
            except Exception as e:
                logger.error('kafka_consumer_error', error=str(e))

        async def process_telemetry(self, data: dict):
            zone_id = data.get('zone_id')
            congestion_level = data.get('congestion_level')
            if not zone_id or congestion_level is None:
                return

            try:
                congestion_value = float(congestion_level)
            except ValueError:
                congestion_value = 0.0

            TRAFFIC_CONGESTION.labels(zone_id=zone_id).set(congestion_value)

            # Store state in Redis
            await set_traffic_state(zone_id, data)

            if congestion_value > 50:
                decision = await get_traffic_decision(zone_id, int(congestion_value))
                decision['zone_id'] = zone_id
                
                # Metrics
                DECISION_COUNT.labels(zone_id=zone_id, signal_state=decision.get('signal_state')).inc()

                # Redis
                await set_signal_state(zone_id, decision)

                # Broadcast
                await manager.broadcast(json.dumps({'type': 'decision', 'data': decision}))

                # Kafka Producer
                await self.producer.send_and_wait('traffic.decision', decision)

                # DB
                async with AsyncSessionLocal() as session:
                    # Save telemetry
                    telemetry = TrafficTelemetry(**data)
                    session.add(telemetry)
                    
                    # Save decision
                    durations = decision.get('durations', {})
                    db_decision = TrafficDecision(
                        decision_id=decision.get('decision_id'),
                        zone_id=zone_id,
                        signal_state=decision.get('signal_state'),
                        green_duration=durations.get('green', 0),
                        yellow_duration=durations.get('yellow', 0),
                        red_duration=durations.get('red', 0),
                        leader_id=decision.get('leader_id')
                    )
                    session.add(db_decision)
                    await session.commit()

    kafka_manager = TrafficKafkaManager()
    '''))

with open(os.path.join(traffic_dir, 'main.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import asyncio
    import json
    from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select

    from .database import init_db, get_db
    from .kafka_consumer import kafka_manager
    from .websocket_manager import manager
    from .redis_cache import get_all_zones_state, get_traffic_state, get_all_signals_state, get_signal_state, set_signal_state
    from .traffic_controller import get_emergency_override
    from .models import TrafficTelemetry

    app = FastAPI(title='Traffic Service')

    @app.on_event('startup')
    async def startup_event():
        await init_db()
        await kafka_manager.start()

    @app.on_event('shutdown')
    async def shutdown_event():
        await kafka_manager.stop()

    @app.get('/health')
    async def health():
        return {'status': 'ok'}

    @app.get('/ready')
    async def ready():
        return {'status': 'ready'}

    @app.get('/metrics')
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get('/traffic/zones')
    async def get_zones():
        return await get_all_zones_state()

    @app.get('/traffic/zones/{zone_id}')
    async def get_zone(zone_id: str):
        state = await get_traffic_state(zone_id)
        if not state:
            raise HTTPException(status_code=404, detail='Zone not found')
        return state

    @app.get('/traffic/signals')
    async def get_signals():
        return await get_all_signals_state()

    @app.put('/traffic/signals/{zone_id}')
    async def override_signal(zone_id: str):
        decision = get_emergency_override()
        decision['zone_id'] = zone_id
        await set_signal_state(zone_id, decision)
        await manager.broadcast(json.dumps({'type': 'override', 'data': decision}))
        await kafka_manager.producer.send_and_wait('traffic.decision', decision)
        return decision

    @app.get('/traffic/history')
    async def get_history(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(TrafficTelemetry).order_by(TrafficTelemetry.timestamp.desc()).limit(100))
        return result.scalars().all()

    @app.websocket('/ws/traffic')
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    '''))

with open(os.path.join(traffic_dir, 'requirements.txt'), 'w') as f:
    f.write(textwrap.dedent('''\
    fastapi==0.115.0
    uvicorn==0.31.0
    pydantic==2.9.2
    pydantic-settings==2.5.2
    sqlalchemy==2.0.35
    asyncpg==0.29.0
    aiokafka==0.11.0
    redis==5.1.1
    structlog==24.4.0
    prometheus-client==0.21.0
    grpcio==1.67.0
    grpcio-tools==1.67.0
    websockets==13.1
    '''))

with open(os.path.join(traffic_dir, 'Dockerfile'), 'w') as f:
    f.write(textwrap.dedent('''\
    FROM python:3.13-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
    '''))

# ----------------- EMERGENCY SERVICE -----------------
with open(os.path.join(emergency_dir, '__init__.py'), 'w') as f: f.write('')

with open(os.path.join(emergency_dir, 'config.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import os
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        KAFKA_BROKERS: str = os.getenv('KAFKA_BROKERS', 'localhost:9092')
        REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
        DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/emergency')
        TRAFFIC_SERVICE_URL: str = os.getenv('TRAFFIC_SERVICE_URL', 'http://localhost:8002')
        PORT: int = int(os.getenv('PORT', '8004'))

    settings = Settings()
    '''))

with open(os.path.join(emergency_dir, 'models.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    from sqlalchemy import Column, Integer, String, Float, DateTime
    from sqlalchemy.orm import declarative_base
    from datetime import datetime, timezone

    Base = declarative_base()

    class EmergencyAlert(Base):
        __tablename__ = 'emergency_alert'
        alert_id = Column(String, primary_key=True, index=True)
        event_id = Column(String, unique=True, index=True)
        alert_type = Column(String)
        severity = Column(String)
        location_lat = Column(Float)
        location_lon = Column(Float)
        zone_id = Column(String, index=True)
        status = Column(String, default='ACTIVE')
        reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        acknowledged_at = Column(DateTime, nullable=True)
        resolved_at = Column(DateTime, nullable=True)
        acknowledged_by = Column(String, nullable=True)
        resolution_notes = Column(String, nullable=True)

    class AlertAuditLog(Base):
        __tablename__ = 'alert_audit_log'
        id = Column(Integer, primary_key=True, index=True)
        alert_id = Column(String, index=True)
        action = Column(String)
        actor = Column(String)
        timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        details = Column(String, nullable=True)
    '''))

with open(os.path.join(emergency_dir, 'database.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from .config import settings
    from .models import Base

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session
    '''))

with open(os.path.join(emergency_dir, 'deduplication.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import redis.asyncio as redis
    from .config import settings

    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def is_duplicate(event_id: str) -> bool:
        key = f"emergency:dedup:{event_id}"
        exists = await redis_client.get(key)
        if exists:
            return True
        await redis_client.setex(key, 86400, "1") # 24h retention
        return False
    '''))

with open(os.path.join(emergency_dir, 'websocket_manager.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import asyncio
    from fastapi import WebSocket
    import structlog

    logger = structlog.get_logger()

    class ConnectionManager:
        def __init__(self):
            self.active_connections: list[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

        async def broadcast(self, message: str):
            for connection in list(self.active_connections):
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error('ws_error', error=str(e))
                    self.disconnect(connection)

    manager = ConnectionManager()
    '''))

with open(os.path.join(emergency_dir, 'kafka_consumer.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    import asyncio
    import json
    import structlog
    import httpx
    import uuid
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
    from .config import settings
    from .deduplication import is_duplicate
    from .database import AsyncSessionLocal
    from .models import EmergencyAlert, AlertAuditLog
    from .websocket_manager import manager

    logger = structlog.get_logger()

    class EmergencyKafkaManager:
        def __init__(self):
            self.consumer = AIOKafkaConsumer(
                'emergency.alert',
                bootstrap_servers=settings.KAFKA_BROKERS,
                group_id='emergency-service',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )

        async def start(self):
            await self.consumer.start()
            await self.producer.start()
            asyncio.create_task(self.consume())

        async def stop(self):
            await self.consumer.stop()
            await self.producer.stop()

        async def consume(self):
            try:
                async for msg in self.consumer:
                    data = msg.value
                    logger.info('received_emergency_alert', data=data)
                    await self.process_alert(data)
            except Exception as e:
                logger.error('kafka_consumer_error', error=str(e))

        async def process_alert(self, data: dict):
            event_id = data.get('event_id')
            if not event_id:
                return

            if await is_duplicate(event_id):
                logger.info('duplicate_alert_skipped', event_id=event_id)
                return

            alert_id = str(uuid.uuid4())
            data['alert_id'] = alert_id
            
            async with AsyncSessionLocal() as session:
                alert = EmergencyAlert(
                    alert_id=alert_id,
                    event_id=event_id,
                    alert_type=data.get('alert_type'),
                    severity=data.get('severity'),
                    location_lat=data.get('location_lat'),
                    location_lon=data.get('location_lon'),
                    zone_id=data.get('zone_id')
                )
                session.add(alert)
                
                audit = AlertAuditLog(
                    alert_id=alert_id,
                    action='CREATED',
                    actor='system'
                )
                session.add(audit)
                await session.commit()

            # Broadcast
            await manager.broadcast(json.dumps({'type': 'new_alert', 'data': data}))

            if data.get('severity') == 'CRITICAL':
                zone_id = data.get('zone_id')
                if zone_id:
                    try:
                        async with httpx.AsyncClient() as client:
                            await client.put(f"{settings.TRAFFIC_SERVICE_URL}/traffic/signals/{zone_id}")
                    except Exception as e:
                        logger.error('failed_to_override_traffic', error=str(e))

                await self.producer.send_and_wait('system.events', {'event_type': 'CRITICAL_EMERGENCY', 'data': data})

    kafka_manager = EmergencyKafkaManager()
    '''))

with open(os.path.join(emergency_dir, 'main.py'), 'w') as f:
    f.write(textwrap.dedent('''\
    from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, update
    from datetime import datetime, timezone
    import json

    from .database import init_db, get_db
    from .kafka_consumer import kafka_manager
    from .models import EmergencyAlert, AlertAuditLog
    from .websocket_manager import manager

    app = FastAPI(title='Emergency Service')

    @app.on_event('startup')
    async def startup_event():
        await init_db()
        await kafka_manager.start()

    @app.on_event('shutdown')
    async def shutdown_event():
        await kafka_manager.stop()

    @app.get('/health')
    async def health():
        return {'status': 'ok'}

    @app.get('/ready')
    async def ready():
        return {'status': 'ready'}

    @app.get('/emergency/alerts')
    async def get_alerts(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.status == 'ACTIVE'))
        return result.scalars().all()

    @app.get('/emergency/alerts/{alert_id}')
    async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.alert_id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail='Alert not found')
        return alert

    @app.post('/emergency/alerts/{alert_id}/acknowledge')
    async def ack_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.alert_id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail='Alert not found')
        
        alert.status = 'ACKNOWLEDGED'
        alert.acknowledged_at = datetime.now(timezone.utc)
        
        audit = AlertAuditLog(alert_id=alert_id, action='ACKNOWLEDGED', actor='user')
        db.add(audit)
        await db.commit()
        await manager.broadcast(json.dumps({'type': 'alert_update', 'alert_id': alert_id, 'status': 'ACKNOWLEDGED'}))
        return {'status': 'acknowledged'}

    @app.put('/emergency/alerts/{alert_id}/resolve')
    async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.alert_id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail='Alert not found')
            
        alert.status = 'RESOLVED'
        alert.resolved_at = datetime.now(timezone.utc)
        
        audit = AlertAuditLog(alert_id=alert_id, action='RESOLVED', actor='user')
        db.add(audit)
        await db.commit()
        await manager.broadcast(json.dumps({'type': 'alert_update', 'alert_id': alert_id, 'status': 'RESOLVED'}))
        return {'status': 'resolved'}

    @app.get('/emergency/history')
    async def get_history(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(EmergencyAlert).order_by(EmergencyAlert.reported_at.desc()).limit(100))
        return result.scalars().all()

    @app.websocket('/ws/emergency')
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    '''))

with open(os.path.join(emergency_dir, 'requirements.txt'), 'w') as f:
    f.write(textwrap.dedent('''\
    fastapi==0.115.0
    uvicorn==0.31.0
    pydantic==2.9.2
    pydantic-settings==2.5.2
    sqlalchemy==2.0.35
    asyncpg==0.29.0
    aiokafka==0.11.0
    redis==5.1.1
    structlog==24.4.0
    prometheus-client==0.21.0
    grpcio==1.67.0
    grpcio-tools==1.67.0
    websockets==13.1
    httpx==0.27.2
    '''))

with open(os.path.join(emergency_dir, 'Dockerfile'), 'w') as f:
    f.write(textwrap.dedent('''\
    FROM python:3.13-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
    '''))

print("All files generated successfully.")
