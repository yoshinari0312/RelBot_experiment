# 会話履歴を保持するためのクラス
class Conversation:
    _instance = None

    # シングルトンパターンを使用
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Conversation, cls).__new__(cls, *args, **kwargs)
            # 初期化
            cls._instance.init_data()
        return cls._instance

    def init_data(self):
        self.history = []

    def add(self, speaker, message):
        entry = f'{speaker}: {message}'
        self.history.append(entry)

    def get(self):
        return self.history
