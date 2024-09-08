from flask import Flask, render_template, request
import threading
import socket
import json
import os
from datetime import datetime


app = Flask(__name__)


# Функція для запуску Flask-сервера
def run_http_server():
    app.run(host="0.0.0.0", port=3000)


# Обробка форми на сторінці message.html
@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        username = request.form.get("username")
        message = request.form.get("message")
        send_message_to_socket_server({"username": username, "message": message})
        return render_template("message.html", success=True)
    return render_template("message.html")


# Головна сторінка
@app.route("/")
def index():
    return render_template("index.html")


# Обробка помилки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


# Функція для збереження повідомлення в JSON файл
def save_message_to_file(message):
    timestamp = str(datetime.now())
    storage_dir = "storage"
    file_path = os.path.join(storage_dir, "data.json")

    # Перевірка наявності директорії та файлу
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump({}, file)

    # Запис даних у файл
    with open(file_path, "r+") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}
        data[timestamp] = message
        file.seek(0)
        json.dump(data, file, indent=4)


# Функція для запуску Socket-сервера
def run_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", 5000))
    print("Socket server is running on port 5000...")

    while True:
        message, _ = server_socket.recvfrom(1024)
        message = json.loads(message.decode("utf-8"))
        save_message_to_file(message)


# Функція для надсилання даних на Socket-сервер
def send_message_to_socket_server(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(json.dumps(message).encode("utf-8"), ("127.0.0.1", 5000))


if __name__ == "__main__":
    # Запуск у різних потоках
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)

    http_thread.start()
    socket_thread.start()

    http_thread.join()
    socket_thread.join()
