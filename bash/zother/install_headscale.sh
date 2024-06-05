#!/bin/bash

# Variables
HEADSCALE_VERSION="0.15.0"  # Example version, update to the latest version from the site
HEADSCALE_ARCH="amd64"      # Your system architecture, e.g., "amd64"
LOG_FILE="/var/log/headscale_install.log"

# Function to log messages
log() {
    local MESSAGE="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $MESSAGE" | tee -a "$LOG_FILE"
}

# Function to handle errors
error_exit() {
    local MESSAGE="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $MESSAGE" | tee -a "$LOG_FILE" >&2
    exit 1
}

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
    error_exit "This script must be run as root."
fi

# Step 1: Download the latest Headscale package
log "Downloading Headscale package..."
wget --output-document=headscale.deb \
    "https://github.com/juanfont/headscale/releases/download/v${HEADSCALE_VERSION}/headscale_${HEADSCALE_VERSION}_linux_${HEADSCALE_ARCH}.deb" \
    || error_exit "Failed to download Headscale package."

# Step 2: Install Headscale
log "Installing Headscale..."
sudo apt install -y ./headscale.deb || error_exit "Failed to install Headscale."

# Step 3: Enable Headscale service
log "Enabling Headscale service to start at boot..."
sudo systemctl enable headscale || error_exit "Failed to enable Headscale service."

# Step 4: Configure Headscale
log "Configuring Headscale..."
CONFIG_FILE="/etc/headscale/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    error_exit "Configuration file $CONFIG_FILE not found."
else
    nano "$CONFIG_FILE" || error_exit "Failed to edit configuration file."
fi

# Step 5: Start Headscale
log "Starting Headscale service..."
sudo systemctl start headscale || error_exit "Failed to start Headscale service."

# Step 6: Check Headscale status
log "Checking Headscale status..."
systemctl status headscale || error_exit "Headscale service is not running as expected."

# Prompt for the first username
read -rp "Enter the username for the first Headscale user: " USERNAME
if [ -z "$USERNAME" ]; then
    error_exit "Username cannot be empty."
fi

# Using Headscale: Create a user
log "Creating a user in Headscale with username: $USERNAME"
headscale users create "$USERNAME" || error_exit "Failed to create user."

# Instructions for registering a machine
log "To register a machine, run the following commands on a client machine:"
echo "tailscale up --login-server <YOUR_HEADSCALE_URL>"
echo "headscale --user $USERNAME nodes register --key <YOUR_MACHINE_KEY>"

# Instructions for registering a machine using a pre-authenticated key
log "To register a machine using a pre-authenticated key, use the following commands:"
echo "headscale --user $USERNAME preauthkeys create --reusable --expiration 24h"
echo "tailscale up --login-server <YOUR_HEADSCALE_URL> --authkey <YOUR_AUTH_KEY>"

log "Headscale installation and configuration completed successfully."
