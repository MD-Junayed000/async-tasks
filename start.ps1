# Start services silently in the background
docker-compose up -d

# Wait a bit for services to initialize
Start-Sleep -Seconds 5

# Show only the required URLs
Write-Host "`n🚀 Services are now running! Access them below:`n"
Write-Host "🔹 Flask API        : http://localhost:5000"
Write-Host "🔹 RabbitMQ UI      : http://localhost:15672  (user: guest | pass: guest)"
Write-Host "🔹 Flower Dashboard : http://localhost:5555"
Write-Host ""
Write-Host "📌 Use 'docker-compose logs -f [service]' to see logs."
Write-Host "📌 Use 'docker-compose down' to stop and clean up."