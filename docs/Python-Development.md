# Python 模块开发手册

本手册用于指导在 `src/python/` 目录中扩展语音转结构化助手的 Python 代码。
内容涵盖环境准备、目录约定、常用开发流程与测试要求。

## 1. 环境准备

1. 安装 **Python 3.10+**。推荐使用 [pyenv](https://github.com/pyenv/pyenv) 或 Conda 统一管理版本。
2. 创建虚拟环境（Windows 示例）：
   ```powershell
   python -m venv .venv
   .venv\\Scripts\\activate
   ```
   macOS/Linux 使用 `source .venv/bin/activate`。
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. （可选）安装开发工具：
   ```bash
   pip install black ruff mypy
   ```

## 2. 目录结构与约定

- `src/python/vtswassistant/`：主包目录。所有核心逻辑保持模块化：
  - `audio.py`：音频块、语音段结构体及工具。
  - `vad.py`：Silero VAD 包装器（阈值、静音检测）。
  - `asr.py`：Doubao ASR 轻量客户端。
  - `llm.py`：结构化 LLM 格式化器。
  - `structuring.py`：结构化草稿合并策略。
  - `template.py`：模板渲染器。
  - `insertion.py`：多策略插入控制器。
  - `pipeline.py`：语音→结构化文本主流程及依赖注入容器。
  - `config.py`：加载 YAML 配置并映射为数据类。
- `tests/python/`：使用 `pytest` 的单元测试。
- `scripts/`：与 Windows 安装、调试相关的脚本。

编写新模块时：
- 遵循 PEP 8；保持函数纯净、带类型注解。
- 能被覆盖测试的逻辑，确保 `pytest` 能在无外部服务情况下跑通。
- 如需外部 API，将调用封装在适配层，便于替换与模拟。

## 3. 常用开发流程

1. **定义配置**：若新增可调参数，在 `config.py` 的相关数据类中补充字段，并在 `Config.from_mapping` 中处理默认值。
2. **实现功能**：在对应模块编写逻辑，必要时更新 `PipelineDependencies` 注入。
3. **编写测试**：在 `tests/python/` 下新增 `test_*.py`。利用虚构的音频块/文本片段构造场景，避免真实 API 依赖。
4. **运行测试**：
   ```bash
   pytest tests/python -q
   ```
5. **代码检查**（可选但推荐）：
   ```bash
   black src/python tests/python
   ruff check src/python tests/python
   mypy src/python
   ```
6. **文档同步**：如有新特性或接口变更，更新 `README.md`、相关 docs 以及示例配置。

## 4. 依赖与秘钥管理

- `requirements.txt` 已列出核心运行依赖：
  - `PyYAML`：加载配置文件。
  - `silero-vad`：本地语音活动检测（生产环境使用）。
  - `requests`：通用 HTTP 客户端，供 Doubao/OpenRouter 适配器使用。
  - `openai`：访问 OpenRouter/OpenAI 兼容接口。
  - `pytest`：单元测试框架。
- 机密信息（如 `api_key`）存放于 `config/config.yaml` 或 `.env`，并确保不提交到版本控制。

## 5. 调试与排错建议

- **日志**：模块使用标准库 `logging`。在开发环境中设置 `logging.basicConfig(level=logging.DEBUG)` 可获得详细输出。
- **模拟输入**：利用 `tests/python/test_pipeline.py` 中的 `build_pipeline` 思路，构造带 `transcript_hint` 的 `AudioChunk` 模拟语音流程。
- **逐步验证**：
  1. 先在离线环境验证模板渲染与合并策略；
  2. 再接入本地 VAD（Silero）；
  3. 最后串联 ASR 与 LLM。
- **回归测试**：每次修改插入逻辑、VAD 参数或结构化模板后都运行 `pytest`，确保实时写入与撤销行为不回归。

## 6. 发布前检查

- 确认配置、脚本、文档同步更新。
- 执行完整测试并保存报告（如 `pytest --maxfail=1 --disable-warnings -q`）。
- 若引入新第三方依赖，更新 `requirements.txt` 并在本文档说明用途。

保持上述流程有助于在 Windows 应用中稳定集成 Python 模块，确保语音转结构化能力可以持续迭代。
