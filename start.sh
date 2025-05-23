#!/bin/bash
docker-compose up -d


sleep 5



echo ""
echo "🚀 Services are now running! Access them below:"
echo "🔹 Flask API        : http://localhost:5000"
echo "🔹 RabbitMQ UI      : http://localhost:15672  (user: guest | pass: guest)"
echo "🔹 Flower Dashboard : http://localhost:5555"
echo ""
echo "✅ Use CTRL+C to stop and 'docker-compose down' to clean up."
