import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

index = 0
index2 = 0
prevy = 0

class Anim:
    def __init__(self, fname, numFrames):
        self.frames = []
        self.index = 0
        self.img = Image.open(fname)
        self.width = self.img.size[0]
        self.height = self.img.size[1]
        self.frameHeight = self.height / numFrames
        self.numFrames = numFrames
        for n in range(numFrames):
            tup = (0, self.frameHeight * n, self.width, self.frameHeight * (n + 1))
            frame = ImageTk.PhotoImage(self.img.crop(tup))
            self.frames.append(frame)
        print(self.width, self.height, self.frameHeight, self.numFrames)

    def getFrame(self):
        print("returning frame ", self.index)
        return self.frames[self.index]

    def setIndex(self, n):
        self.index = n

    def getSize(self):
        returrn (self.width, self.height, self.frameHeight)

    def inc(self):
        if (self.index < self.numFrames):
            self.index = self.index + 1
            print("inc to", self.index)

    def dec(self):
        if self.index >= 1:
            self.index = self.index - 1
            print("dec to", self.index)

def motion(event):
#    global index
#    global index2
#    global prevy
#    newFrame = False
#    print(f"x={event.x}, y={event.y}")
    if event.y > prevy:
        anim1.inc()
        anim2.inc()
#        if index < (numFrames - 1):
#            index = index + 1
#            newFrame = True
    if event.y < prevy:
        anim1.dec()
        anim2.dec()
#        if index > 0:
#            index = index -1
#            newFrame = True
#    if event.y != prevy:
#        index2 = index2 + 1
#        if index2 > 1:
#            index2 = 0
#        print("update pic2", index)
        canvas.delete("pic2")
        canvas.create_image(130, 10, anchor=tk.NW, image = anim2.getFrame(), tag="pic2")
#    prevy = event.y
#    if newFrame == True:
        canvas.delete("pic")
        canvas.create_image(10, 10, anchor=tk.NW, image = anim1.getFrame(), tag="pic")

window = Tk()
window.geometry("640x480")
window.bind('<B1-Motion>', motion)

anim1 = Anim("possible2.png", 128)
#img = Image.open("possible2.png")
#width = img.size[0]
#height = img.size[1]
#vertically stitched PNG
#numFrames = int(height / width)

#frames = []
#for n in range(numFrames):
#    tup = (0, width * n, width, width * (n + 1))
#    frame = ImageTk.PhotoImage(img.crop(tup))
#    frames.append(frame)

anim2 = Anim("on_off.png", 2)
#img2 = Image.open("on_off.png")
#width2 = img2.size[0]
#height2 = img2.size[1]
#vertically stitched PNG
#numFrames2 =2

#frames2 = []
#for n in range(numFrames2):
#    tup = (0, 41 * n, width2, 41 * (n + 1))
#    frame = ImageTk.PhotoImage(img2.crop(tup))
#    frames2.append(frame)
#print(frames2)

canvas = Canvas(window, width = 220, height = 140, bg='#313132')
canvas.place(x=40, y=40)

canvas.create_image(10, 10, anchor=tk.NW, image = anim1.getFrame(), tag="pic")
canvas.create_image(130, 10, anchor=tk.NW, image = anim2.getFrame(), tag="pic2")

window.mainloop()
