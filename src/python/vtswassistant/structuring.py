"""Utilities for merging structured text across VAD segments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class StructuredDraftMerger:
    """Merges structured text according to the configured merge policy."""

    merge_policy: str = "replace-last-unit"
    _segments: List[str] = field(default_factory=list)
    _last_segment_id: int | None = None

    def reset(self) -> None:
        self._segments.clear()
        self._last_segment_id = None

    def merge(self, segment_id: int, text: str) -> str:
        if self.merge_policy == "replace-last-unit" and self._last_segment_id == segment_id:
            if self._segments:
                self._segments[-1] = text
        else:
            self._segments.append(text)
            self._last_segment_id = segment_id
        return "\n\n".join(self._segments)

    @property
    def aggregated_text(self) -> str:
        return "\n\n".join(self._segments)
