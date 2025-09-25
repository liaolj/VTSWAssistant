"""Configuration helpers for the assistant prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore


@dataclass(slots=True)
class AppConfig:
    language_ui: str = "zh-CN"
    autosave_config: bool = True
    mode: str = "desktop_assistant"


@dataclass(slots=True)
class HotkeyConfig:
    toggle_recording: str = "Alt+S"
    insert_now: str = "Alt+Enter"
    undo_last_insert: str = "Alt+Backspace"
    switch_template: str = "Alt+T"
    pause_resume: str = "Alt+P"


@dataclass(slots=True)
class VADConfig:
    provider: str = "silero"
    threshold: float = 0.58
    min_silence_ms: int = 800
    max_segment_ms: int = 5000
    sample_rate: int = 16000
    frame_ms: int = 20


@dataclass(slots=True)
class ASRConfig:
    provider: str = "doubao"
    base_url: str = ""
    api_key: str = ""
    language: str = "zh-CN"
    enable_intermediate_results: bool = True
    punctuation: bool = True
    profanity_filter: bool = False
    connect_timeout_ms: int = 8000
    keepalive_sec: int = 20
    max_reconnect: int = 3
    backoff_ms: int = 800


@dataclass(slots=True)
class LLMSpec:
    provider: str = "openrouter"
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 800
    stream: bool = True
    timeout_ms: int = 15000
    alt_models: Iterable[Mapping[str, str]] = field(default_factory=list)
    prompt: str = (
        "你是“语音转结构化写作助手”。将输入内容整理为：主题、要点、行动项。"
    )


@dataclass(slots=True)
class InsertionConfig:
    strategy_order: Iterable[str] = ("sendinput", "uia", "clipboard")
    atomic_block_undo: bool = True
    newline_style: str = "list"
    max_block_chars: int = 1200


@dataclass(slots=True)
class StructuringConfig:
    default_template: str = "generic"
    realtime_write: bool = False
    auto_bullets: bool = True
    merge_policy: str = "replace-last-unit"
    uncertain_tag: str = "（不确定）"


@dataclass(slots=True)
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)
    vad: VADConfig = field(default_factory=VADConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    llm: LLMSpec = field(default_factory=LLMSpec)
    structuring: StructuringConfig = field(default_factory=StructuringConfig)
    insertion: InsertionConfig = field(default_factory=InsertionConfig)
    templates: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "Config":
        """Create a :class:`Config` from a dictionary-like structure."""

        def load(section: str, model: type) -> object:
            values = data.get(section, {})
            if not isinstance(values, MutableMapping):
                return model()  # pragma: no cover - defensive
            return model(**values)  # type: ignore[arg-type]

        templates = data.get("templates", {})
        if not isinstance(templates, Mapping):
            templates = {}

        return cls(
            app=load("app", AppConfig),
            hotkeys=load("hotkeys", HotkeyConfig),
            vad=load("vad", VADConfig),
            asr=load("asr", ASRConfig),
            llm=load("llm", LLMSpec),
            structuring=load("structuring", StructuringConfig),
            insertion=load("insertion", InsertionConfig),
            templates=templates,
        )


def load_config(path: Path) -> Config:
    """Load configuration from a YAML file."""

    if yaml is None:  # pragma: no cover - optional dependency guard
        raise RuntimeError("PyYAML is required to load configuration files.")

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    if not isinstance(payload, Mapping):  # pragma: no cover - defensive
        raise ValueError("Configuration root must be a mapping.")

    return Config.from_mapping(payload)
