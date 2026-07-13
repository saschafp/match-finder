#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source_dir="$repo_root/data"
target_dir="$repo_root/docs/data"

mkdir -p "$target_dir"

cp "$source_dir/games.json" "$target_dir/games.json"
cp "$source_dir/metadata.json" "$target_dir/metadata.json"

echo "Published data to $target_dir"
