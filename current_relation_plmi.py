from relation_class import Relation


# 現在の関係を+と-の表示で返す
def current_relation_plmi():
    relation_instance = Relation()

    current_relation = {}

    # 点数が0-5なら'-', 6-10なら'+'とする
    if relation_instance.get()[0]['康太と太郎の関係'] >= 6:
        current_relation['康太と太郎の関係'] = '+'
    else:
        current_relation['康太と太郎の関係'] = '-'
    if relation_instance.get()[1]['康太と花子の関係'] >= 6:
        current_relation['康太と花子の関係'] = '+'
    else:
        current_relation['康太と花子の関係'] = '-'
    if relation_instance.get()[2]['太郎と花子の関係'] >= 6:
        current_relation['太郎と花子の関係'] = '+'
    else:
        current_relation['太郎と花子の関係'] = '-'

    return current_relation
    # {'康太と太郎の関係': '-', '康太と花子の関係': '+', '太郎と花子の関係': '-'}という辞書を返す
