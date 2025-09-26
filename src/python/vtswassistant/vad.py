"""Simplified Silero inspired VAD implementation for unit tests."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List

from .audio import AudioChunk, SpeechSegment


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SileroVADSegmenter:
    """A tiny VAD that mimics the behaviour described in the architecture docs."""

    threshold: float
    min_silence_ms: int
    max_segment_ms: int
    frame_ms: int

    _active: bool = field(init=False, default=False)
    _segment_start_ms: int = field(init=False, default=0)
    _segment_samples: List[float] = field(init=False, default_factory=list)
    _segment_transcript: List[str] = field(init=False, default_factory=list)
    _segment_chunks: List[int] = field(init=False, default_factory=list)
    _silence_ms: int = field(init=False, default=0)
    _current_time_ms: int = field(init=False, default=0)
    _segment_index: int = field(init=False, default=0)

    def reset(self) -> None:
        logger.debug("Resetting VAD state")
        self._active = False
        self._segment_start_ms = 0
        self._segment_samples.clear()
        self._segment_transcript.clear()
        self._segment_chunks.clear()
        self._silence_ms = 0
        self._current_time_ms = 0
        self._segment_index = 0

    def process_chunk(self, chunk: AudioChunk, chunk_index: int) -> List[SpeechSegment]:
        """Consume an audio chunk and return any completed speech segments."""

        logger.debug(
            "Processing audio chunk %d at %dms (samples=%d)",
            chunk_index,
            chunk.timestamp_ms,
            len(chunk.samples),
        )
        if not self._active and chunk.has_speech(self.threshold):
            self._start_segment(chunk.timestamp_ms, chunk_index, chunk.transcript_hint)
        elif self._active and (not self._segment_chunks or self._segment_chunks[-1] != chunk_index):
            # A continuing segment spanning multiple chunks.
            self._segment_chunks.append(chunk_index)
            if chunk.transcript_hint:
                self._segment_transcript.append(chunk.transcript_hint.strip())

        segments: List[SpeechSegment] = []
        time_cursor = chunk.timestamp_ms

        for sample in chunk.samples:
            if sample >= self.threshold:
                if not self._active:
                    self._start_segment(time_cursor, chunk_index, chunk.transcript_hint)
                self._segment_samples.append(sample)
                self._silence_ms = 0
            else:
                if self._active:
                    self._silence_ms += self.frame_ms
                    if self._silence_ms >= self.min_silence_ms:
                        segments.append(self._close_segment(time_cursor))
                        continue
            time_cursor += self.frame_ms
            self._current_time_ms = time_cursor

            if self._active and self._segment_duration_ms() >= self.max_segment_ms:
                segments.append(self._close_segment(time_cursor))

        if segments:
            logger.debug("Chunk %d produced %d segments", chunk_index, len(segments))
        return segments

    def flush(self) -> List[SpeechSegment]:
        """Close any pending segment when the stream ends."""

        if not self._active:
            return []

        logger.debug("Flushing trailing segment at %dms", self._current_time_ms)
        return [self._close_segment(self._current_time_ms)]

    # ------------------------------------------------------------------
    def _start_segment(self, start_ms: int, chunk_index: int, transcript_hint: str) -> None:
        self._active = True
        self._segment_start_ms = start_ms
        self._segment_samples = []
        self._segment_transcript = [transcript_hint.strip()] if transcript_hint else []
        self._segment_chunks = [chunk_index]
        self._silence_ms = 0
        logger.debug("Started segment %d at %dms (chunk %d)", self._segment_index, start_ms, chunk_index)

    def _close_segment(self, end_ms: int) -> SpeechSegment:
        self._active = False
        transcript = " ".join(part for part in self._segment_transcript if part)
        segment = SpeechSegment(
            start_ms=self._segment_start_ms,
            end_ms=end_ms,
            samples=tuple(self._segment_samples),
            transcript_hint=transcript.strip(),
            chunk_indices=list(self._segment_chunks),
        )
        self._segment_samples = []
        self._segment_transcript = []
        self._segment_chunks = []
        self._segment_start_ms = end_ms
        self._silence_ms = 0
        self._segment_index += 1
        logger.debug(
            "Closed segment %d at %dms (duration=%dms, hint=%d chars)",
            self._segment_index - 1,
            end_ms,
            segment.duration_ms(),
            len(segment.transcript_hint),
        )
        return segment

    def _segment_duration_ms(self) -> int:
        return self._current_time_ms - self._segment_start_ms
