# start.ps1 - Start the Distributed Smart City Management System
# Run from project root: .\scripts\start.ps1

param(
    [switch]$InfraOnly,      # Start only infrastructure (Kafka, MQTT, DB, Redis)
    [switch]$ServicesOnly,   # Start only application services (assumes infra running)
    [switch]$Build,          # Force rebuild images
    [switch]$Pull            # Pull latest images first
)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

function Write-Step($step, $msg) {
    Write-Host "[$step] $msg" -ForegroundColor Yellow
}

function Write-OK($msg) {
    Write-Host "  OK: $msg" -ForegroundColor Green
}

function Write-Err($msg) {
    Write-Host "  WARNING: $msg" -ForegroundColor Yellow
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Distributed Smart City Management System - Starting" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Ensure .env exists
if (!(Test-Path (Join-Path $PROJECT_ROOT ".env"))) {
    Write-Host "  .env not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $PROJECT_ROOT ".env.example") (Join-Path $PROJECT_ROOT ".env")
    Write-OK ".env created"
}

Set-Location $PROJECT_ROOT

# ============================================================
# STEP 1: Pull images if requested OR start
# ============================================================
if ($Pull) {
    Write-Step "0" "Pulling latest Docker images..."
    docker compose pull
}

if ($InfraOnly) {
    Write-Step "1" "Starting infrastructure services only..."
    docker compose up -d zookeeper kafka mosquitto postgres redis influxdb minio prometheus grafana
} elseif ($ServicesOnly) {
    Write-Step "1" "Starting application services only..."
    docker compose up -d auth-service ingestion-service traffic-service emergency-service environment-service analytics-service notification-service api-gateway fog-node-1 fog-node-2 fog-node-3 edge-gateway traffic-simulator environment-simulator emergency-simulator frontend
} else {
    Write-Step "1" "Starting ALL services..."
    if ($Build) {
        docker compose up -d --build
    } else {
        docker compose up -d
    }
}

Write-Host ""
Write-OK "Docker Compose command sent"

# ============================================================
# STEP 2: Wait for Kafka
# ============================================================
Write-Step "2" "Waiting for Kafka to be ready (up to 90s)..."
$kafkaReady = $false
for ($i = 0; $i -lt 18; $i++) {
    Start-Sleep -Seconds 5
    $result = docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 2>&1
    if ($LASTEXITCODE -eq 0) {
        $kafkaReady = $true
        break
    }
    Write-Host "  Waiting... ($((($i+1)*5))s elapsed)" -ForegroundColor Gray
}

if (!$kafkaReady) {
    Write-Host "  Kafka not ready yet (still starting or image downloading)." -ForegroundColor Yellow
    Write-Host "  You can create topics later with: .\scripts\create-kafka-topics.ps1" -ForegroundColor Yellow
} else {
    Write-OK "Kafka is ready"

    # ============================================================
    # STEP 3: Create Kafka topics
    # ============================================================
    Write-Step "3" "Creating Kafka topics..."
    & (Join-Path $PSScriptRoot "create-kafka-topics.ps1")
    Write-OK "Kafka topics created"
}

# ============================================================
# STEP 4: Check PostgreSQL
# ============================================================
Write-Step "4" "Checking PostgreSQL..."
$pgReady = $false
for ($i = 0; $i -lt 6; $i++) {
    Start-Sleep -Seconds 3
    $result = docker exec postgres pg_isready -U postgres -d smartcity 2>&1
    if ($LASTEXITCODE -eq 0) { $pgReady = $true; break }
}

if ($pgReady) {
    Write-OK "PostgreSQL is ready (schema auto-applied from 001_init.sql)"
} else {
    Write-Host "  PostgreSQL still starting (normal for first run)" -ForegroundColor Yellow
}

# ============================================================
# Summary
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Access URLs (services start in ~2-5 minutes)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Dashboard:      http://localhost:3001" -ForegroundColor Green
Write-Host "  API Gateway:    http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs:       http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Fog Node 1:     http://localhost:8020/status" -ForegroundColor Green
Write-Host "  Fog Node 2:     http://localhost:8022/status" -ForegroundColor Green
Write-Host "  Fog Node 3:     http://localhost:8024/status" -ForegroundColor Green
Write-Host "  Grafana:        http://localhost:3002  (admin/admin)" -ForegroundColor Green
Write-Host "  Prometheus:     http://localhost:9090" -ForegroundColor Green
Write-Host "  MinIO Console:  http://localhost:9002  (admin/admin123)" -ForegroundColor Green
Write-Host ""
Write-Host " Login: admin@smartcity.local / Admin@123" -ForegroundColor Cyan
Write-Host ""
Write-Host " Monitor startup: docker compose logs -f" -ForegroundColor White
Write-Host " Check status:    docker compose ps" -ForegroundColor White
Write-Host " Run demo:        .\scripts\demo.ps1" -ForegroundColor White
Write-Host ""
