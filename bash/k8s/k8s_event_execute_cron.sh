#!/bin/bash

# This script monitors the events of a pod and executes a command when a readiness probe failure is detected
# In this case, we check for a readiness probe failure that causes the vault to seal and unseal the vault

# Set the name of the pod to monitor
POD_NAME="vault-0"

# Set the command to execute when a readiness probe failure is detected
COMMAND_TO_EXECUTE="kubectl exec vault-0 -n vault -- vault operator unseal $VAULT_UNSEAL_KEY"

# Function to execute the command
execute_command() {
    echo "Readiness probe failure detected for pod $POD_NAME"
    $COMMAND_TO_EXECUTE
}

# Check the events of the pod for a readiness probe failure
check_events() {
    EVENTS=$(kubectl get events --field-selector involvedObject.name="$POD_NAME" -n vault --output json | jq '.items[] | select(.reason=="Unhealthy") | select(.message | test("Readiness probe failed: Key"))')
    if [ ! -z "$EVENTS" ]; then
        execute_command
    fi
}

# Run the initial check
check_events

# Set the cron schedule for the script
# Here, we schedule the script to run every hour
# You can adjust the cron schedule as per your requirements
# Make sure to update the path to the script accordingly
(crontab -l 2>/dev/null; echo "0 * * * * /path/to/script.sh") | crontab -
