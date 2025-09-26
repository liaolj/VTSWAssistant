"""Core modules for the VTSW Windows assistant prototype."""

from .config import AppConfig, Config, HotkeyConfig, InsertionConfig, LLMSpec, VADConfig, ASRConfig
from .audio import AudioChunk, SpeechSegment
from .vad import SileroVADSegmenter
from .asr import DoubaoASRClient, TranscriptResult
from .llm import StructuredLLMFormatter, StructuredSegment, ActionItem
from .structuring import StructuredDraftMerger
from .template import TemplateRenderer
from .insertion import InsertionController, InsertionStrategy
from .pipeline import PipelineDependencies, SpeechToStructuredTextPipeline

__all__ = [
    "ActionItem",
    "AppConfig",
    "ASRConfig",
    "AudioChunk",
    "Config",
    "DoubaoASRClient",
    "HotkeyConfig",
    "InsertionConfig",
    "InsertionController",
    "InsertionStrategy",
    "LLMSpec",
    "PipelineDependencies",
    "SileroVADSegmenter",
    "SpeechSegment",
    "SpeechToStructuredTextPipeline",
    "StructuredDraftMerger",
    "StructuredLLMFormatter",
    "StructuredSegment",
    "TemplateRenderer",
    "TranscriptResult",
    "VADConfig",
]
