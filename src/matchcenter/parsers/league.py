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

MATCH_NUMBER_PATTERN = re.compile(
    r"Spielnummer\s*:?\s*(?P<number>\d+)",
    re.IGNORECASE,
)


def parse_league_schedule(
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

        match_row = item.select_one(".spiel")

        if match_row is None:
            continue

        if current_date is None:
            raise MatchcenterParserError(
                f"Found match before date heading in {schedule.key}"
            )

        games.append(
            _parse_match(
                item=item,
                match_row=match_row,
                current_date=current_date,
                schedule=schedule,
            )
        )

    return games


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
    match_row: Tag,
    current_date: date,
    schedule: Schedule,
) -> Game:
    home_team = _required_text(
        match_row,
        ".teamA",
        field_name="home team",
    )

    away_team = _required_text(
        match_row,
        ".teamB",
        field_name="away team",
    )

    details_url = _details_url(
        item,
        schedule=schedule,
        home_team=home_team,
        away_team=away_team,
    )

    return Game(
        id=_extract_match_id(details_url),
        match_number=_parse_match_number(match_row),
        date=current_date,
        time=_parse_time(match_row),
        home_team=home_team,
        away_team=away_team,
        schedule_key=schedule.key,
        competition_name=schedule.competition_name,
        section_name=schedule.section_name,
        details_url=details_url,
    )


def _parse_time(match_row: Tag) -> time | None:
    element = match_row.select_one(".time")

    if element is None:
        return None

    match = TIME_PATTERN.search(_clean_text(element))

    if match is None:
        return None

    return time(
        hour=int(match.group("hour")),
        minute=int(match.group("minute")),
    )


def _parse_match_number(match_row: Tag) -> str | None:
    element = match_row.select_one(".spielInfo")

    if element is None:
        return None

    match = MATCH_NUMBER_PATTERN.search(_clean_text(element))

    if match is None:
        return None

    return match.group("number")


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


def _required_text(
    parent: Tag,
    selector: str,
    *,
    field_name: str,
) -> str:
    element = parent.select_one(selector)

    if element is None:
        raise MatchcenterParserError(f"Missing {field_name} element: {selector}")

    value = _clean_text(element)

    if not value:
        raise MatchcenterParserError(f"Empty {field_name} value")

    return value


def _clean_text(element: Tag) -> str:
    return " ".join(element.get_text(" ", strip=True).split())
