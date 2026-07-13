from __future__ import annotations

from matchcenter.cup_parser import parse_cup_schedule
from matchcenter.league_parser import parse_league_schedule
from matchcenter.models import Game, Schedule


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
