# library.py
import os
from song import Song

SUPPORTED_EXT = (".mp3", ".wav", ".flac", ".ogg")

def load_from_folder(folder_path):
    """Load songs from a folder (returns list of Song)."""
    songs = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(SUPPORTED_EXT):
            title = os.path.splitext(file)[0]
            songs.append(Song(title=title, artist="Unknown", filepath=os.path.join(folder_path, file)))
    return songs


class LibraryManager:
    def __init__(self, app):
        self.app = app  # keep reference to MusicApp for UI + persistence
        self.songs = []

    def load_folder(self, folder):
        self.songs = load_from_folder(folder)
        self.display_library()
        self.app.persist.save_library()

    def display_library(self, songs=None):
        self.app.library_listbox.delete(0, "end")
        songs = songs or self.songs
        for song in songs:
            self.app.library_listbox.insert("end", f"{song.title} - {song.artist}")

    def delete_song(self, indices):
        for index in reversed(indices):
            song = self.songs[index]
            if (self.app.current_node and 
                self.app.current_node.song.filepath == song.filepath):
                self.app.player.stop()
            del self.songs[index]
        self.display_library()
        self.app.persist.save_library()

