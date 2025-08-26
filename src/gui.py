from tkinter import *
import tkinter.ttk as ttk
import os, time
from player import MusicPlayer
from playlist import Playlist

# --- Setup ---
root = Tk()
root.title("Music Player")
root.geometry("550x450")

script_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(script_dir, "..", "resources", "image", "icon")
music_dir = os.path.join(script_dir, "..", "resources", "music")

# --- Core Logic ---
player = MusicPlayer()
playlist = Playlist(music_dir)
player.load(playlist.current())

# --- UI ---
songlist = Listbox(root, bg="black", fg="white", width=100, height=15, selectmode=SINGLE, selectbackground="gray", selectforeground="white")
for s in playlist.songs:
    songlist.insert(END, os.path.basename(s))
songlist.pack()

play_img = PhotoImage(file=os.path.join(image_dir, "play.png"))
pause_img = PhotoImage(file=os.path.join(image_dir, "pause.png"))
next_img = PhotoImage(file=os.path.join(image_dir, "next.png"))
prev_img = PhotoImage(file=os.path.join(image_dir, "previous.png"))

control_frame = Frame(root)
control_frame.pack()

# --- Slider dragging state ---
slider_dragging = False

update_time_id = None

# --- Functions ---
def update_time():
    global update_time_id
    if not player.is_playing and not player.is_paused:
        return  # stop updating if nothing is playing

    current_time = player.get_pos()  # seconds
    song_length = player.get_length()  # seconds

    # For debugging, optional
    slider_label.config(text=f'Slider: {int(slider.get())} and Song Pos: {int(current_time)}')

    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

    current_time += 1  # simulate next tick

    if int(slider.get()) == int(song_length):
        status_bar.config(text=f'Time Elapsed: {converted_song_length} of {converted_song_length}')
    elif player.is_paused:
        pass
    elif int(slider.get()) == int(current_time) and not slider_dragging:
        # slider hasn't been moved
        slider.config(to=int(song_length), value=int(current_time))
        status_bar.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length}')
    else:
        # slider has been moved manually
        slider.config(to=int(song_length), value=int(slider.get()))
        converted_current_time = time.strftime('%M:%S', time.gmtime(int(slider.get())))
        status_bar.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length}')

        # move slider by 1 second
        next_time = int(slider.get()) + 1
        slider.config(value=next_time)

    # schedule next update
    update_time_id = status_bar.after(1000, update_time)

def start_update_time():
    """Cancel previous update loop and start a new one."""
    global update_time_id
    if update_time_id is not None:
        status_bar.after_cancel(update_time_id)
    update_time()

def highlight_current_song():
    # Clear previous selection
    songlist.selection_clear(0, END)
    try:
        # Get the index of the currently playing song in the playlist
        current_index = playlist.get_index()
        songlist.selection_set(current_index)
        songlist.activate(current_index)
        songlist.see(current_index)  # scroll to the selected item
    except Exception as e:
        print(e)
    
def toggle_play():
    if player.is_playing:
        player.pause()
        play_btn.grid()
        pause_btn.grid_remove()
    else:
        if player.is_paused:
            player.unpause()
        else:
            player.play()
            root.after(0,highlight_current_song)
            start_update_time()
        pause_btn.grid()
        play_btn.grid_remove()

def stop_song():
    player.stop()
    slider.config(value=0)
    status_bar.config(text="Time Elapsed: 00:00 of 00:00")
    play_btn.grid()
    pause_btn.grid_remove()
    
def play_next():
    stop_song()
    player.load(playlist.next())
    toggle_play()
    start_update_time()

def play_prev():
    stop_song()
    player.load(playlist.previous())
    toggle_play()
    start_update_time()

def slider_press(event):
    global slider_dragging
    slider_dragging = True

def slider_release(event):
    global slider_dragging
    slider_dragging = False
    pos = int(slider.get())
    
    if player.is_paused or player.get_busy(): #if song is paused or playing
        player.set_pos(pos)
    else:
        player.play(start=pos) #if song is not playing
        start_update_time()

# --- Buttons ---
play_btn = Button(control_frame, image=play_img, borderwidth=0, command=toggle_play)
pause_btn = Button(control_frame, image=pause_img, borderwidth=0, command=toggle_play)
next_btn = Button(control_frame, image=next_img, borderwidth=0, command=play_next)
prev_btn = Button(control_frame, image=prev_img, borderwidth=0, command=play_prev)

prev_btn.grid(row=0, column=0, padx=7, pady=10)
play_btn.grid(row=0, column=1, padx=7, pady=10)
pause_btn.grid(row=0, column=1, padx=7, pady=10)
next_btn.grid(row=0, column=2, padx=7, pady=10)
pause_btn.grid_remove()

# --- Slider + Status ---
slider = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL, value=0, length=360)
slider.pack(pady=20)
slider.bind("<Button-1>", slider_press)
slider.bind("<ButtonRelease-1>", slider_release)

#create slider label
slider_label = Label(root, text="0")
slider_label.pack(pady=10)

status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

# --- Start GUI ---
root.mainloop()

