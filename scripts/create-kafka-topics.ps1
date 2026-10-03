Write-Host "Creating Kafka topics..."
$topics = @(
    "traffic.telemetry:5",
    "traffic.congestion:3",
    "traffic.decision:3",
    "environment.telemetry:3",
    "environment.alert:3",
    "emergency.alert:3",
    "device.status:3",
    "system.events:3",
    "raft.events:3",
    "audit.events:3"
)
foreach ($t in $topics) {
    $parts = $t -split ":"
    $topic = $parts[0]
    $partitions = $parts[1]
    docker exec kafka kafka-topics --create --topic $topic --partitions $partitions --replication-factor 1 --bootstrap-server localhost:9092 --if-not-exists
}
Write-Host "Topics created."
