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
