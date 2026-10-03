#!/bin/bash
set -e

echo "Waiting for MinIO..."
while ! curl -s http://minio:9000/minio/health/live; do
  sleep 1
done

echo "Configuring MinIO client..."
mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

echo "Creating buckets..."
mc mb myminio/smartcity-telemetry --ignore-existing
mc mb myminio/smartcity-analytics --ignore-existing
mc mb myminio/smartcity-archives --ignore-existing
mc mb myminio/smartcity-ml-datasets --ignore-existing

echo "Setting anonymous policies..."
mc anonymous set download myminio/smartcity-telemetry
mc anonymous set download myminio/smartcity-analytics
mc anonymous set download myminio/smartcity-archives
mc anonymous set download myminio/smartcity-ml-datasets

echo "Buckets created successfully."
