import json
import os

import requests

# Zabbix API endpoint
url = "http://zabbix.local.timmybtech.com/api_jsonrpc.php"
headers = {
    "Content-Type": "application/json-rpc",
}

# API Token
api_token = os.environ.get("ZABBIX_API_TOKEN")


def get_unacknowledged_problems(api_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "problem.get",
        "params": {
            "output": "extend",
            "acknowledged": False,
            "sortfield": ["eventid"],
            "sortorder": "DESC",
        },
        "auth": api_token,
        "id": 1,
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
    response.raise_for_status()

    return response.json()["result"]


def main():
    problems = get_unacknowledged_problems(api_token)
    for problem in problems:
        print(problem)


if __name__ == "__main__":
    main()
