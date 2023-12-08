import os

import requests

AUTH_KEY = os.environ.get("TAILSCALE_AUTHKEY")
ORGANIZATION = os.environ.get("EMAIL")
RASBERRYPI_IP = os.environ.get("RASBERRYPI_IP")
PIHOLE_IP = os.environ.get("PIHOLE_IP")

# make sure the auth key is set
if not AUTH_KEY:
    print("No auth key set")
    exit(1)

# make api request to get the current dns settings
r = requests.get(
    f"https://api.tailscale.com/api/v2/tailnet/{ORGANIZATION}/dns/nameservers",
    auth=(f"{AUTH_KEY}", ""),
    timeout=5,
)

if r.status_code != 200:
    print("Error getting current dns settings")
    exit(1)

# get the current dns settings
current_dns = r.json()["dns"][0]
print(f"Current DNS: {current_dns}")

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}
if current_dns == PIHOLE_IP:
    data = f'{"dns": ["{RASBERRYPI_IP}"]}'
    print("Changing DNS to rasberrypi")
else:
    data = f'{"dns": ["{PIHOLE_IP}"]}'
    print("Changing DNS to pihole2")

# make post request to change the dns settings
r = requests.post(
    f"https://api.tailscale.com/api/v2/tailnet/{ORGANIZATION}/dns/nameservers",
    headers=headers,
    data=data,
    auth=(f"{AUTH_KEY}", ""),
    timeout=5,
)

if r.status_code != 200:
    print("Error changing dns settings")
    exit(1)
