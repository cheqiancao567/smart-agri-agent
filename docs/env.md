# 环境记录

> 换电脑、重装、或出问题时，照着这份记录就能复原。
> 最后更新：2026-10-12

## 1. 这台机器

| 项目 | 实测值 | 备注 |
| --- | --- | --- |
| 操作系统 | Windows | |
| GPU | **NVIDIA RTX 3050 Laptop / 显存 4GB** | ⚠️ 设计文档假设的是 4060 8GB，**本地大模型需降级到 3B** |
| 显卡驱动 | 581.42（CUDA 13.0） | |
| C 盘 | 100GB 总量，可用 9.1GB | ⚠️ 系统盘很紧张 |
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

未安装、后续需要：Docker Desktop、Ollama。

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
