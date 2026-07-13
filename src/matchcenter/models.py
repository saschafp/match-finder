from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Literal

CompetitionKind = Literal["league", "cup"]


@dataclass(frozen=True, slots=True)
class MatchcenterSource:
    key: str
    name: str
    base_url: str


@dataclass(frozen=True, slots=True)
class CompetitionDefinition:
    """
    A competition landing page from which schedule pages are discovered.
    """

    key: str
    source_key: str
    name: str
    kind: CompetitionKind
    landing_url: str


@dataclass(frozen=True, slots=True)
class Schedule:
    """
    A concrete Matchcenter page containing fixtures.
    """

    key: str
    source_key: str
    competition_name: str
    section_name: str | None
    url: str
    kind: CompetitionKind


@dataclass(frozen=True, slots=True)
class Game:
    id: str
    match_number: str | None
    date: date
    time: time | None
    home_team: str
    away_team: str
    schedule_key: str
    competition_name: str
    section_name: str | None
    details_url: str

    def to_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "matchNumber": self.match_number,
            "date": self.date.isoformat(),
            "time": (self.time.strftime("%H:%M") if self.time is not None else None),
            "homeTeam": self.home_team,
            "awayTeam": self.away_team,
            "scheduleKey": self.schedule_key,
            "competitionName": self.competition_name,
            "sectionName": self.section_name,
            "detailsUrl": self.details_url,
        }
