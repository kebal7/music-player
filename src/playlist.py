import os

class Playlist:
    def __init__(self, music_dir):
        self.music_dir = music_dir
        self.songs = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.endswith(".mp3")]
        self.index = 0

    def next(self):
        self.index = (self.index + 1) % len(self.songs)
        return self.songs[self.index]

    def previous(self):
        self.index = (self.index - 1) % len(self.songs)
        return self.songs[self.index]

    def current(self):
        return self.songs[self.index]

