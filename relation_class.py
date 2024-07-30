# 3者の関係を保持するためのクラス
class Relation:
    _instance = None

    # シングルトンパターンを使用
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Relation, cls).__new__(cls, *args, **kwargs)
            # 初期化
            cls._instance.init_data()
        return cls._instance

    # 初期値0 or 10 に変更する
    def init_data(self):
        self.relation = [{'康太と太郎の関係': 10, '理由': '初期値'},
                         {'康太と花子の関係': 10, '理由': '初期値'},
                         {'太郎と花子の関係': 0, '理由': '初期値'}]
        self.future_relation = {}

    def set(self, relations_list):
        self.relation = relations_list

    def set_future(self, relations_dict):
        self.future_relation = relations_dict

    def get(self):
        return self.relation

    def get_future(self):
        return self.future_relation
