#!/bin/bash

DOCKER_EXEC="docker exec -i pihole bash -c"

echo "Deleting backups older than 5 days"
#$DOCKER_EXEC "find /backup -name "pi-hole-*" -mtime +5 -exec rm {} \;"
$DOCKER_EXEC "find /backup -maxdepth 1 -mtime +5 -name "pi-hole-*" -exec rm -rf '{}' ';'"

echo "Creating new backup"
$DOCKER_EXEC "cd /backup && pihole -a -t"
