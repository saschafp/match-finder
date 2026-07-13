from __future__ import annotations

from pathlib import Path

import pytest

import matchcenter as mc

FIXTURES = Path(__file__).parent / "fixtures" / "landing"


PROMOTION_LEAGUE = mc.CompetitionDefinition(
    key="promotion-league",
    source_key="erste-liga",
    name="Hoval Promotion League",
    kind="league",
    landing_url=(
        "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&ln=12005"
    ),
)

CLASSIC = mc.CompetitionDefinition(
    key="classic",
    source_key="erste-liga",
    name="1. Liga Classic",
    kind="league",
    landing_url=(
        "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&ln=12010"
    ),
)

CURRENT_CUP = mc.CompetitionDefinition(
    key="classic-cup-qualification",
    source_key="erste-liga",
    name="Cup-Qualifikation 1. Liga Classic",
    kind="cup",
    landing_url=(
        "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&cp=5222"
    ),
)

HISTORICAL_CUP = mc.CompetitionDefinition(
    key="classic-cup-qualification-2026",
    source_key="erste-liga",
    name="Cup-Qualifikation 1. Liga Classic",
    kind="cup",
    landing_url=(
        "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2026&cp=5055"
    ),
)


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_discovers_promotion_league_schedule() -> None:
    schedules = mc.discover_schedules(
        read_fixture("promotion-league.html"),
        definition=PROMOTION_LEAGUE,
    )

    assert len(schedules) == 1

    schedule = schedules[0]

    assert schedule.key == "promotion-league"
    assert schedule.source_key == "erste-liga"
    assert schedule.competition_name == "Hoval Promotion League"
    assert schedule.section_name is None
    assert schedule.kind == "league"
    assert "a=msp" in schedule.url
    assert "sg=" in schedule.url


def test_discovers_three_classic_groups() -> None:
    schedules = mc.discover_schedules(
        read_fixture("classic.html"),
        definition=CLASSIC,
    )

    assert [schedule.key for schedule in schedules] == [
        "classic-group-1",
        "classic-group-2",
        "classic-group-3",
    ]

    assert [schedule.section_name for schedule in schedules] == [
        "Gruppe 1",
        "Gruppe 2",
        "Gruppe 3",
    ]

    assert all(schedule.source_key == "erste-liga" for schedule in schedules)
    assert all(schedule.competition_name == "1. Liga Classic" for schedule in schedules)
    assert all(schedule.kind == "league" for schedule in schedules)
    assert all("a=msp" in schedule.url for schedule in schedules)


def test_discovers_current_cup_schedule() -> None:
    schedules = mc.discover_schedules(
        read_fixture("classic-cup-qualification.html"),
        definition=CURRENT_CUP,
    )

    assert len(schedules) == 1

    schedule = schedules[0]

    assert schedule.key == "classic-cup-qualification"
    assert schedule.source_key == "erste-liga"
    assert schedule.competition_name == ("Cup-Qualifikation 1. Liga Classic")
    assert schedule.section_name is None
    assert schedule.kind == "cup"
    assert schedule.url == CURRENT_CUP.landing_url


def test_discovers_historical_cup_schedule() -> None:
    schedules = mc.discover_schedules(
        read_fixture("classic-cup-qualification-2026.html"),
        definition=HISTORICAL_CUP,
    )

    assert len(schedules) == 1

    schedule = schedules[0]

    assert schedule.key == "classic-cup-qualification-2026"
    assert schedule.source_key == "erste-liga"
    assert schedule.competition_name == ("Cup-Qualifikation 1. Liga Classic")
    assert schedule.section_name is None
    assert schedule.kind == "cup"
    assert schedule.url == HISTORICAL_CUP.landing_url


def test_rejects_cup_page_without_games() -> None:
    html = """
    <!doctype html>
    <html lang="de">
        <body>
            <div class="list-group">
                <div class="list-group-item">
                    No published games
                </div>
            </div>
        </body>
    </html>
    """

    with pytest.raises(
        mc.MatchcenterDiscoveryError,
        match="No cup games found",
    ):
        mc.discover_schedules(
            html,
            definition=CURRENT_CUP,
        )
