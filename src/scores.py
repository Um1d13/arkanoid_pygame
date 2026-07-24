"""Local high-score persistence (top 5, stored as JSON)."""

import json

from src import config

MAX_ENTRIES = 5


def load() -> list[dict]:
    if not config.SCORES_FILE.exists():
        return []
    try:
        with config.SCORES_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save(entries: list[dict]) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with config.SCORES_FILE.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def qualifies(score: int) -> bool:
    entries = load()
    if len(entries) < MAX_ENTRIES:
        return True
    return score > min(e["score"] for e in entries)


def register(name: str, score: int) -> list[dict]:
    entries = load()
    entries.append({"name": name[:3].upper() or "AAA", "score": score})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:MAX_ENTRIES]
    save(entries)
    return entries
