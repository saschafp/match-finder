from __future__ import annotations

from pathlib import Path

import matchcenter as mc

OUTPUT_PATH = Path("data/games.json")


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
]


def main() -> None:
    games: list[mc.Game] = []

    with mc.MatchcenterClient() as client:
        for competition in competitions:
            print(f"Discovering {competition.name}...")

            landing_html = client.fetch_html(
                competition.landing_url,
                wait_for="a[href]",
            )

            schedules = mc.discover_schedules(
                landing_html,
                definition=competition,
            )

            for schedule in schedules:
                print(f"Fetching {schedule.key}...")

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

    print(f"Wrote {len(exported_games)} games to {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
