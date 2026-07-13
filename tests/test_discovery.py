from __future__ import annotations

from pathlib import Path

import matchcenter as mc

FIXTURES = Path(__file__).parent / "fixtures" / "landing"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_discovers_promotion_league_schedule() -> None:
    definition = mc.CompetitionDefinition(
        key="promotion-league",
        source_key="erste-liga",
        name="Hoval Promotion League",
        kind="league",
        landing_url=(
            "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&ln=12005"
        ),
    )

    schedules = mc.discover_schedules(
        read_fixture("promotion-league.html"),
        definition=definition,
    )

    assert len(schedules) == 1

    schedule = schedules[0]

    assert schedule.key == "promotion-league"
    assert schedule.source_key == "erste-liga"
    assert schedule.competition_name == "Hoval Promotion League"
    assert schedule.section_name is None
    assert "a=msp" in schedule.url
    assert "sg=" in schedule.url


def test_discovers_three_classic_groups() -> None:
    definition = mc.CompetitionDefinition(
        key="classic",
        source_key="erste-liga",
        name="1. Liga Classic",
        kind="league",
        landing_url=(
            "https://matchcenter.el-pl.ch/default.aspx?oid=3&lng=1&s=2027&ln=12010"
        ),
    )

    schedules = mc.discover_schedules(
        read_fixture("classic.html"),
        definition=definition,
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
    assert all("a=msp" in schedule.url for schedule in schedules)
