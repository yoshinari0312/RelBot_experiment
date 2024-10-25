from flask import Flask, render_template, url_for, request
from flask_socketio import SocketIO
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
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# 早慶戦 or きのこの山派かたけのこの里派か or 都会に住みたいか田舎に住みたいか or 結婚の必要性 or 朝食の必要性
topic = '早慶戦'

# 会話履歴を保持するためのインスタンス生成
history = Conversation()

# 関係を保持するためのインスタンス生成
relation_instance = Relation()

# 開いたs1やs2を入れる
socket_list = []

# PepperくんとPepperちゃんが話すと1にする
conversation_done = {'Pepperくん': 0, 'Pepperちゃん': 0}

# ログ用の変数
num = 0


@app.route('/')
def index():
    current_relation = current_relation_plmi()
    # 初期値の画像を指定する
    image_src = url_for('static', filename='relation_picture/' + current_relation['康太と太郎の関係']
                        + current_relation['康太と花子の関係'] + current_relation['太郎と花子の関係'] + '.png')
    return render_template('hello_socketio.html', image_src=image_src)


# ログ用
@app.route('/capture-html', methods=['POST'])
def capture_html():
    html_content = request.json.get('html')
    global num
    num += 1
    timestamp = datetime.datetime.now().strftime("%m%d%H%M%S")
    filename = os.path.join("IROS", "test", f"場面{num}_{timestamp}.html")
    # 保存先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(html_content)
    return '', 200


# リロードした時にPepperくんから話すようにする
@socketio.on('start_conversation')
def initiate_conversation():
    pepper1()


@socketio.on('user_message')
def handle_user_message(message):
    # 会話履歴に人間の発言を追加
    history.add("康太", message['data'])
    if conversation_done['Pepperくん'] == 1 and conversation_done['Pepperちゃん'] == 1 and len(history.get()) >= 5:
        three_turn_process()
    next_decide()


def pepper1():
    # Pepperくんの発言をgptで生成
    response1 = chat1(topic)
    if len(history.get()) == 0:
        response1 = topic + 'について話しましょう。' + response1
    # 会話履歴にPepperくんの発言を追加
    history.add("太郎", response1)
    response1 = response1.replace("康太", "人間").replace("太郎", "Pepperくん").replace("花子", "Pepperちゃん")
    # webに表示するために応答を送信
    socketio.emit('Pepper1', {'data': response1})
    if len(history.get()) >= 3:
        conversation_done['Pepperくん'] = 1
    if conversation_done['Pepperくん'] == 1 and conversation_done['Pepperちゃん'] == 1 and len(history.get()) >= 5:
        three_turn_process()
    if len(history.get()) == 1:
        pepper2()
    else:
        next_decide()


def pepper2():
    # Pepperちゃんの発言をgptで生成
    response2 = chat2(topic)
    # 会話履歴にPepperちゃんの発言を追加
    history.add("花子", response2)
    response2 = response2.replace("康太", "人間").replace("太郎", "Pepperくん").replace("花子", "Pepperちゃん")
    # webに表示するために応答を送信
    socketio.emit('Pepper2', {'data': response2})
    if len(history.get()) >= 3:
        conversation_done['Pepperちゃん'] = 1
    if conversation_done['Pepperくん'] == 1 and conversation_done['Pepperちゃん'] == 1 and len(history.get()) >= 5:
        three_turn_process()
    next_decide()


def next_decide():
    next = next_speaker()
    print('次は' + next + 'の番')
    if next == "康太":
        socketio.emit('user_turn')
    if next == "太郎":
        pepper1()
    elif next == "花子":
        pepper2()


# 会話3回ごとに行う処理
def three_turn_process():
    conversation_done['Pepperくん'] = 0
    conversation_done['Pepperちゃん'] = 0
    # 会話履歴をprint
    for h in history.get():
        print(h)
    # 現在の関係をset
    relation()
    # 現在の関係をprint
    print('現在の関係: ')
    print(relation_instance.get())
    # 現在の関係を'+' or '-'で取得
    current_relation = current_relation_plmi()
    # 現在の関係の画像を動的に変更する
    image_src = url_for('static', filename='relation_picture/' + current_relation['康太と太郎の関係']
                        + current_relation['康太と花子の関係'] + current_relation['太郎と花子の関係'] + '.png')
    socketio.emit('update_image1', {'image_src': image_src})  # 新しい画像のパスをクライアントに送信


if __name__ == '__main__':
    socketio.run(app)
