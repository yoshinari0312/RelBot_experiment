import base64
import requests
from flask import Flask, render_template, url_for
from flask_socketio import SocketIO
import socket
import time
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# PepperのIPとPortを設定
pepper_ip = "192.168.1.88"
pepper_port = 2002
use_robot = False

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
history = ""


# 画像をエンコードする関数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_response(history):
    # 画像のローカルパス
    image_path = "/Users/ailab/Documents/研究/VSCODE/RelBot3/static/topic_picture/topic1.JPG"

    # base64に変換
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "以下の画像に関する会話に続いてBさんの発言を100文字以内で生成してください。説明口調ではなく、カジュアルな会話形式にしてください。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"{history}"
                    }
                ]
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # "B："の部分を除いて発言部分だけに
    res_only = response.json()['choices'][0]['message']['content'].replace("B:", "").replace("B: ", "").replace("B：", "").replace("「", "").replace("」", "").replace("A: ", "")

    return res_only


def send_message_to_pepper(response):
    # Pepperとソケット通信開始
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((pepper_ip, pepper_port))
    print("Connected to Pepper!")
    response = "say:" + response + "\n"
    s.sendall(response.encode())
    # Pepperくんから発言終わり信号を受け取る
    finished = s.recv(1024).decode()
    print("Pepper said:", finished)
    if finished == "Finished speaking\n":  # Pepperくんが話し終わったという信号
        return s


@app.route('/')
def index():
    # 初期値の画像を指定する
    image_src = url_for('static', filename='topic_picture/topic1.JPG')
    return render_template('talk_about_image.html', image_src=image_src)


@socketio.on('start_conversation')
def handle_start_conversation():
    global history
    response = "画像について話しましょう！"
    time.sleep(1)
    history += f"B: {response}"
    if use_robot:
        send_message_to_pepper(response)
    socketio.emit('robot_conversation', {'data': response})


@socketio.on('user_message')
def handle_user_message(message):
    global history
    user_text = message['data']
    history += f"\nA: {user_text}"
    response = create_response(history)
    history += f"\nB: {response}"
    if use_robot:
        send_message_to_pepper(response)
    socketio.emit('robot_conversation', {'data': response})


if __name__ == '__main__':
    socketio.run(app)
