import base64
import datetime
import pytz
import streamlit as st
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_credentials():
    service_account_info = st.secrets["google_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    return creds

def create_calendar_event(to_names, to_emails, cc_emails, date, time, agenda):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    current_year = datetime.datetime.now().year
    try:
        start_datetime = datetime.datetime.strptime(f"{date} {current_year} {time}", "%B %d %Y %I %p")
    except ValueError:
        st.error("❌ Failed to parse date/time.")
        return

    start = start_datetime.isoformat()
    end = (start_datetime + datetime.timedelta(hours=1)).isoformat()

    attendees = [{"email": email} for email in to_emails + cc_emails]

    event = {
        "summary": agenda,
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
        "attendees": attendees
    }

    created_event = service.events().insert(
        calendarId="primary", body=event, sendUpdates="all"
    ).execute()

    st.success(f"📅 Event created: [View it here]({created_event.get('htmlLink')})")
    send_confirmation_email(creds, to_emails, cc_emails, agenda, created_event.get("htmlLink"))

def send_confirmation_email(creds, to_emails, cc_emails, subject, calendar_link):
    service = build("gmail", "v1", credentials=creds)
    message_body = f"""
Hello,

The meeting has been scheduled.

📝 Agenda: {subject}
📅 Calendar Event: {calendar_link}

Regards,  
Calendar AI Bot
"""

    message = MIMEText(message_body)
    message["to"] = ", ".join(to_emails)
    if cc_emails:
        message["cc"] = ", ".join(cc_emails)
    message["subject"] = f"Meeting Scheduled: {subject}"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
    st.success("✅ Gmail confirmation sent.")
