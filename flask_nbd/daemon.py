from uuid import uuid4
from flask import Flask, request
import threading
import requests
import time
from contextlib import contextmanager
import sys


methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]


class Daemon:
    def __init__(self, app: Flask):
        self._app = app
        self.uuid = str(uuid4())

        # Create a unique endpoint for shutting down the server.
        # Uses uuid so there are no collisions with already defined endpoints.
        @self._app.route(f'/{self.uuid}', endpoint=self.uuid)
        def shutdown():
            print("Shutting app down")
            func = request.environ.get('werkzeug.server.shutdown')
            func()
            return "stopping"
        self.thread = None
        self.stdout = self.get_stdout()

    def stop(self):
        requests.get(f"http://127.0.0.1:5000/{self.uuid}")
        self.stdout.__exit__(None, None, None, )

    def start(self):
        self.thread = threading.Thread(target=self._app.run, )
        self.stdout.__enter__()
        self.thread.start()
        time.sleep(1)

    def __getattr__(self, key):
        class Endpoint:
            def __init__(self, string):
                self.string = string
                print(string)

            def __getattr__(self, method):
                if method in methods:
                    def call(**kwargs):
                        response = requests.request(method, f"http://127.0.0.1:5000/{self.string}", **kwargs)
                        return response

                    return call
                else:
                    return Endpoint(f"{self.string}/{method}")

        return Endpoint(key)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @contextmanager
    def get_stdout(self):
        class MyStream:
            def __init__(self, parent):
                self.old_stdout = sys.stdout
                self.parent = parent

            def write(self, msg):
                ident = threading.currentThread().ident
                if self.parent.thread:
                    censored = [self.parent.thread.ident]
                else:
                    censored = []
                if ident not in censored:
                    if threading.main_thread().ident != ident:
                        prefix = f'[Daemon]  ' if msg.strip() else ''
                    else:
                        prefix = f'[Main]    ' if msg.strip() else ''
                    self.old_stdout.write(prefix + msg)

            def flush(self):
                self.old_stdout.flush()

        sys.stdout = MyStream(self)
        try:
            yield
        finally:
            sys.stdout = sys.stdout.old_stdout
