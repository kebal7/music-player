from tkinter import *
import os
import pygame

root = Tk()
root.title('Music Player')
root.geometry("550x350")

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

#track playing state
is_playing = False

# Toggle function
def toggle_play():
    global is_playing
    if is_playing:
        # Pause music
        pygame.mixer.music.pause()
        play_btn.grid(row=0, column=1, padx=7, pady=10)
        pause_btn.grid_remove()
        is_playing = False
    else:
        # Resume or play
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.unpause()
        pause_btn.grid(row=0, column=1, padx=7, pady=10)
        play_btn.grid_remove()
        is_playing = True

play_btn = Button(control_frame, image=play_btn_image, borderwidth=0,command=toggle_play)
pause_btn = Button(control_frame, image=pause_btn_image, borderwidth=0, command=toggle_play)
next_btn = Button(control_frame, image=next_btn_image, borderwidth=0)
prev_btn = Button(control_frame, image=prev_btn_image, borderwidth=0)

play_btn.grid(row=0, column=1, padx=7, pady = 10)
pause_btn.grid(row=0, column=1, padx=7, pady = 10)
next_btn.grid(row=0, column=2, padx=7, pady = 10)
prev_btn.grid(row=0, column=0, padx=7, pady = 10)

pause_btn.grid_remove() #Initially Hidden

root.mainloop()
