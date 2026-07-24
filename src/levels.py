"""Level loading.

Levels are stored as JSON (a list of row strings) rather than the
whitespace-separated text grids some other implementations use.
Legend: '.' empty, '1'/'2'/'3' brick hit-points, 'X' indestructible steel.
"""

import json

from src import config
from src.sprites import Brick

LEGEND = {"1": 1, "2": 2, "3": 3, "X": -1}


def available_levels() -> int:
    return len(list(config.LEVELS_DIR.glob("level_*.json")))


def load_level(number: int) -> list[Brick]:
    path = config.LEVELS_DIR / f"level_{number:02d}.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    rows = data["rows"]
    bricks: list[Brick] = []
    for row_index, row in enumerate(rows):
        row = row.ljust(config.FIELD_COLS, ".")
        for col_index, char in enumerate(row[: config.FIELD_COLS]):
            if char in LEGEND:
                bricks.append(Brick(col_index, row_index, LEGEND[char]))
    return bricks
