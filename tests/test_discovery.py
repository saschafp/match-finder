from __future__ import annotations

from pathlib import Path

import pytest

import matchcenter as mc

FIXTURES = Path(__file__).parent / "fixtures"


LEAGUE = mc.CompetitionDefinition(
    key="league",
    source_key="association",
    name="League",
    kind="league",
    landing_url="https://example.test/league",
)

CUP = mc.CompetitionDefinition(
    key="cup",
    source_key="association",
    name="Cup",
    kind="cup",
    landing_url="https://example.test/cup",
)


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_discovers_three_league_groups() -> None:
    schedules = mc.discover_schedules(
        read_fixture("league-landing.html"),
        definition=LEAGUE,
    )

    assert [schedule.key for schedule in schedules] == [
        "league-group-1",
        "league-group-2",
        "league-group-3",
    ]

    assert [schedule.section_name for schedule in schedules] == [
        "Gruppe 1",
        "Gruppe 2",
        "Gruppe 3",
    ]

    assert all(schedule.source_key == "association" for schedule in schedules)
    assert all(schedule.competition_name == "League" for schedule in schedules)
    assert all(schedule.kind == "league" for schedule in schedules)
    assert all("a=msp" in schedule.url for schedule in schedules)


def test_discovers_cup_landing_page_as_schedule() -> None:
    schedules = mc.discover_schedules(
        read_fixture("cup.html"),
        definition=CUP,
    )

    assert len(schedules) == 1

    schedule = schedules[0]

    assert schedule.key == "cup"
    assert schedule.source_key == "association"
    assert schedule.competition_name == "Cup"
    assert schedule.section_name is None
    assert schedule.kind == "cup"
    assert schedule.url == CUP.landing_url


def test_rejects_league_page_without_schedule_links() -> None:
    html = """
    <!doctype html>
    <html lang="de">
      <body>
        <main>No schedule links</main>
      </body>
    </html>
    """

    with pytest.raises(
        mc.MatchcenterDiscoveryError,
        match="No Spielplan links found",
    ):
        mc.discover_schedules(
            html,
            definition=LEAGUE,
        )


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
            definition=CUP,
        )
