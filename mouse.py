from tkinter import *

def motion(event):
    print(f"x={event.x}, y={event.y}")

window = Tk()
window.bind('<B1-Motion>', motion)

window.mainloop()
