# 语音 → 结构化文本 Windows 助手

将麦克风语音实时转为**结构化文本**并写入任意桌面输入框。  
栈：Silero VAD（本地）+ Doubao ASR（第三方流式）+ OpenRouter（LLM，结构化整理）。

## ✨ 功能
- 全局热键召唤（默认 Alt+S），悬浮窗显示波形与字幕
- VAD 分段、ASR 中间/最终结果、LLM 结构化（主题/要点/行动项）
- 两种写入模式：确认后 / 实时；原子撤销；多策略写入（SendInput/UIA/剪贴板）

## 📦 快速开始
1. 复制 `config/config.sample.yaml` 为 `config/config.yaml`，填入 **Doubao** 与 **OpenRouter** 的 `base_url/api_key`。
2. （可选）复制 `.env.sample` 为 `.env`，仅用于本机调试。
3. 运行安装包或调试版本，托盘图标可打开设置页。

更多详见 [`USER_GUIDE.md`](./USER_GUIDE.md)。

## 🔐 隐私
- 本地模式：不发外网（仅字幕+固定模板），可抓包验证。
- API Key 加密存储；诊断包自动脱敏。详见 [`SECURITY.md`](./SECURITY.md)。

## 🧪 测试与兼容
- 测试计划见 [`docs/TestPlan.md`](./docs/TestPlan.md)
- 兼容矩阵与站点策略见 [`docs/Compatibility.md`](./docs/Compatibility.md)

## 🗺️ 架构
- 数据流、线程/进程模型、插入策略见 [`docs/Architecture.md`](./docs/Architecture.md)

## 🧰 调优
- VAD 参数与场景建议：[`docs/VAD-Tuning.md`](./docs/VAD-Tuning.md)
- Doubao ASR 接入与配额：[`docs/ASR-Doubao-Notes.md`](./docs/ASR-Doubao-Notes.md)
- OpenRouter 模型候选与切换：[`docs/LLM-Model-Guide.md`](./docs/LLM-Model-Guide.md)

## 🚀 发布
- 发布前检查清单：[`docs/ReleaseChecklist.md`](./docs/ReleaseChecklist.md)
- 制作安装包脚本：[`scripts/make_installer.ps1`](./scripts/make_installer.ps1)

## 🤝 贡献
请阅读 [`CONTRIBUTING.md`](./CONTRIBUTING.md) 与 PR 模板（.github）。安全问题参见 [`SECURITY.md`](./SECURITY.md)。

## 🐍 Python 开发规划

### 为什么采用 Python？
- Python 作为主要开发语言，将用于核心逻辑实现、脚本自动化和数据处理模块（如 VAD 后处理、ASR 结果解析、LLM 提示工程）。
- 优势：丰富的生态（如 speech recognition 库）、易读性、跨平台支持，便于扩展语音处理功能。
- 与现有栈集成：Python 可通过 subprocess 或 API 与现有组件（如 PowerShell 脚本）交互。

### 环境设置
1. 安装 Python 3.10+（推荐使用 pyenv 或 conda 管理版本）。
2. 创建虚拟环境：`python -m venv venv` 并激活。
3. 安装依赖：`pip install -r requirements.txt`（后续创建）。

### 项目结构建议
- `src/python/`：核心 Python 模块（e.g., vad_processor.py, asr_handler.py, llm_structurer.py）。
- `tests/python/`：单元测试（使用 pytest）。
- `scripts/python/`：自动化脚本（e.g., data_collection.py）。
- `requirements.txt`：列出依赖，如 `silero-vad`, `requests`, `openai`（用于 OpenRouter）。

### 开发流程
1. 在 `src/python/` 中实现新功能。
2. 测试：运行 `pytest tests/python/`。
3. 集成：从主应用调用 Python 脚本（e.g., via `subprocess.run`）。
4. 贡献：Python 代码遵循 PEP 8 规范，使用 black 格式化，添加类型提示。

更多细节见后续 `docs/Python-Development.md`（待创建）。
