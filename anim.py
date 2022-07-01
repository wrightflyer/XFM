import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

class Anim:
    def __init__(self, keyname, title, ctrl, xpos, ypos):
        self.keyname = keyname
        self.ctrl = ctrl
        self.index = 0
        self.xpos = xpos
        self.ypos = ypos
        self.width = ctrlimgs[ctrl]["width"]
        self.height = ctrlimgs[ctrl]["height"]
        numFrames = ctrlimgs[ctrl]["numframes"]
        self.frameHeight = ctrlimgs[ctrl]["frameH"]
        self.numFrames = numFrames
        self.canvas = Canvas(window, width = self.width, height = self.frameHeight + 10, bg='#202020', highlightthickness=0)
        #self.canvas.attributes("-alpha", 0.5)
        self.canvas.place(x=self.xpos, y=self.ypos)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<Button>', self.button_click)
        if len(title) > 0:
            self.canvas.create_text(self.width / 2, 4, text=title, fill='#ffffff')
        self.prevy = 0
        self.prevx = 0

    def getFrame(self):
        return ctrlimgs[self.ctrl]["frames"][self.index]

    def setIndex(self, n):
        if n >= 0 and n < (self.numFrames - 1):
            self.index = n

    def getIndex(self):
        return self.index

    def getKey(self):
        return self.keyname

    def getInfo(self):
        return (self.keyname, self.ctrl, self.index, self.xpos, self.ypos, self.width, self.frameHeight, self.height, self.numFrames)

    def inc(self):
        if (self.index < (self.numFrames - 1)):
            self.index = self.index + 1

    def dec(self):
        if self.index >= 1:
            self.index = self.index - 1

    def draw(self):
        self.canvas.delete(self.keyname)
        self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)

    def motion(self, event):
        newFrame = False

        if event.y < self.prevy or event.x > self.prevx:
            self.inc()
            newFrame = True

        if event.y > self.prevy or event.x < self.prevx:
            self.dec()
            newFrame = True

        if newFrame == True:
            self.draw()
            ctrlType = ctrlimgs[self.ctrl]["type"]
            if ctrlType == "slideV" or ctrlType == "slideH":
                op = self.keyname.split(':')[0] + ":"
                key = op + "Atime"
                for n in controllist:
                    if n.getKey() == key:
                        print(n.getInfo())

        self.prevy = event.y
        self.prevx = event.x

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

def updateADSR(activecanvas, at, al, dt, dl, st, sl, rt, rl):
    activecanvas.delete("all")
    ax = at
    ay = 128 - al

    dx = dt + ax
    dy = 128 - dl

    sx = st + dx
    sy = 128 - sl

    rx = rt + sx
    ry = 128 - rl

    padding = 256 - (at + dt + st + rt)

    activecanvas.create_line(0, 128, ax, ay, width=3)
    activecanvas.create_line(ax, ay, dx, dy, width=3)
    activecanvas.create_line(dx, dy, sx, sy, width=3)
    activecanvas.create_line(sx, sy, sx + padding, sy, width=3, dash=(3,1))
    activecanvas.create_line(sx + padding, sy, 256, ry, width=3)

window = Tk()
window.geometry("1710x890")
window.configure(bg='#313131')
window.resizable(False, False)
rawback = Image.open("xfm/resources/dark-grey-texture-abstract-hd-wallpaper-1920x1200-1223.jpg")
#rawback = rawback.resize((680, 440), Image.Resampling.LANCZOS)
opback = rawback.resize((680, 440))
backimg = ImageTk.PhotoImage(opback)
Label(image=backimg).place(x=0, y=0)
Label(image=backimg).place(x=682, y=0)
Label(image=backimg).place(x=2, y=442)
Label(image=backimg).place(x=682, y=442)
mstrback=rawback.resize((340, 882))
mstrimg = ImageTk.PhotoImage(mstrback)
Label(image=mstrimg).place(x=1364,y=0)
rawlogo = Image.open("logo.png")
logo = ImageTk.PhotoImage(rawlogo)
Label(image = logo, borderwidth=0).place(x = 1380, y = 630)

adsr1 = Canvas(window, width=256, height=128, bg='#707070')
adsr1.place(x=200, y=240)
adsr2 = Canvas(window, width=256, height=128, bg='#707070')
adsr2.place(x=880, y=240)
adsr3 = Canvas(window, width=256, height=128, bg='#707070')
adsr3.place(x=200, y=680)
adsr4 = Canvas(window, width=256, height=128, bg='#707070')
adsr4.place(x=880, y=680)
adsrP = Canvas(window, width=256, height=128, bg='#707070')
adsrP.place(x=1410, y=270)

