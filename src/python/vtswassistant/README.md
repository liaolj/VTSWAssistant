# vtswassistant Python 包

该包实现了语音→结构化文本流水线的各个模拟组件，便于在不依赖实际云服务的情况下进行单元测试与原型验证。

## 模块概览

| 模块 | 作用 |
| --- | --- |
| `audio` | 定义 `AudioChunk`、`SpeechSegment` 数据结构。 |
| `vad` | `SileroVADSegmenter`：根据阈值将音频分段。 |
| `asr` | `DoubaoASRClient`：根据 `SpeechSegment` 生成确定性转写。 |
| `llm` | `StructuredLLMFormatter`：将文本整理为主题/要点/行动项。 |
| `template` | `TemplateRenderer`：将结构化结果渲染为文本模板。 |
| `structuring` | `StructuredDraftMerger`：根据策略合并段落。 |
| `insertion` | `InsertionController`：模拟多策略写入与撤销。 |
| `pipeline` | `SpeechToStructuredTextPipeline`：编排完整流程。 |

## 调试日志

为方便排查各阶段行为，核心模块已在关键步骤添加 `logging` 调试信息：

- VAD：分段开始/结束、刷新、输入 chunk。 
- ASR：是否使用提示文本、回退文案情况。
- LLM：句子拆分、主题/要点/行动项提取。
- 模板渲染：输出长度与所用模板。
- 合并器与写入控制器：段落合并、策略选择、撤销操作。
- 总流水线：chunk 处理、段落计数、最终输出长度。

要查看调试日志，可在运行前配置全局日志级别，例如：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

或直接通过 pytest 输出调试日志：

```bash
python -m pytest -q -o log_cli=true -o log_cli_level=DEBUG
```

> **提示**：默认日志级别为 `WARNING`，因此不会影响现有测试；仅在显式设置为 `DEBUG/INFO` 时输出。

## 测试

仓库提供 `tests/python/test_pipeline.py`，覆盖结构化输出、策略回退与撤销逻辑。运行：

```bash
pytest -q
```

## 下一步

后续集成真实服务时，可在保持日志接口不变的前提下替换各模块实现，便于保留调试语义并快速定位问题。
