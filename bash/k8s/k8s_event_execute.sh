#!/bin/bash

# This script monitors the events of a pod and executes a command when a readiness probe failure is detected
# In this case, we check for a readiness probe failure that causes the vault to seal and unseal the vault

# Set the name of the pod to monitor
POD_NAME="vault-0"

# Set the command to execute when a readiness probe failure is detected
COMMAND_TO_EXECUTE="kubectl exec vault-0 -n vault -- vault operator unseal $VAULT_UNSEAL_KEY"

execute_command=0

while true
do
    # Check the events of the pod for a readiness probe failure
    EVENTS=$(kubectl get events --field-selector involvedObject.name=$POD_NAME -n vault --output json | jq '.items[] | select(.reason=="Unhealthy") | select(.message | test("Readiness probe failed: Key"))')

    # If a readiness probe failure is detected, execute the specified command
    if [ ! -z "$EVENTS" ]
    then
        echo "Readiness probe failure detected for pod $POD_NAME"
        if [ $execute_command -eq 0 ]
        then
            $COMMAND_TO_EXECUTE
            execute_command=1
        fi
    else
        execute_command=0
    fi

    # Wait for an hour or 12 hours before checking again
    if [ $execute_command -eq 1 ]
    then
        sleep 13h
        echo "Waiting 13hours before checking again"
    else
        sleep 61m
        echo "Waiting for an hour before checking again"
    fi
done
