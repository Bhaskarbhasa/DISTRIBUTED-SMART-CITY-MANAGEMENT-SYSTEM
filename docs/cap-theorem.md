# CAP Theorem Analysis

## Definition
The CAP theorem states that a distributed data store can simultaneously provide only two of three guarantees: Consistency, Availability, and Partition Tolerance.

## Application in this Project
- **Traffic Signals (CP)**: In the presence of a network partition, the system must remain consistent to avoid unsafe states (e.g., green lights in conflicting directions), potentially sacrificing availability.
- **Telemetry Ingestion (AP)**: Sensor data ingestion prioritizes availability. If the central DB is unreachable, data is buffered locally (eventual consistency).
