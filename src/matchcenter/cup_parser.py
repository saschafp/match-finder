from __future__ import annotations

import re
from datetime import date, datetime, time
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from matchcenter.exceptions import MatchcenterParserError
from matchcenter.models import Game, Schedule

DATE_FORMAT = "%d.%m.%Y"

DATE_PATTERN = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b")

TIME_PATTERN = re.compile(r"\b(?P<hour>[01]?\d|2[0-3]):(?P<minute>[0-5]\d)\b")


def parse_cup_schedule(
    html: str,
    *,
    schedule: Schedule,
) -> list[Game]:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".list-group-item")

    if not items:
        raise MatchcenterParserError(f"No schedule items found for {schedule.key}")

    games: list[Game] = []
    current_date: date | None = None

    for item in items:
        if _is_date_heading(item):
            current_date = _parse_date_heading(item)
            continue

        if not _is_match(item):
            continue

        if current_date is None:
            raise MatchcenterParserError(
                f"Found match before date heading in {schedule.key}"
            )

        games.append(
            _parse_match(
                item=item,
                current_date=current_date,
                schedule=schedule,
            )
        )

    return games


def _is_match(item: Tag) -> bool:
    if item.name != "a":
        return False

    href = item.get("href")
    return isinstance(href, str) and "tg=" in href


def _is_date_heading(item: Tag) -> bool:
    return "sppTitel" in item.get_attribute_list("class")


def _parse_date_heading(item: Tag) -> date:
    text = _clean_text(item)
    match = DATE_PATTERN.search(text)

    if match is None:
        raise MatchcenterParserError(f"Could not parse date heading {text!r}")

    return datetime.strptime(
        match.group(0),
        DATE_FORMAT,
    ).date()


def _parse_match(
    *,
    item: Tag,
    current_date: date,
    schedule: Schedule,
) -> Game:
    teams = item.select(".col-sm-9 > .row > .col-sm-5")

    if len(teams) < 2:
        raise MatchcenterParserError(f"Could not identify both teams in {schedule.key}")

    home_team = _clean_text(teams[0])
    away_team = _clean_text(teams[1])

    time_element = item.select_one(":scope > .row > .col-sm-1")

    kickoff = (
        _parse_time(_clean_text(time_element)) if time_element is not None else None
    )

    details_url = _details_url(
        item,
        schedule=schedule,
        home_team=home_team,
        away_team=away_team,
    )

    return Game(
        id=_extract_match_id(details_url),
        match_number=None,
        date=current_date,
        time=kickoff,
        home_team=home_team,
        away_team=away_team,
        schedule_key=schedule.key,
        competition_name=schedule.competition_name,
        section_name=schedule.section_name,
        details_url=details_url,
    )


def _parse_time(value: str) -> time | None:
    match = TIME_PATTERN.search(value)

    if match is None:
        return None

    return time(
        hour=int(match.group("hour")),
        minute=int(match.group("minute")),
    )


def _details_url(
    item: Tag,
    *,
    schedule: Schedule,
    home_team: str,
    away_team: str,
) -> str:
    href = item.get("href")

    if not isinstance(href, str) or not href.strip():
        raise MatchcenterParserError(
            f"Missing details link for {home_team} vs {away_team}"
        )

    return urljoin(schedule.url, href)


def _extract_match_id(details_url: str) -> str:
    query = parse_qs(urlparse(details_url).query)
    values = query.get("tg")

    if not values or not values[0]:
        raise MatchcenterParserError(f"No tg parameter found in {details_url!r}")

    return values[0]


def _clean_text(element: Tag) -> str:
    return " ".join(element.get_text(" ", strip=True).split())
