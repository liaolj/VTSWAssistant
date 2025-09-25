"""Simplified Doubao ASR client used for deterministic tests."""

from __future__ import annotations

from dataclasses import dataclass

from .audio import SpeechSegment


@dataclass(slots=True)
class TranscriptResult:
    """Container for ASR output."""

    text: str
    is_final: bool = True
    confidence: float = 0.85


class DoubaoASRClient:
    """A tiny façade that mimics the behaviour of the Doubao streaming API."""

    def __init__(self, language: str = "zh-CN", enable_intermediate_results: bool = True) -> None:
        self.language = language
        self.enable_intermediate_results = enable_intermediate_results

    def transcribe_segment(self, segment: SpeechSegment) -> TranscriptResult:
        """Produce a deterministic transcript for the provided speech segment."""

        if segment.transcript_hint:
            text = segment.transcript_hint.strip()
        else:
            text = self._fallback_transcript(segment)
        return TranscriptResult(text=text)

    def _fallback_transcript(self, segment: SpeechSegment) -> str:
        """Create a naive transcript from raw samples when hints are unavailable."""

        if not segment.samples:
            return ""
        mean_amplitude = sum(segment.samples) / len(segment.samples)
        if mean_amplitude < 0.2:
            return "(静音)"
        return f"(未识别片段，平均幅度 {mean_amplitude:.2f})"
