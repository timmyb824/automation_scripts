#!/bin/bash

# Define the container name and directory path
container_name="netdata"
directory_path="/home/opc/netdata"

# Function to check if docker-compose or docker compose is available
check_docker_compose_command() {
  if [ -x "$(command -v docker-compose)" ]; then
    echo "docker-compose"
  elif [ -x "$(command -v docker)" ]; then
    if docker compose version > /dev/null 2>&1; then
      echo "docker compose"
    else
      echo ""
    fi
  else
    echo ""
  fi
}

# Change directory to where your docker-compose.yml file is located
cd "$directory_path" || exit 1

# Use the appropriate Docker Compose command
compose_command=$(check_docker_compose_command)

if [ -z "$compose_command" ]; then
  echo "Neither docker-compose nor docker compose command is available."
  exit 1
fi

# Check if the container is running
if [ -z "$(docker ps -q -f name=^/${container_name}$)" ]; then
  echo "The container is not running. Starting the container with $compose_command"
  # Start the container with docker-compose if it's not running
  $compose_command up -d --force-recreate
else
    echo "The container is running. No need to start the container."
fi
