#!/bin/bash

# Check if pm2 is installed
if ! command -v pm2 &> /dev/null
then
    echo "pm2 could not be found. Please install it first."
    exit
fi

echo "-----Starting ping and http checks with prometheus-----"
echo ""

pm2 start monika --name="monika-ping-http" -- -c ./config/monika_all.yml --prometheus 3001

echo ""
sleep 5
echo ""

echo "-----Starting db check-----"
pm2 start monika --name="monika-db" -- -c ./config/monika_db.yml

echo ""
echo "All done!"