XOFF = 680
YOFF = 440

anims = {
    "0to127" :  [ "possible2_0_127.png", 128 ],
    "_63to64" : [ "possible2-63.0_64.0.png", 128 ],
    "on_off" :  [ "on_off3.png", 2 ],
    "_18to18" : [ "possible2-18_18.png", 37 ],
    "slideH" :  [ "slide_back_h.png", 128],
    "slideV" :  [ "slide_back_v.png", 128],
    "_63to63" : [ "possible2-63_63.png", 127 ],
    "C1toC7" :  [ "possible2_C1_C7.png", 7 ],
    "chars" :   [ "lcd_chars.png", 36 ]
}

ctrlimgs = {}
for anim in anims:
    fname = anims[anim][0]
    numFrame = anims[anim][1]
    img = Image.open(fname)
    width = img.size[0]
    height = img.size[1]
    frameH = int(height / numFrame)
    ctrlimgs.update({ anim : { "type" : anim, "numframes" : numFrame, "width" : width, "height" : height, "frameH" : frameH, "frames" : []}})
    for n in range(numFrame):
        tup = (0, frameH * n, width, frameH * (n + 1))
        frame = ImageTk.PhotoImage(img.crop(tup))
        ctrlimgs[anim]["frames"].append(frame)

controls = {
    "OP1:Output" :   [ "Output",    "0to127",    100, 10 ],
    "OP1:Feedback" : [ "Feedback",  "_63to64",   10, 100 ],
    "OP1:Lgain" :    [ "L Gain",    "on_off",    200, 10 ],
    "OP1:Rgain" :    [ "R Gain",    "on_off",    270, 10 ],
    "OP1:Peq" :      [ "Pitch EQ",  "on_off",    340, 10 ],
    "OP1:Fixed" :    [ "Fixed",     "on_off",    410, 10 ],
    "OP1:OP2In" :    [ "OP2 Input", "0to127",    100, 100 ],
    "OP1:OP3In" :    [ "OP3 Input", "0to127",    10, 190 ],
    "OP1:OP4In" :    [ "OP4 Input", "0to127",    100, 190 ],
    "OP1:Level" :    [ "Level",     "_18to18",   10, 280 ],
    "OP1:VelSens" :  [ "Velo Sens", "0to127",    100, 280 ],
    "OP1:Atime" :    [ "A Time",    "slideH",    10, 380 ],
    "OP1:Dtime" :    [ "D Time",    "slideH",    180, 380 ],
    "OP1:Stime" :    [ "S Time",    "slideH",    350, 380 ],
    "OP1:Rtime" :    [ "R Time",    "slideH",    520, 380 ],
    "OP1:ALevel" :   [ "A Level",   "slideV",    200, 60 ],
    "OP1:DLevel" :   [ "D Level",   "slideV",    270, 60 ],
    "OP1:SLevel" :   [ "S Level",   "slideV",    340, 60 ],
    "OP1:RLevel" :   [ "R Level",   "slideV",    410, 60 ],
    "OP1:Ratio" :    [ "Output",    "0to127",    500, 10 ],
    "OP1:Detune" :   [ "Detune",    "_63to63",   590, 10 ],
    "OP1:Time" :     [ "TimeScale", "0to127",    500, 100 ],
    "OP1:UpCurv" :   [ "Up Curve",  "_18to18",   590, 100 ],
    "OP1:Scale" :    [ "Scale Pos", "C1toC7",    500, 190 ],
    "OP1:DnCurv" :   [ "Down Curve","_18to18",   590, 190 ],
    "OP1:LGain" :    [ "L Gain",    "_63to63",   500, 280 ],
    "OP1:RGain" :    [ "R Gain",    "_63to63",   590, 280 ],

    "OP2:Output" :   [ "Output",    "0to127",    XOFF + 100, 10 ],
    "OP2:Feedback" : [ "Feedback",  "_63to64",   XOFF + 10, 100 ],
    "OP2:Lgain" :    [ "L Gain",    "on_off",    XOFF + 200, 10 ],
    "OP2:Rgain" :    [ "R Gain",    "on_off",    XOFF + 270, 10 ],
    "OP2:Peq" :      [ "Pitch EQ",  "on_off",    XOFF + 340, 10 ],
    "OP2:Fixed" :    [ "Fixed",     "on_off",    XOFF + 410, 10 ],
    "OP2:OP1In" :    [ "OP1 Input", "0to127",    XOFF + 100, 100 ],
    "OP2:OP3In" :    [ "OP3 Input", "0to127",    XOFF + 10, 190 ],
    "OP2:OP4In" :    [ "OP4 Input", "0to127",    XOFF + 100, 190 ],
    "OP2:Level" :    [ "Level",     "_18to18",   XOFF + 10, 280 ],
    "OP2:VelSens" :  [ "Velo Sens", "0to127",    XOFF + 100, 280 ],
    "OP2:Atime" :    [ "A Time",    "slideH",    XOFF + 10, 380 ],
    "OP2:Dtime" :    [ "D Time",    "slideH",    XOFF + 180, 380 ],
    "OP2:Stime" :    [ "S Time",    "slideH",    XOFF + 350, 380 ],
    "OP2:Rtime" :    [ "R Time",    "slideH",    XOFF + 520, 380 ],
    "OP2:ALevel" :   [ "A Level",   "slideV",    XOFF + 200, 60 ],
    "OP2:DLevel" :   [ "D Level",   "slideV",    XOFF + 270, 60 ],
    "OP2:SLevel" :   [ "S Level",   "slideV",    XOFF + 340, 60 ],
    "OP2:RLevel" :   [ "R Level",   "slideV",    XOFF + 410, 60 ],
    "OP2:Ratio" :    [ "Output",    "0to127",    XOFF + 500, 10 ],
    "OP2:Detune" :   [ "Detune",    "_63to63",   XOFF + 590, 10 ],
    "OP2:Time" :     [ "TimeScale", "0to127",    XOFF + 500, 100 ],
    "OP2:UpCurv" :   [ "Up Curve",  "_18to18",   XOFF + 590, 100 ],
    "OP2:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + 500, 190 ],
    "OP2:DnCurv" :   [ "Down Curve","_18to18",   XOFF + 590, 190 ],
    "OP2:LGain" :    [ "L Gain",    "_63to63",   XOFF + 500, 280 ],
    "OP2:RGain" :    [ "R Gain",    "_63to63",   XOFF + 590, 280 ],

    "OP3:Output" :   [ "Output",    "0to127",    100, YOFF + 10 ],
    "OP3:Feedback" : [ "Feedback",  "_63to64",   10, YOFF + 100 ],
    "OP3:Lgain" :    [ "L Gain",    "on_off",    200, YOFF + 10 ],
    "OP3:Rgain" :    [ "R Gain",    "on_off",    270, YOFF + 10 ],
    "OP3:Peq" :      [ "Pitch EQ",  "on_off",    340, YOFF + 10 ],
    "OP3:Fixed" :    [ "Fixed",     "on_off",    410, YOFF + 10 ],
    "OP3:OP1In" :    [ "OP1 Input", "0to127",    100, YOFF + 100 ],
    "OP3:OP2In" :    [ "OP2 Input", "0to127",    10, YOFF + 190 ],
    "OP3:OP4In" :    [ "OP4 Input", "0to127",    100, YOFF + 190 ],
    "OP3:Level" :    [ "Level",     "_18to18",   10, YOFF + 280 ],
    "OP3:VelSens" :  [ "Velo Sens", "0to127",    100, YOFF + 280 ],
    "OP3:Atime" :    [ "A Time",    "slideH",    10, YOFF + 380 ],
    "OP3:Dtime" :    [ "D Time",    "slideH",    180, YOFF + 380 ],
    "OP3:Stime" :    [ "S Time",    "slideH",    350, YOFF + 380 ],
    "OP3:Rtime" :    [ "R Time",    "slideH",    520, YOFF + 380 ],
    "OP3:ALevel" :   [ "A Level",   "slideV",    200, YOFF + 60 ],
    "OP3:DLevel" :   [ "D Level",   "slideV",    270, YOFF + 60 ],
    "OP3:SLevel" :   [ "S Level",   "slideV",    340, YOFF + 60 ],
    "OP3:RLevel" :   [ "R Level",   "slideV",    410, YOFF + 60 ],
    "OP3:Ratio" :    [ "Output",    "0to127",    500, YOFF + 10 ],
    "OP3:Detune" :   [ "Detune",    "_63to63",   590, YOFF + 10 ],
    "OP3:Time" :     [ "TimeScale", "0to127",    500, YOFF + 100 ],
    "OP3:UpCurv" :   [ "Up Curve",  "_18to18",   590, YOFF + 100 ],
    "OP3:Scale" :    [ "Scale Pos", "C1toC7",    500, YOFF + 190 ],
    "OP3:DnCurv" :   [ "Down Curve","_18to18",   590, YOFF + 190 ],
    "OP3:LGain" :    [ "L Gain",    "_63to63",   500, YOFF + 280 ],
    "OP3:RGain" :    [ "R Gain",    "_63to63",   590, YOFF + 280 ],

    "OP4:Output" :   [ "Output",    "0to127",    XOFF + 100, YOFF + 10 ],
    "OP4:Feedback" : [ "Feedback",  "_63to64",   XOFF + 10, YOFF + 100 ],
    "OP4:Lgain" :    [ "L Gain",    "on_off",    XOFF + 200, YOFF + 10 ],
    "OP4:Rgain" :    [ "R Gain",    "on_off",    XOFF + 270, YOFF + 10 ],
    "OP4:Peq" :      [ "Pitch EQ",  "on_off",    XOFF + 340, YOFF + 10 ],
    "OP4:Fixed" :    [ "Fixed",     "on_off",    XOFF + 410, YOFF + 10 ],
    "OP4:OP1In" :    [ "OP1 Input", "0to127",    XOFF + 100, YOFF + 100 ],
    "OP4:OP2In" :    [ "OP2 Input", "0to127",    XOFF + 10, YOFF + 190 ],
    "OP4:OP3In" :    [ "OP3 Input", "0to127",    XOFF + 100, YOFF + 190 ],
    "OP4:Level" :    [ "Level",     "_18to18",   XOFF + 10, YOFF + 280 ],
    "OP4:VelSens" :  [ "Velo Sens", "0to127",    XOFF + 100, YOFF + 280 ],
    "OP4:Atime" :    [ "A Time",    "slideH",    XOFF + 10, YOFF + 380 ],
    "OP4:Dtime" :    [ "D Time",    "slideH",    XOFF + 180, YOFF + 380 ],
    "OP4:Stime" :    [ "S Time",    "slideH",    XOFF + 350, YOFF + 380 ],
    "OP4:Rtime" :    [ "R Time",    "slideH",    XOFF + 520, YOFF + 380 ],
    "OP4:ALevel" :   [ "A Level",   "slideV",    XOFF + 200, YOFF + 60 ],
    "OP4:DLevel" :   [ "D Level",   "slideV",    XOFF + 270, YOFF + 60 ],
    "OP4:SLevel" :   [ "S Level",   "slideV",    XOFF + 340, YOFF + 60 ],
    "OP4:RLevel" :   [ "R Level",   "slideV",    XOFF + 410, YOFF + 60 ],
    "OP4:Ratio" :    [ "Output",    "0to127",    XOFF + 500, YOFF + 10 ],
    "OP4:Detune" :   [ "Detune",    "_63to63",   XOFF + 590, YOFF + 10 ],
    "OP4:Time" :     [ "TimeScale", "0to127",    XOFF + 500, YOFF + 100 ],
    "OP4:UpCurv" :   [ "Up Curve",  "_18to18",   XOFF + 590, YOFF + 100 ],
    "OP4:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + 500, YOFF + 190 ],
    "OP4:DnCurv" :   [ "Down Curve","_18to18",   XOFF + 590, YOFF + 190 ],
    "OP4:LGain" :    [ "L Gain",    "_63to63",   XOFF + 500, YOFF + 280 ],
    "OP4:RGain" :    [ "R Gain",    "_63to63",   XOFF + 590, YOFF + 280 ],


    "Name:chr0" :    [ "",          "chars",   1430, 10 ],
    "Name:chr1" :    [ "",          "chars",   1430 + 64 - 11, 10 ],
    "Name:chr2" :    [ "",          "chars",   1430 + ((64 - 11) * 2), 10 ],
    "Name:chr3":     [ "",          "chars",   1430 + ((64 - 11) * 3), 10 ],
    "Pitch:Atime" :  [ "A Time",    "slideH",    1400, 410 ],
    "Pitch:Dtime" :  [ "D Time",    "slideH",    1400, 460 ],
    "Pitch:Stime" :  [ "S Time",    "slideH",    1400, 510 ],
    "Pitch:Rtime" :  [ "R Time",    "slideH",    1400, 560 ],
    "Pitch:ALevel" : [ "A Level",   "slideV",    1410, 90 ],
    "Pitch:DLevel" : [ "D Level",   "slideV",    1480, 90 ],
    "Pitch:SLevel" : [ "S Level",   "slideV",    1550, 90 ],
    "Pitch:RLevel" : [ "R Level",   "slideV",    1620, 90 ],
    "Mixer:Level" :  [ "Mixer Level","_63to63",   1600, 500 ],
}

controllist = []
for key in controls:
    thisanim = Anim(key, controls[key][0], controls[key][1], controls[key][2], controls[key][3])
    controllist.append(thisanim)
    thisanim.draw()
    
for a in controllist:
    print(a.getInfo())

window.mainloop()
