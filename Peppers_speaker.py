# ロボットが話している人の方向を見るプログラム
from flask import Flask, render_template, url_for, request
from flask_socketio import SocketIO
import socket
from chatgpt1 import chat1
from chatgpt2 import chat2
from conversation_class import Conversation
from relation_class import Relation
from metagpt import relation
from current_relation_plmi import current_relation_plmi
from next_speaker import next_speaker
import datetime
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
socketio = SocketIO(app)

# PepperのIPとPortを設定
pepper_ip1 = "192.168.1.85"
pepper_port1 = 2002
pepper_ip2 = "192.168.1.104"
pepper_port2 = 2002

# 早慶戦 or きのこの山派かたけのこの里派か or 都会に住みたいか田舎に住みたいか or 結婚の必要性 or 朝食の必要性
topic = "早慶戦"

# 会話履歴を保持するためのインスタンス生成
history = Conversation()

# 関係を保持するためのインスタンス生成
relation_instance = Relation()

# 喋り終わったsocketオブジェクトを入れる
socket_list = []

# PepperくんとPepperちゃんが話すと1にする
conversation_done = {"Pepperくん": 0, "Pepperちゃん": 0}

# ログ用の変数
num = 0


@app.route("/")
def index():
    current_relation = current_relation_plmi()
    # 初期値の画像を指定する
    image_src = url_for(
        "static",
        filename="relation_picture/"
        + current_relation["康太と太郎の関係"]
        + current_relation["康太と花子の関係"]
        + current_relation["太郎と花子の関係"]
        + ".png",
    )
    return render_template("hello_socketio.html", image_src=image_src)


# ログ用
@app.route("/capture-html", methods=["POST"])
def capture_html():
    html_content = request.json.get("html")
    global num
    num += 1
    timestamp = datetime.datetime.now().strftime("%m%d%H%M%S")
    filename = os.path.join("IROS", "IROS", f"場面{num}_{timestamp}.html")
    # 保存先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        file.write(html_content)
    return "", 200


# リロードした時にPepperくんから話すようにする
@socketio.on("start_conversation")
def initiate_conversation():
    pepper1()


@socketio.on("user_message")
def handle_user_message(message):
    # 会話履歴に人間の発言を追加
    history.add("康太", message["data"])

    if (
        conversation_done["Pepperくん"] == 1
        and conversation_done["Pepperちゃん"] == 1
        and len(history.get()) >= 5
    ):
        three_turn_process()
    next_decide()


# もしすでに開いていたらソケットを閉じる関数
def close_socket(ip):
    for s in socket_list:
        if s.getpeername()[0] == ip:
            try:
                s.close()
                socket_list.remove(s)
            except Exception as e:
                print(f"Error closing socket: {e}")
            break


