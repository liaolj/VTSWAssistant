"""Rule-based structured summariser mimicking the OpenRouter workflow."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ActionItem:
    """Represents an action item extracted from the transcript."""

    owner: str
    description: str
    due: str | None = None

    def summary(self) -> str:
        due_part = f"｜截止：{self.due}" if self.due else ""
        return f"负责人：{self.owner}｜下一步：{self.description}{due_part}".strip("｜")


@dataclass(slots=True)
class StructuredSegment:
    topic: str
    points: Sequence[str]
    actions: Sequence[ActionItem]


class StructuredLLMFormatter:
    """A lightweight deterministic formatter used for unit tests."""

    def __init__(self, uncertain_tag: str = "（不确定）") -> None:
        self.uncertain_tag = uncertain_tag

    def structure(self, transcript: str) -> StructuredSegment:
        cleaned = self._normalise_text(transcript)
        logger.debug("Structuring transcript (len=%d)", len(cleaned))
        sentences = [s for s in self._split_sentences(cleaned) if s]
        if not sentences:
            logger.debug("Transcript empty after normalisation; returning uncertain segment")
            return StructuredSegment(topic=self.uncertain_tag, points=(), actions=())

        topic = self._extract_topic(sentences)
        points = self._extract_points(sentences, topic)
        actions = self._extract_actions(sentences)
        logger.debug(
            "Structured result topic='%s' with %d points and %d actions",
            topic,
            len(points),
            len(actions),
        )

        if not points:
            points = (cleaned or self.uncertain_tag,)

        return StructuredSegment(topic=topic, points=points, actions=actions)

    # ------------------------------------------------------------------
    def _normalise_text(self, transcript: str) -> str:
        text = transcript.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _split_sentences(self, text: str) -> Iterable[str]:
        logger.debug("Splitting transcript into sentences")
        for sentence in re.split(r"[。！？!?.]+", text):
            trimmed = sentence.strip(" 。,，；;:：")
            if trimmed:
                yield trimmed

    def _extract_topic(self, sentences: Sequence[str]) -> str:
        logger.debug("Extracting topic from %d sentences", len(sentences))
        for sentence in sentences:
            if "主题" in sentence:
                return sentence
        return sentences[0][:20]

    def _extract_points(self, sentences: Sequence[str], topic: str) -> Sequence[str]:
        points: List[str] = []
        logger.debug("Extracting points (excluding topic '%s')", topic)
        for sentence in sentences:
            if sentence == topic:
                continue
            points.append(sentence)
        return points

    def _extract_actions(self, sentences: Sequence[str]) -> Sequence[ActionItem]:
        actions: List[ActionItem] = []
        logger.debug("Extracting action items")
        for sentence in sentences:
            if "需要" in sentence or "安排" in sentence or "负责" in sentence:
                owner, description = self._split_owner_and_desc(sentence)
                actions.append(ActionItem(owner=owner, description=description, due=self._detect_due(sentence)))
        return actions

    def _split_owner_and_desc(self, sentence: str) -> tuple[str, str]:
        match = re.search(r"([\w\u4e00-\u9fa5]{1,8})(?=负责|需要|安排)", sentence)
        if match:
            owner = match.group(1)
            remainder = sentence[match.end():].lstrip("：:，, ")
            description = remainder or sentence
        else:
            after = re.search(
                r"(?:负责|需要|安排)([\w\u4e00-\u9fa5]{1,8}?)(?=并|和|且|及|，|,|。|\s|$)",
                sentence,
            )
            if after:
                owner = after.group(1)
                remainder = sentence[after.end():].lstrip("：:，, ")
                description = remainder or sentence
            else:
                owner = self.uncertain_tag
                description = sentence
        logger.debug("Parsed action owner='%s' description='%s'", owner, description)
        return owner, description

    def _detect_due(self, sentence: str) -> str | None:
        due_match = re.search(r"(下周[一二三四五六日天]?|明天|后天|今天|本周)", sentence)
        if due_match:
            logger.debug("Detected due date '%s'", due_match.group(1))
            return due_match.group(1)
        return None
