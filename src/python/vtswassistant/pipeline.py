"""High level orchestration of the speech → structured text pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Sequence

from .audio import AudioChunk, SpeechSegment
from .asr import DoubaoASRClient
from .config import Config
from .insertion import InsertionController
from .llm import StructuredLLMFormatter
from .structuring import StructuredDraftMerger
from .template import TemplateRenderer
from .vad import SileroVADSegmenter

logger = logging.getLogger(__name__)


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
        logger.debug("Starting stream processing for %d chunks", len(chunks))
        output_text = ""
        for index, chunk in enumerate(chunks):
            logger.debug(
                "Processing chunk %d at %dms with %d samples", index, chunk.timestamp_ms, len(chunk.samples)
            )
            segments = self.deps.vad.process_chunk(chunk, index)
            logger.debug("Chunk %d produced %d segments", index, len(segments))
            output_text = self._handle_segments(segments)
        trailing = self.deps.vad.flush()
        if trailing:
            logger.debug("Flushing VAD produced %d trailing segments", len(trailing))
            output_text = self._handle_segments(trailing, final=True)
        logger.debug("Finished stream processing with %d characters", len(output_text))
        return output_text

    # ------------------------------------------------------------------
    def _handle_segments(self, segments: Iterable[SpeechSegment], final: bool = False) -> str:
        merged = self.deps.merger.aggregated_text
        segments = list(segments)
        logger.debug("Handling %d segments (final=%s)", len(segments), final)
        for segment in segments:
            logger.debug(
                "Transcribing segment spanning %d-%dms (chunks=%s)",
                segment.start_ms,
                segment.end_ms,
                segment.chunk_indices,
            )
            transcript = self.deps.asr.transcribe_segment(segment)
            logger.debug("Transcript generated (%d chars)", len(transcript.text))
            structured = self.deps.llm.structure(transcript.text)
            logger.debug("Structured topic: %s; %d points; %d actions", structured.topic, len(structured.points), len(structured.actions))
            rendered = self.deps.renderer.render(
                structured, template_name=self.config.structuring.default_template
            )
            self._segment_counter += 1
            logger.debug("Merging segment #%d", self._segment_counter)
            merged = self.deps.merger.merge(self._segment_counter, rendered)
            self.deps.insertion.stage(merged, final=final or self.config.structuring.realtime_write)
        return merged

    def undo_last_insert(self) -> None:
        logger.debug("Undo requested – resetting pipeline state")
        self.deps.insertion.undo_last()
        self.deps.merger.reset()
        self._segment_counter = 0
