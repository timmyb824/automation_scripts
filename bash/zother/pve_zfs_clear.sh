#!/usr/bin/env bash

HEALTHCHECKS_URL=""

# Function to log messages with timestamps
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to send a signal to Healthchecks.io
signal_healthchecks() {
    local status=$1
    curl -m 10 --retry 5 "${HEALTHCHECKS_URL}/${status}" >/dev/null 2>&1
}

# Check if the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    log "This script must be run as root."
    signal_healthchecks 1
    exit 1
fi

# Pool name could be passed as a command-line argument
POOL_NAME=${1:-local-zfs2}

# Check if the pool exists
if ! zpool list "$POOL_NAME" &>/dev/null; then
    log "ZFS pool '$POOL_NAME' does not exist."
    signal_healthchecks 1
    exit 1
fi

# Clear the ZFS pool errors
if zpool clear "$POOL_NAME"; then
    log "Cleared errors on ZFS pool '$POOL_NAME'."
    signal_healthchecks 0
else
    log "Failed to clear errors on ZFS pool '$POOL_NAME'."
    signal_healthchecks 1
    exit 1
fi
