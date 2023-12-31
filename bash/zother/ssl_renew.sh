#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose --ansi never"
DOCKER="/usr/bin/docker"
DIRECTORY="/home/tbryant/wordpress"

cd $DIRECTORY || exit
$COMPOSE run certbot renew && $COMPOSE kill -s SIGHUP webserver
$DOCKER system prune -af
