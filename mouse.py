import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

index = 0
prevy = 0

def motion(event):
    global index
    global prevy
    newFrame = False
    print(f"x={event.x}, y={event.y}")
    if event.y > prevy:
        if index < (numFrames - 1):
            index = index + 1
            newFrame = True
    if event.y < prevy:
        if index > 0:
            index = index -1
            newFrame = True
    prevy = event.y
    if newFrame == True:
        canvas.delete("pic")
        canvas.create_image(10, 10, anchor=tk.NW, image = frames[index], tag="pic")

window = Tk()
window.geometry("640x480")
window.bind('<B1-Motion>', motion)

img = Image.open("KNB_vert.png")
width = img.size[0]
height = img.size[1]
#vertically stitched PNG
numFrames = int(height / width)

frames = []
for n in range(numFrames):
    tup = (0, width * n, width, width * (n + 1))
    frame = ImageTk.PhotoImage(img.crop(tup))
    frames.append(frame)

canvas = Canvas(window, width = 100, height = 100, bg='#313132')
canvas.place(x=40, y=40)

canvas.create_image(10, 10, anchor=tk.NW, image = frames[index], tag="pic")

window.mainloop()
