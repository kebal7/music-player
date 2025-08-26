from tkinter import *
from tkinter import ttk, filedialog, simpledialog, messagebox
import os
import pygame
import time
from mutagen.mp3 import MP3
import json
import random

# ===================== Constants =====================
LIBRARY_FILE = "library.json"
PLAYLIST_FILE = "playlists.json"
SUPPORTED_EXT = (".mp3", ".wav", ".flac", ".ogg")

# ===================== DATA MODELS =====================
class Song:
    def __init__(self, title, artist, filepath):
        self.title = title
        self.artist = artist
        self.filepath = filepath
        self.upvotes = 0

# ===================== LINKED LIST =====================
class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class PlaylistLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, song):
        current = self.head
        while current:
            if current.song.filepath == song.filepath:
                return False
            current = current.next
        new_node = Node(song)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
        return True

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.size -= 1

    def to_list(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.song)
            current = current.next
        return songs

    def shuffle(self):
        songs = self.to_list()
        random.shuffle(songs)
        self.head = self.tail = None
        for s in songs:
            self.append(s)

# ===================== UTILITY =====================
def load_from_folder(folder_path):
    songs = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(SUPPORTED_EXT):
            title = os.path.splitext(file)[0]
            songs.append(Song(title=title, artist="Unknown", filepath=os.path.join(folder_path, file)))
    return songs

