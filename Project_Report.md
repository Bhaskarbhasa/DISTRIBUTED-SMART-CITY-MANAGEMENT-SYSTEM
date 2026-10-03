# Final Project Report: Distributed Systems and Applications

**Project Title:** Distributed Smart City Management System  
**Course Name:** Distributed Systems and Applications  
**Submitted By:** [Insert Your Name/Group Names Here]  
**Date:** [Insert Date]  

---

## 1. Introduction
The concept of a "Smart City" relies on millions of IoT sensors deployed across urban infrastructure to monitor traffic, environmental conditions, and emergencies. Processing this massive volume of data using a traditional centralized server creates severe bottlenecks, high latency, and a single point of failure. 

To solve this, we developed the **Distributed Smart City Management System**. This project simulates a real-world urban environment using a distributed multi-tier architecture. It intelligently routes data from edge sensors to localized decision-making nodes, ensuring high availability, fault tolerance, and real-time responsiveness even in the event of network or server failures.

## 2. Objectives
The primary objectives of this project are:
* **High Availability & Fault Tolerance:** Ensure city infrastructure (like traffic lights) continues operating even if decision servers crash.
* **Low Latency Processing:** Process immediate decisions (like traffic routing) closer to the source rather than relying entirely on distant cloud servers.
* **Scalability:** Handle massive streams of concurrent data from different city zones simultaneously.
* **Real-time Observability:** Provide a live, real-time dashboard for city operators without requiring manual page refreshes.
* **Practical Application of Distributed Concepts:** Implement complex algorithms like the Raft Consensus Protocol from scratch to manage distributed state.

## 3. Project Problem Statement
Modern urban environments generate vast amounts of telemetry data. A centralized cloud architecture struggles to process this data with the low latency required for critical operations, such as emergency vehicle routing. Furthermore, a failure in the central server would paralyze the entire city's traffic grid. 

**The Problem:** How can we design a scalable, fault-tolerant system capable of ingesting high-throughput IoT data, making real-time localized decisions, and surviving server failures without losing data consistency?

## 4. System Architecture
The system is built on a modern **Edge-Fog-Cloud** architecture:

* **Edge Layer (Data Generation & Ingestion):** 
  * Python-based IoT simulators generate realistic traffic, environment, and emergency data.
  * Data is published to an **MQTT Broker** (Mosquitto) designed for lightweight IoT devices.
  * An Edge Gateway normalizes this data and pushes it to a distributed event stream.
* **Fog Layer (Localized Consensus & Decisions):**
  * A cluster of three localized "Fog Nodes" manages critical decisions (like traffic light timing).
  * These nodes use the **Raft Consensus Algorithm** to elect a leader, replicate decision logs, and maintain a consistent state across the cluster.
* **Cloud/Core Layer (Microservices & Storage):**
  * **Apache Kafka** routes high-throughput telemetry across services.
  * Independent **FastAPI Microservices** (Traffic, Emergency, Environment, Auth) handle specific business logic.
  * **PostgreSQL** provides persistent relational storage, while **Redis** offers fast in-memory caching and deduplication.
* **Presentation Layer:**
  * A **React/TypeScript** frontend connects via WebSockets for live UI updates.
  * **Prometheus & Grafana** provide deep metrics and system observability.

*(Note: [Insert a diagram of your architecture here. You can take a screenshot of a flowchart or draw a simple block diagram showing Edge -> MQTT -> Kafka -> Fog/Microservices -> UI])*

## 5. Distributed Systems Concepts Used
This project serves as a practical implementation of several core academic distributed systems concepts:
1. **Raft Consensus Algorithm:** Implemented from scratch to handle Leader Election and Log Replication among the Fog Nodes. Ensures the system operates correctly as long as a majority of nodes are alive.
2. **CAP Theorem:** The system balances **C**onsistency (Raft logs) and **P**artition Tolerance (Kafka streams) over absolute Availability. 
3. **Publish-Subscribe Model:** Utilized heavily via MQTT (for sensors) and Apache Kafka (for microservices) to decouple data producers from consumers.
4. **Microservices Architecture:** Monolithic logic is split into specialized, independently scalable services communicating via REST, gRPC, and Kafka.
5. **Idempotency & Deduplication:** The Emergency Service uses Redis to ensure that duplicate alerts (common in distributed retries) are only processed once.
6. **Circuit Breakers:** Prevent cascading network failures if the Fog cluster becomes temporarily unreachable.

