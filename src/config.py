"""Central configuration for Neon Breaker.

Every tunable number lives here so gameplay can be balanced without
touching game logic.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LEVELS_DIR = ROOT_DIR / "levels"
DATA_DIR = ROOT_DIR / "data"
SCORES_FILE = DATA_DIR / "highscores.json"

# --- Window -----------------------------------------------------------
WIDTH, HEIGHT = 900, 650
FPS = 60
TITLE = "Neon Breaker"

# --- Playfield ----------------------------------------------------------
BRICK_W, BRICK_H = 60, 24
FIELD_MARGIN = 30
FIELD_TOP = 110
FIELD_COLS = (WIDTH - 2 * FIELD_MARGIN) // BRICK_W
FIELD_LEFT = FIELD_MARGIN
FIELD_RIGHT = WIDTH - FIELD_MARGIN

# --- Paddle -------------------------------------------------------------
PADDLE_W, PADDLE_H = 110, 14
PADDLE_Y_OFFSET = 34  # distance from bottom of screen
PADDLE_SPEED = 8.5
PADDLE_WIDE = 160
PADDLE_NARROW = 65

# --- Ball -----------------------------------------------------------------
BALL_RADIUS = 7
BALL_SPEED = 6.3
BALL_MAX_BOUNCE_ANGLE = 68  # degrees off vertical at paddle edges
BALL_HASTE_MULT = 1.4
BALL_CALM_MULT = 0.7

# --- Lives / scoring ------------------------------------------------------
START_LIVES = 3
BRICK_SCORE = {1: 10, 2: 25, 3: 45}

# --- Power-ups --------------------------------------------------------------
POWERUP_DROP_CHANCE = 0.22
POWERUP_FALL_SPEED = 3.2
POWERUP_DURATION = 480  # frames (~8s at 60 FPS)
POWERUP_SIZE = (28, 16)

POWERUPS = {
    "wide":   {"color": (60, 220, 255), "label": "W", "caption": "PADDLE WIDENED"},
    "narrow": {"color": (255, 90, 90),  "label": "N", "caption": "PADDLE NARROWED"},
    "multi":  {"color": (255, 210, 60), "label": "M", "caption": "MULTI-BALL"},
    "sticky": {"color": (170, 90, 255), "label": "S", "caption": "STICKY PADDLE"},
    "laser":  {"color": (255, 60, 180), "label": "L", "caption": "LASER ARMED"},
    "life":   {"color": (90, 255, 140), "label": "+", "caption": "EXTRA LIFE"},
    "shield": {"color": (255, 255, 255),"label": "O", "caption": "SHIELD READY"},
    "haste":  {"color": (255, 140, 0),  "label": ">", "caption": "BALL HASTE"},
    "calm":   {"color": (0, 200, 200),  "label": "<", "caption": "BALL CALMED"},
}

# --- Colors -----------------------------------------------------------------
BG_TOP = (8, 6, 22)
BG_BOTTOM = (26, 10, 46)
PANEL = (18, 14, 36)
WHITE = (235, 235, 245)
DIM = (150, 150, 170)
NEON_PINK = (255, 70, 170)
NEON_CYAN = (60, 230, 255)
NEON_YELLOW = (255, 220, 70)

PADDLE_COLOR = NEON_CYAN
BALL_COLOR = WHITE
STEEL_COLOR = (90, 90, 105)

BRICK_PALETTE = {
    1: (70, 200, 130),
    2: (240, 170, 60),
    3: (235, 80, 90),
}

# --- Input keys (chosen to avoid overlap with reference key scheme) ------
KEY_FIRE = "x"  # documented for reference; actual pygame const used in game.py
