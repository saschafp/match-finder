from __future__ import annotations

import json
import subprocess
import time

from matchcenter.clients.base import MatchcenterClient
from matchcenter.exceptions import MatchcenterFetchError
from matchcenter.models import Schedule


class SafariClient(MatchcenterClient):
    def __init__(
        self,
        timeout: float = 30.0,
        *,
        poll_interval: float = 0.25,
    ) -> None:
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._window_id: int | None = None

    def __enter__(self) -> SafariClient:
        result = _run_applescript(
            """
            tell application "Safari"
                activate
                make new document
                return id of front window
            end tell
            """
        )

        try:
            self._window_id = int(result)
        except ValueError as exc:
            raise MatchcenterFetchError(
                f"Could not determine Safari window ID: {result!r}"
            ) from exc

        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()

    def fetch_html(
        self,
        url: str,
        *,
        wait_for: str | None = None,
    ) -> str:
        window_id = self._require_window_id()

        self._navigate(
            window_id=window_id,
            url="about:blank",
        )

        self._navigate(
            window_id=window_id,
            url=url,
        )

        self._wait_until_ready(
            window_id=window_id,
            wait_for=wait_for,
            url=url,
        )

        html = _run_applescript(
            """
            on run argv
                set windowId to item 1 of argv as integer

                tell application "Safari"
                    return do JavaScript ¬
                        "document.documentElement.outerHTML" ¬
                        in current tab of window id windowId
                end tell
            end run
            """,
            str(window_id),
        )

        if not html.strip():
            raise MatchcenterFetchError(f"Safari returned empty HTML for {url}")

        return html

    def fetch_schedule(
        self,
        schedule: Schedule,
    ) -> str:
        return self.fetch_html(
            schedule.url,
            wait_for=".list-group-item",
        )

    def close(self) -> None:
        if self._window_id is None:
            return

        try:
            _run_applescript(
                """
                on run argv
                    set windowId to item 1 of argv as integer

                    tell application "Safari"
                        close window id windowId
                    end tell
                end run
                """,
                str(self._window_id),
            )
        finally:
            self._window_id = None

    def _require_window_id(self) -> int:
        if self._window_id is None:
            raise RuntimeError("SafariClient must be used as a context manager")

        return self._window_id

    def _navigate(
        self,
        *,
        window_id: int,
        url: str,
    ) -> None:
        _run_applescript(
            """
            on run argv
                set windowId to item 1 of argv as integer
                set targetUrl to item 2 of argv

                tell application "Safari"
                    set URL of current tab of window id windowId to targetUrl
                end tell
            end run
            """,
            str(window_id),
            url,
        )

        deadline = time.monotonic() + self.timeout

        while time.monotonic() < deadline:
            current_url = _run_applescript(
                """
                on run argv
                    set windowId to item 1 of argv as integer

                    tell application "Safari"
                        return URL of current tab of window id windowId
                    end tell
                end run
                """,
                str(window_id),
            )

            if current_url == url:
                return

            time.sleep(self.poll_interval)

        raise MatchcenterFetchError(
            f"Timed out waiting for Safari to navigate to {url}"
        )

    def _wait_until_ready(
        self,
        *,
        window_id: int,
        wait_for: str | None,
        url: str,
    ) -> None:
        if wait_for is None:
            return

        deadline = time.monotonic() + self.timeout
        javascript = f"document.querySelector({json.dumps(wait_for)}) !== null"

        while time.monotonic() < deadline:
            result = _run_applescript(
                """
                on run argv
                    set windowId to item 1 of argv as integer
                    set javascriptCode to item 2 of argv

                    tell application "Safari"
                        return do JavaScript javascriptCode ¬
                            in current tab of window id windowId
                    end tell
                end run
                """,
                str(window_id),
                javascript,
            )

            if result.lower() == "true":
                return

            time.sleep(self.poll_interval)

        raise MatchcenterFetchError(f"Timed out waiting for {wait_for!r} at {url}")


def _run_applescript(
    script: str,
    *arguments: str,
) -> str:
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                script,
                *arguments,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise MatchcenterFetchError(
            "SafariClient requires macOS and osascript"
        ) from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip()

        raise MatchcenterFetchError(f"Safari automation failed: {message}") from exc

    return result.stdout.strip()
