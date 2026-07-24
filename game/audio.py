"""game/audio.py – audio manager."""

import pygame

import settings as cfg

sound_enabled = True  
hit_sound: pygame.mixer.Sound | None = None
bonus_sound: pygame.mixer.Sound | None = None
laser_sound: pygame.mixer.Sound | None = None


def init_audio() -> None:
    global hit_sound, bonus_sound, laser_sound
    pygame.mixer.init()
    try:
        hit_sound = pygame.mixer.Sound(cfg.ASSETS_DIR / "hit.mp3")
        bonus_sound = pygame.mixer.Sound(cfg.ASSETS_DIR / "bonus.mp3")
        laser_sound = pygame.mixer.Sound(cfg.ASSETS_DIR / "laser.mp3")
    except pygame.error:
        print("Error loading sounds, please check the assets/ folder")


def play_sound(sound: pygame.mixer.Sound | None) -> None:
    if sound_enabled and sound is not None:
        sound.play()


def play_music() -> None:
    if sound_enabled:
        pygame.mixer.music.load(cfg.ASSETS_DIR / "music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # Infinite


def stop_music() -> None:
    pygame.mixer.music.stop()


def toggle_sound() -> None:
    global sound_enabled
    sound_enabled = not sound_enabled
    if sound_enabled:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()
