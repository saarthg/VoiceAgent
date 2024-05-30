import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.tools import tool

from datetime import date
import datetime
today = date.today()

def docstring_parameter(*sub):
     def dec(obj):
         obj.__doc__ = obj.__doc__.format(*sub)
         return obj
     return dec

@tool
@docstring_parameter(today)
def add_calendar_event(summary, location, description, start_time, end_time):
  """Add event on Google calendar. Function takes in summary, location, description, and time of event. 
    The time should be formatted in the following format: 2024-05-28T09:00:00-07:00. Today's date is {0}.
  """
  SCOPES = ["https://www.googleapis.com/auth/gmail.compose", "https://www.googleapis.com/auth/calendar"]
  creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

  event = {
  'summary': summary,
  'location': location,
  'description': description,
  'start': {
    'dateTime': start_time,
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': end_time,
    'timeZone': 'America/Los_Angeles',
  },
  }

  try:
    service = build("calendar", "v3", credentials=creds)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

  except HttpError as error:
    print(f"An error occurred: {error}")


@tool
def get_upcoming_events(number_of_events):
  """Gets the next certain number of upcoming Google Calendar based on the user input. Takes in number of upcoming events.
  """
  SCOPES = ["https://www.googleapis.com/auth/gmail.compose", "https://www.googleapis.com/auth/calendar"]
  creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print(f"Getting the upcoming {number_of_events} events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=number_of_events,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")
  
  
  