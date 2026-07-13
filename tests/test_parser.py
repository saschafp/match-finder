from __future__ import annotations

from datetime import date, time
from pathlib import Path

import pytest

import matchcenter as mc

FIXTURES = Path(__file__).parent / "fixtures"


LEAGUE_SCHEDULE = mc.Schedule(
    key="league-group-1",
    source_key="association",
    competition_name="League",
    section_name="Gruppe 1",
    url="https://example.test/league?a=msp",
    kind="league",
)

CUP_SCHEDULE = mc.Schedule(
    key="cup",
    source_key="association",
    competition_name="Cup",
    section_name=None,
    url="https://example.test/cup",
    kind="cup",
)


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("fixture_name", "schedule", "expected_count"),
    [
        ("league-schedule.html", LEAGUE_SCHEDULE, 2),
        ("cup.html", CUP_SCHEDULE, 3),
    ],
)
def test_parses_schedule(
    fixture_name: str,
    schedule: mc.Schedule,
    expected_count: int,
) -> None:
    games = mc.parse_schedule(
        read_fixture(fixture_name),
        schedule=schedule,
    )

    assert len(games) == expected_count
    assert len({game.id for game in games}) == expected_count

    assert all(game.schedule_key == schedule.key for game in games)
    assert all(game.competition_name == schedule.competition_name for game in games)
    assert all(game.section_name == schedule.section_name for game in games)
    assert all(game.home_team for game in games)
    assert all(game.away_team for game in games)
    assert all(game.details_url.startswith("https://") for game in games)


def test_parses_known_league_game() -> None:
    games = mc.parse_schedule(
        read_fixture("league-schedule.html"),
        schedule=LEAGUE_SCHEDULE,
    )

    game = next(game for game in games if game.id == "1001")

    assert game.match_number == "50001"
    assert game.date == date(2026, 8, 1)
    assert game.time == time(16, 0)
    assert game.home_team == "Home Team"
    assert game.away_team == "Away Team"
    assert game.schedule_key == "league-group-1"
    assert game.competition_name == "League"
    assert game.section_name == "Gruppe 1"
    assert "tg=1001" in game.details_url


def test_allows_missing_league_kickoff_time() -> None:
    games = mc.parse_schedule(
        read_fixture("league-schedule.html"),
        schedule=LEAGUE_SCHEDULE,
    )

    game = next(game for game in games if game.id == "1002")

    assert game.match_number == "50002"
    assert game.date == date(2026, 8, 1)
    assert game.time is None
    assert game.home_team == "Second Home Team"
    assert game.away_team == "Second Away Team"


def test_parses_known_cup_game_and_preserves_suffixes() -> None:
    games = mc.parse_schedule(
        read_fixture("cup.html"),
        schedule=CUP_SCHEDULE,
    )

    game = next(game for game in games if game.id == "2001")

    assert game.match_number is None
    assert game.date == date(2026, 10, 17)
    assert game.time == time(16, 0)
    assert game.home_team == "Home Club (1.)"
    assert game.away_team == "Away Club (1.)"
    assert game.schedule_key == "cup"
    assert game.competition_name == "Cup"
    assert game.section_name is None
    assert "tg=2001" in game.details_url


def test_allows_missing_cup_kickoff_time() -> None:
    games = mc.parse_schedule(
        read_fixture("cup.html"),
        schedule=CUP_SCHEDULE,
    )

    game = next(game for game in games if game.id == "2002")

    assert game.date == date(2026, 10, 17)
    assert game.time is None
    assert game.home_team == "Second Home Club (1.)"
    assert game.away_team == "Second Away Club (1.)"


def test_updates_date_after_new_heading() -> None:
    games = mc.parse_schedule(
        read_fixture("cup.html"),
        schedule=CUP_SCHEDULE,
    )

    game = next(game for game in games if game.id == "2003")

    assert game.date == date(2026, 10, 18)
    assert game.time == time(14, 30)
    assert game.home_team == "Sunday Home Club (1.)"
    assert game.away_team == "Sunday Away Club (1.)"


@pytest.mark.parametrize(
    "schedule",
    [
        LEAGUE_SCHEDULE,
        CUP_SCHEDULE,
    ],
)
def test_rejects_html_without_schedule_items(
    schedule: mc.Schedule,
) -> None:
    html = """
    <!doctype html>
    <html lang="de">
      <body>
        <main>No fixtures found.</main>
      </body>
    </html>
    """

    with pytest.raises(
        mc.MatchcenterParserError,
        match="No schedule items found",
    ):
        mc.parse_schedule(
            html,
            schedule=schedule,
        )
