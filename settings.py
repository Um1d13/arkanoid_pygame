"""settings.py – Game parameters and variables"""

from pathlib import Path

# --- Пути -------------------------------------------------------------------
# Считаются от расположения этого файла, а не от текущей рабочей директории:
# так игра находит assets/ и levels/ независимо от того, откуда её запустили.
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LEVELS_DIR = BASE_DIR / "levels"

# --- Экран и таймер -----------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- Game Field -------------------------------------------------------------
BRICK_WIDTH, BRICK_HEIGHT = 60, 20
TOP_OFFSET = 60  # UI Bar height
FIELD_LEFT = 40  # Left offset for bricks

# Game Field size calc
FIELD_COLS = (WIDTH - 2 * FIELD_LEFT) // BRICK_WIDTH
FIELD_RIGHT = FIELD_LEFT + FIELD_COLS * BRICK_WIDTH

# --- Paddle, Ball -----------------------------------------------------------
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 12
PADDLE_SPEED = 7

BALL_RADIUS = 8
BALL_SPEED_X = 4
BALL_SPEED_Y = -5
SLIDE_FACTOR = 0.8
MAX_BALL_SPEED_X = 8
BALL_SPEED_UP_FACTOR = 1.4
BALL_SPEED_DOWN_FACTOR = 0.7

PADDLE_MIN_WIDTH = 40  # floor for the shrink bonus

# --- Bonuses ---------------------------------------------------------------------
BONUS_PROBABILITY = 0.3
BONUS_TYPES = ["extend", "multiball", "laser", "extra_life", "shrink", "speed_up", "speed_down"]

# --- Visuals -----------------------------------------------------------
TRAIL_LENGTH = 6  
PARTICLE_COUNT = 10  
PARTICLE_LIFETIME = (12, 24)
PARTICLE_SPEED = (1.5, 4.0)
PARTICLE_GRAVITY = 0.15
MAX_PARTICLES = 200

# --- Colors -------------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PADDLE_COLOR = CYAN
BALL_COLOR = WHITE

# HP -> Brick Color
BRICK_COLORS = {
    2: ORANGE,
    1: RED,
    0: GRAY,
    -1: DARK_GRAY,  # wall
}
