# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Progress Logging Utilities."""

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


@dataclass
class Progress:
    """A class representing the progress of a task."""

    percent: float | None = None
    """0 - 1 progress"""

    description: str | None = None
    """Description of the progress"""

    total_items: int | None = None
    """Total number of items"""

    completed_items: int | None = None
    """Number of items completed"""


ProgressHandler = Callable[[Progress], None]
"""A function to handle progress reports."""


class ProgressTicker:
    """A class that emits progress reports incrementally."""

    _callback: ProgressHandler | None
    _description: str
    _num_total: int
    _num_complete: int

    def __init__(
        self, callback: ProgressHandler | None, num_total: int, description: str = ""
    ):
        self._callback = callback
        self._description = description
        self._num_total = num_total
        self._num_complete = 0

    def __call__(self, num_ticks: int = 1) -> None:
        """Emit progress."""
        self._num_complete += num_ticks
        if self._callback is not None:
            p = Progress(
                total_items=self._num_total,
                completed_items=self._num_complete,
                description=self._description,
            )
            if p.description:
                logger.info(
                    "%s%s/%s", p.description, str(p.completed_items), str(p.total_items)
                )
            self._callback(p)

    def done(self) -> None:
        """Mark the progress as done."""
        if self._callback is not None:
            self._callback(
                Progress(
                    total_items=self._num_total,
                    completed_items=self._num_total,
                    description=self._description,
                )
            )


def progress_ticker(
    callback: ProgressHandler | None, num_total: int, description: str = ""
) -> ProgressTicker:
    """Create a progress ticker."""
    return ProgressTicker(callback, num_total, description=description)


def progress_iterable(
    iterable: Iterable[T],
    progress: ProgressHandler | None,
    num_total: int | None = None,
    description: str = "",
) -> Iterable[T]:
    """Wrap an iterable with a progress handler. Every time an item is yielded, the progress handler will be called with the current progress."""
    if num_total is None:
        num_total = len(list(iterable))

    tick = ProgressTicker(progress, num_total, description=description)

    for item in iterable:
        tick(1)
        yield item
