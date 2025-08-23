from tkinter import *
import os

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

# Toggle function
def toggle_play():
    if play_btn.winfo_ismapped():
        play_btn.grid_remove()
        pause_btn.grid(row=0, column=1, padx=7, pady=10)
    else:
        pause_btn.grid_remove()
        play_btn.grid(row=0, column=1, padx=7, pady=10)

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
