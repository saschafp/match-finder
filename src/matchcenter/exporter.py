from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from matchcenter.exceptions import MatchcenterExportError
from matchcenter.models import Game


def deduplicate_games(games: Iterable[Game]) -> list[Game]:
    unique: dict[str, Game] = {}

    for game in games:
        existing = unique.get(game.id)

        if existing is None:
            unique[game.id] = game
            continue

        if existing != game:
            raise MatchcenterExportError(
                f"Conflicting records for game ID {game.id}: {existing!r} != {game!r}"
            )

    return list(unique.values())


def sort_games(games: Iterable[Game]) -> list[Game]:
    return sorted(
        games,
        key=lambda game: int(game.id),
    )


def prepare_games(games: Iterable[Game]) -> list[Game]:
    return sort_games(deduplicate_games(games))


def write_games_json(
    games: Iterable[Game],
    output_path: Path,
) -> list[Game]:
    prepared_games = prepare_games(games)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        output_path.write_text(
            json.dumps(
                [game.to_dict() for game in prepared_games],
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise MatchcenterExportError(f"Could not write games to {output_path}") from exc

    return prepared_games
