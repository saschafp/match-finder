from __future__ import annotations

from matchcenter.models import Game, Schedule
from matchcenter.parsers.cup import parse_cup_schedule
from matchcenter.parsers.league import parse_league_schedule


def parse_schedule(
    html: str,
    *,
    schedule: Schedule,
) -> list[Game]:
    if schedule.kind == "league":
        return parse_league_schedule(
            html,
            schedule=schedule,
        )

    return parse_cup_schedule(
        html,
        schedule=schedule,
    )
