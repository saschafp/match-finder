from __future__ import annotations

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Playwright,
    sync_playwright,
)

from matchcenter.clients.base import MatchcenterClient
from matchcenter.exceptions import MatchcenterFetchError
from matchcenter.models import Schedule


class PlaywrightClient(MatchcenterClient):
    def __init__(
        self,
        timeout: float = 30.0,
        *,
        headless: bool = True,
    ) -> None:
        self.timeout_ms = int(timeout * 1000)
        self.headless = headless

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> PlaywrightClient:
        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
        )

        self._context = self._browser.new_context(
            locale="de-CH",
            timezone_id="Europe/Zurich",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept-Language": "de-CH,de;q=0.9,en;q=0.8",
            },
        )

        return self

    def fetch_html(
        self,
        url: str,
        *,
        wait_for: str | None = None,
    ) -> str:
        if self._context is None:
            raise RuntimeError("PlaywrightClient must be used as a context manager")

        page = self._context.new_page()

        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            if response is None:
                raise MatchcenterFetchError(f"No HTTP response received for {url}")

            if not response.ok:
                raise MatchcenterFetchError(
                    f"Request for {url} returned HTTP {response.status}"
                )

            if wait_for is not None:
                page.wait_for_selector(
                    wait_for,
                    timeout=self.timeout_ms,
                )

            return page.content()

        except MatchcenterFetchError:
            raise
        except Exception as exc:
            raise MatchcenterFetchError(f"Could not fetch {url}: {exc}") from exc
        finally:
            page.close()

    def fetch_schedule(self, schedule: Schedule) -> str:
        return self.fetch_html(
            schedule.url,
            wait_for=".list-group-item",
        )

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
            self._context = None

        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()
