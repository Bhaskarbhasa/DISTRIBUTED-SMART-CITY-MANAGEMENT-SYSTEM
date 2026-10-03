Write-Host "Starting load test: 100 events/sec for 60 seconds..."
for ($i=1; $i -le 60; $i++) {
    for ($j=1; $j -le 100; $j++) {
        # Simulate send (in reality use a proper tool like k6 or locust, this is a placeholder script structure)
    }
    Start-Sleep -Seconds 1
    Write-Host "Sent 100 events..."
}
Write-Host "Load test completed."
