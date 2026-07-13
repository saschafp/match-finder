# Match Finder

Match Finder fetches fixtures from the Swiss football Matchcenter and publishes them as a static JSON file for a lightweight GitHub Pages frontend.

## Features

- Fetch fixtures from multiple competitions
- Parse league and cup competitions
- Export a single `games.json`
- Static frontend with no backend
- Comprehensive test suite

## Project Structure

```text
.
├── data/               # Generated game data
├── docs/               # GitHub Pages frontend
├── scripts/            # Utility scripts
├── src/                # Python package
└── tests/              # Unit tests
```

## Installation

Create a virtual environment and install the development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
playwright install chromium
```

## Fetch Fixtures

Generate the latest fixture data:

```bash
python scripts/fetch_games.py
```

This writes:

```text
data/games.json
```

To update the frontend:

```bash
mkdir -p docs/data
cp data/games.json docs/data/games.json
```

## Run the Frontend

Serve the `docs` directory locally:

```bash
python -m http.server 8000 --directory docs
```

Then open:

```
http://localhost:8000
```

## Run the Tests

```bash
python -m pytest
```
