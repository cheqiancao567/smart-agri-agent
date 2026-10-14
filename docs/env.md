# 环境记录

> 换电脑、重装、或出问题时，照着这份记录就能复原。
> 最后更新：2026-10-13

## 1. 这台机器

| 项目 | 实测值 | 备注 |
| --- | --- | --- |
| 操作系统 | Windows | |
| GPU | **NVIDIA RTX 3050 Laptop / 显存 4GB** | ⚠️ 设计文档假设的是 4060 8GB，**本地大模型需降级到 3B** |
| 显卡驱动 | 581.42（CUDA 13.0） | |
| C 盘 | 100GB 总量，可用约 6.6GB | ⚠️ 系统盘很紧张，大文件一律放 E 盘 |
| E 盘 | 477GB 总量，可用 455GB | **大文件全部放这里** |

## 2. 已安装的工具

| 工具 | 版本 | 安装位置 |
| --- | --- | --- |
| Python | 3.12.10 | `%LOCALAPPDATA%\Programs\Python\Python312` |
| uv | 0.13.0 | `...\Python312\Scripts\uv.exe` |
| Git | 2.56.0.windows.2 | |
| Node.js | v24.21.0 | 项目一前端用 |
| npm | 11.19.0 | |
| VS Code | 1.141.0 | |
| Docker Desktop | 29.8.2 | `E:\Docker\Docker`（详见第 10 节） |

VS Code 插件：`ms-python.python`、`ms-python.vscode-pylance`、`ms-toolsai.jupyter`（另自动带入 6 个依赖插件，如 debugpy、jupyter-renderers）。

开发环境所需的工具（Python / uv / Git / Node / VS Code / Docker / Ollama）已全部就位。

## 3. 环境变量（用户级，已配置）

把开发相关的大文件全部改道到 E 盘，避免 C 盘被塞满。

| 变量 | 值 | 作用 |
| --- | --- | --- |
| `PIP_CACHE_DIR` | `E:\dev-cache\pip` | pip 下载缓存 |
| `UV_CACHE_DIR` | `E:\dev-cache\uv` | uv 下载缓存 |
| `HF_HOME` | `E:\dev-cache\huggingface` | HuggingFace 模型缓存 |
| `HUGGINGFACE_HUB_CACHE` | `E:\dev-cache\huggingface\hub` | 同上（新版变量名） |
| `TORCH_HOME` | `E:\dev-cache\torch` | PyTorch 预训练权重 |
| `OLLAMA_MODELS` | `E:\dev-cache\ollama` | 本地大模型权重 |
| `PIP_INDEX_URL` | 清华 PyPI 镜像 | 国内源，实测快约 200 倍 |
| `UV_DEFAULT_INDEX` | 清华 PyPI 镜像 | 同上，给 uv 用 |

> 验证方法：新开终端执行 `echo $env:UV_CACHE_DIR`，应输出 `E:\dev-cache\uv`。

## 4. 踩过的坑

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 敲 `python` 弹出微软商店 | Windows「应用执行别名」占位程序挡在前面 | 装完真 Python 后把它排到 PATH 最前 |
| `winget` 报 "file cannot be accessed" | 系统限制 | 改用官网安装包 |
| 装 uv 时报 `No space left on device` | C 盘 100GB 仅剩 0.05GB | 清理出约 9GB，并把缓存改道 E 盘 |
| 清理脚本静默失败 | PowerShell 5.1 在中文 Windows 上按 GBK 读 `.ps1`，UTF-8 中文变乱码导致语法错误 | **`.ps1` 一律用纯 ASCII，或存成带 BOM 的 UTF-8** |
| uv 报 "Failed to hardlink files" | 缓存与虚拟环境跨盘，无法硬链接 | 缓存改到 E 盘，与项目同盘后即可硬链接 |
| git 报 `dubious ownership` | 沙箱进程以另一账户读写文件，git 认为仓库不属于当前用户 | 把项目目录加入例外：`git config --global --add safe.directory <项目绝对路径>` |
| `code --install-extension` 卡死 5 分钟无输出 | 插件市场域名在本机网络下时通时断（同一域名一会 200、一会 18 秒超时） | 优先从 VS Code 界面装（`Ctrl+Shift+X`）；或下载 `.vsix` 本地装 |
| 下载的 `.vsix` 报 "not a valid zip" | 市场返回 gzip 内容，下载命令未解压，文件头是 `1F 8B` 而非 `50 4B` | 下载时加 `--compressed` |
| `git push` 报 `Failed to connect ... Could not connect to server` | 网络瞬时抖动，**不是操作错误** | 直接重敲 `git push`，推送是幂等的 |
| 下载 Ollama 安装包只有 3~11 KB/s | `ollama.com` 和 GitHub releases 在国内被限速（同一机器其他源可达 1~10 MB/s） | 改用国内 GitHub 加速镜像 `gh-proxy.com`，实测 **10.7 MB/s** 且支持断点续传 |
| `ollama pull` 卡住不动 | 官方模型仓库 `registry.ollama.ai` 国内不可达（连接超时） | 从 ModelScope 下 GGUF，用 Modelfile 本地导入（见第 7 节） |