# ===================== MUSIC APP =====================
class MusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Music Player with Playlists")
        self.root.geometry("1000x600")
        self.root.config(bg="#2B2B2B")
        pygame.mixer.init()

        # --- Music state ---
        self.is_playing = False
        self.is_paused = False
        self.current_node = None
        self.current_playlist_name = None
        self.play_next_queue = []
        self.history_stack = []

        # --- Directories and images ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_dir = os.path.join(self.script_dir, "..", "resources", "image", "icon")
        self.play_img = PhotoImage(file=os.path.join(self.image_dir, "play.png"))
        self.pause_img = PhotoImage(file=os.path.join(self.image_dir, "pause.png"))
        self.next_img = PhotoImage(file=os.path.join(self.image_dir, "next.png"))
        self.prev_img = PhotoImage(file=os.path.join(self.image_dir, "previous.png"))

        # --- Data structures ---
        self.library = []
        self.playlists = {}

        # --- UI Components ---
        self.setup_ui()

        # --- Load saved library & playlists ---
        self.load_saved_library()
        self.load_saved_playlists()

    # ===================== UI SETUP =====================
    def setup_ui(self):
        # --- Library Frame ---
        library_frame = Frame(self.root, bg="#2B2B2B")
        library_frame.pack(side=LEFT, padx=15, pady=15, fill=Y)
        Label(library_frame, text="🎧 Music Library", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.library_listbox = Listbox(library_frame, width=40, height=20, selectmode=MULTIPLE, bg="#1E1E1E", fg="white")
        self.library_listbox.pack(pady=5)
        Button(library_frame, text="📂 Load Folder", command=self.load_folder, bg="#4CAF50", fg="white", width=22).pack(pady=5)
        Button(library_frame, text="➕ Add to Playlist", command=self.add_to_playlist, bg="#2196F3", fg="white", width=22).pack(pady=5)
        Button(library_frame, text="🗑 Delete Song", command=self.delete_library_song, bg="#F44336", fg="white", width=22).pack(pady=5)

        # --- Playlist Frame ---
        playlist_frame = Frame(self.root, bg="#2B2B2B")
        playlist_frame.pack(side=RIGHT, padx=15, pady=15, fill=BOTH, expand=True)
        Label(playlist_frame, text="🎶 Playlists", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.playlist_listbox = Listbox(playlist_frame, width=35, height=6, bg="#1E1E1E", fg="white")
        self.playlist_listbox.pack(pady=5)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.select_playlist)

        # Playlist buttons
        btn_frame_playlist = Frame(playlist_frame, bg="#2B2B2B")
        btn_frame_playlist.pack(pady=5)
        Button(btn_frame_playlist, text="🆕 New Playlist", command=self.new_playlist, bg="#FF9800", fg="white", width=15).grid(row=0, column=0, padx=5)
        Button(btn_frame_playlist, text="🗑 Delete Playlist", command=self.delete_playlist, bg="#F44336", fg="white", width=15).grid(row=0, column=1, padx=5)

        # Playlist songs
        Label(playlist_frame, text="🎵 Songs in Playlist", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.playlist_songs_listbox = Listbox(playlist_frame, width=50, height=15, bg="#1E1E1E", fg="white")
        self.playlist_songs_listbox.pack(pady=5)
        self.playlist_songs_listbox.bind("<Double-Button-1>", self.play_selected_song)

        btn_frame_songs = Frame(playlist_frame, bg="#2B2B2B")
        btn_frame_songs.pack(pady=5)
        Button(btn_frame_songs, text="🗑 Delete Song", command=self.delete_playlist_song, bg="#F44336", fg="white", width=15).grid(row=0, column=0, padx=5)
        Button(btn_frame_songs, text="🔀 Shuffle", command=self.shuffle_playlist, bg="#9C27B0", fg="white", width=15).grid(row=0, column=1, padx=5)
        Button(btn_frame_songs, text="⭐ Upvote", command=self.upvote_song, bg="#FFC107", fg="white", width=15).grid(row=0, column=2, padx=5)
        Button(btn_frame_songs, text="⏩ Play Next", command=self.queue_play_next, bg="#00BCD4", fg="white", width=15).grid(row=0, column=3, padx=5)

        # --- Control Frame ---
        control_frame = Frame(playlist_frame, bg="#2B2B2B")
        control_frame.pack(pady=10)
        self.prev_btn = Button(control_frame, image=self.prev_img, borderwidth=0, command=self.previous_song)
        self.prev_btn.grid(row=0, column=0, padx=7)
        self.play_pause_btn = Button(control_frame, image=self.play_img, borderwidth=0, command=self.toggle_play)
        self.play_pause_btn.grid(row=0, column=1, padx=7)
        self.next_btn = Button(control_frame, image=self.next_img, borderwidth=0, command=self.next_song)
        self.next_btn.grid(row=0, column=2, padx=7)

        # --- Slider ---
        self.slider = ttk.Scale(playlist_frame, from_=0, to=100, orient=HORIZONTAL, length=600, command=self.slide)
        self.slider.pack(pady=10)
        self.slider_label = Label(playlist_frame, text="00:00 / 00:00", bg="#2B2B2B", fg="white")
        self.slider_label.pack()
        self.status_bar = Label(self.root, text='', bd=1, relief=GROOVE, anchor=E)
        self.status_bar.pack(fill=X, side=BOTTOM, ipady=2)

    # ===================== LIBRARY =====================
    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            new_songs = load_from_folder(folder)
            self.library.extend(new_songs)
            self.display_library()
            self.save_library()

    def display_library(self):
        self.library_listbox.delete(0, END)
        for song in self.library:
            self.library_listbox.insert(END, f"{song.title} - {song.artist}")

    def delete_library_song(self):
        selection = self.library_listbox.curselection()
        if not selection:
            return
        for index in reversed(selection):
            del self.library[index]
        self.display_library()
        self.save_library()

    # ===================== PLAYLIST =====================
    def new_playlist(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name:
            if name in self.playlists:
                messagebox.showwarning("Warning", "Playlist already exists!")
                return
            self.playlists[name] = PlaylistLinkedList()
            self.playlist_listbox.insert(END, name)
            self.save_playlists()

    def select_playlist(self, event):
        selection = self.playlist_listbox.curselection()
        if selection:
            self.current_playlist_name = self.playlist_listbox.get(selection[0])
            self.display_playlist_songs()
            self.current_node = self.playlists[self.current_playlist_name].head

    def delete_playlist(self):
        selection = self.playlist_listbox.curselection()
        if not selection:
            return
        name = self.playlist_listbox.get(selection[0])
        if self.current_playlist_name == name:
            pygame.mixer.music.stop()
            self.current_node = None
            self.current_playlist_name = None
        del self.playlists[name]
        self.playlist_listbox.delete(selection[0])
        self.playlist_songs_listbox.delete(0, END)
        self.save_playlists()

    def display_playlist_songs(self):
        self.playlist_songs_listbox.delete(0, END)
        playlist = self.playlists.get(self.current_playlist_name)
        if playlist:
            for song in playlist.to_list():
                self.playlist_songs_listbox.insert(END, f"{song.title} - {song.artist}")

    def add_to_playlist(self):
        if not self.current_playlist_name:
            messagebox.showwarning("Warning", "Select a playlist first!")
            return
        selections = self.library_listbox.curselection()
        playlist = self.playlists[self.current_playlist_name]
        for index in selections:
            playlist.append(self.library[index])
        self.display_playlist_songs()
        self.save_playlists()

    def delete_playlist_song(self):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if not selection or not playlist:
            return
        node = playlist.head
        for _ in range(selection[0]):
            node = node.next
        playlist.remove(node)
        self.display_playlist_songs()
        self.save_playlists()

    def shuffle_playlist(self):
        playlist = self.playlists.get(self.current_playlist_name)
        if playlist:
            playlist.shuffle()
            self.display_playlist_songs()
            self.save_playlists()

    def upvote_song(self):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if selection and playlist:
            node = playlist.head
            for _ in range(selection[0]):
                node = node.next
            node.song.upvotes += 1
            messagebox.showinfo("Info", f"{node.song.title} now has {node.song.upvotes} upvotes!")

    def queue_play_next(self):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if selection and playlist:
            node = playlist.head
            for _ in range(selection[0]):
                node = node.next
            self.play_next_queue.insert(0, node.song)
            messagebox.showinfo("Info", f"{node.song.title} queued to play next.")

    # ===================== PLAYBACK =====================
    def play_song(self):
        song_to_play = None
        if self.play_next_queue:
            song_to_play = self.play_next_queue.pop(0)
        elif self.current_node:
            song_to_play = self.current_node.song
        elif self.current_playlist_name:
            playlist = self.playlists[self.current_playlist_name]
            self.current_node = playlist.head
            if self.current_node:
                song_to_play = self.current_node.song
        if not song_to_play:
            return

        pygame.mixer.music.load(song_to_play.filepath)
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_paused = False
        self.play_pause_btn.config(image=self.pause_img)
        self.update_history(song_to_play)
        self.play_time()

    def play_selected_song(self, event):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if selection and playlist:
            node = playlist.head
            for _ in range(selection[0]):
                node = node.next
            self.current_node = node
            self.play_song()

    def toggle_play(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.play_pause_btn.config(image=self.play_img)
        else:
            if self.is_paused:
                pygame.mixer.music.unpause()
            else:
                self.play_song()
            self.is_playing = True
            self.is_paused = False
            self.play_pause_btn.config(image=self.pause_img)

    def next_song(self):
        if self.play_next_queue:
            self.current_node = None
            self.play_song()
        elif self.current_node and self.current_node.next:
            self.current_node = self.current_node.next
            self.play_song()

    def previous_song(self):
        if self.current_node and self.current_node.prev:
            self.current_node = self.current_node.prev
            self.play_song()

    # ===================== SLIDER =====================
    def play_time(self):
        if not self.current_node or not self.is_playing:
            return

        current_song = self.current_node.song
        song_length = MP3(current_song.filepath).info.length
        current_time = pygame.mixer.music.get_pos() / 1000

        # Update slider and label
        self.slider.config(to=int(song_length), value=int(current_time))
        self.slider_label.config(text=f"{time.strftime('%M:%S', time.gmtime(current_time))} / {time.strftime('%M:%S', time.gmtime(song_length))}")

        # Auto-next song
        if int(current_time) >= int(song_length) - 1:
            self.next_song()

        self.root.after(1000, self.play_time)

    def slide(self, x):
        if self.current_node:
            pygame.mixer.music.play(start=int(float(x)))
            self.is_playing = True
            self.is_paused = False
            self.play_pause_btn.config(image=self.pause_img)

    # ===================== HISTORY =====================
    def update_history(self, song):
        self.history_stack.append(song)

    # ===================== SAVE & LOAD =====================
    def save_library(self):
        data = [{"title": s.title, "artist": s.artist, "filepath": s.filepath} for s in self.library]
        with open(LIBRARY_FILE, "w") as f:
            json.dump(data, f)

    def load_saved_library(self):
        if os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, "r") as f:
                data = json.load(f)
                self.library = [Song(d["title"], d["artist"], d["filepath"]) for d in data]
                self.display_library()

    def save_playlists(self):
        data = {}
        for name, playlist in self.playlists.items():
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
                        song_obj = Song(s["title"], s["artist"], s["filepath"])
                        song_obj.upvotes = s.get("upvotes", 0)
                        playlist.append(song_obj)
                    self.playlists[name] = playlist
                    self.playlist_listbox.insert(END, name)


# ===================== RUN APP =====================
if __name__ == "__main__":
    root = Tk()
    app = MusicApp(root)
    root.mainloop()

