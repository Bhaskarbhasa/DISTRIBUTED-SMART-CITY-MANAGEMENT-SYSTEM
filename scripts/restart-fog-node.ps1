param([Parameter(Mandatory=$true)][string]$NodeName)
Write-Host "Restarting fog node: $NodeName"
docker compose start $NodeName
Write-Host "Node started. Observe cluster state recovery."
