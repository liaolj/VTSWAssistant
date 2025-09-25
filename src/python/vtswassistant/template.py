"""Template rendering helpers for structured output."""

from __future__ import annotations

from string import Template
from typing import Dict, Mapping, Sequence

from .llm import ActionItem, StructuredSegment


class TemplateRenderer:
    """Render structured segments using user-defined templates."""

    def __init__(self, templates: Mapping[str, str] | None = None, uncertain_tag: str = "（不确定）") -> None:
        self.templates: Dict[str, Template] = {
            name: Template(body)
            for name, body in (templates or {}).items()
        }
        if "generic" not in self.templates:
            self.templates["generic"] = Template(
                "主题：${topic}\n要点：\n${points}\n\n行动项：\n${actions}"
            )
        self.uncertain_tag = uncertain_tag

    def render(self, segment: StructuredSegment, template_name: str = "generic") -> str:
        template = self.templates.get(template_name, self.templates["generic"])
        mapping = self._build_mapping(segment)
        return template.safe_substitute(mapping).strip()

    def _build_mapping(self, segment: StructuredSegment) -> Dict[str, str]:
        mapping: Dict[str, str] = {
            "topic": segment.topic or self.uncertain_tag,
            "points": self._format_points(segment.points),
            "actions": self._format_actions(segment.actions),
        }
        for index, point in enumerate(segment.points, start=1):
            mapping[f"point_{index}"] = point
        for index, action in enumerate(segment.actions, start=1):
            summary = action.summary()
            mapping[f"action_{index}"] = summary
            mapping[f"owner_{index}"] = action.owner or self.uncertain_tag
            mapping[f"due_{index}"] = action.due or ""
            mapping[f"next_{index}"] = action.description
        return mapping

    def _format_points(self, points: Sequence[str]) -> str:
        if not points:
            return f"- {self.uncertain_tag}"
        return "\n".join(f"- {point}" for point in points)

    def _format_actions(self, actions: Sequence[ActionItem]) -> str:
        if not actions:
            return f"- {self.uncertain_tag}"
        return "\n".join(f"- {action.summary()}" for action in actions)
