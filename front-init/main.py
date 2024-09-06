import json
import socket
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# Маршрутизація для сторінок
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        username = request.form["username"]
        message = request.form["message"]
        # Відправка даних на Socket сервер
        send_message_to_socket_server(username, message)
        return redirect(url_for("index"))
    return render_template("message.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


# Функція для відправки даних на Socket сервер
def send_message_to_socket_server(username, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = json.dumps({"username": username, "message": message})
    sock.sendto(data.encode("utf-8"), ("localhost", 5000))
    sock.close()


# Запуск HTTP сервера
def run_http_server():
    app.run(port=3000)


# Функція для обробки UDP повідомлень на Socket сервері
def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", 5000))
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode("utf-8"))
        save_message_to_file(message)


def save_message_to_file(message):
    timestamp = str(datetime.now())
    with open("storage/data.json", "r+") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}
        data[timestamp] = message
        file.seek(0)
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    # Запуск у різних потоках
    threading.Thread(target=run_http_server).start()
    threading.Thread(target=run_socket_server).start()
