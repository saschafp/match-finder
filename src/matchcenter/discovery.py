from __future__ import annotations

import re
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from matchcenter.exceptions import MatchcenterDiscoveryError
from matchcenter.models import CompetitionDefinition, Schedule

GROUP_PATTERN = re.compile(
    r"\bGruppe\s+(?P<number>\d+)\b",
    re.IGNORECASE,
)


def discover_schedules(
    html: str,
    *,
    definition: CompetitionDefinition,
) -> list[Schedule]:
    if definition.kind == "league":
        return _discover_league_schedules(
            html,
            definition=definition,
        )

    return _discover_cup_schedules(
        html,
        definition=definition,
    )


def _discover_league_schedules(
    html: str,
    *,
    definition: CompetitionDefinition,
) -> list[Schedule]:
    soup = BeautifulSoup(html, "html.parser")

    schedules: list[Schedule] = []
    seen_urls: set[str] = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href")

        if not isinstance(href, str):
            continue

        url = urljoin(definition.landing_url, href)
        query = parse_qs(urlparse(url).query)

        if query.get("a") != ["msp"]:
            continue

        if url in seen_urls:
            continue

        context = _context_text(anchor)
        group_match = GROUP_PATTERN.search(context)

        if group_match is None:
            schedule_key = definition.key
            section_name = None
        else:
            group_number = int(group_match.group("number"))
            schedule_key = f"{definition.key}-group-{group_number}"
            section_name = f"Gruppe {group_number}"

        schedules.append(
            Schedule(
                key=schedule_key,
                source_key=definition.source_key,
                competition_name=definition.name,
                section_name=section_name,
                url=url,
            )
        )

        seen_urls.add(url)

    if not schedules:
        raise MatchcenterDiscoveryError(
            f"No Spielplan links found for {definition.key}"
        )

    return sorted(
        schedules,
        key=lambda schedule: (
            schedule.section_name is None,
            schedule.section_name or "",
        ),
    )


def _discover_cup_schedules(
    html: str,
    *,
    definition: CompetitionDefinition,
) -> list[Schedule]:
    raise MatchcenterDiscoveryError(
        f"Cup discovery is not implemented for {definition.key}"
    )


def _context_text(anchor: Tag) -> str:
    values = [_clean_text(anchor)]
    parent = anchor.parent

    for _ in range(4):
        if not isinstance(parent, Tag):
            break

        values.append(_clean_text(parent))
        parent = parent.parent

    return " ".join(value for value in values if value)


def _clean_text(element: Tag) -> str:
    return " ".join(element.stripped_strings)
