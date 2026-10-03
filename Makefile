.PHONY: setup infra-up services-up all-up down logs test load-test demo fog-fail fog-restart kafka-topics db-migrate seed

# Variables
DOCKER_COMPOSE = docker-compose

setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; else echo ".env already exists"; fi
	@mkdir -p mosquitto/data mosquitto/log
	@echo "Setup complete."

infra-up: setup
	@echo "Starting infrastructure services..."
	$(DOCKER_COMPOSE) up -d zookeeper kafka mosquitto postgres redis influxdb minio prometheus grafana
	@echo "Waiting for infra to be ready..."
	@sleep 15
	$(MAKE) kafka-topics

services-up:
	@echo "Starting application services..."
	$(DOCKER_COMPOSE) up -d api-gateway auth-service ingestion-service traffic-service emergency-service environment-service analytics-service notification-service fog-node-1 fog-node-2 fog-node-3 edge-gateway traffic-simulator environment-simulator emergency-simulator frontend

all-up: infra-up services-up
	@echo "All services started."

down:
	@echo "Stopping all services..."
	$(DOCKER_COMPOSE) down -v

logs:
	$(DOCKER_COMPOSE) logs -f

test:
	@echo "Running tests..."
	# Add test execution commands here
	pytest .

load-test:
	@echo "Running load tests..."
	# Add load testing commands (e.g., locust, k6)
	echo "Load tests not implemented yet"

demo:
	@echo "Running demo script..."
	# Script to simulate scenarios
	python scripts/demo.py

fog-fail:
	@echo "Simulating failure of fog-node-1..."
	$(DOCKER_COMPOSE) stop fog-node-1

fog-restart:
	@echo "Restarting fog-node-1..."
	$(DOCKER_COMPOSE) start fog-node-1

kafka-topics:
	@echo "Creating initial Kafka topics..."
	$(DOCKER_COMPOSE) exec kafka kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic traffic.events
	$(DOCKER_COMPOSE) exec kafka kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic environment.events
	$(DOCKER_COMPOSE) exec kafka kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic emergency.events

db-migrate:
	@echo "Running database migrations..."
	# Add alembic or other migration commands
	echo "Migrations not implemented yet"

seed:
	@echo "Seeding database..."
	# Add seed script execution
	python scripts/seed_db.py
