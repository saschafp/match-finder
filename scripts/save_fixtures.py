from __future__ import annotations

from pathlib import Path

import matchcenter as mc

FIXTURE_ROOT = Path("tests/fixtures")

definitions = [
    mc.CompetitionDefinition(
        key="promotion-league",
        source_key="erste-liga",
        name="Hoval Promotion League",
        kind="league",
        landing_url=(
            "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&ln=12005"
        ),
    ),
    mc.CompetitionDefinition(
        key="classic",
        source_key="erste-liga",
        name="1. Liga Classic",
        kind="league",
        landing_url=(
            "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&ln=12010"
        ),
    ),
]


def write_html(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print(f"Saved {path}")


def main() -> None:
    with mc.MatchcenterClient() as client:
        for definition in definitions:
            landing_html = client.fetch_html(
                definition.landing_url,
                wait_for="a[href]",
            )

            write_html(
                FIXTURE_ROOT / "landing" / f"{definition.key}.html",
                landing_html,
            )

            schedules = mc.discover_schedules(
                landing_html,
                definition=definition,
            )

            for schedule in schedules:
                schedule_html = client.fetch_schedule(schedule)

                write_html(
                    FIXTURE_ROOT / "schedules" / f"{schedule.key}.html",
                    schedule_html,
                )


if __name__ == "__main__":
    main()
