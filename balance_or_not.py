from current_relation_plmi import current_relation_plmi


# バランス理論に従っているかどうかを判定
def balance_or_not():
    current_relation_t = []
    current_relation = current_relation_plmi()

    # バランス理論に従っているかどうかの判定の準備
    if current_relation['康太と太郎の関係'] == '+':
        current_relation_t.append(1)
    else:
        current_relation_t.append(-1)
    if current_relation['康太と花子の関係'] == '+':
        current_relation_t.append(1)
    else:
        current_relation_t.append(-1)
    if current_relation['太郎と花子の関係'] == '+':
        current_relation_t.append(1)
    else:
        current_relation_t.append(-1)

    multi = current_relation_t[0] * current_relation_t[1] * current_relation_t[2]

    # バランス理論に従っていたらyesを返す
    if multi == 1:
        print('balance')
        return 'yes'
    # 従っていなかったらnoを返す
    else:
        print('not balance')
        return 'no'
