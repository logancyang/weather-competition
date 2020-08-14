"""Send an email message from the user's account.
To run, in root directory:
    python scheduled_email/send_email.py
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


url = settings.DRAGONBOT_URL
resp = requests.get(
    url, headers={"Content-Type": "application/json"}
)
data = resp.json()

sender = "lolo.yang86@gmail.com"
tos = {
    "logan1934@gmail.com": "Logan",
    "yuliaa001@gmail.com": "Evelyn"
}
subject = "Daily Weather Score Report by DragonBot🐲"
yesterday = datetime.today() - timedelta(days=1)
message_body = (
    f"Weather competition scores for yesterday "
    f"{yesterday.strftime('%m/%d/%Y')}:\n\n"
)
for city, score in data:
    message_body += f"\t{city}: {score:.2f}\n"


# This runs daily at ET06:00
@sched.scheduled_job("cron", hour=6, minute=0, timezone="America/New_York")
def send_daily_report():
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
            print(f"{datetime.now()}: Scheduled email sent for "
                  f"recipient: {address}")
        except Exception as e:
            print(f"Scheduled email failed to send to recipient "
                  f"{address}: {e}")


print("Scheduled job: started...")
sched.start()
