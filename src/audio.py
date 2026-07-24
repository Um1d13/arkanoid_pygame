"""Procedurally synthesized sound effects.

No external audio assets are shipped with the project: every sound is a
short waveform generated at startup with numpy and handed to pygame's
mixer via sndarray. If numpy or the mixer is unavailable the game keeps
running silently.
"""

import math

import pygame

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


class _SilentSound:
    def play(self):
        pass


def _tone(freq, duration, volume=0.5, wave="sine", sample_rate=44100):
    n_samples = int(sample_rate * duration)
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    amplitude = int(volume * 32767)
    for i in range(n_samples):
        t = i / sample_rate
        fade = min(1.0, (n_samples - i) / (sample_rate * 0.02))
        if wave == "square":
            value = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            value = math.sin(2 * math.pi * freq * t)
        sample = int(amplitude * value * fade)
        buf[i][0] = sample
        buf[i][1] = sample
    return pygame.sndarray.make_sound(buf)


def _sweep(start_freq, end_freq, duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    amplitude = int(volume * 32767)
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        freq = start_freq + (end_freq - start_freq) * progress
        fade = min(1.0, (n_samples - i) / (sample_rate * 0.02))
        sample = int(amplitude * math.sin(2 * math.pi * freq * t) * fade)
        buf[i][0] = sample
        buf[i][1] = sample
    return pygame.sndarray.make_sound(buf)


class SoundBank:
    """Lazily-built collection of synthesized sound effects."""

    def __init__(self):
        self.enabled = _HAS_NUMPY and pygame.mixer.get_init() is not None
        if not self.enabled:
            self.brick = self.paddle = self.wall = self._silent = _SilentSound()
            self.powerup = self.laser = self.lose_life = self.win = _SilentSound()
            return
        self.brick = _tone(520, 0.05, 0.4)
        self.paddle = _tone(300, 0.06, 0.45, wave="square")
        self.wall = _tone(220, 0.04, 0.3)
        self.powerup = _sweep(400, 900, 0.18, 0.4)
        self.laser = _sweep(900, 300, 0.08, 0.3, )
        self.lose_life = _sweep(500, 120, 0.35, 0.5)
        self.win = _sweep(300, 1200, 0.6, 0.45)
