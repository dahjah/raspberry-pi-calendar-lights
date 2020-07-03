import datetime
from datetime import timedelta
from dateutil.parser import parse
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import keyboard
import pytz
import board
import neopixel
from ast import literal_eval
from threading import Thread, Event

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
DEFAULT_SETTINGS = {"calendarFormat": {
    "summary": "Busy Timer Set",
    "description": "Busy"
},
    "time_per_push": 15,
    "poll_rate": 300,
    "neo_strip_size": 8,
    "neo_brightness": 0.5,
    "warning_RGB": "255,255,0",
    "busy_RGB": "255,0,0",
    "available_RGB": "0,255,0",
    "warning_time": 600,
    "tick_freq":1.0}


class raspberryCalendar:

    def __init__(self, debug=False):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.settings = None
        self.calservice = None
        self.debug = debug
        self.next_event = None
        self.last_checked = None
        self.connect_to_google()
        self.load_settings()
        self.pixels = neopixel.NeoPixel(
            board.D18,
            self.settings.get(
                "neo_strip_size",
                DEFAULT_SETTINGS["neo_strip_size"]),
            brightness=self.settings.get(
                "neo_brightness",
                DEFAULT_SETTINGS["neo_brightness"]))
        self.check_calendar()

    def connect_to_google(self):
        """Connects to gCal using existing token.pickle, or asks the user to
        open their browser and auth.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens,
        # and is  automatically when the authorization flow completes for the
        # first time.
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

    def load_settings(self, directory=""):
        """Loads (or reloads) the settings for the application.
        """
        # Load up settings file, or set defaults
        default_settings = DEFAULT_SETTINGS
        default_path = 'gcalsettings.json'
        if directory:
            default_path = f'{directory}/{default_path}'
        if os.path.exists(default_path):
            with open(default_path, 'rb') as f:
                default_settings = json.load(f)

            self.debug and print("Using Custom Settings:", default_settings)
        else:
            self.debug and print("No settings file found, using defaults")
        self.settings = default_settings
        debug_mode = self.settings.get("debug")
        if debug_mode == "true" or debug_mode:
            self.debug = True

    def set_calendar(self):
        """ Sets calendar event based on settings to mark as busy
        """
        self.debug and print(
            (datetime.datetime.now() +
             timedelta(
                minutes=self.settings["time_per_push"]))
            .strftime("%Y-%m-%dT%H:%M:%S"))
        self.debug and print("starting set calendar")
        event = self.settings.get("calendarFormat")
        event["start"] = {
            'dateTime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'America/Denver',
        }
        event["end"] = {
            'dateTime': (
                datetime.datetime.now() +
                timedelta(
                    minutes=self.settings["time_per_push"]))
            .strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'America/Denver',
        }
        self.debug and print(event)

        event = self.calservice.events().insert(
            calendarId='primary', body=event).execute()
        self.debug and print(event.get('htmlLink'))
        return event.get('htmlLink')

    def check_calendar(self):
        """ Checks the calendar and updates the next event, and last checked
        values on the object
        """
        self.debug and print("Check Calendar Called!")
        # Call the Calendar API
        # 'Z' indicates UTC
        now_utc_str = datetime.datetime.utcnow().isoformat() + 'Z'
        self.debug and print('Getting the upcoming 10 events')
        events_result = self.calservice.events().list(
            calendarId='primary',
            timeMin=now_utc_str,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime').execute()
        now = datetime.datetime.utcnow()
        self.last_checked = now
        events = events_result.get('items', [])
        if events:
            event = events[0]
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            next_event_start = parse(start).astimezone(pytz.timezone('UTC'))
            next_event_end = parse(end).astimezone(pytz.timezone('UTC'))
            next_event = {
                "start": next_event_start,
                "end": next_event_end,
                "details": event}
            self.next_event = next_event
            return next_event
        return None

    def get_seconds_until_next_event(self):
        """Checks the associated calendar for the next event, and returns the
        number of seconds before that event starts. This method will manage
        the polling frequency of gcal to ensure that it doesn't overload API
        requests to google. returns 0 if in an event, and -1 if no events are
        found
        """
        now = pytz.utc.localize(datetime.datetime.utcnow())
        since_last_poll = (now - pytz.utc.localize(self.last_checked)).seconds
        self.debug and print(f"Seconds since last poll: {since_last_poll}")

        if not self.next_event or since_last_poll > self.settings.get(
                "poll_rate", DEFAULT_SETTINGS["poll_rate"]):
            self.check_calendar()
        # No events found
        if not self.next_event:
            return -1
        # Currently in an event
        if self.next_event["start"] < now < self.next_event["end"]:
            return 0
        return (self.next_event["start"] - now).seconds

    def fill_lights(self, color):
        """ Color can be hex or RGB
        """
        if isinstance(color, str):
            if "#" in color:
                color = int(color.split("#")[1], 16)
            if "x" in color:
                color = int(color.split("x")[1], 16)
            if "," in color:
                color = literal_eval(color)
        self.pixels.fill(color)

    def turn_off_lights(self):
        """ Turns off all pixels
        """
        self.pixels.fill((0, 0, 0))

    def change_brightness(self, brightness):
        """ Changes pixel brightness
        """
        if isinstance(brightness, str):
            brightness = literal_eval(brightness)
        self.pixels.brightness(brightness)

    def listen_to_calendar(self, e=None):
        """ Listens to the user's calendar and updates pixels accordingly
        """
        self.debug and print("listening to calendar")
        warning_time = self.settings.get(
            "warning_time", DEFAULT_SETTINGS["warning_time"])
        keep_going = True
        while keep_going:
            if e:
                keep_going = not e.isSet()
            time_remaining = self.get_seconds_until_next_event()
            self.debug and print(
                f"time remaining until next event: {time_remaining}")
            if time_remaining > warning_time:
                self.fill_lights(
                    self.settings.get(
                        "available_RGB",
                        DEFAULT_SETTINGS["available_RGB"]))
            elif warning_time > time_remaining > 0:
                self.debug and print("warning")
                self.fill_lights(
                    self.settings.get(
                        "warning_RGB",
                        DEFAULT_SETTINGS["warning_RGB"]))
            elif time_remaining == 0:
                self.debug and print("busy")
                self.fill_lights(
                    self.settings.get(
                        "busy_RGB",
                        DEFAULT_SETTINGS["busy_RGB"]))
            elif time_remaining == -1:
                self.debug and print("No events found")
                self.pixels[0] = (255, 0, 0)
                self.pixels[-1] = (255, 0, 0)
                for pixel_num in range(1, len(self.pixels) - 1):
                    self.pixels[pixel_num] = (0, 0, 0)
                self.change_brightness(1.0)
            time.sleep(self.settings.get("tick_freq",DEFAULT_SETTINGS["tick_freq"]))
        self.turn_off_lights()

    def listen_for_button(self, e=None):
        """ Listens for button presses to quit or set event
        """
        self.debug and print('listening to keyboard')
        keep_going = True
        while keep_going:
            if e:
                keep_going = not e.isSet()
            try:
                if keyboard.is_pressed('q'):
                    self.debug and print('Quit!')
                    e.set()
                    return
                if keyboard.is_pressed('enter'):
                    self.debug and print("Setting calendar")
                    self.set_calendar()
                    self.check_calendar()
                    time.sleep(.05)

            except Exception as e:
                self.debug and print(e)
                return


if __name__ == '__main__':
    rasp = raspberryCalendar()
    e = Event()
    Thread(target=rasp.listen_for_button, kwargs={"e": e}).start()
    Thread(target=rasp.listen_to_calendar, kwargs={"e": e}).start()
