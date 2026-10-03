# API Documentation

## Auth Service
- `POST /api/v1/auth/login`: Authenticate and get JWT.
- `POST /api/v1/auth/register`: Register a new user.

## Traffic Service
- `GET /api/v1/traffic/status`: Get overall traffic status.
- `GET /api/v1/traffic/intersections/{id}`: Get specific intersection details.

## Emergency Service
- `POST /api/v1/emergency/dispatch`: Dispatch emergency vehicle route.

## Environment Service
- `GET /api/v1/env/air-quality`: Get current AQI.

## Analytics Service
- `GET /api/v1/analytics/report`: Generate historical report.

## Fog Node
- `POST /fog/raft/vote`: Request Raft vote.
- `POST /fog/raft/append`: Append entries (heartbeat).
