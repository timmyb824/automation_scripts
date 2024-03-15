#!/usr/bin/env bash

# Function to log messages with timestamps
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if the script is run as root
if [ "$(id -u)" -ne 0 ]; then
    log "This script must be run as root."
    exit 1
fi

# Safety check: confirm with the user if run manually
# read -p "Are you sure you want to drop caches? This can affect system performance. Type 'yes' to confirm: " confirm
# if [ "$confirm" != "yes" ]; then
#     log "Cache drop canceled by the user."
#     exit 0
# fi

# Cache drop level can be passed as a command-line argument
# Default to 3 if no argument is provided
CACHE_LEVEL=${1:-3}

# Validate cache drop level
if ! [[ "$CACHE_LEVEL" =~ ^[1-3]$ ]]; then
    log "Invalid cache level '$CACHE_LEVEL'. Use a value between 1 and 3."
    exit 1
fi

# Drop caches
echo "$CACHE_LEVEL" > /proc/sys/vm/drop_caches
log "Dropped caches with level $CACHE_LEVEL."

curl -m 10 --retry 5 https://healthchecks.timmybtech.com/ping/$SLUG >/dev/null 2>&1

exit 0
