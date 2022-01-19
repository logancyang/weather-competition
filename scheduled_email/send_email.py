"""Send an email message from the user's account.
To run, in root directory:
    nohup python -u scheduled_email/send_email.py &> emaillog.out &
"""
import base64
import pickle
import requests
import os
import importlib.util
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apiclient import errors
from googleapiclient.discovery import build


path = Path(os.path.abspath(__file__))
parent = path.parent
root = parent.parent


# Trick to import parent folder (root) module
spec = importlib.util.spec_from_file_location(
    "settings.py", root/"settings.py")
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)

# NOTE: Cities in the email are hardcoded in this url
PROD_API_URL = settings.DRAGONBOT_URL
TEST_API_URL = settings.TEST_URL


sched = BlockingScheduler()


def sendMessage(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        msg_sent = (
            service.users().messages().send(
                userId=user_id, body=message).execute()
        )
        print("Message Id: %s" % msg_sent["id"])
        return msg_sent
    except errors.HttpError as error:
        print("An error occurred: %s" % error)


def createMessage(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': raw_message.decode()}


def construct_message_body(data):
    yesterday = datetime.today() - timedelta(days=1)
    message_body = (
        f"Weather score ranking for yesterday "
        f"{yesterday.strftime('%m/%d/%Y')}:\n\n"
    )
    for ind, (city, score, *description) in enumerate(data):
        message_body += f"\t{ind+1}. {city}: {score:.2f}\n"
        if not description:
            continue
        desc_list = []
        for prop, value in description[0].items():
            if value is True:
                desc_list.append(prop)
        max_temp = description[0].get('max_temp')
        desc_list.append(f"max real feel temperature: {max_temp:.2f}")
        avg_humid = description[0].get('avg_humid')
        desc_list.append(f"average humidity: {avg_humid:.2f}")
        desc = "\t\t" + ", ".join(desc_list) + "\n\n"
        message_body += desc
    return message_body


def query_build_msg_last24h(url):
    resp = requests.get(
        url, headers={"Content-Type": "application/json"}
    )
    data = resp.json()

    sender = "lolo.yang86@gmail.com"
    tos = {
        "logan1934@gmail.com": "Logan",
        "yuliaa001@gmail.com": "Evelyn"
    }
    subject = "Daily Weather Score Report for yesterday by DragonBot🐲"
    message_body = construct_message_body(data)
    return sender, tos, subject, message_body


@sched.scheduled_job("cron", hour=7, minute=0, timezone="America/New_York")
def send_daily_report():
    print("Query for daily report...")
    sender, tos, subject, message_body = query_build_msg_last24h(PROD_API_URL)
    print(f"Message constructed:\n\n{message_body}\n\n")
    print("Scheduled email: sending...")
    with open(parent/'token.pickle', 'rb') as token:
        creds = pickle.load(token)
    service = build('gmail', 'v1', credentials=creds)

    for address, user in tos.items():
        try:
            greeting = f"Hi {user},\n\n"
            message_text = greeting + message_body
            msg = createMessage(sender, address, subject, message_text)
            sendMessage(service, sender, msg)
            print(f"{datetime.now()}: Scheduled email successfully sent to "
                  f"recipient: {address}")
        except Exception as e:
            print(f"Scheduled email failed to send to recipient "
                  f"{address}: {e}")


# sender, tos, subject, message_body = query_build_msg_last24h(TEST_API_URL)
# print(message_body)
print("Scheduled job: started...")
sched.start()
