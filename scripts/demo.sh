#!/bin/bash
echo -e "\033[1;32mStarting Smart City Demo...\033[0m"
echo "Step 1: Simulating traffic sensor data..."
curl -X POST http://localhost:8000/api/v1/traffic/telemetry -d '{"sensor_id":"S1","count":50}' -H "Content-Type: application/json"
sleep 2
echo "Step 2: Checking traffic decision..."
curl http://localhost:8000/api/v1/traffic/status
echo "Demo complete."
