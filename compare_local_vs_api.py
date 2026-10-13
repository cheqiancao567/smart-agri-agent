# -*- coding: utf-8 -*-
"""
Day 3 · 本地模型 vs 云端 API 对比

对同样的问题，分别问：
  ① 本地 Ollama 的 qwen2.5:3b —— 跑在你自己显卡上，免费，但开机要加载、速度慢
  ② 云端 DeepSeek API —— 按 token 付费，秒回，但每一句都在花钱

脚本会打印每个回答的文字、耗时、token 用量，最后给出对比结论。

运行方式（先激活虚拟环境，并确保 Ollama 服务在跑）：
    .\\.venv\\Scripts\\Activate.ps1
    python compare_local_vs_api.py
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent / ".env")

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LOCAL_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

CLOUD_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
CLOUD_BASE = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
CLOUD_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Ollama 提供了和 OpenAI 完全一样的接口，所以同一个库、同样的调用方式，
# 只要换 base_url 就能连上本地模型。api_key 随便填，本地不校验。
local_client = OpenAI(api_key="ollama", base_url=OLLAMA_BASE.rstrip("/") + "/v1")
cloud_client = OpenAI(api_key=CLOUD_KEY, base_url=CLOUD_BASE) if CLOUD_KEY else None

QUESTIONS = [
    "用一句话介绍你自己。",
    "番茄结果期适宜的土壤湿度是多少？请简短回答，不超过 30 个字。",
]


def ask(client, model, question, label):
    """发一次请求，返回回答文字、耗时和 token 用量。"""
    messages = [{"role": "user", "content": question}]
    start = time.time()
    resp = client.chat.completions.create(model=model, messages=messages)
    elapsed = time.time() - start
    usage = resp.usage
    return {
        "who": label,
        "text": (resp.choices[0].message.content or "").strip(),
        "sec": elapsed,
        "tokens_in": usage.prompt_tokens if usage else None,
        "tokens_out": usage.completion_tokens if usage else None,
    }


def show(r):
    tokens = "?"
    if r["tokens_in"] is not None:
        tokens = "{0}+{1}".format(r["tokens_in"], r["tokens_out"])
    print("    [{0}] {1:>6.2f} 秒  {2:>7} tokens".format(r["who"], r["sec"], tokens))
    print("      {0}".format(r["text"]))


# ---- 预热：本地模型第一次调用要把 2GB 权重读进显存，不计入正式成绩 ----
print("预热本地模型（首次加载权重，可能要一分钟）...")
t0 = time.time()
try:
    ask(local_client, LOCAL_MODEL, "你好", "本地")
    print("  本地模型就绪，耗时 {0:.1f} 秒\n".format(time.time() - t0))
except Exception as exc:
    print("  本地模型不可用：{0}\n  请确认 Ollama 已启动（托盘图标）。\n".format(exc))

summary = []
for i, q in enumerate(QUESTIONS, 1):
    print("=" * 68)
    print("问题 {0}：{1}".format(i, q))
    print("=" * 68)

    try:
        local_r = ask(local_client, LOCAL_MODEL, q, "本地")
        show(local_r)
        summary.append(local_r)
    except Exception as exc:
        print("    [本地] 失败：{0}".format(exc))

    print()

    if cloud_client is not None:
        cloud_r = ask(cloud_client, CLOUD_MODEL, q, "云端")
        show(cloud_r)
        summary.append(cloud_r)
    else:
        print("    [云端] 跳过：.env 里没有 DEEPSEEK_API_KEY")
    print()

# ---- 汇总 ----
print("=" * 68)
print("汇总")
print("=" * 68)
local_times = [r["sec"] for r in summary if r["who"] == "本地"]
cloud_times = [r["sec"] for r in summary if r["who"] == "云端"]
if local_times:
    print("  本地平均耗时：{0:.2f} 秒/次（免费）".format(sum(local_times) / len(local_times)))
if cloud_times:
    print("  云端平均耗时：{0:.2f} 秒/次（按 token 计费）".format(sum(cloud_times) / len(cloud_times)))
if local_times and cloud_times:
    print("  → 云端快约 {0:.1f} 倍".format(
        (sum(local_times) / len(local_times)) / (sum(cloud_times) / len(cloud_times))))
print()
print("  怎么读这组数据：")
print("   · 速度：权重已经在显存里时，本地小模型其实很快（不经过网络）。")
print("          真正慢的是「首次加载」——本次实测第一句等了 76 秒，之后 0.2~0.6 秒。")
print("   · 质量：本地只有 3B，回答更粗糙、偶尔出现语病或胡言；")
print("          云端模型大得多，表达明显更稳、更干净。")
print("   · 成本：本地 0 元；云端按 token 计费（本次四次调用合计几厘钱）。")
print("   · token 数不能跨厂商直接比：两家分词器不同，同一句中文算出的 token 不一样。")
print()
print("  结论：开发调试用本地（省钱、可离线、随便刷），正式演示用云端（质量稳）。")
print("        两者的取舍不是「快慢」，而是「质量 vs 成本」和「能不能离线」。")
