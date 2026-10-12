# 智慧农业环境监测与决策智能体系统

> 农业环境监测场景下的 LLM 智能体系统。软件模拟的传感器网络产生实时环境数据，经 MQTT
> 传输并写入数据库；智能体通过**工具调用 + RAG + 记忆**对数据进行分析、诊断与决策
> （灌溉 / 通风 / 补光 / 降温），并在异常时主动预警。
>
> 毕业设计项目（物联网专业）。完整覆盖「感知模拟 → 智能体决策 → 后端服务 → 前端可视化
> → 部署上线」全链路，**不依赖任何硬件**。

---

## 技术栈

| 层面 | 选型 |
| --- | --- |
| 语言 / 包管理 | Python 3.12 + uv |
| 大语言模型 | DeepSeek / 通义 Qwen API；本地 Ollama + Qwen2.5-3B（本机显存 4GB，故不上 7B） |
| 智能体 | 先手写 ReAct 工具调用循环，后用 LangGraph 编排 |
| RAG | 手写最小实现 → LangChain；BGE 中文 embedding + Chroma 向量库 |
| 通信 | MQTT（Eclipse Mosquitto）+ paho-mqtt |
| 存储 | SQLite（起步）→ TimescaleDB；SQLAlchemy |
| 后端 | FastAPI + Uvicorn + Pydantic v2 |
| 前端 | Next.js + Tailwind CSS + ECharts |
| 部署 | Docker Compose + Nginx |

## 目录结构

```
smart-agri-agent/
├── simulator/    感知模拟层：生成"像真的"农业环境数据并经 MQTT 发布
├── gateway/      网关订阅器：订阅 MQTT，把数据写入存储层
├── storage/      数据访问层：时序数据与业务数据的读写
├── agent/        智能体核心：LLM 抽象、工具集、ReAct 循环、记忆
├── rag/          知识库：切分 → 嵌入 → 入库 → 检索
├── api/          后端服务：FastAPI 路由、WebSocket、鉴权
├── tests/        测试
├── docs/         环境记录、架构笔记、接口说明
└── data/         本地数据（SQLite / 向量库，已被 git 忽略）
```

## 快速开始

```powershell
uv venv                            # 创建虚拟环境
.\.venv\Scripts\Activate.ps1       # 激活（提示符出现 (.venv) 才算成功）
uv sync                            # 按 pyproject.toml 安装依赖
```

首次运行前，复制 `.env.example` 为 `.env` 并填入自己的 API Key：

```powershell
Copy-Item .env.example .env
```

> `.env` 已被 git 忽略，**永远不会**被提交。密钥只放在本地。

## 开发进度

- [x] **M0** 环境与设计 —— 环境就绪，需求与架构定稿
- [ ] M1 数据模拟层（模拟器 + MQTT + 存储）
- [ ] M2 智能体核心（LLM 抽象 + 工具集 + 手写 ReAct）
- [ ] M3 RAG + 记忆
- [ ] M4 后端 API
- [ ] M5 前端仪表盘
- [ ] M6 部署与优化
- [ ] M7 论文与答辩

## 相关文档

| 文档 | 位置 |
| --- | --- |
| 环境记录 | `docs/env.md` |
| 设计文档总览 | `../大模型项目设计（智能体+多模态）/00_总览与学习路线图.md` |
| 项目设计方案 | `../大模型项目设计（智能体+多模态）/项目一_智慧农业环境监测决策智能体/01_项目设计方案.md` |
| 开发计划与验收 | `../大模型项目设计（智能体+多模态）/项目一_智慧农业环境监测决策智能体/05_开发计划与验收标准.md` |
