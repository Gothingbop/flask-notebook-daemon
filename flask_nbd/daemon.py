from uuid import uuid4
from flask import Flask, request
import threading
import requests

methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]


class Daemon:
    def __init__(self, app: Flask):
        self._app = app
        self.uuid = str(uuid4())

        # Create a unique endpoint for shutting down the server.
        # Uses uuid so there are no collisions with already defined endpoints.
        @self._app.route(f'/{self.uuid}')
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            func()
            return "stopping"
        self.thread = None

    def stop(self):
        requests.get(f"http://127.0.0.1:5000/{self.uuid}")

    def start(self):
        self.thread = threading.Thread(target=self._app.run)
        self.thread.start()

    def __getattr__(self, key):
        class Endpoint:
            def __init__(self, string):
                self.string = string
                print(string)

            def __getattr__(self, method):
                if method in methods:
                    def call(**kwargs):
                        response = requests.request(method, f"http://127.0.0.1:5000/{self.string}", **kwargs)
                        response.raise_for_status()
                        return response

                    return call
                else:
                    return Endpoint(f"{self.string}/{method}")

        return Endpoint(key)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
