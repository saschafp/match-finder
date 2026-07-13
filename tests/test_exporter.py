from __future__ import annotations

import json
from datetime import date, time
from pathlib import Path

import pytest

import matchcenter as mc


def make_game(
    *,
    game_id: str,
    game_date: date,
    kickoff: time | None,
    home_team: str = "Home",
    away_team: str = "Away",
    schedule_key: str = "classic-group-1",
) -> mc.Game:
    return mc.Game(
        id=game_id,
        match_number=None,
        date=game_date,
        time=kickoff,
        home_team=home_team,
        away_team=away_team,
        schedule_key=schedule_key,
        competition_name="1. Liga Classic",
        section_name="Gruppe 1",
        details_url=(
            f"https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&tg={game_id}"
        ),
    )


def test_deduplicates_identical_games() -> None:
    game = make_game(
        game_id="100",
        game_date=date(2026, 8, 1),
        kickoff=time(16, 0),
    )

    result = mc.deduplicate_games([game, game])

    assert result == [game]


def test_rejects_conflicting_duplicate_ids() -> None:
    first = make_game(
        game_id="100",
        game_date=date(2026, 8, 1),
        kickoff=time(16, 0),
        home_team="Team A",
    )

    second = make_game(
        game_id="100",
        game_date=date(2026, 8, 1),
        kickoff=time(16, 0),
        home_team="Different Team",
    )

    with pytest.raises(mc.MatchcenterExportError):
        mc.deduplicate_games([first, second])


def test_sorts_games_by_date_and_time() -> None:
    games = [
        make_game(
            game_id="3",
            game_date=date(2026, 8, 2),
            kickoff=time(15, 0),
        ),
        make_game(
            game_id="2",
            game_date=date(2026, 8, 1),
            kickoff=None,
        ),
        make_game(
            game_id="1",
            game_date=date(2026, 8, 1),
            kickoff=time(16, 0),
        ),
    ]

    result = mc.sort_games(games)

    assert [game.id for game in result] == ["1", "2", "3"]


def test_writes_games_json(tmp_path: Path) -> None:
    output_path = tmp_path / "games.json"

    games = [
        make_game(
            game_id="1",
            game_date=date(2026, 8, 1),
            kickoff=time(16, 0),
            home_team="FC Zürich U-21",
            away_team="SC Cham",
        )
    ]

    exported = mc.write_games_json(games, output_path)

    assert exported == games
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data == [
        {
            "id": "1",
            "matchNumber": None,
            "date": "2026-08-01",
            "time": "16:00",
            "homeTeam": "FC Zürich U-21",
            "awayTeam": "SC Cham",
            "scheduleKey": "classic-group-1",
            "competitionName": "1. Liga Classic",
            "sectionName": "Gruppe 1",
            "detailsUrl": (
                "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&tg=1"
            ),
        }
    ]
