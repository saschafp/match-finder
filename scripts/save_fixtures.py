from __future__ import annotations

from pathlib import Path

import matchcenter as mc

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "tests" / "fixtures"


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
    mc.CompetitionDefinition(
        key="classic-cup-qualification",
        source_key="erste-liga",
        name="Cup-Qualifikation 1. Liga Classic",
        kind="cup",
        landing_url=(
            "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&cp=5222"
        ),
    ),
    mc.CompetitionDefinition(
        key="classic-cup-qualification-2026",
        source_key="erste-liga",
        name="Cup-Qualifikation 1. Liga Classic",
        kind="cup",
        landing_url=(
            "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2026&cp=5055"
        ),
    ),
]


def write_html(path: Path, html: str) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        html,
        encoding="utf-8",
    )

    print(f"Saved {path}")


def main() -> None:
    with mc.MatchcenterClient() as client:
        for definition in definitions:
            print(f"Fetching {definition.key}...")

            landing_html = client.fetch_html(
                definition.landing_url,
                wait_for=".list-group-item",
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
                if schedule.url == definition.landing_url:
                    schedule_html = landing_html
                else:
                    schedule_html = client.fetch_schedule(schedule)

                write_html(
                    FIXTURE_ROOT / "schedules" / f"{schedule.key}.html",
                    schedule_html,
                )


if __name__ == "__main__":
    main()
