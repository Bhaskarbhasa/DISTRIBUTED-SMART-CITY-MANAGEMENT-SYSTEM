# Architecture Documentation

## 1. High-level system architecture
```mermaid
graph TD
    Devices[IoT Devices] -->|MQTT| Edge[Edge Gateways]
    Edge -->|gRPC/HTTP| Fog[Fog Nodes]
    Fog -->|Kafka| Services[Cloud Microservices]
    Services --> DB[(PostgreSQL)]
    Services --> Cache[(Redis)]
    UI[Web Dashboard] <-->|REST/WS| API[API Gateway]
    API <--> Services
```

## 2. Edge-Fog-Cloud hierarchy
```mermaid
graph TD
    subgraph Edge
        Sensor1
        Sensor2
    end
    subgraph Fog
        Node1[Fog Node 1]
        Node2[Fog Node 2]
    end
    subgraph Cloud
        Core[Central Services]
    end
    Sensor1 --> Node1
    Sensor2 --> Node2
    Node1 --> Core
    Node2 --> Core
```

## 3. Traffic data flow
```mermaid
sequenceDiagram
    participant Sensor
    participant Edge
    participant Fog
    participant Kafka
    participant Cloud
    Sensor->>Edge: MQTT Telemetry
    Edge->>Fog: gRPC Data
    Fog->>Fog: Raft Consensus (Local Decision)
    Fog->>Kafka: Publish Event
    Kafka->>Cloud: Consume Event
    Cloud->>Database: Store
```

## 4. Kafka event flow
```mermaid
graph LR
    P[Producers] -->|Publish| T[Topics: traffic, env]
    T -->|Consume| C[Consumers: Traffic Service, Analytics]
```

## 5. Raft consensus state machine
```mermaid
stateDiagram-v2
    [*] --> Follower
    Follower --> Candidate: Timeout
    Candidate --> Leader: Won Election
    Candidate --> Follower: Lost Election / Higher Term
    Leader --> Follower: Higher Term Discovered
```

## 6. Emergency response flow
```mermaid
sequenceDiagram
    Ambulance->>Fog: Emergency Broadcast
    Fog->>Fog: Priority Processing
    Fog->>TrafficLight: Force Green
    Fog->>Cloud: Log Emergency Route
```

## 7. Database architecture
```mermaid
erDiagram
    USER ||--o{ ROLES : has
    TRAFFIC_EVENT }o--|| INTERSECTION : at
    ENVIRONMENT_DATA }o--|| SENSOR : read_by
```

## 8. Authentication/security flow
```mermaid
sequenceDiagram
    Client->>Auth: Login(Credentials)
    Auth->>Client: JWT Token
    Client->>API: Request + JWT
    API->>Auth: Validate JWT
    Auth->>API: OK
    API->>Service: Forward Request
```
