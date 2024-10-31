from openai import OpenAI  # type: ignore
import ast
from conversation_class import Conversation
from relation_class import Relation
import re
import os
from dotenv import load_dotenv  # type: ignore

# .envファイルの読み込み
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 会話履歴から、2者間の関係を推測する
def relation():
    default_messages = [{"role": "system",
                        "content": "康太、太郎、花子の3人の会話を入力します。会話内容に対して康太、太郎、花子のそれぞれ2者間の仲の良さを0〜10の点数で答えてください。\
    ただし、関係が良い場合5より大きく、悪い場合は5未満にしてください。ただし、新しい会話ほど仲の良さへの影響を大きくしてください。pythonのリストの中に辞書を入れる形式で答えること。\
    \n解答例: [{'康太と太郎の関係':number},\n{'康太と花子の関係':number},\n{'太郎と花子の関係':number}]\
    \nという形式で答えてください。理由は答えないでください。"}
                        ]  # プロンプトを入力
    next_messages = default_messages
    # シングルトンパターンにより、インスタンス生成によりクラスに保存された情報を受け取れる
    history = Conversation()
    relation_instance = Relation()

    # 最新9つの会話履歴を読み込み、関係を推定
    last_9_list = history.get()[-9:]
    combined_content = "\n".join(last_9_list)  # 各要素を1つの文字列に結合
    next_messages.append({"role": "user",
                          "content": combined_content})

    res = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        # model="gpt-4",
        model="gpt-4o",
        messages=next_messages)

    while True:
        try:
            only_relation = re.search(r'\[.*?\]', res.choices[0].message.content, re.DOTALL).group(0)
            # GPTからの返答を変数に格納
            gpt_response_dict = ast.literal_eval(only_relation)
            break
        except Exception as e:
            print('エラーが発生したため、再生成しました。エラー内容：', e)
            res = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                model="gpt-4",
                # model="gpt-4-1106-preview",
                messages=next_messages)

    relation_instance.set(gpt_response_dict)
    # [{'康太と太郎の関係': 8},
    #  {'康太と花子の関係': 4},
    #  {'太郎と花子の関係': 6}]
    # といったようなリストをセットする


# キーボード入力での動作確認用
if __name__ == '__main__':
    history = Conversation()
    relation_instance = Relation()
    history.add("康太", "2人とも好き")
    history.add("太郎", "2人とも好き")
    history.add("花子", "康太は嫌いだけど、太郎は好き")
    relation()
    print(relation_instance.get())
