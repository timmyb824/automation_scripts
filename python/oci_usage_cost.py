import datetime
import os

import oci.usage_api.models
from gotify import Gotify
from oci.usage_api.models import RequestSummarizedUsagesDetails
from rocketry import Rocketry
from rocketry.conds import daily, every
from slack_sdk import WebClient

app = Rocketry()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
THRESHOLD = 5
GOTIFY = Gotify(
    base_url=os.environ["GOTIFY_HOST"],
    app_token=os.environ["GOTIFY_TOKEN_ADHOC_SCRIPTS"],
)

# Load the config file
config = oci.config.from_file("~/.oci/config")

# Create a usage api client
usage_api_client = oci.usage_api.UsageapiClient(config)

# Get the tenant ID
tenant_id = config["tenancy"]

# Get the start date and end date for the current month
today = datetime.date.today()
start_date = datetime.date(today.year, today.month, 1)
end_date = today + datetime.timedelta(days=1)


def get_usage_totals() -> tuple:
    # Query the usage API for the total cost for this month
    usage_request = RequestSummarizedUsagesDetails(
        tenant_id=tenant_id,
        time_usage_started=start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        time_usage_ended=end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        granularity="DAILY",
        query_type="COST",
    )

    usage_response = usage_api_client.request_summarized_usages(usage_request)

    # Calculate the total computed amount and quantity for all services
    total_computed_amount = 0.0
    total_computed_quantity = 0.0

    items = usage_response.data.items

    for item in items:
        if item.computed_amount is not None:
            total_computed_amount += item.computed_amount
        if item.computed_quantity is not None:
            total_computed_quantity += item.computed_quantity

    return (total_computed_amount, total_computed_quantity)


def get_usage_totals_by_service() -> tuple:
    # Query the usage API for the total cost for this month, grouped by service
    usage_request = RequestSummarizedUsagesDetails(
        tenant_id=tenant_id,
        time_usage_started=start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        time_usage_ended=end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        granularity="DAILY",
        query_type="COST",
        group_by=["service"],
    )

    usage_response = usage_api_client.request_summarized_usages(usage_request)

    # Calculate the total computed amount and quantity for each service
    total_computed_amounts_by_service = {}
    total_computed_quantities_by_service = {}

    items = usage_response.data.items

    for item in items:
        if item.service not in total_computed_amounts_by_service:
            total_computed_amounts_by_service[item.service] = 0.0
        if item.service not in total_computed_quantities_by_service:
            total_computed_quantities_by_service[item.service] = 0.0

        if item.computed_amount is not None:
            total_computed_amounts_by_service[item.service] += item.computed_amount
        if item.computed_quantity is not None:
            total_computed_quantities_by_service[item.service] += item.computed_quantity

    return (total_computed_amounts_by_service, total_computed_quantities_by_service)


def send_slack_notification(message) -> dict:
    client = WebClient(token=SLACK_BOT_TOKEN)

    return client.chat_postMessage(channel="#alerts", text=message)


def send_gotify_notification(message) -> dict:
    try:
        return GOTIFY.create_message(
            title="OCI Cost Alert",
            message=message,
            priority=5,
            extras={"client::display": {"contentType": "text/markdown"}},
        )
    except Exception as exception:
        print(exception)
        return {}


def check_threshold_exceeded(total_computed_amount: float) -> bool:
    if total_computed_amount > THRESHOLD:
        message = f"ATTENTION! OCI costs of {total_computed_amount:.2f} USD exceeds {THRESHOLD} USD!"
        slack_response = send_slack_notification(message)
        gotify_response = send_gotify_notification(message)
        if slack_response["ok"] and gotify_response["id"]:
            print("\nSlack and Gotify notifications sent successfully.\n")
            print("###############################################\n")
            return True
        elif slack_response["ok"]:
            print("\nSlack notification sent successfully.\n")
            print("###############################################\n")
            return True
        elif gotify_response["id"]:
            print("\nGotify notification sent successfully.\n")
            print("###############################################\n")
            return True
        else:
            print("Failed to send Slack and Gotify notifications.\n")
            return False


# @app.task(daily.at("22:30"))
@app.task(every("60 seconds"))
def main() -> None:
    # Get the total cost for this month
    (total_computed_amount, total_computed_quantity) = get_usage_totals()

    # Get the total cost for this month, grouped by service
    (
        total_computed_amounts_by_service,
        total_computed_quantities_by_service,
    ) = get_usage_totals_by_service()

    print(f"Total cost for this month: {str(total_computed_amount)}")
    print(f"Total quantity for this month: {str(total_computed_quantity)}")

    for service, amount in total_computed_amounts_by_service.items():
        print(f"\nFor service {service}:")
        print(f"\tTotal Computed Amount: {amount}")
        print(
            f"\tTotal Computed Quantity: {total_computed_quantities_by_service[service]}"
        )

    if not check_threshold_exceeded(total_computed_amount):
        print("\nNo threshold exceeded.\n")
        print("###############################################\n")
    return


if __name__ == "__main__":
    app.run()
