# Distributed Smart City Management System

## 1. Project Overview
This project is a comprehensive Distributed Smart City Management System demonstrating real-time processing of traffic, environment, and emergency events across an Edge-Fog-Cloud hierarchy. It showcases advanced distributed systems concepts such as Raft consensus, Eventual Consistency, CQRS, Event Sourcing, and fault tolerance.

## 2. Problem Statement
Modern smart cities generate terabytes of telemetry data per minute. Centralized cloud architectures suffer from high latency, single points of failure, and bandwidth bottlenecks. A distributed approach using edge computing and fog nodes allows localized decision-making, reducing latency and ensuring high availability even during network partitions.

## 3. Architecture Overview
```text
[Sensors/Devices] -> [Edge Gateways] (MQTT) 
                        |
                        v
                 [Fog Nodes (Raft Cluster)] -> Local Decisions (Traffic Signals)
                        |
                        v (Kafka)
                 [Cloud Services] (Microservices via API Gateway)
                        |
            +-----------+-----------+
            |                       |
       [Databases]             [Analytics]
    (PostgreSQL/Redis)       (Data Warehouse)
```

## 4. Technology Stack
| Layer | Technologies |
|-------|--------------|
| Cloud | Python 3.13, FastAPI, Node.js 22 |
| Data | Kafka, PostgreSQL, Redis |
| Messaging | MQTT, gRPC, REST, WebSockets |
| Consensus | Raft Algorithm |
| Deployment | Docker Compose, Kubernetes |
| Monitoring | Prometheus, Grafana |

## 5. Quick Start
```bash
git clone <repo>
cd distributed-smart-city
cp .env.example .env
./scripts/setup.sh
./scripts/start.sh
```

## 6. Prerequisites
- Python 3.13+
- Node.js 22+
- Docker and Docker Compose
- Kubernetes (Minikube/Kind) (optional)
- Git

## 7. Installation
See Quick Start. Use `./scripts/start.ps1` on Windows.

## 8. Environment Variables
| Variable | Description |
|----------|-------------|
| KAFKA_BROKERS | Kafka connection string |
| POSTGRES_URI | PostgreSQL connection string |
| REDIS_URL | Redis connection string |
| JWT_SECRET | Secret for auth |
| NODE_ID | ID for fog node |

## 9. Docker Compose instructions
Run `docker compose up -d` to start the infrastructure and services. Use `docker compose stop <service>` to simulate failures.

## 10. Kubernetes instructions
Apply manifests in `deployment/kubernetes/`:
```bash
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/configmaps/
kubectl apply -f deployment/kubernetes/secrets/
kubectl apply -f deployment/kubernetes/statefulsets/
kubectl apply -f deployment/kubernetes/deployments/
kubectl apply -f deployment/kubernetes/services/
```

## 11. API documentation summary
- **API Gateway**: Route `/api/v1/*` to respective services.
- **Auth**: `/auth/login`, `/auth/register`
- **Traffic**: `/traffic/status`, `/traffic/intersections`
- **Emergency**: `/emergency/dispatch`

## 12. Kafka topics
| Topic | Description |
|-------|-------------|
| traffic.telemetry | Raw traffic data |
| traffic.decision | Signal control decisions |
| emergency.alert | Emergency events |
| raft.events | Raft cluster communications |

## 13. MQTT topics
- `sensor/traffic/+/count`
- `sensor/environment/+/pm25`
- `device/actuator/+/command`

## 14. Database architecture
- **PostgreSQL**: Relational data, users, historical telemetry.
- **Redis**: Caching, real-time leaderboards, rate limiting.

## 15. Raft consensus
Fog nodes use Raft for leader election and state replication to ensure consistent decision-making for traffic light control.

## 16. CAP theorem
This system is CP for traffic control (consistency/partition tolerance) and AP for telemetry ingestion (availability/partition tolerance).

## 17. Failure handling
Circuit breakers prevent cascading failures. Retry mechanisms with exponential backoff for network glitches. Fallback mechanisms if cloud is unreachable.

## 18. Security model
Zero Trust, JWT-based authentication, RBAC, mTLS for internal communication.

## 19. Monitoring setup
Prometheus scrapes `/metrics`. Grafana dashboards visualize system health.

## 20. Testing instructions
Run `./scripts/run-tests.sh` or `.ps1`.

## 21. Demo instructions
Run `./scripts/demo.ps1` for a walkthrough.

## 22. Troubleshooting
Check logs: `docker compose logs -f <service>`

## 23. Known limitations
- Kafka is single-node in local dev.
- Distributed tracing (Jaeger) not yet implemented.
