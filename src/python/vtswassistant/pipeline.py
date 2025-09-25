"""High level orchestration of the speech → structured text pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .audio import AudioChunk, SpeechSegment
from .asr import DoubaoASRClient
from .config import Config
from .insertion import InsertionController
from .llm import StructuredLLMFormatter
from .structuring import StructuredDraftMerger
from .template import TemplateRenderer
from .vad import SileroVADSegmenter


@dataclass(slots=True)
class PipelineDependencies:
    vad: SileroVADSegmenter
    asr: DoubaoASRClient
    llm: StructuredLLMFormatter
    merger: StructuredDraftMerger
    renderer: TemplateRenderer
    insertion: InsertionController


class SpeechToStructuredTextPipeline:
    """Coordinates the major components described in the architecture docs."""

    def __init__(self, config: Config, deps: PipelineDependencies) -> None:
        self.config = config
        self.deps = deps
        self._segment_counter = 0

    def process_stream(self, chunks: Sequence[AudioChunk]) -> str:
        output_text = ""
        for index, chunk in enumerate(chunks):
            segments = self.deps.vad.process_chunk(chunk, index)
            output_text = self._handle_segments(segments)
        trailing = self.deps.vad.flush()
        if trailing:
            output_text = self._handle_segments(trailing, final=True)
        return output_text

    # ------------------------------------------------------------------
    def _handle_segments(self, segments: Iterable[SpeechSegment], final: bool = False) -> str:
        merged = self.deps.merger.aggregated_text
        for segment in segments:
            transcript = self.deps.asr.transcribe_segment(segment)
            structured = self.deps.llm.structure(transcript.text)
            rendered = self.deps.renderer.render(
                structured, template_name=self.config.structuring.default_template
            )
            self._segment_counter += 1
            merged = self.deps.merger.merge(self._segment_counter, rendered)
            self.deps.insertion.stage(merged, final=final or self.config.structuring.realtime_write)
        return merged

    def undo_last_insert(self) -> None:
        self.deps.insertion.undo_last()
        self.deps.merger.reset()
        self._segment_counter = 0
