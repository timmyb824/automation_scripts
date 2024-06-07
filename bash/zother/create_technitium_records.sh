#!/bin/bash

# Set up logging
log_file="record_creation.log"
exec > >(tee -a "$log_file") 2>&1

token=$TECH_TOKEN
api_url="http://192.168.86.213:5380/api/zones/records/add"
zone=timmybtech.com

declare -A records=(
    [LIST IN ANOTHER FILE]
)

for domain in "${!records[@]}"; do
    answer=${records[$domain]}

    if echo "$answer" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
        # A record
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$api_url?token=$token&domain=$domain&zone=$zone" \
            -H 'Content-Type: application/x-www-form-urlencoded' \
            --data-urlencode "type=A" \
            --data-urlencode "ttl=3600" \
            --data-urlencode "ipAddress=$answer")
    else
        # CNAME record
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$api_url?token=$token&domain=$domain&zone=$zone" \
            -H 'Content-Type: application/x-www-form-urlencoded' \
            --data-urlencode "type=CNAME" \
            --data-urlencode "ttl=3600" \
            --data-urlencode "cname=$answer")
    fi

    if [ "$response" -eq 200 ]; then
        echo "Successfully created record for $domain"
    else
        echo "Failed to create record for $domain with response code $response"
    fi
done
