# -*- coding: utf-8 -*-
"""
Python 语法练习场

用法（两条命令）：
    cd E:\\codex代码\\smart-agri-agent
    .\\.venv\\Scripts\\Activate.ps1
    python practice/basics.py

改这个文件不会影响项目里的任何东西，放心乱改、乱试。

每一节的格式都是：
    【示范】 一段能跑的代码，运行后你能看到结果
    【练习】 让你动手改的地方 —— 改完再运行一次，看输出变了没有

建议节奏：一节一节来，每节花 15 分钟。别一口气读完。
"""

print("=" * 60)
print("Python 语法练习场")
print("=" * 60)


# ======================================================================
# 第 1 节：变量与字符串
# ======================================================================
print("\n【第 1 节】变量与字符串")

# 变量 = 给一个值起名字。= 不是"等于"，是"把右边存进左边"
device = "greenhouse-1"
temperature = 26.5
count = 3
is_running = True

print("设备:", device)
print("温度:", temperature)
print("设备数量:", count)
print("在运行:", is_running)

# 字符串可以拼接（+）和重复（*）
label = device + " 的温度"
print("拼接:", label)
print("重复:", "-" * 20)

# f-string：最常用的格式化方式。前面加 f，花括号里能直接放变量
print(f"格式化: {device} 当前 {temperature} 度")

# 【练习 1-1】把 device 改成 "greenhouse-2"，运行，看哪些行跟着变了
# 【练习 1-2】加一个变量 humidity = 65，用 f-string 把它打印出来
# 【练习 1-3】先猜 print("=" * 5) 会输出什么，再运行验证


# ======================================================================
# 第 2 节：列表 list —— 一串有序的东西
# ======================================================================
print("\n【第 2 节】列表")

metrics = ["temperature", "humidity", "soil_moisture"]
print("整个列表:", metrics)
print("第 1 个:", metrics[0])
print("最后 1 个:", metrics[-1])
print("有几个:", len(metrics))

metrics.append("co2")
print("加完之后:", metrics)

for m in metrics:
    print("  -", m)

# 【练习 2-1】往列表里再加一个 "soil_ph"
# 【练习 2-2】注意：下标从 0 开始。那 metrics[1] 是哪个？
# 【练习 2-3】故意写 metrics[99] 运行一次，看报什么错 —— 知道边界在哪很有用


# ======================================================================
# 第 3 节：字典 dict —— 一堆"名字: 值"的配对
# ======================================================================
print("\n【第 3 节】字典")

# 这就是你项目里传感器数据的样子
reading = {
    "device_id": "greenhouse-1",
    "metric": "temperature",
    "value": 26.5,
}

print("整个字典:", reading)
print("按名字取值 value:", reading["value"])
print("按名字取值 metric:", reading["metric"])

reading["unit"] = "celsius"
print("加了个新键之后:", reading)

for key in reading:
    print(f"  {key} = {reading[key]}")

# 字典套字典、字典套列表，在真实数据里很常见
device_info = {
    "id": "greenhouse-1",
    "metrics": ["temperature", "humidity"],
    "online": True,
}
print("嵌套取值 metrics:", device_info["metrics"])
print("再往里一层 [0]:", device_info["metrics"][0])

# 【练习 3-1】把 reading 里的 value 改成 30.2
# 【练习 3-2】给 reading 加一个 "ts" 键，值随便写个时间字符串
# 【练习 3-3】把 device_info 里的 "online" 改成 False 并打印


# ======================================================================
# 第 4 节：if 判断
# ======================================================================
print("\n【第 4 节】if 判断")

soil_moisture = 18

if soil_moisture < 30:
    print("  土壤太干，需要灌溉")
elif soil_moisture < 60:
    print("  湿度偏低，再观察")
else:
    print("  湿度正常")

# 冒号和缩进是 Python 的核心语法，别丢
# 同样缩进的几行属于同一个分支

# 【练习 4-1】把 soil_moisture 改成 45，运行看走哪个分支
# 【练习 4-2】改成 75，再看
# 【练习 4-3】加一个分支：大于 80 时打印"湿度过高，注意排水"


# ======================================================================
# 第 5 节：for 循环 —— 对一串东西挨个处理
# ======================================================================
print("\n【第 5 节】for 循环")

greenhouses = ["greenhouse-1", "greenhouse-2", "greenhouse-3"]
values = {"greenhouse-1": 26.5, "greenhouse-2": 24.1, "greenhouse-3": 28.0}

for gh in greenhouses:
    temp = values[gh]
    print(f"  {gh}: {temp} 度")

for index, gh in enumerate(greenhouses, start=1):
    print(f"  第 {index} 个棚: {gh}")

for i in range(3):
    print("  range 循环第", i, "次")

# 【练习 5-1】给 greenhouses 和 values 各加一个 greenhouse-4
# 【练习 5-2】把第一个循环的输出改成一行一句话，用 ", " 连接


