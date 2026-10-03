param([Parameter(Mandatory=$true)][string]$NodeName)
Write-Host "Failing fog node: $NodeName"
docker compose stop $NodeName
Write-Host "Node stopped. Observe Raft leader election in dashboard/logs."