> 通用规律：**下载下来的文件打不开，先看文件头** —— `50 4B` = zip，`1F 8B` = gzip，`3C` = HTML（通常是错误页）。

## 5. 常用命令

```powershell
uv venv                          # 建虚拟环境
.\.venv\Scripts\Activate.ps1     # 激活（提示符出现 (.venv) 才算成功）
uv add <包名>                     # 添加依赖
deactivate                       # 退出虚拟环境
```

若激活时报「禁止运行脚本」：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 6. git 报错速查表

| 报错关键词 | 是什么问题 | 怎么办 |
| --- | --- | --- |
| `Failed to connect` / `Could not connect to server` / `timed out` | 网络问题 | 重敲一遍 |
| `Authentication failed` / `Permission denied` | 登录凭据失效 | 重新授权 |
| `rejected ... non-fast-forward` | 远程有你本地没有的提交 | 先 `git pull` 再 push |
| `nothing to commit` | 无改动可提交 | 正常，不是错误 |
| `dubious ownership` | 仓库归属不对 | 加 `safe.directory` |
| `No space left on device` | 磁盘满了 | 清空间 |

## 7. 本地大模型（Ollama）

| 项目 | 值 |
| --- | --- |
| 版本 | 0.40.3 |
| 程序位置 | `E:\Programs\Ollama`（2852 MB，**装在 E 盘，不占 C 盘**） |
| 服务地址 | `http://127.0.0.1:11434`（托盘程序自动拉起） |
| 权重位置 | `E:\dev-cache\ollama`（由 `OLLAMA_MODELS` 决定；`C:\Users\<用户>\.ollama` 只有密钥文件，0 MB） |
| 已装模型 | `qwen2.5:3b`（2.1 GB） |

**模型是怎么装进来的（重要）**

`ollama pull qwen2.5:3b` 在本机**用不了**——官方仓库国内不可达。改走这条路：

```powershell
# 1. 从国内 ModelScope 下载 GGUF 权重（实测 14 MB/s，2GB 约 2.5 分钟）
curl.exe -L -C - -o "E:\dev-cache\ollama\gguf\qwen2.5-3b-instruct-q4_k_m.gguf" `
  "https://modelscope.cn/models/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/master/qwen2.5-3b-instruct-q4_k_m.gguf"

