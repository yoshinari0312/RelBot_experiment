from openai import OpenAI
from conversation_class import Conversation
import json
from current_relation_plmi import current_relation_plmi
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 人間がどのような関係を望んでいるかを出力する関数
def human_intention():
    # シングルトンパターンにより、インスタンス生成によりクラスに保存された情報を受け取れる
    history = Conversation()

    default_messages = [{"role": "system",
                        "content": '康太、太郎、花子の3人が会話しています。\
    \n康太の直前の発言のみに着目して、康太は現在の3者の関係をどのように変化させたいと考えていると予想されますか？\nわかる場合のみ以下の"?"の部分に"+", "-"を入れて答えてください。\
    \n{"康太と太郎の関係": "?", "康太と花子の関係": "?", "太郎と花子の関係": "?"}\nそれ以外の回答はしないでください。'}
                        ]  # プロンプトを入力
    next_messages = default_messages

    # 最新9つの会話履歴プロンプトに追加
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
            # GPTからの返答を変数に格納
            gpt_response_dict = json.loads(res.choices[0].message.content)
            break
        except (json.JSONDecodeError, TypeError) as e:
            print('エラーが発生したため、再生成しました。エラー内容：', e)
            res = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                # model="gpt-4",
                model="gpt-4-1106-preview",
                messages=next_messages)

    # "+","-","?"以外なら"?"に変更
    for key, value in gpt_response_dict.items():
        if value not in ["+", "-", "?"]:
            gpt_response_dict[key] = "?"

    # この下でgpt_response_dictを返す → 普通ver
    # この下でadjustment(gpt_response_dict)を返す → 人間がバランス理論に従うことを前提にしたver
    print('人間は以下のような関係にしたいと考えています')
    print(gpt_response_dict)
    result = adjustment(gpt_response_dict)
    print(result)

    # GPTの返答を辞書にし、もしバランス理論に従っていない場合は従うように変更したもの
    # return gpt_response_dict
    return result
    # {"康太と太郎の関係": "-", "康太と花子の関係": "+", "太郎と花子の関係": "?"}を返す


# もし人間の望む関係がバランス理論に従った関係じゃなければ、従った関係に変換
def adjustment(gpt_response_dict):
    current_relation = current_relation_plmi()
    gpt_response_dict_copy = gpt_response_dict.copy()

    # "?"をcurrent_relationの対応するキーの値に置換
    for key, value in gpt_response_dict_copy.items():
        if value == "?":
            gpt_response_dict_copy[key] = current_relation[key]

    # バランス理論に従った関係かどうかを判定
    t = []
    if gpt_response_dict_copy["康太と太郎の関係"] == "+":
        t.append(1)
    else:
        t.append(-1)
    if gpt_response_dict_copy["康太と花子の関係"] == "+":
        t.append(1)
    else:
        t.append(-1)
    if gpt_response_dict_copy["太郎と花子の関係"] == "+":
        t.append(1)
    else:
        t.append(-1)

    # 従っている場合、pepper同士の関係が'?'なら置換
    if t[0] * t[1] * t[2] == 1:
        if gpt_response_dict["太郎と花子の関係"] == "?":
            if (gpt_response_dict["康太と太郎の関係"] == "+" and gpt_response_dict["康太と花子の関係"] == "+") or (gpt_response_dict["康太と太郎の関係"] == "-" and gpt_response_dict["康太と花子の関係"] == "-"):
                gpt_response_dict["太郎と花子の関係"] = "+"
            elif (gpt_response_dict["康太と太郎の関係"] == "+" and gpt_response_dict["康太と花子の関係"] == "-") or (gpt_response_dict["康太と太郎の関係"] == "-" and gpt_response_dict["康太と花子の関係"] == "+"):
                gpt_response_dict["太郎と花子の関係"] = "-"
        return gpt_response_dict
    # 従っていない場合のみ、gpt_response_dict_copyを変更
    else:
        a = gpt_response_dict_copy["康太と太郎の関係"]
        b = gpt_response_dict_copy["康太と花子の関係"]
        c = gpt_response_dict_copy["太郎と花子の関係"]

        if a == "+" and b == "+" and c == "-":
            a = "+"
            b = "+"
            c = "+"
        elif a == "+" and b == "-" and c == "+":
            a = "+"
            b = "-"
            c = "-"
        elif a == "-" and b == "+" and c == "+":
            a = "-"
            b = "+"
            c = "-"
        elif a == "-" and b == "-" and c == "-":
            a = "-"
            b = "-"
            c = "+"

        gpt_response_dict_copy["康太と太郎の関係"] = a
        gpt_response_dict_copy["康太と花子の関係"] = b
        gpt_response_dict_copy["太郎と花子の関係"] = c

        return gpt_response_dict_copy
