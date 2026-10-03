#!/bin/bash
docker compose up -d
echo "Waiting for Kafka..."
sleep 15
./scripts/create-kafka-topics.sh
echo "System started. Access API at http://localhost:8000"
