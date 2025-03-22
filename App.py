from flask import Flask, request, jsonify
from bot import Bot
from db.main import DataBase
from datetime import datetime
import os
import threading


class App:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._db = DataBase("data")
        self._bot = Bot("TOKEN")
        self._app_= Flask(__name__)
        self._inits()

    def _inits(self):
        @self._app_.route('/test/', methods=["GET"])
        def test_server():
            try:
                return jsonify({
                    'status': 'ok'
                })
            except Exception as e:
                return jsonify({
                    'status': 'notok',
                    'error': str(e)
                })

        @self._app_.route('/set-log/', methods=["POST"])
        def set_log():
            try:
                data = request.get_json()
                user_id = self._db.get("owner")["user_id"]
                filename = data.get('filename')
                content = data.get('content')

                if not filename or not content:
                    self._bot.send_status({'error': 'file name or file content not detected'}, 'error', user_id)
                    return jsonify({
                        'status': 'ok',
                        'error': 'file not detected'
                    }), 404
                else:
                    with open(filename, "w") as f:
                        f.write(content)
                    
                    logs = self._db.get('logs')
                    logs[filename] = {
                        'filename': filename,
                        'date': str(datetime.now())
                    }
                    self._db.update('logs', logs)
                    self._bot.send_status({'status': 'ok', 'desc': 'log successfuly added'}, 'ok', user_id)
                    return jsonify({
                        'status': 'ok',
                        'msg': 'file saved'
                    }), 200
            except Exception as e:
                self._bot.send_status({'error': 'error detected', 'desc': str(e)}, 'error', user_id)
                return jsonify({
                    'status': 'error',
                    'error': str(e)
                }), 500
    
    def start(self):
        task1 = threading.Thread(target=self._bot.run)
        task2 = threading.Thread(target=self._app_.run, args=(self._host, self._port))
        task1.start()
        task2.start()
        

app = App("127.0.0.1", "6700")
app.start()
