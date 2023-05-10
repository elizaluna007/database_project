from datetime import datetime
def is_time(time_string, time_range=["-838:59:59", "838:59:59"]):
    try:
        # 解析时间范围
        start_time = time_range[0]
        end_time = time_range[1]

        # 解析目标时间
        target_time = time_string

        # 检查时间格式是否满足要求
        if not all(x.isdigit() for x in target_time.split(":")):
            return False

        # 分割时间字符串为小时、分钟和秒钟
        target_hour, target_minute, target_second = map(
            int, target_time.split(":"))

        # 检查分钟和秒钟是否在有效范围内
        if not (0 <= target_minute <= 59 and 0 <= target_second <= 59):
            return False

        # 处理负数时间的情况
        if start_time.startswith("-") or end_time.startswith("-"):
            # 将时间转换为秒数进行比较
            start_seconds = sum(int(x) * 60**i for i,
                                x in enumerate(reversed(start_time.split(":"))))
            end_seconds = sum(int(x) * 60**i for i,
                              x in enumerate(reversed(end_time.split(":"))))
            target_seconds = target_hour * 3600 + target_minute * 60 + target_second

            if start_seconds <= target_seconds <= end_seconds:
                return True
            else:
                return False
        else:
            # 解析时间范围为小时、分钟和秒钟
            start_hour, start_minute, start_second = map(
                int, start_time.split(":"))
            end_hour, end_minute, end_second = map(int, end_time.split(":"))

            # 检查时间是否在范围内
            if (
                start_hour <= target_hour <= end_hour
                and start_minute <= target_minute <= end_minute
                and start_second <= target_second <= end_second
            ):
                return True
            else:
                return False
    except ValueError:
        # 解析时间出错，不满足要求的字符串
        return False
    
print(is_time("-1:34:56", ["0:0:0", "23:59:59"])) # True