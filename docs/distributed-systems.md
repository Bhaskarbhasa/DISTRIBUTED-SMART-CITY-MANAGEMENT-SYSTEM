# Distributed Systems Concepts

## What is distributed and WHY
The system distributes computation across Edge, Fog, and Cloud to minimize latency for critical tasks (traffic lights) while enabling global analytics in the cloud.

## Edge vs Fog vs Cloud
- **Edge**: Data ingestion, filtering, basic protocol translation.
- **Fog**: Local consensus (Raft), real-time control loops.
- **Cloud**: Long-term storage, machine learning, global coordination.

## Kafka vs MQTT vs gRPC vs REST vs WebSocket
- MQTT: Lightweight, for IoT sensors.
- gRPC: Fast, binary, for internal microservices.
- REST: Standard, for public APIs.
- WebSockets: Real-time UI updates.
- Kafka: High-throughput, durable event streaming.

## Raft Consensus
Ensures multiple Fog nodes agree on the state of traffic intersections, even if some nodes fail. Uses leader election and log replication.

## CAP Theorem
- **Traffic Control (CP)**: Prioritizes consistency and partition tolerance.
- **Telemetry (AP)**: Prioritizes availability; eventually consistent.

## Leader Election
Nodes start as followers. If no heartbeat is received, a node becomes a candidate and requests votes.

## Failure Detection
Heartbeats (ping/pong) and circuit breakers are used to detect and isolate failures.

## Horizontal Scaling
Services can be scaled horizontally by adding more instances (replicas in Kubernetes). Kafka partitions allow parallel event processing.

## Idempotency
Message processing relies on unique IDs to ensure safe retries.

## Circuit Breaker Pattern
Prevents cascading failures by stopping calls to a failing service and returning a fallback response.

## Message Delivery
At-least-once delivery semantics typically used, with idempotency on the consumer side.
