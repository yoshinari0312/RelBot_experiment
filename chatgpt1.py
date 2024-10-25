from openai import OpenAI
from conversation_class import Conversation
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# chatGPTに会話履歴を入力し，Pepperくんの発言を生成。Pepperくんの態度の制御も行う。
def chat1(topic):
    # シングルトンパターンによるインスタンス生成により、クラスに保存された情報を受け取れる
    history = Conversation()

    if topic == '早慶戦':
        topic_sentence = '\n早慶戦について、\n慶応大学を応援する側として会話してください。'
    elif topic == 'きのこの山派かたけのこの里派か':
        topic_sentence = '\nきのこたけのこ戦争について、\nきのこの山派として会話してください。'
    elif topic == '都会に住みたいか田舎に住みたいか':
        topic_sentence = '\n都会と田舎どっちで住みたいかについて、\n都会派として会話してください。'
    elif topic == '結婚の必要性':
        topic_sentence = '\n結婚の必要性について、\n結婚は必要派として会話してください。'
    elif topic == '朝食の必要性':
        topic_sentence = '\n朝食の必要性について、\n朝食は必要派として会話してください。'

    default_messages = [{"role": "system",
                        "content": f"あなたは太郎です。太郎、花子、康太が会話します。過去の会話を考慮して太郎の会話を50文字以内で生成してください。\
    {topic_sentence}\
    \n太郎の会話部分のみを生成してください。\
    \n1人称は「僕」です。2人称と3人称の人代名詞は使わず、もしどちらかに話しかける場合は名前を呼んでください。\n康太の会話は生成しないでください。\n花子の会話は生成しないでください。"}]  # プロンプトを入力
    next_messages = default_messages

    # 会話履歴をプロンプトに追加
    combined_content = "\n".join(history.get())
    next_messages.append({"role": "user",
                         "content": combined_content}
                         )

    res = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        # model="gpt-4",
        model="gpt-4o",
        messages=next_messages)

    # "太郎："の部分を除いて発言部分だけに
    res_only = res.choices[0].message.content.replace("太郎:", "").replace("太郎: ", "").replace("太郎：", "")\
        .replace("「", "").replace("」", "")

    # GPTの返答
    return res_only


# キーボード入力での動作確認用
if __name__ == '__main__':
    history = Conversation()
    history.add("康太", "こんにちは")
    history.add("太郎", "こんにちは")
    history.add("花子", "こんにちは")
    history.add("康太", "今日はいい天気ですね")
    res = chat1()
    print('Pepperくん: ' + res)
