# Final Code - v10 - CLI Arguments
import subprocess
import threading
import os
import sys
from datetime import datetime

# --- Configuration ---
# 1. Place your alarm sound file (e.g., alarm.wav) in the same directory.
# 2. Set the correct file name here.
ALARM_SOUND_FILE = "alarm.wav"

# 3. The keyword in a message from the target sender that will stop the alarm.
STOP_KEYWORD = "stop the alarm"

# --- Global variables for alarm control ---
stop_alarm_event = threading.Event()
alarm_thread = None

class DiscordNotification:
    """
    A class to represent a parsed Discord notification.
    It holds the sender, message body, and the time it was received.
    """
    def __init__(self, sender, body, timestamp):
        self.sender = sender
        self.body = body
        self.timestamp = timestamp

    def __str__(self):
        """
        Provides a clean, professional string representation of the notification.
        """
        readable_time = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        output = (
            f"┌─────────────────────────────────────────────────────────┐\n"
            f"│  New Discord Notification                               │\n"
            f"├─────────────────────────────────────────────────────────┤\n"
            f"│ Time:    {readable_time:<46} │\n"
            f"│ From:    {self.sender:<46} │\n"
            f"│ Message: {self.body:<46} │\n"
            f"└─────────────────────────────────────────────────────────┘"
        )
        return output

def alarm_function(sound_file):
    """
    This function runs in a separate thread and plays the alarm sound repeatedly
    until the stop_alarm_event is set.
    """
    print("\n>>> ALARM THREAD STARTED <<<")
    if not os.path.exists(sound_file):
        print(f"!!! ALARM ERROR: Sound file not found at '{sound_file}'")
        return

    while not stop_alarm_event.is_set():
        try:
            subprocess.run(["paplay", sound_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"!!! ALARM ERROR: Could not play sound. Is 'paplay' installed?")
            break
    print(">>> ALARM THREAD STOPPED <<<\n")


def parse_notification_block(lines):
    """
    Parses a block of text from dbus-monitor to create a DiscordNotification object.
    """
    block_text = "".join(lines)
    if "member=Notify" not in block_text or 'string "discord"' not in block_text:
        return None

    string_lines = [line.strip() for line in lines if line.strip().startswith('string')]
    if len(string_lines) >= 4:
        sender = string_lines[2][8:-1]
        body = string_lines[3][8:-1]
        return DiscordNotification(sender=sender, body=body, timestamp=datetime.now())
    return None

def start_listening(target_senders):
    """
    Starts the dbus-monitor command and processes its output block by block.
    """
    global alarm_thread
    print("Listener v10 (CLI Arguments Mode) is starting...")
    print(f"Monitoring for senders: {target_senders}")
    command = ["dbus-monitor", "interface='org.freedesktop.Notifications'"]

    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
        )
        print("dbus-monitor is running. Waiting for notifications...")
        print("====================================================================")

        notification_block_lines = []
        for line in iter(process.stdout.readline, ''):
            if line.startswith('method call'):
                notification = parse_notification_block(notification_block_lines)
                if notification:
                    print(notification)
                    
                    # --- ALARM LOGIC ---
                    # Check if the notification sender is in our target list
                    is_target_sender = any(sender in notification.sender for sender in target_senders)
                    
                    if is_target_sender:
                        if STOP_KEYWORD in notification.body.lower():
                            if alarm_thread and alarm_thread.is_alive():
                                print("\n>>> STOP COMMAND RECEIVED. STOPPING ALARM... <<<")
                                stop_alarm_event.set()
                        
                        elif not (alarm_thread and alarm_thread.is_alive()):
                            print("\n>>> IMPORTANT SENDER DETECTED. STARTING ALARM... <<<")
                            stop_alarm_event.clear()
                            alarm_thread = threading.Thread(target=alarm_function, args=(ALARM_SOUND_FILE,), daemon=True)
                            alarm_thread.start()

                notification_block_lines = [line]
            else:
                notification_block_lines.append(line)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            print("Terminated the dbus-monitor background process.")

if __name__ == "__main__":
    # Check if command-line arguments (senders) are provided
    if len(sys.argv) < 2:
        print("ERROR: No senders provided.")
        print("Usage: python notification_listener.py \"Sender Name 1\" \"Sender Name 2\" ...")
        sys.exit(1)
        
    # The first argument (sys.argv[0]) is the script name, so senders start from index 1
    senders_from_args = sys.argv[1:]
    
    try:
        start_listening(senders_from_args)
    except KeyboardInterrupt:
        print("\nListener stopped by user.")
        stop_alarm_event.set()