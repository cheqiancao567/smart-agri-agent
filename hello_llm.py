# -*- coding: utf-8 -*-
"""
Day 3 · 第一次调用大模型

这个脚本做三件事：
  1. 从 .env 读出 API Key（绝不写死在代码里，也绝不进 git）
  2. 发一句话给 DeepSeek，把回答打印出来
  3. 顺便报告这次调用花了多少 token、用了多少秒

运行方式（先激活虚拟环境）：
    .\\.venv\\Scripts\\Activate.ps1
    python hello_llm.py
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 读取项目根目录下的 .env
load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not api_key:
    raise SystemExit(
        "\n没有找到 DEEPSEEK_API_KEY。\n"
        "请打开项目根目录下的 .env 文件，把 Key 填在 DEEPSEEK_API_KEY= 后面，然后存盘。\n"
    )

# DeepSeek 兼容 OpenAI 的接口协议，所以直接复用 openai 这个库，只换 base_url
client = OpenAI(api_key=api_key, base_url=base_url)


def ask(messages, label):
    """发一次请求，打印问题、回答、耗时和 token 用量。"""
    print("\n" + "=" * 64)
    print("【" + label + "】")
    print("=" * 64)
    for m in messages:
        print("  {0:>9} | {1}".format(m["role"], m["content"]))

    start = time.time()
    resp = client.chat.completions.create(model=model, messages=messages)
    elapsed = time.time() - start

    print("\n  → 模型回答：" + (resp.choices[0].message.content or "").strip())
    print("  → 耗时：{0:.2f} 秒".format(elapsed))
    if resp.usage:
        print(
            "  → 用量：输入 {0} + 输出 {1} = {2} tokens".format(
                resp.usage.prompt_tokens,
                resp.usage.completion_tokens,
                resp.usage.total_tokens,
            )
        )


# ---- 第一次：最简单的对话，只有一条 user 消息 ----
ask(
    [{"role": "user", "content": "你好，请用一句话介绍你自己。"}],
    "第一次调用：单条用户消息",
)

# ---- 第二次：加一条 system 消息 ----
# system 是"人设设定"：它在用户开口之前，就规定了模型的身份和说话风格
ask(
    [
        {"role": "system", "content": "你是一位严谨的农业技术顾问，回答简短专业，不说客套话。"},
        {"role": "user", "content": "你好，请用一句话介绍你自己。"},
    ],
    "第二次调用：加一条 system 消息",
)

print("\n对比两次回答——同样的提问，只多了一条 system 消息，语气和长度变了没有？")
