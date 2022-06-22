import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

index = 13
prevy = 0

def motion(event):
    global index
    global prevy
    newFrame = False
    print(f"x={event.x}, y={event.y}")
    if event.y > prevy:
        if index < 126:
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

imgObj = Image.open("KNB_metal_green_L.gif")
numFrames = imgObj.n_frames
#rgba = imgObj.convert("RGBA")
#data = rgba.getdata()
#newdata = []
#for pix in data:
#    if pix[0] == 49 and pix[1] == 49 and pix[2] == 50:
#        newdata.append((255, 255, 255, 0))
#    else:
#        newdata.append(pix)
#rgba.putdata(newdata)

frames = []
for n in range(numFrames):
    imgObj.seek(n)
    frame = ImageTk.PhotoImage(imgObj)
    frames.append(frame)

canvas = Canvas(window, width = 100, height = 100, bg='#313132')
canvas.place(x=40, y=40)

canvas.create_image(10, 10, anchor=tk.NW, image = frames[index], tag="pic")

window.mainloop()
