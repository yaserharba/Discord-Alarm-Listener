
# 🚨 Discord Alarm Listener

  

> A Python script that listens for Discord notifications from specific users on a Linux desktop and triggers a persistent, audible alarm that can be stopped remotely.

  

This tool is designed for users who need an unmissable alert for messages from critical contacts, such as family or team leads, ensuring that important notifications are never ignored.

  

---

  

## ✨ Features

  

*  **Real-time Monitoring**: Listens directly to the Linux desktop's notification system for instant alerts.

*  **Targeted Alarms**: The alarm only triggers for senders you specify when running the script.

*  **Persistent Sound**: Plays an alarm sound on a continuous loop until it is acknowledged.

*  **Remote Stop Command**: The alarm can be silenced by a follow-up message from a target sender containing a specific keyword.

*  **No API/Bot Required**: Does not violate Discord's ToS as it does not use the Discord API or automate a user account. It simply reads local system notifications.

  

---

  

## ⚙️ Requirements

  

Before you begin, ensure you have the following:

  

1.  **A Linux Desktop Environment**: This script is built for and tested on Ubuntu (or similar Debian-based systems) using the standard notification system.

2.  **Python 3**: Your system must have Python 3 installed.

3.  **PulseAudio Player**: The script uses the `paplay` command to play sounds. You can install it with the following command if it's not already on your system:

```bash

sudo apt-get update && sudo  apt-get  install  pulseaudio-utils

```

  

---

  

## 🚀 Setup & Installation

  

Follow these steps to get the project running:

  

1.  **Download the Script**:

Save the latest version of the script and name it `notification_listener.py`.

  

2.  **Create a Virtual Environment** (Recommended):

Open a terminal in the project directory and run the following commands to create and activate an isolated Python environment.

```bash

python3 -m venv venv

source venv/bin/activate

```

  

3.  **Prepare the Alarm Sound**:

* Find a sound file you wish to use for the alarm (e.g., a `.wav` file).

* Place it in the **same directory** as the script.

* Rename the file to `alarm.wav` or update its name in the script's configuration section.

  

---

  

## ▶️ How to Use

  

You must specify the target senders' names as command-line arguments when you run the script.

  

### Running the Listener

  

Execute the script from your terminal using the following format. Enclose each sender's name in quotes if it contains spaces.

  

```bash

python  notification_listener.py  "Sender Name 1"  "Sender Name 2"  "Another Sender"

```

  

**Example:**

To monitor for notifications from "Yaser Harba 2" and "Waseem":

```bash

python  notification_listener.py  "Yaser Harba 2"  "Waseem"

```

  

The script will then start and print a confirmation of the senders it is monitoring.

  

### How the Alarm Works

  

*  **Triggering the Alarm**: When a Discord notification arrives and the sender's name is in your target list, the alarm will start playing continuously.

*  **Stopping the Alarm**: To stop the ringing, a **follow-up message** must be sent from **any of the target senders**. This message must contain the stop keyword (by default, "stop the alarm").

  

---

  

## 🔧 Configuration

  

You can easily customize the alarm behavior by editing the configuration variables at the top of the `notification_listener.py` script:

  

*  `ALARM_SOUND_FILE`: Change the string to match the name of your sound file (e.g., `"my_siren.wav"`).

*  `STOP_KEYWORD`: Change the keyword used to silence the alarm (e.g., `"quiet now"`).

  

---

  

## 🧠 How It Works

  

This script cleverly avoids the complexities and restrictions of the Discord API.

  

1. It runs the Linux command-line tool `dbus-monitor` as a background **subprocess**.

2.  `dbus-monitor` listens to all system-level notification signals sent by applications.

3. The Python script reads the output from this subprocess in real-time, line by line.

4. When it parses a block of text recognized as a Discord notification, it checks the sender's name against the target list provided at launch.

5. If a match is found, it spawns a separate **thread** to play the alarm sound in a loop. Using a thread prevents the main program from freezing while the alarm is active.

6. The alarm thread continuously checks a shared `Event` flag. When a stop command is received, the main thread sets this flag, causing the alarm loop in the secondary thread to terminate gracefully.