from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src/python"))

from vtswassistant import (
    AudioChunk,
    Config,
    DoubaoASRClient,
    InsertionController,
    InsertionStrategy,
    PipelineDependencies,
    SileroVADSegmenter,
    SpeechToStructuredTextPipeline,
    StructuredDraftMerger,
    StructuredLLMFormatter,
    TemplateRenderer,
)


def build_pipeline(realtime: bool = True) -> SpeechToStructuredTextPipeline:
    config = Config.from_mapping(
        {
            "app": {"language_ui": "zh-CN"},
            "vad": {
                "threshold": 0.5,
                "min_silence_ms": 40,
                "max_segment_ms": 4000,
                "frame_ms": 20,
            },
            "structuring": {
                "default_template": "generic",
                "realtime_write": realtime,
                "merge_policy": "replace-last-unit",
            },
        }
    )

    vad = SileroVADSegmenter(
        threshold=config.vad.threshold,
        min_silence_ms=config.vad.min_silence_ms,
        max_segment_ms=config.vad.max_segment_ms,
        frame_ms=config.vad.frame_ms,
    )
    asr = DoubaoASRClient(language=config.asr.language)
    llm = StructuredLLMFormatter(config.structuring.uncertain_tag)
    merger = StructuredDraftMerger(config.structuring.merge_policy)
    renderer = TemplateRenderer(config.templates, uncertain_tag=config.structuring.uncertain_tag)
    strategies = [
        InsertionStrategy(name="sendinput", max_length=10),
        InsertionStrategy(name="uia"),
        InsertionStrategy(name="clipboard"),
    ]
    insertion = InsertionController(strategies=strategies, realtime_write=realtime)

    deps = PipelineDependencies(
        vad=vad,
        asr=asr,
        llm=llm,
        merger=merger,
        renderer=renderer,
        insertion=insertion,
    )
    return SpeechToStructuredTextPipeline(config=config, deps=deps)


def test_pipeline_generates_structured_text_and_fallback_strategy():
    pipeline = build_pipeline(realtime=True)
    chunks = [
        AudioChunk(timestamp_ms=0, samples=[0.1, 0.6, 0.7, 0.2], transcript_hint="会议主题确定产品发布"),
        AudioChunk(timestamp_ms=80, samples=[0.6, 0.7, 0.65, 0.3], transcript_hint="需要王强准备物料 下周彩排"),
        AudioChunk(timestamp_ms=160, samples=[0.0, 0.0, 0.0, 0.0], transcript_hint=""),
        AudioChunk(timestamp_ms=240, samples=[0.6, 0.72, 0.7, 0.1], transcript_hint="安排下周彩排并更新日程"),
        AudioChunk(timestamp_ms=320, samples=[0.0, 0.0, 0.0, 0.0], transcript_hint=""),
    ]

    final_text = pipeline.process_stream(chunks)

    # sendinput should fail due to max_length constraint; uia should succeed.
    strategies = pipeline.deps.insertion.strategies
    assert len(strategies[0].inserted) == 0
    assert len(strategies[1].inserted) >= 1
    assert strategies[1].inserted[-1] == final_text

    assert "主题" in final_text
    assert "行动项" in final_text
    assert "王强" in final_text


def test_pipeline_undo_resets_state():
    pipeline = build_pipeline(realtime=True)
    chunks = [
        AudioChunk(timestamp_ms=0, samples=[0.8, 0.7, 0.6], transcript_hint="会议主题讨论测试"),
        AudioChunk(timestamp_ms=60, samples=[0.0, 0.0, 0.0], transcript_hint=""),
    ]

    pipeline.process_stream(chunks)
    assert pipeline.deps.insertion.committed_blocks

    pipeline.undo_last_insert()
    assert not pipeline.deps.insertion.committed_blocks
    assert pipeline.deps.merger.aggregated_text == ""
