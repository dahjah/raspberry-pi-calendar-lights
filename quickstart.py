from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import keyboard
import time
from datetime import timedelta

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class raspberryCalendar:

    def __init__(self,debug=False):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.settings = None
        self.calservice = None
        self.debug = debug
        self.connectToGoogle()
        self.loadSettings()
    
    def runCalTest(self):
        """Runs the default calendar code found in the python gCal tutorial.
        """
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        self.debug and print('Getting the upcoming 10 events')
        events_result = self.calservice.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    def connectToGoogle(self):
        """Connects to gCal using existing token.pickle, or asks the user to open their
        browser and auth.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        self.calservice = service

    def loadSettings(self, dir=""):
        """Loads (or reloads) the settings for the application.
        """
        # Load up settings file, or set defaults
        default_settings = {"time_per_push":15, "poll_rate":5}
        default_path = 'gcalsettings.json'
        if dir:
            default_path = f"dir/{default_path}"
        if os.path.exists(default_path):
            with open(default_path, 'rb') as f:
                default_settings = json.load(f)
                
            self.debug and print("Using Custom Settings:", default_settings)
        else:
            self.debug and print("No settings file found, using defaults")
        self.settings = default_settings


    def listenForButton(self):
        print('listening for button press')
        while True:
            try:
                if keyboard.is_pressed('q'):
                    print('Quit!')
                    return
                if keyboard.is_pressed('enter'):
                    print("Setting calendar")
                    self.setCalendar()
                    time.sleep(.05)
            except Exception as e:
                print(e)
                return

    def setCalendar(self):
        self.debug and print((datetime.datetime.now() + timedelta(minutes=self.settings["time_per_push"]))
                .strftime("%Y-%m-%dT%H:%M:%S"))
        self.debug and print("starting set calendar")
        event = self.settings.get("calendarFormat")
        event["start"] = {
            'dateTime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'America/Denver',
        }
        event["end"]= {
            'dateTime': (datetime.datetime.now() + timedelta(minutes=self.settings["time_per_push"]))
                            .strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'America/Denver',
        }
        self.debug and print(event)

        event = self.calservice.events().insert(calendarId='primary', body=event).execute()
        print(event.get('htmlLink'))
        return event.get('htmlLink')
    
    def checkCalendar(self):
        """ TODO: FINISH comparing dates to see what lights to show
        """
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        self.debug and print('Getting the upcoming 10 events')
        events_result = self.calservice.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        if events:
            event = events[0]
            start = event['start'].get('dateTime', event['start'].get('date'))
            next_event = datetime.datetime.strptime(start[:19],"%Y-%m-%dT%H:%M:%S")

    

if __name__ == '__main__':
    rasp = raspberryCalendar()
    rasp.listenForButton()

