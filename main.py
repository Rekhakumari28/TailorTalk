# main.py
from fastapi import FastAPI, Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

import datetime
import os

app = FastAPI()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SERVICE_ACCOUNT_FILE = "credentials/service_account.json"
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")  
TIMEZONE = "Asia/Kolkata"

# Set up Google Calendar API client
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build("calendar", "v3", credentials=credentials)

@app.post("/book")
async def book_event(request: Request):
    data = await request.json()
    event = {
        "summary": data["summary"],
        "start": {"dateTime": data["start"], "timeZone": TIMEZONE},
        "end": {"dateTime": data["end"], "timeZone": TIMEZONE},
    }
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return {"message": "Event created", "event_id": created_event["id"]}

@app.delete("/cancel/{event_id}")
def cancel_event(event_id: str):
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    return {"message": "Event cancelled"}
