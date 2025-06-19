import streamlit as st
from ollama_parser import parse_command_with_ollama
from google_calendar import create_calendar_event

def auto_detect_email(name):
    return name.lower().replace(" ", ".") + "@girnarsoft.com"

def resolve_emails_web(name_list):
    emails = []
    for name in name_list:
        default = auto_detect_email(name)
        email = st.text_input(f"Email for {name}:", default)
        emails.append(email)
    return emails

st.set_page_config(page_title="Calendar AI Assistant", layout="centered")
st.title("📅 Calendar AI Bot")
st.markdown("Type a meeting command and let AI do the rest.")

input_text = st.text_area("📝 Meeting command", height=120, placeholder="Book a meeting with Abhya Khare and Dhruv Gupta on June 20 at 5 PM for partner demo")

if st.button("🔧 Parse and Schedule"):
    if not input_text.strip():
        st.warning("Please enter a meeting command.")
    else:
        parsed = parse_command_with_ollama(input_text)
        if not parsed:
            st.error("❌ Could not parse the input.")
        else:
            st.success("✅ Parsed successfully!")
            st.json(parsed)

            to_emails = resolve_emails_web(parsed["To"])
            cc_emails = resolve_emails_web(parsed["Cc"]) if parsed["Cc"] else []

            create_calendar_event(
                to_names=parsed["To"],
                to_emails=to_emails,
                cc_emails=cc_emails,
                date=parsed["Date"],
                time=parsed["Time"],
                agenda=parsed["Agenda"]
            )
            st.success("🎉 Meeting scheduled and confirmation sent.")
