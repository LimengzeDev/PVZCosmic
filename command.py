import re

KEYWORDS = {'sun', 'door_open', 'call', 'kill', 'move', 'buff'}


def command(statements: str) -> None:

    no_space_str: str = ""
    # 去除语句中的空格
    for _ in statements:
        if _ != ' ':
            no_space_str = no_space_str + _

    # 正则表达式匹配括号中内容
    parameter = re.search('(\\(.+?\\))|(\\(\\))', no_space_str)

    # 语句异常处理
    if parameter is None:
        if no_space_str.find('(') == -1:
            if no_space_str.find(')') == -1:
                print(f"未知的命令:\"{statements}\"")
            else:
                print(f"命令:\"{statements}\" 缺少 \'(\'")
        else:
            print(f"命令:\"{statements}\" 缺少 \')\'")

    else:
        cmd_name = no_space_str[:parameter.start()]
        if cmd_name in KEYWORDS:
            if parameter.end() != len(no_space_str):
                print(f"未知的:\"{no_space_str[parameter.end():len(no_space_str)]}\" 在命令后")

            parameters = parameter.group()[1:len(parameter.group())-1]
            # 分离出参数
            parameters = parameters.split(',')
            # 参数预处理
            for i in range(len(parameters)):
                if parameters[i].isdigit():
                    parameters[i] = int(parameters[i])
            print(parameters)
        else:
            print(f"未知的命令:\"{cmd_name}\"")


if __name__ == '__main__':
    while True:
        a = input()
        if a == 'break':
            break
        command(a)
