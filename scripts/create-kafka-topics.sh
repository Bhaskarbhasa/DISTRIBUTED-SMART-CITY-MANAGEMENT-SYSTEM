#!/bin/bash
echo "Creating Kafka topics..."
# Assuming single node setup for local
docker exec kafka kafka-topics.sh --create --topic traffic.telemetry --partitions 5 --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
echo "Topics created."
