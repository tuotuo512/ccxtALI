def calculate_parameter(current_price, support_level, resistance_level):
    # 计算中间值
    middle_price = (support_level + resistance_level) / 2

    # 计算 current_price 与中间值的距离
    distance = abs(current_price - middle_price)

    # 将距离转换为参数值。我们使用指数函数来实现从中间值到支撑或阻力的指数增长。
    # 我们将距离除以最大可能距离（即 middle_price - support_level）并取指数
    max_distance = (resistance_level - support_level) / 2
    parameter_value = (distance / max_distance) ** 3  # 指数增长

    # 确保参数值在 0% 到 100% 之间
    parameter_value = max(0, min(100, parameter_value * 100))
    # 如果参数值小于 20%，则归零
    if parameter_value < 20:
        parameter_value = 0

    return parameter_value


# 示例
support_level = 1900
resistance_level = 2100
current_price = 1910

parameter_value = calculate_parameter(current_price, support_level, resistance_level)
print(f"参数值: {parameter_value}%")

