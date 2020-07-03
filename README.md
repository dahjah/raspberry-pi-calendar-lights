# Raspberry Pi Google Calendar LED Notifier

> For those times when you need a visual queue you're late for a meeting.


---

## Installation
### Clone

- Clone this repo to your local machine using `https://github.com/dahjah/raspberry-pi-calendar-lights.git`

### Setup

- Install requirements:

```shell
$ pip install -r requirements.txt
```

Sometimes a few packages are needed to be installed system wide for the lights to work. If your lights aren't working, try installing with this:


```shell
$ sudo pip install -r requirements.txt
```
---

## Features

- Display colors based on time until next meeting

- automatically schedule out blocks of time with the push of a button

- Communicate to those around you if you're able to talk

- And more!

## Usage:
- run the following code to start up your application (sudo rights are needed to access the GPIO. If you won't be using the GPIO to interface with your lights, you can execute it sans sudo)
```shell
$ sudo python3 rasp_cal_notif.py
```

- If this is the first time running, it will open a web browser to have you login to your google account. This will require the pi be plugged into a monitor, or that you run on another machine and then copy the token.pickle file generated to your pi. (TODO: setup local webserver to oauth with.)
- Once running, the lights should immediately respond based on your calendar settings. If no events were able to be found, the first and last pixel will illuminate Red. This probably means that you need to auth a different calendar.
- Press ENTER to automatically fill in a busy time, and press "q" to shut the server down.
- If no gcalsettings.json is present, default settings will be used. Further documentation on what each setting does can be found below.

## Documentation


> Settings explanation:
- time_per_push: The amount of time (in minutes) to block off on the calendar for every button press. Defaults to 15 minutes
- poll_rate: The amount of time (in seconds) between checking the server for new calendar events. Defaults to 300 (5 minutes)
- calendarFormat: Template to use for each calendar event. Anything defined <a href="https://developers.google.com/calendar/create-events">here</a> goes, with the exception of start_time and end_time. Defaults to "Busy Timer Set"
- neo_strip_size: The number of neopixels in your strip. Defaults to 8
- neo_brightness: Decimal number from 0.0-1.0 representing the brightness of the strip. Defaults to .50 (50%)
- warning_RGB: Color value for the warning light- can be comma separated RGB, or hex. Defaults to Yellow
- busy_RGB: Color value for the busy light- can be comma separated RGB, or hex. Defaults to Red
- available_RGB: Color value for the available light- can be comma separated RGB, or hex. Defaults to Green
- warning_time: Time (in seconds) before an event to show the warning light. Defaults to 600 (10 minutes)
- tick_freq: Time (in seconds, can be partial seconds) to update lights. Defaults to 1.0
- debug: set this to true to print out debug statements in the console. Defaults to false
---

## Contributing

> To get started...

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone this repo to your local machine using `https://github.com/dahjah/raspberry-pi-calendar-lights.git`

### Step 2

- **HACK AWAY!** 🔨🔨🔨

### Step 3

- 🔃 Create a new pull request using <a href="https://github.com/dahjah/raspberry-pi-calendar-lights/compare/" target="_blank">`https://github.com/dahjah/raspberry-pi-calendar-lights/compare/`</a>.

---
---

## FAQ

---