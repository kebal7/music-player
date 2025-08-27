import os
import json
from song import Song
from playlist import Node, PlaylistLinkedList
import tkinter as tk

LIBRARY_FILE = "library.json"
PLAYLIST_FILE = "playlists.json"

class Persist:
    # ===================== Persistent Library & Playlists =====================
    def __init__(self, musicplayer):
        self.library = []
        self.musicplayer = musicplayer

    def save_library(self):
        data = [{"title": s.title, "artist": s.artist, "filepath": s.filepath} for s in self.library]
        with open(LIBRARY_FILE, "w") as f:
            json.dump(data, f)

    def load_saved_library(self):
        if os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    if os.path.exists(item["filepath"]):
                        self.library.append(Song(item["title"], item["artist"], item["filepath"]))
                self.musicplayer.library_manager.display_library()

    def save_playlists(self):
        data = {}
        for name, playlist in self.musicplayer.playlists.items():
            data[name] = [{"title": s.title, "artist": s.artist, "filepath": s.filepath, "upvotes": s.upvotes} for s in playlist.to_list()]
        with open(PLAYLIST_FILE, "w") as f:
            json.dump(data, f)

    def load_saved_playlists(self):
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, "r") as f:
                data = json.load(f)
                for name, songs in data.items():
                    playlist = PlaylistLinkedList()
                    for s in songs:
                        song = Song(s["title"], s["artist"], s["filepath"])
                        song.upvotes = s.get("upvotes", 0)
                        playlist.append(song)
                    self.musicplayer.playlists[name] = playlist
                    self.musicplayer.playlist_listbox.insert(tk.END, name)

