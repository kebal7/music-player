import os
import random
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog, simpledialog, messagebox
import pygame
import json
from mutagen.mp3 import MP3
import time
from song import Song
from playlist import Node, PlaylistLinkedList
from persist import Persist
from library import LibraryManager

# Try to import mutagen to get accurate track length (optional) 
try: 
    from mutagen import File as MutagenFile 
    HAS_MUTAGEN = True 
except Exception: 
    HAS_MUTAGEN = False

LIBRARY_FILE = "library.json"
PLAYLIST_FILE = "playlists.json"
SUPPORTED_EXT = (".mp3", ".wav", ".flac", ".ogg")


# =====================
# LIBRARY FUNCTIONS
# =====================
def load_from_folder(folder_path):
    songs = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(SUPPORTED_EXT):
            title = os.path.splitext(file)[0]
            songs.append(Song(title=title, artist="Unknown", filepath=os.path.join(folder_path, file)))
    return songs

# =====================
# GUI APP
# =====================
class MusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Gray Beat Music Player")
        self.root.geometry("1000x900")
        self.root.config(bg="#2B2B2B")
        pygame.mixer.init()

        self.library = []
        self.playlists = {}
        self.current_playlist_name = None
        self.current_node = None
        
        self.persist = Persist(self)
        self.library_manager = LibraryManager(self)
        self.is_paused = False
        
        
        # track length in seconds
        self.current_length = 0

        # Stack for history
        self.history_stack = []

        # Queue for "play next"
        self.play_next_queue = []

        # ===================== Frames =====================
        library_frame = tk.Frame(root, bg="#2B2B2B")
        library_frame.pack(side=tk.LEFT, padx=15, pady=15, fill=tk.Y)

        playlist_frame = tk.Frame(root, bg="#2B2B2B")
        playlist_frame.pack(side=tk.RIGHT, padx=15, pady=15, fill=tk.BOTH, expand=True)

        # ===================== Library Section =====================
        tk.Label(library_frame, text="🎧 Music Library", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.library_listbox = tk.Listbox(library_frame, width=40, height=20, selectmode=tk.MULTIPLE, bg="#1E1E1E", fg="white", font=("Helvetica", 11))
        self.library_listbox.pack(pady=5)

        tk.Button(library_frame, text="📂 Load Folder", command=self.load_folder, bg="#4CAF50", fg="white", width=22, height=2).pack(pady=5)
        tk.Button(library_frame, text="➕ Add to Playlist", command=self.add_to_playlist, bg="#2196F3", fg="white", width=22, height=2).pack(pady=5)
        tk.Button(library_frame, text="🗑 Delete Song", command=self.delete_library_song, bg="#F44336", fg="white", width=22, height=2).pack(pady=5)

        # ===================== Playlist Section =====================
        tk.Label(playlist_frame, text="🎶 Playlists", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.playlist_listbox = tk.Listbox(playlist_frame, width=35, height=6, bg="#1E1E1E", fg="white", font=("Helvetica", 11))
        self.playlist_listbox.pack(pady=5)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.select_playlist)

        btn_frame_playlist = tk.Frame(playlist_frame, bg="#2B2B2B")
        btn_frame_playlist.pack(pady=5)
        tk.Button(btn_frame_playlist, text="🆕 New Playlist", command=self.new_playlist, bg="#FF9800", fg="white", width=15, height=2).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame_playlist, text="🗑 Delete Playlist", command=self.delete_playlist, bg="#F44336", fg="white", width=15, height=2).grid(row=0, column=1, padx=5)

        tk.Label(playlist_frame, text="🎵 Songs in Playlist", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.playlist_songs_listbox = tk.Listbox(playlist_frame, width=50, height=15, bg="#1E1E1E", fg="white", font=("Helvetica", 11))
        self.playlist_songs_listbox.pack(pady=5)

        btn_frame_songs = tk.Frame(playlist_frame, bg="#2B2B2B")
        btn_frame_songs.pack(pady=5)
        tk.Button(btn_frame_songs, text="🗑 Delete Song", command=self.delete_playlist_song, bg="#F44336", fg="white", width=15, height=2).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame_songs, text="🔀 Shuffle", command=self.shuffle_playlist, bg="#9C27B0", fg="white", width=15, height=2).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame_songs, text="⭐ Upvote", command=self.upvote_song, bg="#FFC107", fg="white", width=15, height=2).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame_songs, text="⏩ Play Next", command=self.queue_play_next, bg="#00BCD4", fg="white", width=15, height=2).grid(row=0, column=3, padx=5)

        # ===================== Playback Controls =====================
        control_frame = tk.Frame(playlist_frame, bg="#2B2B2B")
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="▶ Play", command=self.play_song, bg="#4CAF50", fg="white", width=15, height=2).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="⏸ Pause/Resume", command=self.toggle_pause, bg="#FFC107", fg="white", width=15, height=2).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="⏮ Previous", command=self.previous_song, bg="#9C27B0", fg="white", width=15, height=2).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(control_frame, text="⏭ Next", command=self.next_song, bg="#F44336", fg="white", width=15, height=2).grid(row=0, column=3, padx=5, pady=5)

        self.slider_dragging = False

        # Slider frame
        self.slider_frame = tk.Frame(playlist_frame, bg="#2B2B2B")
        self.slider_frame.pack(pady=10)

        # Slider (on top)
        self.slider = ttk.Scale(self.slider_frame, from_=0, to=100, orient=HORIZONTAL, value=0, length=620)
        self.slider.pack(padx=10, pady=(0,5))  # add small bottom padding
        self.slider.bind("<Button-1>", self.slider_press)
        self.slider.bind("<ButtonRelease-1>", self.slider_release)

        # Time label (centered below slider)
        self.time_label = tk.Label(
            self.slider_frame, 
            text="00:00 / 00:00", 
            bg="#2B2B2B", 
            fg="white", 
            font=("Helvetica", 10)
        )
        self.time_label.pack(pady=(0,5))  # vertical spacing

        
        # ===================== Play History Section =====================
        history_frame = tk.Frame(playlist_frame, bg="#2B2B2B")
        history_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)
        tk.Label(history_frame, text="🕒 Play History", bg="#2B2B2B", fg="white", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.history_listbox = tk.Listbox(history_frame, width=70, height=8, bg="#1E1E1E", fg="white", font=("Helvetica", 11))
        self.history_listbox.pack(pady=5)
        self.history_listbox.bind("<Double-Button-1>", self.play_history_song)

        # Double click to play song from playlist
        self.playlist_songs_listbox.bind("<Double-Button-1>", self.play_selected_song)

        # Load saved library & playlists if exist
        self.persist.load_saved_library()
        self.persist.load_saved_playlists()


        # slider updater id
        self._slider_updater_id = None

    def start_slider_updater(self):
        # start periodic update (cancels existing)
        if self._slider_updater_id:
            self.root.after_cancel(self._slider_updater_id)
            self._slider_updater_id = None
        self._slider_updater_id = self.root.after(500, self.update_time)

    def stop_slider_updater(self):
        if self._slider_updater_id:
            self.root.after_cancel(self._slider_updater_id)
            self._slider_updater_id = None
            
    def update_time(self):
        if not pygame.mixer.music.get_busy() and not self.is_paused:
            self.next_song()
            return  # stop updating if nothing is playing

        current_time = pygame.mixer.music.get_pos()  # seconds
        song_length = self.current_length  # seconds

        converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
        converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

        current_time += 1  # simulate next tick

        if int(self.slider.get()) == int(song_length):
            self.time_label.config(text=f'Time Elapsed: {converted_song_length} of {converted_song_length}')
        elif self.is_paused:
            pass
        elif int(self.slider.get()) == int(current_time) and not self.slider_dragging:
            # slider hasn't been moved
            self.slider.config(to=int(song_length), value=int(current_time))
            self.time_label.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length}')
        else:
            # slider has been moved manually
            self.slider.config(to=int(song_length), value=int(self.slider.get()))
            converted_current_time = time.strftime('%M:%S', time.gmtime(int(self.slider.get())))
            self.time_label.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length}')

            # move slider by 1 second
            next_time = int(self.slider.get()) + 1
            self.slider.config(value=next_time)

        # schedule next update
        self._slider_updater_id = self.root.after(1000, self.update_time)
    
    def slider_press(self, event):
        self.slider_dragging = True

    def slider_release(self, event):
        self.slider_dragging = False
        pos = int(self.slider.get())
        
        if self.is_paused or pygame.mixer.music.get_busy(): #if song is paused or playing
            pygame.mixer.music.set_pos(pos)
        else:
            pygame.mixer.music.play(start=pos) #if song is not playing
            self.start_slider_updater()
            
    def highlight_current_song(self):
        self.playlist_songs_listbox.selection_clear(0, tk.END)
        if self.current_node and self.current_playlist_name:
            playlist = self.playlists[self.current_playlist_name]
            idx = 0
            node = playlist.head
            while node:
                if node == self.current_node:
                    self.playlist_songs_listbox.selection_set(idx)
                    self.playlist_songs_listbox.see(idx)  # scroll to it
                    break
                node = node.next
                idx += 1
   
    # Small adapter functions 
    def load_folder(self): 
        folder = filedialog.askdirectory() 
        if folder: 
            self.library_manager.load_folder(folder) 

    def delete_library_song(self): 
        selection = self.library_listbox.curselection() 
        if selection: 
            self.library_manager.delete_song(selection)

    def new_playlist(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name:
            if name in self.playlists:
                messagebox.showwarning("Warning", "Playlist already exists!")
                return
            self.playlists[name] = PlaylistLinkedList()
            self.playlist_listbox.insert(tk.END, name)
            self.persist.save_playlists()

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
        playlist_name = self.playlist_listbox.get(selection[0])
        # Stop if currently playing song belongs to this playlist
        if self.current_playlist_name == playlist_name:
            pygame.mixer.music.stop()
            self.stop_slider_updater()
            self.current_node = None
            self.current_playlist_name = None
            self.current_length = 0
        del self.playlists[playlist_name]
        self.playlist_listbox.delete(selection[0])
        self.playlist_songs_listbox.delete(0, tk.END)
        self.persist.save_playlists()

    def display_playlist_songs(self):
        self.playlist_songs_listbox.delete(0, tk.END)
        playlist = self.playlists.get(self.current_playlist_name)
        if playlist:
            for song in playlist.to_list():
                self.playlist_songs_listbox.insert(tk.END, f"{song.title} - {song.artist}")

    def add_to_playlist(self):
        if not self.current_playlist_name:
            messagebox.showwarning("Warning", "Select a playlist first!")
            return
        selections = self.library_listbox.curselection()
        playlist = self.playlists[self.current_playlist_name]
        added = 0
        for index in selections:
            song = self.library_manager.songs[index]
            if playlist.append(song):
                added += 1
        if added == 0:
            messagebox.showinfo("Info", "All selected songs are already in the playlist.")
        self.display_playlist_songs()
        self.persist.save_playlists()

    def delete_playlist_song(self):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if not selection or not playlist:
            return
        node = playlist.head
        idx = 0
        while node:
            if idx == selection[0]:
                # Stop if currently playing
                if self.current_node == node and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    self.stop_slider_updater()
                    self.current_length = 0
                playlist.remove(node)
                break
            node = node.next
            idx += 1
        self.display_playlist_songs()
        self.persist.save_playlists()
   

    # ===================== Playback Functions =====================
    def _set_current_length_from_file(self, filepath):
        self.current_length = 0
        if HAS_MUTAGEN:
            try:
                meta = MutagenFile(filepath)
                if meta and meta.info and getattr(meta.info, "length", None):
                    self.current_length = int(meta.info.length)
            except Exception:
                self.current_length = 0
                
    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.slider.config(value=0)
        self.time_label.config(text="Time Elapsed: 00:00 of 00:00")

    def play_song(self):
        song_to_play = None
        # Priority: play next queue
        if self.play_next_queue:
            song_to_play = self.play_next_queue.pop(0)
        # Selected node
        elif self.current_node:
            song_to_play = self.current_node.song
        # If nothing selected, play first song in playlist
        elif self.current_playlist_name:
            playlist = self.playlists[self.current_playlist_name]
            self.current_node = playlist.head
            if self.current_node:
                song_to_play = self.current_node.song

        if not song_to_play:
            return
        try:
            self.stop()
            pygame.mixer.music.load(song_to_play.filepath)
            self.highlight_current_song()
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to load: {e}")
            return

        # attempt to get track length (optional)
        self._set_current_length_from_file(song_to_play.filepath)
        if self.current_length and self.current_length > 0:
            self.slider.config(from_=0, to=self.current_length)
        else:
            self.slider.config(from_=0, to=100)

        pygame.mixer.music.play()
        self.is_paused = False
        self.update_history(song_to_play)
        self.start_slider_updater()

    def play_selected_song(self, event):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if selection and playlist:
            node = playlist.head
            for _ in range(selection[0]):
                node = node.next
            self.current_node = node
            self.play_song()

    def toggle_pause(self):
        # Maintain explicit paused state
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            # If paused, unpause; else nothing to unpause
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False

    def next_song(self):
        if not self.current_node or not self.current_playlist_name:
            return
        if self.current_node.next:
            self.current_node = self.current_node.next
            self.play_song()
        else:
            # If at last song, loop back to first song
            playlist = self.playlists[self.current_playlist_name]
            self.current_node = playlist.head
            self.play_song()


    def previous_song(self):
        if not self.current_node or not self.current_playlist_name:
            return
        if self.current_node.prev:
            self.current_node = self.current_node.prev
            self.play_song()
        else:
            playlist = self.playlists[self.current_playlist_name]
            self.current_node = playlist.tail
            self.play_song()

    # ===================== History & Queue =====================
    def update_history(self, song):
        self.history_stack.append(song)
        self.history_listbox.insert(tk.END, f"{song.title} - {song.artist}")

    def play_history_song(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            song = self.history_stack[selection[0]]
            try:
                pygame.mixer.music.load(song.filepath)
                pygame.mixer.music.play()
                self._set_current_length_from_file(song.filepath)
                self.start_slider_updater()
            except Exception:
                messagebox.showerror("Playback Error", "Failed to play that history item.")

    def queue_play_next(self):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if selection and playlist:
            node = playlist.head
            for _ in range(selection[0]):
                node = node.next
            self.play_next_queue.insert(0, node.song)
            messagebox.showinfo("Info", f"{node.song.title} queued to play next.")

    def shuffle_playlist(self):
        playlist = self.playlists.get(self.current_playlist_name)
        if not playlist:
            return

        # Save currently playing song
        current_song = self.current_node.song if self.current_node else None

        # Save queue song filepaths
        queue_filepaths = [song.filepath for song in self.play_next_queue]

        # Shuffle the playlist
        playlist.shuffle()
        self.display_playlist_songs()
        self.persist.save_playlists()

        # Restore current node
        if current_song:
            node = playlist.head
            while node:
                if node.song.filepath == current_song.filepath:
                    self.current_node = node
                    break
                node = node.next

        # Rebuild the play next queue using shuffled playlist nodes
        new_queue = []
        for filepath in queue_filepaths:
            node = playlist.head
            while node:
                if node.song.filepath == filepath:
                    new_queue.append(node.song)
                    break
                node = node.next
        self.play_next_queue = new_queue

        # Highlight current song in UI
        self.highlight_current_song()


    def upvote_song(self):
        selection = self.playlist_songs_listbox.curselection()
        playlist = self.playlists.get(self.current_playlist_name)
        if selection and playlist:
            node = playlist.head
            for _ in range(selection[0]):
                node = node.next
            node.song.upvotes += 1
            messagebox.showinfo("Info", f"{node.song.title} now has {node.song.upvotes} upvotes!")

# ===================== MAIN =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()

