
def v_prime(v, epsilon, a, b,):
    # v is the original valuation function
    # v_prime = base_value / 2 + perturbation
    return v(a, b)/2 + epsilon*abs(b-a)



def v_double_prime(v_prime, delta, a, b):
    # Letting delta := epsilon, so,
    # any epsilon-envy-free allocation for (v_double_prime) is 5*epsilon-envy-free for (v_prime) for each agent.

    # Get the grid points around a and b
    a_underline = underline(a, delta)
    a_overline = overline(a, delta)
    b_underline = underline(b, delta)
    b_overline = overline(b, delta)

    # Check if a equals b, and interpolate accordingly
    if a != b:
        # Interpolation when a and b are different
        return ((a - a_underline) * (b - b_underline) / delta**2) * v_prime(a_overline, b_overline) \
               + ((a_overline - a) * (b_overline - b) / delta**2) * v_prime(a_underline, b_underline) \
               + ((a_overline - a) * (b - b_underline) / delta**2) * v_prime(a_underline, b_overline) \
               + ((a - a_underline) * (b_overline - b) / delta**2) * v_prime(a_overline, b_underline)
    else:
        # Special case when a equals b
        return ((b_overline - b) / delta) * v_prime(a, b_underline) \
               + ((b - b_underline) / delta) * v_prime(a, b_overline)





def overline(x, delta):
    # Calculates the smallest multiple of delta greater than or equal to x
    return -(-x // delta) * delta

def underline(x, delta):
    # Calculates the largest multiple of delta less than or equal to x
    return (x // delta) * delta

def equipartition(v, cake_start, cake_end):
    """
    根据Agent1的价值函数将蛋糕均分成四个部分。

    :param v: Agent1的价值函数，接受两个参数（a, b）并返回a和b之间的价值
    :param cake_start: 蛋糕的起始点
    :param cake_end: 蛋糕的结束点
    :return: 四个分割点的列表
    """
    total_value = v(cake_start, cake_end)
    part_value = total_value / 4
    cut_points = [cake_start]

    current_value = 0
    current_start = cake_start

    for i in range(3):  # 需要找到三个分割点
        low = current_start
        high = cake_end

        # 二分法找到合适的分割点，使得每部分的价值接近于part_value
        while high - low > 1e-5:  # 假设精度为1e-5
            mid = (low + high) / 2
            value = v(current_start, mid)

            if value < part_value:
                low = mid
            else:
                high = mid

        cut_point = (low + high) / 2
        cut_points.append(cut_point)
        current_start = cut_point

    cut_points.append(cake_end)
    return cut_points

# 示例价值函数
def v(a, b):
    return b - a

# 调用equipartition函数
cake_start = 0
cake_end = 1
cut_points = equipartition(v, cake_start, cake_end)
print(cut_points)  # 输出：[0, 0.25, 0.5, 0.75, 1]
