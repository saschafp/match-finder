# Match Finder

Match Finder fetches fixtures from the Swiss football Matchcenter and publishes them as a static JSON file for a lightweight GitHub Pages frontend.

## Features

- Fetch fixtures from multiple competitions
- Parse league and cup competitions
- Export game data and update metadata
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

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate

python -m pip install -e .
python -m playwright install chromium
```

## Fetch Fixtures

Generate the latest fixture data:

```bash
python scripts/fetch_games.py
```

This creates:

```text
data/
├── games.json
└── metadata.json
```

## Publish & Deploy

Copy the generated data to the website:

```bash
./scripts/publish_games.sh
```

The complete manual workflow is:

```bash
python scripts/fetch_games.py
./scripts/publish_games.sh

git add docs/data/games.json docs/data/metadata.json
git commit -m "Update fixture data"
git push
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
