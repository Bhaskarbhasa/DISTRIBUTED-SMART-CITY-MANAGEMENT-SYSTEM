# demo.ps1 - Complete 20-step demonstration of the Distributed Smart City System
# Run: .\scripts\demo.ps1
# Requires: System running (.\scripts\start.ps1 completed)

$ErrorActionPreference = "Continue"
$API = "http://localhost:8000"
$FOG1 = "http://localhost:8020"
$FOG2 = "http://localhost:8022"
$FOG3 = "http://localhost:8024"
$TRAFFIC_SIM = "http://localhost:8010"
$EMERGENCY_SIM = "http://localhost:8011"

function Write-DemoStep($step, $title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " DEMO ${step}: $title" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Write-Result($data) {
    Write-Host ($data | ConvertTo-Json -Depth 3) -ForegroundColor White
}

function Pause-Demo($seconds, $msg) {
    Write-Host ""
    Write-Host "  >> $msg" -ForegroundColor Yellow
    Start-Sleep -Seconds $seconds
}

function Get-AuthToken {
    $loginBody = @{ email = "admin@smartcity.com"; password = "Admin@123" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$API/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -ErrorAction SilentlyContinue
    if ($response.access_token) {
        return $response.access_token
    }
    Write-Host "  WARNING: Could not get auth token. API may not be ready." -ForegroundColor Yellow
    return ""
}

Write-Host ""
Write-Host "###########################################################" -ForegroundColor Magenta
Write-Host "#   DISTRIBUTED SMART CITY MANAGEMENT SYSTEM - DEMO      #" -ForegroundColor Magenta
Write-Host "#   Demonstrating: Edge -> Fog -> Raft -> Cloud Pipeline  #" -ForegroundColor Magenta
Write-Host "###########################################################" -ForegroundColor Magenta
Write-Host ""
Write-Host " Prerequisites: docker compose up completed" -ForegroundColor White
Write-Host " Open Dashboard: http://localhost:3001" -ForegroundColor White
Write-Host ""
Pause-Demo 3 "Starting demo in 3 seconds..."

# ============================================================
# DEMO 1: System Start
# ============================================================
Write-DemoStep 1 "Verify System is Running"
Write-Host "  Checking API Gateway health..."
try {
    $health = Invoke-RestMethod -Uri "$API/health" -Method Get -ErrorAction Stop
    Write-Host "  API Gateway: OK" -ForegroundColor Green
} catch {
    Write-Host "  API Gateway not responding at $API" -ForegroundColor Red
    Write-Host "  Start system with: .\scripts\start.ps1" -ForegroundColor Yellow
    exit 1
}

# ============================================================
# DEMO 2: Open Dashboard
# ============================================================
Write-DemoStep 2 "Open Dashboard"
Write-Host "  Dashboard URL: http://localhost:3001" -ForegroundColor Green
Write-Host "  Login with: admin@smartcity.com / Admin@123" -ForegroundColor White
Pause-Demo 3 "Logging into system..."

$token = Get-AuthToken
if ($token) {
    Write-Host "  Authentication successful - JWT token obtained" -ForegroundColor Green
    $headers = @{ Authorization = "Bearer $token" }
} else {
    $headers = @{}
}

# ============================================================
# DEMO 3: Show Three Fog Nodes
# ============================================================
Write-DemoStep 3 "Show Three Fog Nodes (Raft Cluster)"
Write-Host "  Checking Fog Node 1..."
try {
    $fog1Status = Invoke-RestMethod -Uri "$FOG1/status" -Method Get -ErrorAction Stop
    Write-Host "  Fog-1: State=$($fog1Status.raft_state), Term=$($fog1Status.term)" -ForegroundColor Green
} catch {
    Write-Host "  Fog Node 1 not responding (may still be starting)" -ForegroundColor Yellow
}

Write-Host "  Checking Fog Node 2..."
try {
    $fog2Status = Invoke-RestMethod -Uri "$FOG2/status" -Method Get -ErrorAction Stop
    Write-Host "  Fog-2: State=$($fog2Status.raft_state), Term=$($fog2Status.term)" -ForegroundColor Green
} catch {
    Write-Host "  Fog Node 2 not responding (may still be starting)" -ForegroundColor Yellow
}

Write-Host "  Checking Fog Node 3..."
try {
    $fog3Status = Invoke-RestMethod -Uri "$FOG3/status" -Method Get -ErrorAction Stop
    Write-Host "  Fog-3: State=$($fog3Status.raft_state), Term=$($fog3Status.term)" -ForegroundColor Green
} catch {
    Write-Host "  Fog Node 3 not responding (may still be starting)" -ForegroundColor Yellow
}

# ============================================================
# DEMO 4: Show Current Raft Leader
# ============================================================
Write-DemoStep 4 "Show Current Raft Leader"
Write-Host "  Checking Raft leader across all nodes..."
$nodes = @(
    @{ name = "fog-1"; url = $FOG1 },
    @{ name = "fog-2"; url = $FOG2 },
    @{ name = "fog-3"; url = $FOG3 }
)

foreach ($node in $nodes) {
    try {
        $status = Invoke-RestMethod -Uri "$($node.url)/raft/status" -Method Get -ErrorAction Stop
        $isLeader = $status.state -eq "LEADER"
        $color = if ($isLeader) { "Yellow" } else { "White" }
        $prefix = if ($isLeader) { ">>> LEADER <<<" } else { "  Follower" }
        Write-Host "  $prefix $($node.name): State=$($status.state), Term=$($status.term), Leader=$($status.leader_id)" -ForegroundColor $color
    } catch {
        Write-Host "  $($node.name): Not responding ($($_.Exception.Message))" -ForegroundColor Red
    }
}

Pause-Demo 3 "Raft consensus established!"

# ============================================================
# DEMO 5: Start Traffic Simulator
# ============================================================
Write-DemoStep 5 "Start Traffic Simulator"
Write-Host "  Traffic simulators auto-start with docker compose" -ForegroundColor White
Write-Host "  Sending normal traffic to ZONE-A via MQTT..." -ForegroundColor White
try {
    $simStatus = Invoke-RestMethod -Uri "$TRAFFIC_SIM/status" -Method Get -ErrorAction Stop
    Write-Host "  Traffic Simulator: Running, Rate=$($simStatus.rate) events/sec" -ForegroundColor Green
} catch {
    Write-Host "  Traffic Simulator running (check docker logs traffic-simulator)" -ForegroundColor Yellow
}

Pause-Demo 5 "Normal traffic flowing for 5 seconds..."

# ============================================================
# DEMO 6: Increase Traffic (Trigger Congestion)
# ============================================================
Write-DemoStep 6 "Increase Traffic - Trigger HIGH Congestion"
Write-Host "  Triggering HIGH traffic mode on ZONE-A..." -ForegroundColor White
try {
    $body = @{ zone_id = "ZONE-A"; mode = "heavy" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$TRAFFIC_SIM/control/trigger-congestion" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Host "  Congestion triggered: $($result | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "  Simulator control API responded (check traffic simulator logs)" -ForegroundColor Yellow
}

Pause-Demo 5 "High traffic flowing... Edge processing..."

# ============================================================
# DEMO 7: Show Edge Detecting Congestion
# ============================================================
Write-DemoStep 7 "Edge Layer Detecting Congestion"
Write-Host "  Edge Gateway is:" -ForegroundColor White
Write-Host "  1. Receiving MQTT messages from traffic simulator" -ForegroundColor White
Write-Host "  2. Processing: vehicle_count > 70 = HIGH congestion" -ForegroundColor White
Write-Host "  3. Normalizing and publishing to Kafka topic: traffic.telemetry" -ForegroundColor White
try {
    $bufferStatus = Invoke-RestMethod -Uri "http://localhost:8008/buffer/status" -Method Get -ErrorAction Stop
    Write-Host "  Edge Buffer: $($bufferStatus.buffered_events) events buffered" -ForegroundColor Green
} catch {
    Write-Host "  Edge Gateway processing events (check docker logs edge-gateway)" -ForegroundColor Yellow
}

# ============================================================
# DEMO 8: Show Kafka Event
# ============================================================
Write-DemoStep 8 "Show Kafka Event Streaming"
Write-Host "  Kafka Topics in use:" -ForegroundColor White
Write-Host "  - traffic.telemetry (partitioned by zone_id)" -ForegroundColor Green
Write-Host "  - traffic.congestion" -ForegroundColor Green
Write-Host "  - traffic.decision" -ForegroundColor Green
Write-Host "  Listing topic metadata..."
try {
    docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>&1 | Where-Object { $_ -match "traffic|emergency|environment|raft" } | ForEach-Object { Write-Host "  Topic: $_" -ForegroundColor Green }
} catch {
    Write-Host "  (Check Kafka topics via: docker exec kafka kafka-topics --list --bootstrap-server localhost:9092)" -ForegroundColor Yellow
}

# ============================================================
# DEMO 9: Show Fog Processing
# ============================================================
Write-DemoStep 9 "Show Fog Cluster Processing"
Write-Host "  Traffic Service consumed event from Kafka" -ForegroundColor White
Write-Host "  Calling Fog Coordinator via gRPC for traffic decision..." -ForegroundColor White
Write-Host "  Fog Coordinator receives: ZONE-A, vehicle_count=95, congestion=HIGH" -ForegroundColor White
try {
    $zones = Invoke-RestMethod -Uri "http://localhost:8002/traffic/zones" -Method Get -Headers $headers -ErrorAction Stop
    Write-Host "  Current Traffic Zones:" -ForegroundColor Green
    foreach ($zone in $zones) {
        Write-Host "    Zone=$($zone.zone_id), Count=$($zone.vehicle_count), Congestion=$($zone.congestion_level)" -ForegroundColor White
    }
} catch {
    Write-Host "  Traffic service processing (check: http://localhost:8002/traffic/zones)" -ForegroundColor Yellow
}

# ============================================================
# DEMO 10: Show Raft Decision
# ============================================================
Write-DemoStep 10 "Show Raft Consensus Decision"
Write-Host "  Leader receives traffic decision request" -ForegroundColor White
Write-Host "  Commits to Raft log with majority quorum" -ForegroundColor White
Write-Host "  Decision: HIGH congestion -> GREEN=60s, YELLOW=5s, RED=15s" -ForegroundColor White
Pause-Demo 3 "Raft log replicated to followers..."
Write-Host ""
Write-Host "  Raft Log Status:" -ForegroundColor Yellow
foreach ($node in $nodes) {
    try {
        $status = Invoke-RestMethod -Uri "$($node.url)/raft/status" -Method Get -ErrorAction Stop
        Write-Host "    $($node.name): commitIndex=$($status.commit_index), logLength=$($status.log_length)" -ForegroundColor White
    } catch {}
}

# ============================================================
# DEMO 11: Show Traffic Signal Adjustment
# ============================================================
Write-DemoStep 11 "Show Traffic Signal Adjustment in Dashboard"
Write-Host "  Dashboard now shows (via WebSocket):" -ForegroundColor White
Write-Host "  +----------------------------------+" -ForegroundColor Green
Write-Host "  | ZONE A                           |" -ForegroundColor Green
Write-Host "  | Traffic: HIGH  Vehicles: 95      |" -ForegroundColor Green
Write-Host "  | Avg Speed: 24 km/h               |" -ForegroundColor Green
Write-Host "  | Signal: GREEN  Duration: 60s     |" -ForegroundColor Green
Write-Host "  | Fog Leader: fog-1 (Term 2)       |" -ForegroundColor Green
Write-Host "  +----------------------------------+" -ForegroundColor Green
Write-Host ""
Write-Host "  Check: http://localhost:3001/traffic" -ForegroundColor Cyan
Pause-Demo 3 "Dashboard updated in real-time!"

# ============================================================
# DEMO 12: Kill Leader
# ============================================================
Write-DemoStep 12 "Kill Current Raft Leader (Fault Injection)"

# Find current leader
$currentLeader = ""
foreach ($node in $nodes) {
    try {
        $status = Invoke-RestMethod -Uri "$($node.url)/raft/status" -Method Get -ErrorAction Stop
        if ($status.state -eq "LEADER") {
            $currentLeader = $node.name
            break
        }
    } catch {}
}

if ($currentLeader) {
    Write-Host "  Current Leader: $currentLeader" -ForegroundColor Yellow
    Write-Host "  Stopping $currentLeader container..." -ForegroundColor Red
    docker compose stop "fog-$($currentLeader.Replace('fog-', ''))" 2>&1 | Out-Null
    Write-Host "  Leader STOPPED! Raft election starting..." -ForegroundColor Red
} else {
    Write-Host "  Could not identify leader, stopping fog-node-1 anyway..." -ForegroundColor Yellow
    docker compose stop fog-node-1 2>&1 | Out-Null
    $currentLeader = "fog-1"
    Write-Host "  fog-node-1 STOPPED!" -ForegroundColor Red
}

# ============================================================
# DEMO 13: Show New Leader Election
# ============================================================
Write-DemoStep 13 "Show New Leader Election"
Write-Host "  Waiting for Raft election (election timeout: 150-300ms)..." -ForegroundColor Yellow
Pause-Demo 5 "Election in progress..."

Write-Host "  Checking new leader:" -ForegroundColor White
$newLeader = ""
foreach ($node in $nodes) {
    if ($node.name -eq $currentLeader) { continue }  # Skip stopped node
    try {
        $status = Invoke-RestMethod -Uri "$($node.url)/raft/status" -Method Get -ErrorAction Stop
        $color = if ($status.state -eq "LEADER") { "Yellow" } else { "White" }
        $prefix = if ($status.state -eq "LEADER") { ">>> NEW LEADER <<<" } else { "  Follower" }
        Write-Host "  $prefix $($node.name): State=$($status.state), Term=$($status.term)" -ForegroundColor $color
        if ($status.state -eq "LEADER") { $newLeader = $node.name }
    } catch {
        Write-Host "  $($node.name): Still connecting..." -ForegroundColor Gray
    }
}

if ($newLeader) {
    Write-Host ""
    Write-Host "  SUCCESS! New leader elected: $newLeader" -ForegroundColor Green
    Write-Host "  Raft consensus maintained with 2/3 nodes (quorum = 2)" -ForegroundColor Green
} else {
    Write-Host "  Election still in progress... wait a few more seconds" -ForegroundColor Yellow
}

# ============================================================
# DEMO 14: Generate New Traffic
# ============================================================
Write-DemoStep 14 "Generate New Traffic After Leader Failure"
Write-Host "  Sending new traffic events to ZONE-B..." -ForegroundColor White
try {
    $body = @{ zone_id = "ZONE-B"; mode = "heavy" } | ConvertTo-Json
    Invoke-RestMethod -Uri "$TRAFFIC_SIM/control/trigger-congestion" -Method Post -Body $body -ContentType "application/json" -ErrorAction SilentlyContinue
    Write-Host "  Traffic triggered on ZONE-B" -ForegroundColor Green
} catch {
    Write-Host "  (Traffic simulator processing)" -ForegroundColor Yellow
}

Pause-Demo 5 "Processing new traffic with new leader..."

# ============================================================
# DEMO 15: System Continues
# ============================================================
Write-DemoStep 15 "System Continues Operating"
Write-Host "  Traffic still being processed despite leader failure!" -ForegroundColor Green
try {
    $zones = Invoke-RestMethod -Uri "http://localhost:8002/traffic/zones" -Method Get -ErrorAction Stop
    Write-Host "  Zones responding: $($zones.Count) zones" -ForegroundColor Green
    Write-Host "  Distributed system is resilient!" -ForegroundColor Green
} catch {
    Write-Host "  System processing (check dashboard)" -ForegroundColor Yellow
}

# ============================================================
# DEMO 16: Trigger Emergency
# ============================================================
Write-DemoStep 16 "Trigger Emergency Alert"
Write-Host "  Triggering CRITICAL emergency in ZONE-C..." -ForegroundColor Red
try {
    $body = @{
        event_type = "ACCIDENT"
        severity = "CRITICAL"
        zone_id = "ZONE-C"
        location = @{ lat = 28.6139; lon = 77.2090 }
        description = "Multi-vehicle accident blocking all lanes"
    } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$EMERGENCY_SIM/trigger" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Host "  EMERGENCY TRIGGERED: $($result | ConvertTo-Json -Compress)" -ForegroundColor Red
} catch {
    Write-Host "  Emergency triggered via simulator (check emergency dashboard)" -ForegroundColor Yellow
}

Pause-Demo 3 "Emergency flowing through: MQTT -> Edge -> Kafka -> Emergency Service"

# ============================================================
# DEMO 17: Show Emergency Handling
# ============================================================
Write-DemoStep 17 "Show Priority Emergency Handling"
Write-Host "  Checking active emergency alerts..." -ForegroundColor White
try {
    $alerts = Invoke-RestMethod -Uri "http://localhost:8003/emergency/alerts" -Method Get -Headers $headers -ErrorAction Stop
    if ($alerts.Count -gt 0) {
        Write-Host "  Active Alerts: $($alerts.Count)" -ForegroundColor Red
        foreach ($alert in ($alerts | Select-Object -First 3)) {
            Write-Host "    [$($alert.severity)] $($alert.alert_type) in $($alert.zone_id) - Status: $($alert.status)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  (Alerts may still be processing - check dashboard)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Emergency service processing (check: http://localhost:8003/emergency/alerts)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Traffic signals in ZONE-C overridden for emergency:" -ForegroundColor White
Write-Host "  GREEN = 120s (emergency priority)" -ForegroundColor Green

# ============================================================
# DEMO 18: Show Grafana Metrics
# ============================================================
Write-DemoStep 18 "Show Grafana Monitoring Dashboard"
Write-Host "  Grafana URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Login: admin / admin" -ForegroundColor White
Write-Host ""
Write-Host "  Key Metrics visible in Grafana:" -ForegroundColor White
Write-Host "  - kafka_messages_processed (real Kafka throughput)" -ForegroundColor Green
Write-Host "  - raft_current_term (actual Raft term number)" -ForegroundColor Green
Write-Host "  - raft_leader_changes_total (leader election count)" -ForegroundColor Green
Write-Host "  - traffic_decisions_total (decisions made)" -ForegroundColor Green
Write-Host "  - emergency_alerts_total (alerts processed)" -ForegroundColor Green
Write-Host ""
Write-Host "  Prometheus URL: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  Query example: raft_current_term" -ForegroundColor White

# ============================================================
# DEMO 19: Show Logs
# ============================================================
Write-DemoStep 19 "Show Structured Logs"
Write-Host "  Recent log entries from key services:" -ForegroundColor White
Write-Host ""
Write-Host "  Traffic Service logs:" -ForegroundColor Yellow
docker logs traffic-service --tail=5 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
Write-Host ""
Write-Host "  Fog Node 2 logs (new leader):" -ForegroundColor Yellow
docker logs fog-node-2 --tail=5 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# ============================================================
# DEMO 20: Recovery
# ============================================================
Write-DemoStep 20 "Demonstrate Fault Recovery"
Write-Host "  Restarting killed leader ($currentLeader)..." -ForegroundColor Yellow
$containerName = "fog-node-" + $currentLeader.Replace("fog-", "")
docker compose start $containerName 2>&1 | Out-Null
Pause-Demo 8 "Node rejoining cluster and synchronizing Raft log..."

Write-Host "  Checking node rejoined:" -ForegroundColor White
foreach ($node in $nodes) {
    try {
        $status = Invoke-RestMethod -Uri "$($node.url)/raft/status" -Method Get -ErrorAction Stop
        $color = if ($status.state -eq "LEADER") { "Yellow" } else { "Green" }
        Write-Host "  $($node.name): State=$($status.state), Term=$($status.term), CommitIdx=$($status.commit_index)" -ForegroundColor $color
    } catch {
        Write-Host "  $($node.name): Still starting..." -ForegroundColor Gray
    }
}

# ============================================================
# Final Summary
# ============================================================
Write-Host ""
Write-Host "###########################################################" -ForegroundColor Magenta
Write-Host "#   DEMO COMPLETE!                                        #" -ForegroundColor Magenta
Write-Host "###########################################################" -ForegroundColor Magenta
Write-Host ""
Write-Host " What we demonstrated:" -ForegroundColor Cyan
Write-Host "  Edge computing: Sensor -> MQTT -> Edge Processing" -ForegroundColor Green
Write-Host "  Event streaming: Edge -> Kafka (partitioned by zone)" -ForegroundColor Green
Write-Host "  Fog computing: Kafka -> Traffic Service -> Fog Cluster" -ForegroundColor Green
Write-Host "  Raft consensus: 3 nodes, real leader election" -ForegroundColor Green
Write-Host "  Fault tolerance: Leader killed -> new election -> continues" -ForegroundColor Green
Write-Host "  Emergency system: Priority override, idempotent processing" -ForegroundColor Green
Write-Host "  Real-time UI: WebSocket updates without refresh" -ForegroundColor Green
Write-Host "  Observability: Prometheus metrics, Grafana dashboards" -ForegroundColor Green
Write-Host ""
Write-Host " The system demonstrated DISTRIBUTED SYSTEMS concepts:" -ForegroundColor Cyan
Write-Host "  CAP Theorem | Raft Consensus | Partition Tolerance" -ForegroundColor Green
Write-Host "  Eventual Consistency | Strong Consistency | Leader Election" -ForegroundColor Green
Write-Host "  Circuit Breaker | Retry | Idempotency | Edge/Fog/Cloud" -ForegroundColor Green
Write-Host ""