## 6. Technology Stack
* **Backend:** Python 3.11, FastAPI, gRPC, asyncio
* **Frontend:** React 18, TypeScript, Material UI, Zustand, Recharts
* **Message Brokers:** Apache Kafka (Event Streaming), Eclipse Mosquitto (MQTT)
* **Databases:** PostgreSQL (Relational), Redis (In-Memory/Cache)
* **Observability:** Prometheus (Metrics), Grafana (Dashboards)
* **Infrastructure:** Docker, Docker Compose

## 7. Implementation
The project was implemented as a containerized stack using Docker. 
* **Container Orchestration:** Over 20 independent containers were configured using `docker-compose.yml` mapped to a custom bridged network.
* **Custom Raft Implementation:** The core logic involves a custom Python Raft implementation utilizing randomized timers for elections and asynchronous RPCs (HTTP/gRPC) for heartbeats and log replication.
* **API Gateway:** A central API Gateway handles JWT token validation, rate limiting, and reverse-proxies requests to the underlying microservice architecture.

## 8. Working/Demo
The system includes an automated 20-step demonstration script (`demo.ps1`) that executes the following workflow:
1. **System Boot:** All services start and initialize database schemas.
2. **Normal Flow:** Sensors generate regular traffic data; the Dashboard displays standard green light durations.
3. **Congestion Event:** Traffic load is artificially spiked. The Edge Gateway detects this and alerts Kafka.
4. **Fog Decision:** The Raft Leader processes the congestion, proposes a new signal timing (e.g., 60s Green), replicates the log to followers, and commits the change.
5. **Fault Injection (Leader Killed):** The current Raft Leader is forcefully terminated.
6. **Leader Election:** The remaining Fog nodes detect missed heartbeats, increment their term, and elect a new leader automatically.
7. **Recovery:** The system continues processing new traffic data using the newly elected leader without downtime.
8. **Emergency Override:** A critical ambulance alert overrides normal traffic logic, forcing an immediate 120s Green light in the affected zone.

## 9. Testing Results
* **Fault Tolerance Testing:** Successfully verified that stopping `fog-node-1` triggers an election within 300ms, allowing `fog-node-2` or `fog-node-3` to seamlessly assume command.
* **Throughput Testing:** Kafka successfully handled rapid streams of telemetry data from the simulators without dropping messages.
* **Idempotency Testing:** Sending the exact same emergency alert multiple times resulted in a single database record, proving the Redis-based deduplication functions correctly.
* **UI Responsiveness:** The React Dashboard updated instantaneously via WebSockets without requiring browser reloads.

*(Note: [Insert Screenshots of your working React Dashboard, Grafana Metrics, and the terminal output showing the Raft Leader Election here])*

## 10. Individual Student Contribution
* **[Your Name 1]:** [e.g., Designed the overall system architecture, implemented the custom Raft consensus algorithm in Python, and configured the Docker networking.]
* **[Your Name 2]:** [e.g., Built the React TypeScript dashboard, integrated WebSockets for real-time updates, and developed the API Gateway.]
* **[Your Name 3]:** [e.g., Developed the IoT simulators, configured Apache Kafka and Mosquitto, and wrote the automated PowerShell demonstration script.]

*(Note: Adjust the above names and descriptions based on your actual group members and tasks. If you did it alone, simply summarize your journey building the full stack.)*

## 11. Conclusion
The Distributed Smart City Management System successfully demonstrates how modern distributed architectures can solve the scaling limitations of centralized servers. By moving critical decision-making to a localized Fog cluster governed by the Raft consensus protocol, the system achieved high fault tolerance and low-latency processing. The integration of Kafka and microservices ensures the platform can easily scale to accommodate future smart city requirements, providing a robust blueprint for next-generation urban infrastructure.

## 12. Annexures
### A. How to Run the Code
```bash
# Clone the repository and navigate to the project root
cd distributed-smart-city

# Build and start the entire infrastructure
docker compose up -d --build

# Run the automated demonstration
.\scripts\demo.ps1
```

### B. References
1. *In Search of an Understandable Consensus Algorithm (Extended Version)* by Diego Ongaro and John Ousterhout (The Raft Paper)
2. Apache Kafka Documentation
3. FastAPI Documentation
4. *Designing Data-Intensive Applications* by Martin Kleppmann

---
*(End of Report)*
