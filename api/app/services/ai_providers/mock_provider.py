"""Deterministic summary built from aggregate metrics. No external calls."""

from . import BatchMetrics


class MockProvider:
    name = "mock"

    def summarize(self, metrics: BatchMetrics) -> str:
        if metrics.total == 0:
            return "This batch contains no records."

        parts = [f"This batch contains {metrics.total} record(s)."]

        needs_review = metrics.failed + metrics.duplicate
        if needs_review == 0:
            parts.append("All records passed validation.")
            parts.append(
                "Recommended action: this batch is safe to sync to "
                "downstream systems."
            )
            return " ".join(parts)

        if metrics.top_reasons:
            reasons = ", ".join(metrics.top_reasons)
            parts.append(
                f"{needs_review} record(s) require review due to {reasons}."
            )
        else:
            parts.append(f"{needs_review} record(s) require review.")

        parts.append(
            f"Breakdown: {metrics.passed} passed, {metrics.failed} failed, "
            f"{metrics.duplicate} duplicate."
        )
        parts.append(
            "Recommended action: clean failed records before syncing to "
            "downstream systems."
        )
        return " ".join(parts)
