#!/bin/bash

# Explicitly set your PATH
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Define the container name, directory path, and log file
container_name="netdata"
directory_path="/home/opc/netdata"
log_file="/home/opc/scripts/check_and_run_container.log"

# Logging function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$log_file"
}

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

# Log the start of the script
log "Checking if $container_name container is running."

# Use the appropriate Docker Compose command
compose_command=$(check_docker_compose_command)

if [ -z "$compose_command" ]; then
  log "Neither docker-compose nor docker compose command is available."
  exit 1
fi

# Check if the container is running
if [ -z "$(docker ps -q -f name=^/${container_name}$)" ]; then
  log "The container $container_name is not running. Starting the container with $compose_command."
  # Start the container with docker-compose if it's not running
  if $compose_command -f "$directory_path/docker-compose.yml" up -d --force-recreate >> "$log_file" 2>&1; then
    log "The container $container_name has been started successfully."
  else
    log "Failed to start the container $container_name."
  fi
else
  log "The container $container_name is already running. No need to start the container."
fi
