from __future__ import annotations

from datetime import date, time
from pathlib import Path

import pytest

import matchcenter as mc

FIXTURES = Path(__file__).parent / "fixtures" / "schedules"


PROMOTION_LEAGUE = mc.Schedule(
    key="promotion-league",
    source_key="erste-liga",
    competition_name="Hoval Promotion League",
    section_name=None,
    url=(
        "https://matchcenter.el-pl.ch/default.aspx"
        "?oid=3&lng=1&s=2027&ln=12005"
        "&ls=25789&sg=70226&a=msp"
    ),
    kind="league",
)

CLASSIC_GROUP_1 = mc.Schedule(
    key="classic-group-1",
    source_key="erste-liga",
    competition_name="1. Liga Classic",
    section_name="Gruppe 1",
    url=(
        "https://matchcenter.el-pl.ch/default.aspx"
        "?oid=3&lng=1&s=2027&ln=12010"
        "&ls=25790&sg=70227&a=msp"
    ),
    kind="league",
)

CLASSIC_GROUP_2 = mc.Schedule(
    key="classic-group-2",
    source_key="erste-liga",
    competition_name="1. Liga Classic",
    section_name="Gruppe 2",
    url=(
        "https://matchcenter.el-pl.ch/default.aspx"
        "?oid=3&lng=1&s=2027&ln=12010"
        "&ls=25790&sg=70228&a=msp"
    ),
    kind="league",
)

CLASSIC_GROUP_3 = mc.Schedule(
    key="classic-group-3",
    source_key="erste-liga",
    competition_name="1. Liga Classic",
    section_name="Gruppe 3",
    url=(
        "https://matchcenter.el-pl.ch/default.aspx"
        "?oid=3&lng=1&s=2027&ln=12010"
        "&ls=25790&sg=70229&a=msp"
    ),
    kind="league",
)

CURRENT_CUP = mc.Schedule(
    key="classic-cup-qualification",
    source_key="erste-liga",
    competition_name="Cup-Qualifikation 1. Liga Classic",
    section_name=None,
    url=("https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&cp=5222"),
    kind="cup",
)


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("fixture_name", "schedule", "expected_count"),
    [
        ("promotion-league.html", PROMOTION_LEAGUE, 306),
        ("classic-group-1.html", CLASSIC_GROUP_1, 240),
        ("classic-group-2.html", CLASSIC_GROUP_2, 240),
        ("classic-group-3.html", CLASSIC_GROUP_3, 240),
        ("classic-cup-qualification.html", CURRENT_CUP, 20),
    ],
)
def test_parses_full_schedule(
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


def test_parses_known_promotion_league_game() -> None:
    games = mc.parse_schedule(
        read_fixture("promotion-league.html"),
        schedule=PROMOTION_LEAGUE,
    )

    game = next(game for game in games if game.id == "4314601")

    assert game.match_number == "104496"
    assert game.date == date(2026, 8, 1)
    assert game.time == time(16, 0)
    assert game.home_team == "SC Cham"
    assert game.away_team == "FC Breitenrain"
    assert game.schedule_key == "promotion-league"
    assert game.competition_name == "Hoval Promotion League"
    assert game.section_name is None
    assert "tg=4314601" in game.details_url


def test_allows_missing_league_kickoff_time() -> None:
    games = mc.parse_schedule(
        read_fixture("promotion-league.html"),
        schedule=PROMOTION_LEAGUE,
    )

    game = next(game for game in games if game.id == "4314602")

    assert game.match_number == "104497"
    assert game.date == date(2026, 8, 1)
    assert game.time is None
    assert game.home_team == "FC Paradiso"
    assert game.away_team == "FC Schaffhausen"


def test_parses_known_cup_game_and_preserves_suffixes() -> None:
    games = mc.parse_schedule(
        read_fixture("classic-cup-qualification.html"),
        schedule=CURRENT_CUP,
    )

    game = next(game for game in games if game.id == "4316161")

    assert game.match_number is None
    assert game.date == date(2026, 10, 17)
    assert game.time == time(16, 0)
    assert game.home_team == "FC Freienbach (1.)"
    assert game.away_team == "FC Wettswil-Bonstetten (1.)"
    assert game.schedule_key == "classic-cup-qualification"
    assert game.competition_name == ("Cup-Qualifikation 1. Liga Classic")
    assert game.section_name is None
    assert "tg=4316161" in game.details_url


def test_allows_missing_cup_kickoff_time() -> None:
    games = mc.parse_schedule(
        read_fixture("classic-cup-qualification.html"),
        schedule=CURRENT_CUP,
    )

    game = next(game for game in games if game.id == "4316147")

    assert game.date == date(2026, 10, 17)
    assert game.time is None
    assert game.home_team == "FC Solothurn (1.)"
    assert game.away_team == "FC Echallens Région (1.)"


@pytest.mark.parametrize(
    "schedule",
    [
        PROMOTION_LEAGUE,
        CURRENT_CUP,
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
