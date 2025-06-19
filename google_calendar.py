import base64
import datetime
import pytz
import os

from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES for both Calendar and Gmail
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_calendar_event(to_names, to_emails, cc_emails, date, time, agenda):
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # 🔧 Add current year if missing
    current_year = datetime.datetime.now().year
    try:
        start_datetime = datetime.datetime.strptime(f"{date} {current_year} {time}", "%B %d %Y %I %p")
    except ValueError:
        print("❌ Date/time parsing failed. Please check your input.")
        return

    start = start_datetime.isoformat()
    end = (start_datetime + datetime.timedelta(hours=1)).isoformat()

    attendees = [{'email': email} for email in to_emails + cc_emails]

    event = {
        'summary': agenda,
        'start': {'dateTime': start, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end, 'timeZone': 'Asia/Kolkata'},
        'attendees': attendees,
        'creator': {'email': to_emails[0]},     # Organizer
        'organizer': {'email': to_emails[0]}    # Ensure invites go out
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        sendUpdates='all'  # 🔔 Critical: triggers email invites
    ).execute()

    print(f"📅 Event created: {created_event.get('htmlLink')}")

    # Optional: Send manual Gmail confirmation
    send_confirmation_email(creds, to_emails, cc_emails, agenda, created_event.get('htmlLink'))

def send_confirmation_email(creds, to_emails, cc_emails, subject, calendar_link):
    service = build('gmail', 'v1', credentials=creds)

    message_body = f"""
Hello,

The meeting has been scheduled.

📝 Agenda: {subject}
📅 Calendar Event: {calendar_link}

Regards,  
Calendar AI Bot
"""

    message = MIMEText(message_body)
    message['to'] = ', '.join(to_emails)
    if cc_emails:
        message['cc'] = ', '.join(cc_emails)
    message['subject'] = f"Meeting Scheduled: {subject}"

    raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(userId="me", body={'raw': raw_msg}).execute()
    print("✅ Gmail confirmation sent.")
