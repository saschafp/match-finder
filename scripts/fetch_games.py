from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matchcenter as mc

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "games.json"
METADATA_PATH = OUTPUT_PATH.with_name("metadata.json")


competitions = [
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
        key="axa-womens-super-league",
        source_key="sfv",
        name="AXA Women's Super League",
        kind="league",
        landing_url=(
            "https://matchcenter.football.ch/default.aspx?oid=1&lng=1&s=2027&ln=21011"
        ),
    ),
    mc.CompetitionDefinition(
        key="axa-womens-cup",
        source_key="sfv",
        name="AXA Women's Cup",
        kind="cup",
        landing_url=(
            "https://matchcenter.football.ch/default.aspx?oid=1&lng=1&s=2027&cp=5216"
        ),
    ),
]


def write_metadata(game_count: int) -> None:
    metadata = {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "gameCount": game_count,
    }

    METADATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    games: list[mc.Game] = []

    with mc.SafariClient() as client:
        for definition in competitions:
            print(f"Discovering {definition.name}...")

            landing_html = client.fetch_html(
                definition.landing_url,
                wait_for=".list-group-item",
            )

            schedules = mc.discover_schedules(
                landing_html,
                definition=definition,
            )

            for schedule in schedules:
                print(f"Fetching {schedule.key}...")

                if schedule.url == definition.landing_url:
                    schedule_html = landing_html
                else:
                    schedule_html = client.fetch_schedule(schedule)

                parsed_games = mc.parse_schedule(
                    schedule_html,
                    schedule=schedule,
                )

                print(f"  {len(parsed_games)} games")
                games.extend(parsed_games)

    exported_games = mc.write_games_json(
        games,
        OUTPUT_PATH,
    )

    write_metadata(len(exported_games))

    print(f"Wrote {len(exported_games)} games to {OUTPUT_PATH}")
    print(f"Wrote metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()
