from tkinter import *
import os
import pygame
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk

root = Tk()
root.title('Music Player')
root.geometry("550x450")

songlist = Listbox(root, bg="black", fg="white", width=100, height=15)
songlist.pack()

script_dir = os.path.dirname(os.path.abspath(__file__))

image_dir = os.path.join(script_dir, "..", "resources", "image", "icon")

play_btn_image = PhotoImage(file=os.path.join(image_dir, "play.png"))
pause_btn_image = PhotoImage(file=os.path.join(image_dir, "pause.png"))
next_btn_image = PhotoImage(file=os.path.join(image_dir, "next.png"))
prev_btn_image = PhotoImage(file=os.path.join(image_dir, "previous.png"))

control_frame = Frame(root)
control_frame.pack()


#pygame init for music playback
pygame.mixer.init()

#load a sample song
song_path = os.path.join(script_dir, "..", "resources", "music", "monta_rey.mp3")
pygame.mixer.music.load(song_path)

# Track playing state
is_playing = False
is_paused = False


# === Functions ===

#Grab Song Length Time Info
def play_time():
    current_time = pygame.mixer.music.get_pos()/1000
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
    
    #get song length with mutagen
    song = song_path
    song_mut = MP3(song)
    global song_length
    song_length = song_mut.info.length
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

    #output time to status bar
    status_bar.config(text=f'Time Elapsed: {converted_current_time} of {converted_song_length} ')
    slider.config(value=current_time)
    #update time
    status_bar.after(1000, play_time)

#create slider
def slide(x):
    slider_label.config(text=f'{int(slider.get())} of {int(song_length)}')

def toggle_play():
    global is_playing, is_paused
    if is_playing:
        # Pause music
        pygame.mixer.music.pause()
        is_playing = False
        is_paused = True
        play_btn.grid(row=0, column=1, padx=7, pady=10)
        pause_btn.grid_remove()
    else:
        if is_paused:
            # Resume from pause
            pygame.mixer.music.unpause()
        else:
            # First time play
            pygame.mixer.music.play()
            play_time()

            #update slider to position
            slider_position = int(song_length)
            slider.config(to=slider_position, value=0)

        is_playing = True
        is_paused = False
        pause_btn.grid(row=0, column=1, padx=7, pady=10)
        play_btn.grid_remove()

play_btn = Button(control_frame, image=play_btn_image, borderwidth=0,command=toggle_play)
pause_btn = Button(control_frame, image=pause_btn_image, borderwidth=0, command=toggle_play)
next_btn = Button(control_frame, image=next_btn_image, borderwidth=0)
prev_btn = Button(control_frame, image=prev_btn_image, borderwidth=0)

play_btn.grid(row=0, column=1, padx=7, pady = 10)
pause_btn.grid(row=0, column=1, padx=7, pady = 10)
next_btn.grid(row=0, column=2, padx=7, pady = 10)
prev_btn.grid(row=0, column=0, padx=7, pady = 10)

pause_btn.grid_remove() #Initially Hidden

#create slider
slider = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length = 360)
slider.pack(pady=20)

#create slider label
slider_label = Label(root, text="0")
slider_label.pack(pady=10)

#Create Status Bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

root.mainloop()
