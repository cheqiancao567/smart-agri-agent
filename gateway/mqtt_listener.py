# -*- coding: utf-8 -*-
"""
MQTT 消息监听器 —— gateway 模块的第一个原型

它做的事：订阅 sensors/# ，把收到的每条消息打印出来。
这就是你项目里 gateway/ 的核心工作，只差最后一步「写进数据库」。

用法：
    python gateway/mqtt_listener.py                 # 一直守着，Ctrl+C 退出
    python gateway/mqtt_listener.py --seconds 60    # 只守 60 秒

先在另一个窗口发消息（MQTTX 或下面的命令），回来看这个窗口的输出：
    docker exec mosquitto mosquitto_pub -t sensors/test/temp -m '{"value": 26.5}'
"""

import argparse
import json
import sys
import time

import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "sensors/#"          # # 是通配符：sensors/ 底下的所有主题全都要


def on_connect(client, userdata, connect_flags, reason_code, properties):
    """连接成功时被调用。注意：每次重连成功也会再调用一次。"""
    if reason_code == 0:
        print("[连接] 已连上 {0}:{1}".format(BROKER, PORT))
        # 必须在这里订阅：broker 不记得你上次的订阅，
        # 每次（重）连都要重新登记一遍。
        client.subscribe(TOPIC, qos=0)
        print("[订阅] " + TOPIC)
    else:
        print("[连接] 失败，原因码 {0}".format(reason_code))


def on_message(client, userdata, message):
    """收到消息时被调用 —— 这就是整个程序的核心。"""
    stamp = time.strftime("%H:%M:%S")
    raw = message.payload.decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
        print("[{0}] {1}  ->  {2}".format(
            stamp, message.topic, json.dumps(data, ensure_ascii=False)))
    except json.JSONDecodeError:
        # 收到不是 JSON 的内容也不崩，原样打印出来
        print("[{0}] {1}  ->  {2}   （不是合法 JSON）".format(
            stamp, message.topic, raw))
    sys.stdout.flush()


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """断开时被调用 —— 这就是 MQTTX 没有自动重连、而我们要自己兜住的地方。"""
    print("[断开] 连接中断（原因码 {0}），等待自动重连...".format(reason_code))
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="订阅 sensors/# 并打印收到的消息")
    parser.add_argument("--seconds", type=int, default=0,
                        help="运行多少秒后自动退出；0 表示一直运行")
    args = parser.parse_args()

    # paho-mqtt 2.x 要求显式声明回调 API 版本
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="gateway-listener")

    # 断线后自动重连，间隔从 1 秒逐步放宽到 10 秒，避免疯狂重试
    client.reconnect_delay_set(min_delay=1, max_delay=10)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print("正在连接 {0}:{1} ...".format(BROKER, PORT))
    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as exc:
        print("[错误] 连不上 broker：{0}".format(exc))
        print("       确认容器在跑：docker ps")
        return 1

    # loop_start 在后台线程里跑网络循环，这样主线程还能做别的事
    # （它同时负责断线重连）
    client.loop_start()

    try:
        if args.seconds > 0:
            print("监听 {0} 秒后自动退出...".format(args.seconds))
            time.sleep(args.seconds)
        else:
            print("开始监听（Ctrl+C 退出）...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[退出] 已断开连接")
    return 0


if __name__ == "__main__":
    sys.exit(main())
