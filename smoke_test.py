# -*- coding: utf-8 -*-
"""
M0 冒烟测试 —— 四条链路一次性体检

这个脚本确认项目的四根地基都还在：
  1. Python 环境    —— 在虚拟环境里、版本够新
  2. MQTT 收发      —— 能连上 broker，发出去的消息能收回来
  3. SQLite 读写    —— 能建表、写一条、读回来
  4. 大模型 API     —— 能成功调一次 DeepSeek

四项全 PASS = M0 环境验收通过，可以进入 M1（写数据模拟器）。

用法：
    cd E:\\codex代码\\smart-agri-agent
    .\\.venv\\Scripts\\Activate.ps1
    python smoke_test.py
"""

import json
import os
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent / ".env")

BROKER = os.getenv("MQTT_HOST", "127.0.0.1")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TEST_TOPIC = "sensors/_smoke_test"


# ----------------------------------------------------------------------
# 检查 1：Python 环境
# ----------------------------------------------------------------------
def check_python():
    print("[1/4] Python 环境")
    ok = True

    version = sys.version_info
    print("      解释器 : " + sys.executable)
    print("      版本   : " + sys.version.split()[0])

    if (version.major, version.minor) >= (3, 11):
        print("      版本 >= 3.11            ✓")
    else:
        print("      版本过低，需要 >= 3.11    ✗")
        ok = False

    if ".venv" in sys.executable:
        print("      运行在虚拟环境里          ✓")
    else:
        print("      不在虚拟环境里            ✗")
        print("      先执行: .\\.venv\\Scripts\\Activate.ps1")
        ok = False

    return ok


# ----------------------------------------------------------------------
# 检查 2：MQTT 收发（自己发一条，看能不能收回来）
# ----------------------------------------------------------------------
def check_mqtt():
    print("[2/4] MQTT 收发")

    got_message = threading.Event()
    box = {}

    def on_connect(client, userdata, connect_flags, reason_code, properties):
        # 连接成功后立刻订阅测试主题
        client.subscribe(TEST_TOPIC, qos=1)

    def on_message(client, userdata, message):
        box["payload"] = message.payload.decode("utf-8", errors="replace")
        got_message.set()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="smoke-test")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, keepalive=15)
    except Exception as exc:
        print("      连不上 broker {0}:{1}   ✗".format(BROKER, PORT))
        print("      原因: {0}".format(exc))
        print("      检查: docker ps  看 mosquitto 容器在不在")
        return False

    client.loop_start()
    time.sleep(1)                       # 等订阅登记完成

    marker = "smoke-{0}".format(int(time.time()))
    client.publish(TEST_TOPIC, json.dumps({"marker": marker}), qos=1)

    received = got_message.wait(timeout=8)
    client.loop_stop()
    client.disconnect()

    if not received:
        print("      发布了消息但 8 秒内没收到   ✗")
        return False

    print("      连上 {0}:{1}                ✓".format(BROKER, PORT))
    print("      发布 -> {0}".format(TEST_TOPIC))
    print("      收回 -> {0}".format(box.get("payload")))

    if marker in box.get("payload", ""):
        print("      内容与发出的一致            ✓")
        return True

    print("      内容与发出的不一致          ✗")
    return False


# ----------------------------------------------------------------------
# 检查 3：SQLite 读写
# ----------------------------------------------------------------------
def check_sqlite():
    print("[3/4] SQLite 读写")

    # 用临时文件，测完自动删掉，不污染 data/ 目录
    fd, path = tempfile.mkstemp(suffix=".db", prefix="smoke-")
    os.close(fd)

    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()

        # 建表：这张表的字段设计来自 docs 里的数据模型
        cur.execute("""
            CREATE TABLE sensor_readings (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT    NOT NULL,
                metric    TEXT    NOT NULL,
                value     REAL    NOT NULL,
                ts        TEXT    NOT NULL
            )
        """)
        print("      建表 sensor_readings        ✓")

        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        cur.execute(
            "INSERT INTO sensor_readings (device_id, metric, value, ts) VALUES (?, ?, ?, ?)",
            ("greenhouse-1", "temperature", 26.5, now),
        )
        conn.commit()
        print("      写入一条记录                ✓")

        cur.execute(
            "SELECT device_id, metric, value FROM sensor_readings ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        print("      读回 -> {0}".format(row))

        conn.close()

        if row == ("greenhouse-1", "temperature", 26.5):
            print("      内容与写入的一致            ✓")
            return True

        print("      读回的内容不对              ✗")
        return False
    except Exception as exc:
        print("      SQLite 操作失败             ✗")
        print("      原因: {0}".format(exc))
        return False
    finally:
        # 清理临时文件
        try:
            os.remove(path)
        except OSError:
            pass


# ----------------------------------------------------------------------
# 检查 4：大模型 API
# ----------------------------------------------------------------------
def check_llm():
    print("[4/4] 大模型 API")

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("      .env 里没有 DEEPSEEK_API_KEY   ✗")
        return False

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        start = time.time()
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "只回复两个字：收到"}],
            # 注意：deepseek-flash 默认开启「思考模式」，会先在内部消耗一段 token 推理，
            # 之后才输出可见文字。max_tokens 设得太小（比如 10）会把这些预算全用光，
            # 结果是「调用成功但回答为空」。所以这里必须留足余量。
            max_tokens=128,
        )
        elapsed = time.time() - start
    except Exception as exc:
        print("      调用失败                    ✗")
        print("      原因: {0}".format(exc))
        return False

    answer = (resp.choices[0].message.content or "").strip()
    print("      模型       : {0}".format(model))
    print("      回答       : {0}".format(answer))
    print("      耗时       : {0:.2f} 秒".format(elapsed))
    if resp.usage:
        print("      用量       : {0}+{1} = {2} tokens".format(
            resp.usage.prompt_tokens,
            resp.usage.completion_tokens,
            resp.usage.total_tokens))
    print("      调用成功                    ✓")
    return True


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------
def main():
    print("=" * 62)
    print("M0 冒烟测试 —— 四条链路体检")
    print("=" * 62)
    print()

    results = [
        ("Python 环境", check_python),
        ("MQTT 收发", check_mqtt),
        ("SQLite 读写", check_sqlite),
        ("大模型 API", check_llm),
    ]

    passed = 0
    detail = []
    for name, func in results:
        try:
            ok = func()
        except Exception as exc:
            print("      未捕获的异常: {0}".format(exc))
            ok = False
        passed += 1 if ok else 0
        detail.append((name, ok))
        print()

    print("=" * 62)
    print("结果汇总")
    print("=" * 62)
    for name, ok in detail:
        print("  {0:<16} {1}".format(name, "PASS" if ok else "FAIL"))
    print()
    print("  {0} / {1} 项通过".format(passed, len(results)))
    print()

    if passed == len(results):
        print("  M0 验收通过，可以进入 M1（数据模拟层）")
        return 0

    print("  还有链路不通，先修好再往下走")
    return 1


if __name__ == "__main__":
    sys.exit(main())
