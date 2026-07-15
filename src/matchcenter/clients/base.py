from __future__ import annotations

from typing import Protocol, Self

from matchcenter.models import Schedule


class MatchcenterClient(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None: ...

    def fetch_html(
        self,
        url: str,
        *,
        wait_for: str | None = None,
    ) -> str: ...

    def fetch_schedule(
        self,
        schedule: Schedule,
    ) -> str: ...
