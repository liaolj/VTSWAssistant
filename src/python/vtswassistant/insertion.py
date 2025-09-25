"""Simulated insertion strategies with undo support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class InsertionStrategy:
    """Simple representation of a text insertion strategy."""

    name: str
    max_length: int | None = None
    fail: bool = False
    inserted: List[str] = field(default_factory=list)

    def insert(self, text: str) -> bool:
        if self.fail:
            return False
        if self.max_length is not None and len(text) > self.max_length:
            return False
        self.inserted.append(text)
        return True

    def undo(self) -> None:
        if self.inserted:
            self.inserted.pop()


@dataclass
class InsertionController:
    strategies: Sequence[InsertionStrategy]
    realtime_write: bool = False
    atomic_block_undo: bool = True

    committed_blocks: List[str] = field(default_factory=list)
    _last_strategy: InsertionStrategy | None = None
    _staged_text: str = ""

    def stage(self, text: str, final: bool = False) -> None:
        self._staged_text = text
        if self.realtime_write or final:
            self.commit()

    def commit(self) -> None:
        for strategy in self.strategies:
            if strategy.insert(self._staged_text):
                self._last_strategy = strategy
                self.committed_blocks.append(self._staged_text)
                return
        raise RuntimeError("All insertion strategies failed.")

    def undo_last(self) -> None:
        if not self.committed_blocks:
            return
        if self.atomic_block_undo and self._last_strategy is not None:
            self._last_strategy.undo()
        self.committed_blocks.pop()
        self._staged_text = ""
        self._last_strategy = None
