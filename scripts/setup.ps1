Write-Host "Setting up Distributed Smart City Management System..."
Copy-Item -Path .env.example -Destination .env -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path data/postgres, data/redis, data/kafka | Out-Null
Write-Host "Setup complete. Please review .env and run ./scripts/start.ps1"
