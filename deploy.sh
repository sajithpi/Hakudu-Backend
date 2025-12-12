#!/bin/bash

# Build and deploy script for Haikudo Backend

set -e

echo "Building Haikudo Backend Docker image..."
docker build -t haikudo-backend:latest .

echo "Initializing Docker Swarm (if not already initialized)..."
docker swarm init 2>/dev/null || echo "Swarm already initialized"

echo "Deploying Haikudo Backend stack..."
docker stack deploy -c docker-compose.yml haikudo

echo "Waiting for services to be ready..."
sleep 10

echo "Checking service status..."
docker service ls | grep haikudo

echo "Stack deployed successfully!"
echo "API should be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"

echo "To check logs:"
echo "  docker service logs haikudo_haikudo-api"
echo "  docker service logs haikudo_postgres"

echo "To scale the API service:"
echo "  docker service scale haikudo_haikudo-api=3"

echo "To remove the stack:"
echo "  docker stack rm haikudo"
