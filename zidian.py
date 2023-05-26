import random

positions_state = {i: 0 for i in range(13)}

while True:
    print("当前字典内容：", positions_state)
    user_input = input("请输入一个数字（按 q 退出）: ")

    if user_input == 'q':
        break

    try:
        number = int(user_input)
        key = random.choice(list(positions_state.keys()))
        positions_state[key] = number
        print(f"键 {key} 的值已更新为: {positions_state[key]}")
    except ValueError:
        print("无效的输入，请输入一个数字或按 q 退出")

print("最终字典内容：", positions_state)
