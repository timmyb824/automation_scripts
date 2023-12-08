import calendar
import os
from datetime import date, datetime, timezone

import boto3
from gotify import Gotify
from rocketry import Rocketry
from rocketry.conds import daily, every

# import logging
from slack_sdk import WebClient

app = Rocketry()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
THRESHOLD = 5
GOTIFY = Gotify(
    base_url=os.environ["GOTIFY_HOST"],
    app_token=os.environ["GOTIFY_TOKEN_ADHOC_SCRIPTS"],
)

# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')


def get_current_costs() -> float:
    client = boto3.client("ce", "us-east-1")  # AWS Cost Explorer client

    # Get the current date and the first day of the month
    end = datetime.now(timezone.utc).date()
    start = datetime(end.year, end.month, 1).date()

    try:
        # Retrieve the cost and usage data
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
        )
    except Exception as exception:
        print(exception)
        return 0.0

    return response["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]


def get_end_of_month_projection(current_cost) -> tuple[float, float]:
    current_date = datetime.now().date()
    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
    current_day_of_month = current_date.day
    remaining_days = days_in_month - current_day_of_month
    projected_cost = (current_cost / current_date.day) * days_in_month
    projected_spending = (current_cost / current_date.day) * remaining_days

    return projected_cost, projected_spending


def send_slack_notification(message) -> dict:
    client = WebClient(token=SLACK_BOT_TOKEN)

    return client.chat_postMessage(channel="#alerts", text=message)


def send_gotify_notification(message) -> dict:
    try:
        return GOTIFY.create_message(
            title="AWS Cost Alert",
            message=message,
            priority=5,
            extras={"client::display": {"contentType": "text/markdown"}},
        )
    except Exception as exception:
        print(exception)
        return {}


def check_threshold_exceeded(projected_cost: float) -> bool | None:
    if projected_cost > THRESHOLD:
        message = f"ATTENTION! Projected end-of-month AWS costs of {projected_cost:.2f} USD exceeds {THRESHOLD} USD!"
        slack_response = send_slack_notification(message)
        gotify_response = send_gotify_notification(message)
        if slack_response["ok"] and gotify_response["id"]:
            print("Slack and Gotify notifications sent successfully.\n")
            return True
        elif slack_response["ok"]:
            print("Slack notification sent successfully.\n")
            return True
        elif gotify_response["id"]:
            print("Gotify notification sent successfully.\n")
            return True
        else:
            print("Failed to send Slack and Gotify notifications.\n")
            return False


# @app.task(daily.at("22:30"))
@app.task(every("1 minutes"))
def main():
    # logging.info('Script started successfully.')
    current_cost = get_current_costs()
    projected_cost, projected_spending = get_end_of_month_projection(
        float(current_cost)
    )
    print(f"Current month costs: {current_cost} USD")
    print(f"Projected end-of-month costs: {projected_cost:.2f} USD")
    print(f"Projected end-of-month spending: {projected_spending:.2f} USD")
    if not check_threshold_exceeded(projected_cost):
        print("No threshold exceeded.\n")
    return


if __name__ == "__main__":
    app.run()
