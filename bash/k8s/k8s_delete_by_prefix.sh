#!/bin/bash

# Set the name prefix of the pods you want to delete
name_prefix="loki"
namespace="logging"

# Use `kubectl` to get a list of pods with the given prefix and force delete them
kubectl get pods --no-headers=true -n "$namespace" | awk '{if ($1 ~ /^'"$name_prefix"'/) print $1}' | xargs kubectl delete pod --force -n "$namespace"
