import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

class Anim:
    def __init__(self, fname, numFrames, title, xpos, ypos):
        self.fname = fname
        self.frames = []
        self.index = 0
        self.xpos = xpos
        self.ypos = ypos
        self.img = Image.open(fname)
        self.width = self.img.size[0]
        self.height = self.img.size[1]
        self.frameHeight = int(self.height / numFrames)
        self.numFrames = numFrames
        for n in range(numFrames):
            tup = (0, self.frameHeight * n, self.width, self.frameHeight * (n + 1))
            frame = ImageTk.PhotoImage(self.img.crop(tup))
            self.frames.append(frame)
        self.canvas = Canvas(window, width = self.width, height = self.frameHeight + 10, bg='#313132', highlightthickness=0)
        self.canvas.place(x=self.xpos, y=self.ypos)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<Button>', self.button_click)
        self.canvas.create_text(self.width / 2, 4, text=title, fill='#ffffff')
        self.prevy = 0

    def getFrame(self):
        return self.frames[self.index]

    def setIndex(self, n):
        if n >= 0 and n < (self.numFrames - 1):
            self.index = n

    def getIndex(self):
        return self.index

    def getSize(self):
        return (self.width, self.height, self.frameHeight)

    def inc(self):
        if (self.index < (self.numFrames - 1)):
            self.index = self.index + 1

    def dec(self):
        if self.index >= 1:
            self.index = self.index - 1

    def draw(self):
        self.canvas.delete(self.fname)
        self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.fname)

    def motion(self, event):
        newFrame = False

        if event.y < self.prevy:
            self.inc()
            newFrame = True

        if event.y > self.prevy:
            self.dec()
            newFrame = True

        if newFrame == True:
            self.draw()

        self.prevy = event.y

    def button_click(self, event):
        if event.num == 1:
            self.index = self.index + 1
            if self.index >= self.numFrames:
                self.index = 0
        if event.num == 3:
            self.index = self.index - 1
            if self.index < 0:
                self.index = (self.numFrames - 1)
        self.draw()

window = Tk()
window.geometry("640x480")
window.configure(bg='#313132')
#window.wm_attributes('-transparentcolor', '#123456')

anim1 = Anim("possible2-18_18.png", 37, "Feedback", 10, 10)
anim2 = Anim("on_off3.png", 2, "Pitch EQ", 140, 10)
anim3 = Anim("possible2-63.0_64.0.png", 128, "Level", 10, 10 + anim1.getSize()[2] + 15)
anim4 = Anim("possible2_C1_C7.png", 7, "Scale Pos", 10, 10 + ((anim1.getSize()[2] + 15) * 2))

anim1.setIndex(35)

anim1.draw()
anim2.draw()
anim3.draw()
anim4.draw()

window.mainloop()
