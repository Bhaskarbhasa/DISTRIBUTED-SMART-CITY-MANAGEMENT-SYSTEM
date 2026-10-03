#!/bin/bash
echo "Setting up Distributed Smart City Management System..."
cp .env.example .env
mkdir -p data/postgres data/redis data/kafka
echo "Setup complete. Please review .env and run ./scripts/start.sh"
