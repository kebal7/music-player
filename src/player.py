import pygame
from mutagen.mp3 import MP3
import time

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.song_length = 0

    def load(self, path):
        pygame.mixer.music.load(path)
        self.current_song = path
        self.song_length = MP3(path).info.length

    def play(self, start=0):
        pygame.mixer.music.play(start=start)
        self.is_playing = True
        self.is_paused = False

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False
        self.is_paused = True

    def unpause(self):
        pygame.mixer.music.unpause()
        self.is_playing = True
        self.is_paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def set_pos(self, pos):
        pygame.mixer.music.set_pos(pos)

    def get_pos(self):
        return pygame.mixer.music.get_pos() / 1000  # seconds

    def get_length(self):
        return self.song_length
    
    def get_busy(self):
        return pygame.mixer.music.get_busy()
