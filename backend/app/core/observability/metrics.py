from __future__ import annotations

import threading
import time
from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from sqlalchemy import event

Labels = Mapping[str, str]


def _label_key(labels: Labels | None) -> tuple[tuple[str, str], ...]:
    if not labels:
        return ()
    return tuple(sorted((str(key), str(value)) for key, value in labels.items()))


def _format_labels(label_key: tuple[tuple[str, str], ...]) -> str:
    if not label_key:
        return ""
    escaped = []
    for key, value in label_key:
        safe_value = value.replace("\\", "\\\\").replace('"', '\\"')
        escaped.append(f'{key}="{safe_value}"')
    values = ",".join(escaped)
    return "{" + values + "}"


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, dict[tuple[tuple[str, str], ...], float]] = defaultdict(lambda: defaultdict(float))
        self._summaries: dict[str, dict[tuple[tuple[str, str], ...], dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {"count": 0.0, "sum": 0.0, "max": 0.0})
        )

    def increment(self, name: str, labels: Labels | None = None, amount: float = 1.0) -> None:
        with self._lock:
            self._counters[name][_label_key(labels)] += amount

    def observe(self, name: str, value: float, labels: Labels | None = None) -> None:
        with self._lock:
            bucket = self._summaries[name][_label_key(labels)]
            bucket["count"] += 1
            bucket["sum"] += value
            bucket["max"] = max(bucket["max"], value)

    def render_prometheus(self) -> str:
        lines: list[str] = []
        with self._lock:
            for name, values in sorted(self._counters.items()):
                lines.append(f"# TYPE {name} counter")
                for label_key, value in sorted(values.items()):
                    lines.append(f"{name}{_format_labels(label_key)} {value:g}")
            for name, values in sorted(self._summaries.items()):
                lines.append(f"# TYPE {name} summary")
                for label_key, stats in sorted(values.items()):
                    labels = _format_labels(label_key)
                    lines.append(f"{name}_count{labels} {stats['count']:g}")
                    lines.append(f"{name}_sum{labels} {stats['sum']:g}")
                    lines.append(f"{name}_max{labels} {stats['max']:g}")
        return "\n".join(lines) + "\n"


metrics = MetricsRegistry()


def instrument_sqlalchemy(engine: Any) -> None:
    sync_engine = getattr(engine, "sync_engine", engine)
    if getattr(sync_engine, "_itam_metrics_instrumented", False):
        return

    @event.listens_for(sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool) -> None:
        context._itam_query_start = time.perf_counter()

    @event.listens_for(sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool) -> None:
        started = getattr(context, "_itam_query_start", None)
        if started is None:
            return
        metrics.observe("itam_database_query_duration_ms", (time.perf_counter() - started) * 1000)

    sync_engine._itam_metrics_instrumented = True
