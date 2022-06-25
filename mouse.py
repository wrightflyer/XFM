import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

index = 0
index2 = 0
prevy = 0

def motion(event):
    global index
    global index2
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
    if event.y != prevy:
        index2 = index2 + 1
        if index2 > 1:
            index2 = 0
        print("update pic2", index)
        canvas.delete("pic2")
        canvas.create_image(130, 10, anchor=tk.NW, image = frames2[index2], tag="pic2")
    prevy = event.y
    if newFrame == True:
        canvas.delete("pic")
        canvas.create_image(10, 10, anchor=tk.NW, image = frames[index], tag="pic")

window = Tk()
window.geometry("640x480")
window.bind('<B1-Motion>', motion)

img = Image.open("possible2.png")
width = img.size[0]
height = img.size[1]
#vertically stitched PNG
numFrames = int(height / width)

frames = []
for n in range(numFrames):
    tup = (0, width * n, width, width * (n + 1))
    frame = ImageTk.PhotoImage(img.crop(tup))
    frames.append(frame)

img2 = Image.open("on_off.png")
width2 = img2.size[0]
height2 = img2.size[1]
#vertically stitched PNG
numFrames2 =2

frames2 = []
for n in range(numFrames2):
    tup = (0, 41 * n, width2, 41 * (n + 1))
    frame = ImageTk.PhotoImage(img2.crop(tup))
    frames2.append(frame)
print(frames2)

canvas = Canvas(window, width = 220, height = 140, bg='#313132')
canvas.place(x=40, y=40)

canvas.create_image(10, 10, anchor=tk.NW, image = frames[index], tag="pic")
canvas.create_image(130, 10, anchor=tk.NW, image = frames2[index2], tag="pic2")

window.mainloop()
