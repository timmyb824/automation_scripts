import logging
import os

# import sys
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

import requests

# Set up logging to output to a file
logging.basicConfig(
    filename="/home/tbryant/logs/bills_reminder.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Set up logging to output to the terminal
# logging.basicConfig(
#     stream=sys.stdout,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com",
}

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("GOOGLE_APP_PASSWORD")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")
HEALTHCHECKS_URL = os.environ.get("HEALTHCHECKS_URL")


def send_message(phone_number, carrier, subject, message):
    # sourcery skip: extract-method
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)

    # Create the email message
    email_message = EmailMessage()
    email_message.set_content(message)
    email_message["To"] = recipient
    email_message["From"] = auth[0]
    email_message["Subject"] = subject

    try:
        # Connect to the Gmail SMTP server and send the message
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(auth[0], auth[1])
        server.send_message(email_message)
        server.quit()
        requests.get(HEALTHCHECKS_URL, timeout=10)

    except Exception as e:
        requests.get(f"{HEALTHCHECKS_URL}/fail", timeout=10)
        logging.error(
            "Failed to send reminder for the following bill(s): %s. Exception: %s",
            subject,
            e,
        )


# List of bills with the day of the month they are due
bills = {
    "Discover": 1,
    "Navient": 1,
    "CitiBank": 19,
    "Mohela": 24,
    "CapitalOne": 27,
    "Vickies": 27,
}

# Check if any bill is due tomorrow
tomorrow = (datetime.now() + timedelta(days=1)).date()
if bills_due_tomorrow := [
    bill_name for bill_name, due_day in bills.items() if due_day == tomorrow.day
]:
    bills_list = ", ".join(bills_due_tomorrow)
    subject = "Bill Reminder: Bills Due"
    message = f"Reminder: Your {bills_list} bill(s) are due tomorrow, on {tomorrow.strftime('%Y-%m-%d')}. Don't forget to pay them on time!"
    send_message(PHONE_NUMBER, "tmobile", subject, message)
    logging.info("Reminder sent for the following bill(s): %s", bills_list)
else:
    logging.info("No bills due tomorrow.")
    try:
        requests.get(HEALTHCHECKS_URL, timeout=10)
    except requests.RequestException as re:
        logging.error(
            "Failed to send health check signal when no bills are due. Exception: %s",
            re,
        )