# ======================================================================
# 第 6 节：while 循环 —— 条件成立就一直做
# ======================================================================
print("\n【第 6 节】while 循环")

attempt = 1
while attempt <= 3:
    print(f"  第 {attempt} 次尝试连接...")
    attempt = attempt + 1
print("  放弃连接")

# 【练习 6-1】把 3 改成 5，看输出变长没
# 【练习 6-2】把 attempt = attempt + 1 这行前面加 # 注释掉，运行，
#             然后按 Ctrl+C 停掉 —— 亲手体会一次"死循环"


# ======================================================================
# 第 7 节：函数 def —— 把一段代码起个名字，随时调用
# ======================================================================
print("\n【第 7 节】函数")


def celsius_to_fahrenheit(c):
    """把摄氏度转成华氏度。"""
    f = c * 9 / 5 + 32
    return f


def describe(device, value):
    """打印一句设备描述。没有 return，它只负责打印。"""
    print(f"  {device} 当前 {value} 度")


f = celsius_to_fahrenheit(26.5)
print(f"  26.5 摄氏度 = {f:.1f} 华氏度")
describe("greenhouse-1", 26.5)
describe("greenhouse-2", 24.1)

# 关键：上面的 def 只是"教会 Python 怎么做"，真正执行的是下面这几行调用

# 【练习 7-1】写一个函数 is_too_dry(moisture)：湿度小于 30 返回 True，否则 False
# 【练习 7-2】调用它三次，分别传 20、45、80，把结果打印出来
# 【练习 7-3】把 celsius_to_fahrenheit 改写成 fahrenheit_to_celsius（反着算）


# ======================================================================
# 第 8 节：异常处理 try / except —— 出错不要崩
# ======================================================================
print("\n【第 8 节】异常处理")

bad_data = ["26.5", "abc", "30.1"]

for item in bad_data:
    try:
        number = float(item)
        print(f"  解析成功: {item} -> {number}")
    except ValueError:
        print(f"  解析失败: {item} 不是数字，跳过")

print("  循环跑完了，程序还活着")

# 这就是网关遇到脏数据时必须做的事

# 【练习 8-1】往 bad_data 里加一个空字符串 ""，看会不会崩
# 【练习 8-2】再往 bad_data 里加一个 None，运行看报什么错
#             （提示：None 会触发 TypeError 而不是 ValueError，可以再加一个 except 分支）


# ======================================================================
# 第 9 节：文件读写
# ======================================================================
print("\n【第 9 节】文件读写")

from pathlib import Path

note_file = Path(__file__).parent / "my_note.txt"

# with open(...) 是最推荐的写法：出了缩进块，文件自动关闭
with open(note_file, "w", encoding="utf-8") as f:
    f.write("第一行：今天学会了写文件\n")
    f.write("第二行：这里可以写任何东西\n")
print("  写完了:", note_file.name)

with open(note_file, "r", encoding="utf-8") as f:
    content = f.read()

print("  读回来:")
for line in content.splitlines():
    print("    " + line)

note_file.unlink()
print("  已删除临时文件")

# 【练习 9-1】把写入的内容改成三行，写你自己的
# 【练习 9-2】把 "w" 改成 "a"（追加），运行两次，看文件是不是变长了
#             （要先把这个文件底部的 note_file.unlink() 注释掉，否则文件被删了看不到）


# ======================================================================
# 第 10 节：类 class —— 只需要看懂，不要求会写
# ======================================================================
print("\n【第 10 节】类（认识一下就好）")


class Sensor:
    """一个模拟传感器。类就像一张图纸。"""

    def __init__(self, device_id, metric):
        """创建对象时自动执行，用来初始化。"""
        self.device_id = device_id
        self.metric = metric

    def report(self, value):
        """这个对象能做的一件事。"""
        print(f"  [{self.device_id}] {self.metric} = {value}")


temp_sensor = Sensor("greenhouse-1", "temperature")
hum_sensor = Sensor("greenhouse-1", "humidity")

temp_sensor.report(26.5)
hum_sensor.report(65)

# 这部分你能看懂就够了：
#   Sensor(...)        照着图纸造一个对象
#   sensor.report(...) 让这个对象做某件事
#   self               类内部指代"我自己"
#
# 你项目里到处是这种用法，比如 mqtt.Client(...)。
# 前期你自己基本不用写 class，但必须看得懂库里的 class 怎么用。

# 【练习 10-1】再建一个 Sensor 对象，设备名和指标自己定
# 【练习 10-2】调用它的 report 方法，传一个值进去


# ======================================================================
print("\n" + "=" * 60)
print("全部跑完了。现在回头把每节重读一遍，然后动手做每节的【练习】")
print("—— 那才是真正长本事的地方。")
print("=" * 60)