# 2. 用 Modelfile 导入（文件在项目里：local-model/Modelfile）
ollama create qwen2.5:3b -f local-model/Modelfile
```

> `Modelfile` 里的 `FROM` 是绝对路径，换电脑后需要改成本机 GGUF 的实际位置。
> 导入后 `E:\dev-cache\ollama\gguf\` 里那份原始 GGUF 已冗余（权重已复制进 `blobs`），可以删掉省 2GB。

**运行测试**

```powershell
ollama list                       # 看已装模型
ollama run qwen2.5:3b "你好"       # 命令行对话
```

> 首次调用要等约 76 秒（把 2GB 权重读进显存），之后每句 0.2~0.6 秒。

**已关闭自动更新**

Ollama 的 Windows 应用会自动下载更新包并留存在本地。已在它的设置里关掉：

- 设置存放在 `%LOCALAPPDATA%\Ollama\db.sqlite` 的 `settings` 表
- 字段 `auto_update_enabled` 由 `1` 改为 `0`（**改动前已备份为 `db.sqlite.bak`**）
- 改数据库前需先退出 `ollama app.exe` 与 `ollama.exe`，改完再启动

## 8. 大模型选型与成本（DeepSeek）

**这个 Key 实际可用的模型只有两个：**

```
deepseek-flash     便宜，支持图像理解
deepseek-v4-pro    更强更贵，不支持图像理解
```

`deepseek-chat` **不在**可用列表里——它是保留的旧别名，能跑通但路由到哪个模型没有保证。已把 `.env` 改成正式名字 `deepseek-flash`。

**价格（元 / 百万 tokens，2026-10 官网截图）**

| | flash 空闲 | flash 高峰 | v4-pro 空闲 | v4-pro 高峰 |
| --- | --- | --- | --- | --- |
| 输入（缓存命中） | 0.02 | 0.04 | 0.15 | 0.30 |
| 输入（缓存未命中） | 1 | 2 | 4.5 | 9.0 |
| 输出 | 4 | 8 | 13.5 | 27.0 |

**三个省钱要点**

1. **高峰 / 空闲差价一倍** —— 调试尽量避开白天工作时段。
2. **缓存命中便宜 50 倍**（0.02 vs 1）—— 智能体每次调用都要重发 system 提示词、工具清单和历史对话，**把不变的内容放在消息前面**，这部分费用降到 1/50。这是项目一最重要的成本优化点。
3. **上下文 1M / 输出上限 384K** —— 上下文长度完全不是瓶颈，token 成本才是。工具返回的数据要做截断或摘要，别把整张表塞进去。

**实测花销**：4 次调用合计 73 输入 + 82 输出 token ≈ **0.0004 元**（flash、空闲时段）。**10 元够做完整个项目。**

## 9. 本地 vs 云端实测对比

同一组问题分别问本地 `qwen2.5:3b` 与云端 `deepseek-flash`（脚本：`compare_local_vs_api.py`）：

| 问题 | 本地 | 云端 |
| --- | --- | --- |
| 用一句话介绍你自己 | 0.63 秒 / 34+42 tokens | 0.82 秒 / 9+31 tokens |
| 番茄结果期适宜土壤湿度 | 0.24 秒 / 51+14 tokens | 0.54 秒 / 22+12 tokens |
| **平均** | **0.44 秒（免费）** | **0.68 秒（计费）** |

**三个反直觉的发现**

1. **本地比云端快。** 权重已在显存时推理不经过网络；云端要打包 → 传输 → 排队 → 返回。**真正慢的是首次加载（76 秒）**——所以本地模型适合连续调试，不适合"问一句关一次"。
2. **质量差距明显。** 本地 3B 在"介绍你自己"那句里生成了"我叫你一声'wen'"这种胡话；云端表达干净。**事实性问题上 3B 够用，需要流畅表达时才露怯。**
3. **token 数不能跨厂商比较。** 同一句中文，Qwen 分词器算 34 个 token，DeepSeek 算 9 个。只能在同一家服务商内部比较才有意义。

**结论**：开发调试用本地（省钱、可离线、随便刷），正式演示用云端（质量稳）。取舍的不是"快慢"，而是"**质量 vs 成本**"和"**能不能离线**"。

## 10. Docker 与 WSL2

| 项目 | 值 |
| --- | --- |
| Docker Desktop | 29.8.2 |
| 主程序位置 | `E:\Docker\Docker`（3354 MB） |
| CLI 插件位置 | `C:\Program Files\Docker\cli-plugins`（664 MB） |
| 镜像数据位置 | `E:\Docker\data`（`disk\docker_data.vhdx`） |
| WSL2 内核 | `6.18.40.1-microsoft-standard-WSL2` |
| WSL 发行版 | `docker-desktop`（VERSION 2） |

**WSL2 是前置条件，而且必须重启**

Docker 容器依赖 Linux 内核，Windows 上要先启用两项可选功能：

```powershell
dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
# ——重启电脑——
wsl --update
wsl --set-default-version 2
```

> DISM 返回 **3010** 代表"操作成功，但需要重启"。不重启的话 `wsl --update` 会失败。
> 验证 WSL2 是否真的生效：`docker info` 里的 `Kernel Version` 应含 `WSL2`，且 `wsl -l -v` 应显示发行版 `VERSION 2`。

**装到 E 盘的两个关键参数**

```powershell
DockerDesktopInstaller.exe install --accept-license --backend=wsl-2 `
  --installation-dir=E:\Docker\Docker `
  --wsl-default-data-root=E:\Docker\data
```

`--wsl-default-data-root` 尤其重要：不加的话镜像数据会以 vhdx 形式落在系统盘，并随拉取的镜像持续增长。实测加了之后数据在 `E:\Docker\data\disk\docker_data.vhdx`。

> 另注：若安装时报空间不足，多半是安装程序要把 3.3GB 临时文件解压到 `%TEMP%`。把该进程的 `$env:TEMP` / `$env:TMP` 临时指向空间充足的盘即可——大型安装程序卡在空间检查时都能用这招。

**国内镜像加速器（2026-10 实测）**

Docker Hub 直连超时。测了 11 个国内站点，**只有 4 个可用**：

| 站点 | 地址 |
| --- | --- |
| 1ms.run | `https://docker.1ms.run` |
| daocloud | `https://docker.m.daocloud.io` |
| 1panel | `https://docker.1panel.live` |
| 轩辕 | `https://docker.xuanyuan.me` |

> 中科大、网易163、腾讯云、dockerpull、rainbond 均已停服或不可达；南京大学返回 403。

配置写在 `%USERPROFILE%\.docker\daemon.json` 的 `registry-mirrors` 数组里。两个坑：

- **改完必须重启 Docker Desktop**，它不热加载 `daemon.json`
- 即使配了加速器，**第一次拉取仍可能报 `short read: unexpected EOF`，重试即可**（实测第二次成功）

**常用命令**

```powershell
docker run --rm hello-world                                     # 验证引擎
docker images                                                   # 镜像列表（模板）
docker ps -a                                                    # 容器列表（实例）
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto   # 起 MQTT broker
```

概念上记住三层：**Docker Desktop（工具）→ 镜像（模板）→ 容器（实例）**。项目里真正用到的是最外层那层容器。
