"""Audio domain data structures used by the assistant pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence


@dataclass(slots=True)
class AudioChunk:
    """Represents a chunk of audio samples coming from the microphone.

    The implementation intentionally keeps the type generic – *samples* are modelled
    as floating point amplitudes so that the class works with synthetic fixtures used
    in unit tests.  In the real application these would map to PCM frames.
    """

    timestamp_ms: int
    samples: Sequence[float]
    transcript_hint: str = ""

    def has_speech(self, threshold: float) -> bool:
        """Return ``True`` if any sample crosses the VAD threshold."""

        return any(value >= threshold for value in self.samples)


@dataclass(slots=True)
class SpeechSegment:
    """Represents a contiguous region of speech detected by the VAD."""

    start_ms: int
    end_ms: int
    samples: Sequence[float]
    transcript_hint: str = ""
    chunk_indices: List[int] = field(default_factory=list)

    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)

    def iter_samples(self) -> Iterable[float]:
        yield from self.samples
