"""Simulated insertion strategies with undo support."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Sequence


logger = logging.getLogger(__name__)


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
        logger.debug(
            "Staging text (len=%d, final=%s, realtime=%s)",
            len(text),
            final,
            self.realtime_write,
        )
        self._staged_text = text
        if self.realtime_write or final:
            self.commit()

    def commit(self) -> None:
        logger.debug("Attempting commit via %d strategies", len(self.strategies))
        for strategy in self.strategies:
            logger.debug("Trying strategy '%s'", strategy.name)
            if strategy.insert(self._staged_text):
                self._last_strategy = strategy
                self.committed_blocks.append(self._staged_text)
                logger.debug("Strategy '%s' committed text", strategy.name)
                return
        raise RuntimeError("All insertion strategies failed.")

    def undo_last(self) -> None:
        if not self.committed_blocks:
            logger.debug("Undo requested with no committed blocks")
            return
        if self.atomic_block_undo and self._last_strategy is not None:
            logger.debug("Undoing last commit via strategy '%s'", self._last_strategy.name)
            self._last_strategy.undo()
        self.committed_blocks.pop()
        self._staged_text = ""
        self._last_strategy = None
        logger.debug("Undo complete; %d blocks remain", len(self.committed_blocks))
