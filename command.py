KEYWORDS = ('sun', 'door_open', 'call', 'kill', 'move', 'buff')


def command(statements: str) -> None:
    no_space_str: str = ""
    # 去除语句中的空格
    for _ in statements:
        if _ != ' ':
            no_space_str = no_space_str + _
    # 用 '(' 分割命令名和参数
    cmd_name, _, parameter = no_space_str.partition('(')

    if cmd_name not in KEYWORDS:
        print(f"{statements}不是有效命令")

    parameters: list = []
    new_parameter: str = ""

    if parameter.endswith(')'):

        for _ in parameter:
            if _ == ')':
                break
            else:
                new_parameter = parameter + _

        parameters = new_parameter.split(sep=',')

    else:
        print("命令应以')'结尾")
    for _ in parameters:
        print(parameters)

    print(no_space_str)


if __name__ == '__main__':
    a = input()
    print(a)
    command(a)
