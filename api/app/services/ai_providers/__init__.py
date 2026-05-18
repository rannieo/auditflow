"""AI summary providers.

A provider takes a ``BatchMetrics`` (aggregate counts + friendly failure
labels, never raw record values) and returns a plain-English summary.

The ``BatchMetrics`` dataclass is the only thing reachable inside a
provider — adding any field that could carry PII requires a deliberate
code change here.
"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class BatchMetrics:
    filename: str
    total: int
    passed: int
    failed: int
    duplicate: int
    top_reasons: list[str] = field(default_factory=list)


class AiProvider(Protocol):
    """Plain-English summarizer over aggregate batch metrics."""

    name: str

    def summarize(self, metrics: BatchMetrics) -> str: ...


__all__ = ["AiProvider", "BatchMetrics"]
