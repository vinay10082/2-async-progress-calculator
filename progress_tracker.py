import asyncio
import os
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional


def _get_polling_interval_ms() -> int:
    return int(os.environ.get("PROGRESS_POLLING_INTERVAL_MS", "100"))


@dataclass
class ProgressSnapshot:
    total: int
    completed: int
    failed: int
    pending: int
    elapsed_seconds: float

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 100.0
        return round((self.completed + self.failed) / self.total * 100, 2)


class ProgressTracker:
    """Tracks resolved vs. pending asyncio Futures/Tasks and yields live progress."""

    def __init__(self, futures: Iterable["asyncio.Future"], polling_interval_ms: Optional[int] = None):
        self._futures = list(futures)
        self._polling_interval_ms = (
            polling_interval_ms if polling_interval_ms is not None else _get_polling_interval_ms()
        )
        self._start_time: Optional[float] = None

    @property
    def total(self) -> int:
        return len(self._futures)

    def snapshot(self) -> ProgressSnapshot:
        completed = 0
        failed = 0
        for fut in self._futures:
            if fut.done():
                if fut.cancelled() or fut.exception() is not None:
                    failed += 1
                else:
                    completed += 1
        pending = self.total - completed - failed
        elapsed = time.monotonic() - self._start_time if self._start_time is not None else 0.0
        return ProgressSnapshot(
            total=self.total,
            completed=completed,
            failed=failed,
            pending=pending,
            elapsed_seconds=round(elapsed, 3),
        )

    def is_done(self) -> bool:
        return all(fut.done() for fut in self._futures)

    async def track(self, on_update: Optional[Callable[[ProgressSnapshot], None]] = None) -> ProgressSnapshot:
        """Poll the bound futures at the configured interval until all resolve."""
        self._start_time = time.monotonic()
        interval_seconds = self._polling_interval_ms / 1000

        snapshot = self.snapshot()
        if on_update:
            on_update(snapshot)

        while not self.is_done():
            await asyncio.sleep(interval_seconds)
            snapshot = self.snapshot()
            if on_update:
                on_update(snapshot)

        return snapshot
