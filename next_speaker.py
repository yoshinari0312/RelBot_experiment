from openai import OpenAI
from conversation_class import Conversation
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 会話履歴から、2者間の関係を推測する
def next_speaker():
    default_messages = [{"role": "system",
                        "content": "太郎、花子、康太の3人が一緒に会話しています。他には誰もいません。\n上の会話ほど過去で、下の会話ほど最近のものになります。\
    \nこの会話の後に発言すると予想されるのは誰ですか？\n康太, 太郎, 花子\nのうち1人だけ答えてください。\n他の形式の回答は許されません。"}
                        ]  # プロンプトを入力
    next_messages = default_messages
    # シングルトンパターンにより、インスタンス生成によりクラスに保存された情報を受け取れる
    history = Conversation()

    # systemを最新の発言者以外から選択するように編集
    t = next_messages[0]["content"].split("\n")
    if "康太: " in history.get()[-1]:
        t[3] = "太郎, 花子"
    elif "太郎: " in history.get()[-1]:
        t[3] = "康太, 花子"
    elif "花子: " in history.get()[-1]:
        t[3] = "康太, 太郎"
    next_messages[0]["content"] = "\n".join(t)

    # 最新4つの会話履歴のみをプロンプトに追加
    last_4_list = history.get()[-4:]
    combined_content = "\n".join(last_4_list)  # 各要素を1つの文字列に結合
    next_messages.append({"role": "user",
                          "content": combined_content})

    res = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        # model="gpt-4",
        model="gpt-4o",
        messages=next_messages)

    res_only = res.choices[0].message.content
    if '康太' in res_only:
        res_only = '康太'
    elif '太郎' in res_only:
        res_only = '太郎'
    elif '花子' in res_only:
        res_only = '花子'

    return res_only
    # "康太" or "太郎" or "花子" という文字列を返す


# キーボード入力での動作確認用
if __name__ == '__main__':
    history = Conversation()
    history.add("康太", "2人とも好き")
    history.add("太郎", "2人とも好き")
    history.add("花子", "康太は嫌い")
    history.add("康太", "ふざけんな")
    next = next_speaker()
    print(next)
    print(next == "康太")
    print(next == "太郎")
    print(next == "花子")
