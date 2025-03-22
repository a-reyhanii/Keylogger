from telebot import TeleBot
from db.main import DataBase
import os

class Bot:
    def __init__(self, token):
        self._bot_ = TeleBot(token)
        self._db = DataBase("data")
        self._init()

    def _init(self):
        @self._bot_.message_handler(func=lambda message: message.text.startswith('/start'))
        def welcome(message):
            self._bot_.send_message(message.chat.id, "Hi dear, welcome to the bot!")

        @self._bot_.message_handler(func=lambda message: message.text.startswith('/getlogs'))
        def get_logs(message):
            owner_data = self._db.get("owner")
            if not owner_data or "user_id" not in owner_data:
                self._bot_.send_message(message.chat.id, "Owner not defined!")
                return

            user_id = owner_data["user_id"]
            if message.chat.id != user_id:
                self._bot_.send_message(message.chat.id, "You do not have access!")
                return

            logs = self._db.get('logs')
            if logs:
                self._bot_.send_message(message.chat.id, f"Logs data: \n{logs}")
            else:
                self._bot_.send_message(message.chat.id, "No logs available.")

            directory_path = "logs"
            if not os.path.exists(directory_path):
                self._bot_.send_message(message.chat.id, "Log directory not found.")
                return

            files_sent = False
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        self._bot_.send_document(message.chat.id, f)
                    files_sent = True

            if not files_sent:
                self._bot_.send_message(message.chat.id, "No log files found.")

    def run(self):
        self._bot_.infinity_polling(timeout=125)

    def send_status(self, datas, mode, user_id):
        if mode == 'ok':
            self._bot_.send_message(user_id, f"Log successfully saved:\n{datas}")
        elif mode == 'error':
            self._bot_.send_message(user_id, f"Error detected:\n{datas}")