# 指定したipのロボットがtargetの方をみる関数
def look_to(ip, port, target):
    try:
        close_socket(ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(f"look:{target}\n".encode())
        if s not in socket_list:
            socket_list.append(s)
    except Exception as e:
        print(f"Error in look_to function: {e}")


def pepper1():
    # Pepperくんのソケットを確認し、開いていれば閉じる
    close_socket(pepper_ip1)
    # Pepperくんの発言をgptで生成
    response1 = chat1(topic)
    if len(history.get()) == 0:
        response1 = topic + "について話しましょう。" + response1
    # 会話履歴にPepperくんの発言を追加
    history.add("太郎", response1)
    response1 = (
        response1.replace("康太", "人間")
        .replace("太郎", "Pepperくん")
        .replace("花子", "Pepperちゃん")
    )
    # webに表示するために応答を送信
    socketio.emit("Pepper1", {"data": response1})
    # Pepperくんとソケット通信開始
    s1 = send_message_to_pepper1(response1)
    if len(history.get()) >= 3:
        conversation_done["Pepperくん"] = 1
    if s1 not in socket_list:
        socket_list.append(s1)
    if (
        conversation_done["Pepperくん"] == 1
        and conversation_done["Pepperちゃん"] == 1
        and len(history.get()) >= 5
    ):
        three_turn_process()
    if len(history.get()) == 1:
        pepper2()
    else:
        next_decide()


def pepper2():
    # Pepperちゃんのソケットを確認し、開いていれば閉じる
    close_socket(pepper_ip2)
    # Pepperちゃんの発言をgptで生成
    response2 = chat2(topic)
    # 会話履歴にPepperちゃんの発言を追加
    history.add("花子", response2)
    response2 = (
        response2.replace("康太", "人間")
        .replace("太郎", "Pepperくん")
        .replace("花子", "Pepperちゃん")
    )
    # webに表示するために応答を送信
    socketio.emit("Pepper2", {"data": response2})
    s2 = send_message_to_pepper2(response2)
    if len(history.get()) >= 3:
        conversation_done["Pepperちゃん"] = 1
    if s2 not in socket_list:
        socket_list.append(s2)
    if (
        conversation_done["Pepperくん"] == 1
        and conversation_done["Pepperちゃん"] == 1
        and len(history.get()) >= 5
    ):
        three_turn_process()
    next_decide()


def user_speak():
    # Pepperくんに人間の方を見るように指示
    look_to(pepper_ip1, pepper_port1, "人間")
    print("Connected to Pepper1!")
    # Pepperちゃんに人間の方を見るように指示
    look_to(pepper_ip2, pepper_port2, "人間")
    print("Connected to Pepper2!")
    # 人間の音声認識イベント
    socketio.emit("user_turn")


# response1はPepperくんの喋る内容
def send_message_to_pepper1(response1):
    # Pepperくんとソケット通信開始
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s1.connect((pepper_ip1, pepper_port1))
        print("Connected to Pepper1!")
        s1.sendall("look:Pepperくん\n".encode())
        response1 = "say:" + response1 + "\n"
        s1.sendall(response1.encode())
        # PepperちゃんにPepperくんの方を見るように指示
        look_to(pepper_ip2, pepper_port2, "Pepperくん")
        print("Connected to Pepper2!")
        # Pepperくんから発言終わり信号を受け取る
        finished = s1.recv(1024).decode()
        print("Pepperくん said:", finished)
        if finished == "Finished speaking\n":  # Pepperくんが話し終わったという信号
            return s1
    except Exception as e:
        print(f"Error in send_message_to_pepper1: {e}")


# response2はPepperちゃんの喋る内容
def send_message_to_pepper2(response2):
    # Pepperちゃんとソケット通信開始
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s2.connect((pepper_ip2, pepper_port2))
        print("Connected to Pepper2!")
        s2.sendall("look:Pepperちゃん\n".encode())
        response2 = "say:" + response2 + "\n"
        s2.sendall(response2.encode())
        # PepperくんにPepperちゃんの方を見るように指示
        look_to(pepper_ip1, pepper_port1, "Pepperちゃん")
        print("Connected to Pepper1!")
        # Pepperちゃんから発言終わり信号を受け取る
        finished = s2.recv(1024).decode()
        print("Pepperちゃん said:", finished)
        if finished == "Finished speaking\n":  # Pepperちゃんが話し終わったという信号
            return s2
    except Exception as e:
        print(f"Error in send_message_to_pepper2: {e}")


# 次の話者を決める
def next_decide():
    next = next_speaker()
    print("次は" + next + "の番")
    if next == "康太":
        user_speak()
    if next == "太郎":
        pepper1()
    elif next == "花子":
        pepper2()


# 会話3回ごとに行う処理
def three_turn_process():
    try:
        conversation_done["Pepperくん"] = 0
        conversation_done["Pepperちゃん"] = 0
        # 会話履歴をprint
        for h in history.get():
            print(h)
        # 現在の関係をset
        relation()
        # 現在の関係をprint
        print("現在の関係: ")
        print(relation_instance.get())
        # 現在の関係を'+' or '-'で取得
        current_relation = current_relation_plmi()
        # 現在の関係の画像を動的に変更する
        image_src = url_for(
            "static",
            filename="relation_picture/"
            + current_relation["康太と太郎の関係"]
            + current_relation["康太と花子の関係"]
            + current_relation["太郎と花子の関係"]
            + ".png",
        )
        socketio.emit(
            "update_image1", {"image_src": image_src}
        )  # 新しい画像のパスをクライアントに送信
    finally:
        for s in socket_list:
            s.close()
        socket_list.clear()


if __name__ == "__main__":
    socketio.run(app)

