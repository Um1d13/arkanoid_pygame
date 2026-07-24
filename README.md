# Neon Breaker

An original Arkanoid/Breakout-style game built with Pygame.

## Features

- Mouse-driven menu with a persistent local high-score table (top 5, saved to `data/highscores.json`)
- 5 hand-designed levels loaded from JSON (`levels/level_0X.json`), including a checkerboard,
  a diamond core and a steel fortress
- Vector-based ball physics with paddle-angle bounce, wall/brick collision, and a glowing motion trail
- 9 power-ups: paddle **wide**/**narrow**, **multi-ball**, **sticky** paddle, **laser** cannons,
  extra **life**, one-hit **shield**, and ball **haste**/**calm**
- Particle burst effects when bricks are destroyed
- Pause menu, and all sound effects synthesized procedurally at runtime (no external audio files)

## Requirements

1. Git
2. Python 3.10+
3. `venv` (ships with Python)

Check your setup:

```
git -v
python3 --version
```

## Installation and local run

```
git clone https://github.com/Um1d13/arkanoid_pygame.git
cd arkanoid_pygame
python3 -m venv env
source env/bin/activate        # Windows: .\env\Scripts\Activate.ps1
pip install -r requirements.txt
python3 main.py
```

## Controls

| Key             | Action                          |
|-----------------|----------------------------------|
| Left/Right, A/D | Move paddle                     |
| SPACE           | Launch a stuck ball              |
| X               | Fire lasers (while laser powered)|
| P / ESC         | Pause / resume                   |

## Project layout

```
main.py            screen flow: menu, high scores, end screen
src/config.py       all tunable constants
src/sprites.py       Paddle, Ball, Brick, PowerUp, LaserBolt, Particle, Star
src/game.py          Game class — runs a single level
src/levels.py        JSON level loader
src/audio.py         procedurally synthesized sound effects
src/scores.py        high-score persistence
src/ui.py             gradients, panels, buttons, text helpers
levels/*.json         level layouts
```
# arkanoid_pygame
