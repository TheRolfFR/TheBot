import flask
import threading
from werkzeug.serving import make_server

app = flask.Flask("myapp")

global server


class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server("0.0.0.0", 8080, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def start():
    global server
    server = ServerThread(app)
    server.start()


def stop():
    global server
    server.shutdown()


@app.route("/")
def main():
    return "Your bot is alive!"
