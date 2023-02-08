import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import json
import mido
import json

# ADSR class is simply for drawing the rectangular envelope graph. It draws a light grey background
# then, after .update() is called it draws a blue line between the key points in the graph. Each OP (and
# "master") owns one of these so self.key holds the identity of each one and is used for it to access
# the right "controller" to pull the values.
class Adsr:
    def __init__(self, key, xpos, ypos):
        self.key = key
        self.xpos = xpos
        self.ypos = ypos
        self.canvas = Canvas(window, width=256, height=128, bg='#707070')
        self.canvas.create_image(0, 0, anchor=tk.NW, image = ctrlimgs["litegrey"]["frames"][0], tag = "adsrback")
        self.canvas.place(x = xpos, y = ypos)
    
    def update(self, at, al, dt, dl, st, sl, rt, rl):
        # horizontally 128+128+128+128 is 512 but the window is only 256 wide
        # so start by halving all the horizontal values (but just for display)
        at = at / 2
        dt = dt / 2
        st = st / 2
        rt = rt / 2
        self.canvas.delete("adsrline")
        ax = at
        ay = 128 - al

        dx = dt + ax
        dy = 128 - dl

        sx = st + dx
        sy = 128 - sl

        rx = rt + sx
        ry = 128 - rl

        padding = 256 - (at + dt + st + rt)

        ystart = 128 # as Y coordinates start at top left this is bottom left pixel
        if self.key == "Pitch:":
            # pitch curve is -48..+48 bi-polar so start at mid height
            ystart = 64
        #print("start=(", 0, ystart, ") end= (", ax, ay, ")")
        self.canvas.create_line(0, ystart, ax, ay, width=3, fill='#000CFF', tag="adsrline")
        self.canvas.create_line(ax, ay, dx, dy, width=3, fill='#000CFF', tag="adsrline")
        self.canvas.create_line(dx, dy, sx, sy, width=3, fill='#000CFF', tag="adsrline")
        self.canvas.create_line(sx, sy, sx + padding, sy, width=3, dash=(3,1), fill='#000CFF', tag="adsrline")
        self.canvas.create_line(sx + padding, sy, 256, ry, width=3, fill='#000CFF', tag="adsrline")

    def init(self):
        self.update(0, 127, 0, 127, 0, 127, 0, 0)

    def draw(self):
        op = self.key
        key = op + "ATime"
        at = controllist[key][0].getValue()
        key = op + "DTime"
        dt = controllist[key][0].getValue()
        key = op + "STime"
        st = controllist[key][0].getValue()
        key = op + "RTime"
        rt = controllist[key][0].getValue()

        offset = 0
        if op == "Pitch:":
            offset = 64
        key = op + "ALevel"
        al = controllist[key][0].getValue() + offset
        key = op + "DLevel"
        dl = controllist[key][0].getValue() + offset
        key = op + "SLevel"
        sl = controllist[key][0].getValue() + offset
        key = op + "RLevel"
        rl = controllist[key][0].getValue() + offset
        #print("draw ADSR ", op, "with ",at, al, dt, dl, st, sl, rt, rl)
        self.update(at, al, dt, dl, st, sl, rt, rl)

# This is actually the core of this program. It's really just about 100 separate controls
# each handled by this class. Part of it is a series of animated images that represent each
# position of the control. Then it binds to mouse messages which cause the animation to
# cycle through the animated frames while maintaing the "value" of the control which can
# be queried at any time.
#
# It tries to be as generic as possible but some controls have "special requirements" so
# I'm afraid there's quite a smattering of "special case" code in there too this is especially
# prevalent for the "big knobs" ;-)
#
# Most controls accept mouse drag up/right to increase and left/down to decrease but the big
# knobs use up/down for coarse adjustment and left/right for fine adjustments
class Anim:
    def __init__(self, keyname, title, ctrl, xpos, ypos, offset = 0):
        self.keyname = keyname
        self.ctrl = ctrl
        self.index = 0
        self.fraction = 0
        self.xpos = xpos
        self.ypos = ypos
        self.offset = offset # difference between 0 frame and lowest value (maybe -63 or -48 etc)
        self.width = ctrlimgs[ctrl]["width"]
        self.height = ctrlimgs[ctrl]["height"]
        numFrames = ctrlimgs[ctrl]["numframes"]
        self.frameHeight = ctrlimgs[ctrl]["frameH"]
        self.numFrames = numFrames
        self.canvas = Canvas(window, width = self.width, height = self.frameHeight + 10, bg='#202020', highlightthickness=0)
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
        #print(self.keyname, "set value=", n, "limit=", self.numFrames)
        if n >= 0 and n < self.numFrames:
            self.index = n

    def getIndex(self):
        return self.index

    def getValue(self):
        return self.index + self.offset # likely negative so really a subtraction

    def setValue(self, n):
        n = n - self.offset
        self.setIndex(n)

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

    def make_inbounds(self):
        ctrl = self.keyname.split(':')[1]
        if ctrl == "Feedback":
            value = self.getValue() * 10
            if value > 0:
                value = value + self.fraction
            else:
                value = value - self.fraction
            if value < -630:
                self.index = 0 # that is -63
                self.fraction = 0
            if value > 640:
                self.fraction = 0
        if ctrl == "Ratio":
            value = self.getValue() * 100
            value = value + self.fraction
            if value < 50: # can't go lower than 0.50
                self.fraction = 50;
            if value > 3200: # can't go above 32.00
                self.fraction = 0
        if ctrl == "Freq":
            value = self.getValue() * 100
            value = value + self.fraction
            if value > 9755:
                self.fraction = 55
            if value == 0:
                self.fraction = 1

    def draw(self):
        op = self.keyname.split(':')[0]
        ctrl = self.keyname.split(':')[1]
        self.make_inbounds()
        self.canvas.delete(self.keyname)
        self.canvas.delete("digits")
        if ctrl[:3] != "chr":
            self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)
        else:
            # for the characters in name special handling because index>100 means char + dot overlay
            if self.index < 100:
                self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)
            else:
                self.canvas.create_image(0, 11, anchor=tk.NW, image = ctrlimgs[self.ctrl]["frames"][self.index - 100], tag=self.keyname)
                self.canvas.create_image(47, 60, anchor=tk.NW, image = ctrlimgs["dot"]["frames"][0], tag=self.keyname)
        if ctrl == "Fixed":
            ctrl_w = controllist[op + ":Freq"][0].width
            ctrl_h = controllist[op + ":Freq"][0].frameHeight + 10 # +10 for the label above
            if self.index == 0:
                controllist[op + ":Freq"][0].canvas.config(width=0, height=0)
                controllist[op + ":Ratio"][0].canvas.config(width = ctrl_w, height = ctrl_h)
            else:
                controllist[op + ":Freq"][0].canvas.config(width = ctrl_w, height = ctrl_h)
                controllist[op + ":Ratio"][0].canvas.config(width=0, height=0)

        # following to handle "big knobs" that need their digits drawn separately...
        if ctrl == "Feedback":
            if self.getValue() < 0:
                # a leading negative sign
                self.canvas.create_image(1, 80, anchor=tk.NW, image = ctrlimgs["neg"]["frames"][0], tag = "digits")
            self.canvas.create_image(18, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][abs(self.getValue())], tag = "digits")
            self.canvas.create_image(38, 80, anchor=tk.NW, image = ctrlimgs["dig_d_9"]["frames"][self.fraction], tag = "digits")
        if ctrl == "Freq":
            # no leading 0 if only fraction
            if self.getValue() != 0:
                if self.getValue() < 10:
                    self.canvas.create_image(20, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.getValue()], tag = "digits")
                else:
                    self.canvas.create_image(16, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.getValue()], tag = "digits")
                self.canvas.create_image(38, 80, anchor=tk.NW, image = ctrlimgs["digits0"]["frames"][self.fraction], tag = "digits")
            else:
                self.canvas.create_image(38, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.fraction], tag = "digits")
        if ctrl == "Ratio":
            self.canvas.create_image(17, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.getValue()], tag = "digits")
            self.canvas.create_image(39, 80, anchor=tk.NW, image = ctrlimgs["dig_d_99"]["frames"][self.fraction], tag = "digits")

    def motion(self, event):
        newFrame = False
        ctrl = self.keyname.split(':')[1]

        if event.y < self.prevy:
            self.inc()
            newFrame = True

        if event.y > self.prevy:
            self.dec()
            newFrame = True

        if event.x > self.prevx:
            if ctrl == "Feedback":
                if self.fraction < 9:
                    self.fraction = self.fraction + 1
                    newFrame = True
            elif ctrl == "Freq" or ctrl == "Ratio":
                if self.fraction < 99:
                    self.fraction = self.fraction + 1
                    newFrame = True
            elif ctrl == "Ratio":
                if self.fraction < 99:
                    self.fraction = self.fraction + 1
                    newFrame = True
            else:
                self.inc()
                newFrame = True

        if event.x < self.prevx:
            if ctrl == "Feedback" or ctrl == "Freq" or ctrl == "Ratio":
                if self.fraction > 0:
                    self.fraction = self.fraction - 1
                    newFrame = True
            else:
                self.dec()
                newFrame = True

        if newFrame == True:
            self.draw()
            routeWin.draw()
            # if a control just moved that would change ADSR then redraw the ADSR graph
            ctrlType = ctrlimgs[self.ctrl]["type"]
            if ctrlType == "slideV" or ctrlType == "slideH" or ctrlType == "slideVbi":
                op = self.keyname.split(':')[0] + ":"
                adsrs[op].draw()

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

# The main display is basically 5 rectangles:
#
#  OP1 | OP3 | M
#      |     | A
#  ----------| I
#  OP2 | OP4 | N
#      |     | 
#
# so this class fills each with a similar textured, dark grey rectangles
# image passed in as "img"
class Backdrop:
    def __init__(self, id, xpos, ypos, width, height, img, logo, xlog, ylog):
        self.id = id
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.canvas = Canvas(width = width, height = height, bg='#202020', highlightbackground = '#404040')
        self.canvas.place(x = xpos, y = ypos)
        self.canvas.create_image(0, 0, anchor=tk.NW, image = img)
        self.canvas.create_image(xlog, ylog, anchor=tk.NW, image = logo)

# This opens a secondary window that attempts to do a Chris Dodsworth-esque rendition of how the
# operators are interacting with one another and what, if anything they are sending to the
# output. Each open box shows non-0 levels to (a) itself (ie "feedback"), (b) other operators
# using line stippling to show intensity and (c) to the output. When feedback is used it can change
# the waveform between default sine, square and saw (and at the extreme "noise") so a small wave
# symbol gives an idea of the wwaveform it's likely producing. As FM is all about the rations of
# the operators each square is also annotated with the ratio setting or its frequency if it's
# set to a fixed frequency. Mouse clicks turn annotation on/off to help declutter the display
class RouteWindow:
    def __init__(self):
        self.routeWin = Toplevel(window)
        self.routeWin.geometry("940x670")
        self.routeWin.title("Operator signal routing")
        self.routeWin.resizable(False, False)
        self.routeWin.protocol("WM_DELETE_WINDOW", self.toggle_window)
        self.canvas = Canvas(self.routeWin, width = 940, height = 670, bg='#313131')
        self.canvas.place(x = 0, y = 0)
        self.showNums = True
        self.canvas.bind('<Button>', self.toggleNums)
        self.hide()

    def show(self):
        self.routeWin.deiconify()
        self.Showing = True
        self.draw()

    def hide(self):
        self.routeWin.withdraw()
        self.Showing = False

    def toggleNums(self, event):
        if self.showNums == True:
            self.showNums = False
        else:
            self.showNums = True
        self.draw()
    
    def toggle_window(self):
        if self.Showing:
            self.hide()
        else:
            self.show()

    def getStipple(self, key):
        val = abs(controllist[key][0].getValue())
        name = "@./stipple/stip"
        # there are 0..255 stipple files but values are only 0..63 or 0..127 so need *2 or *4
        mult = 2
        if "Feedback" in key:
            mult = 4
        name = name + str(val * mult) + ".xbm"
        # feedback can be +64 and *4 that is 256 but stipples are 0 .. 255 so...
        if name == "@./stipple/stip256.xbm":
            name = "@./stipple/stip255.xbm"
        return name
        
    def getDigits(self, key):
        if "Feedback" in key:
            fb = controllist[key][0].getValue() * 10
            if fb < 0.0:
                fb = fb - controllist[key][0].fraction
            else:
                fb = fb + controllist[key][0].fraction
            fb = fb / 10
            val = "{:03.1f}".format(fb)
        else:
            val = "{:03d}".format(controllist[key][0].getValue())
        if val == "000" or val == "0.0":
            val = ""
        if not self.showNums:
            val = ""
        return val

    def getWave(self, fbk):
        if fbk < -32.0:
            return waveSquareImage
        elif fbk >= -32.0 and fbk < 32.0:
            return waveSineImage
        elif fbk >= 32.0 and fbk < 63.0:
            return waveSawImage
        else:
            return waveNoiseImage

    def draw(self):
        if not self.Showing:
            return
        self.canvas.delete("route") # delete everything already on the canvas (if any)
        OP_W = 280
        OP_H = 180
        OP1_LOCX1 = 80
        OP1_LOCY1 = 90
        OP1_LOCX2 = OP1_LOCX1 + OP_W
        OP1_LOCY2 = OP1_LOCY1 + OP_H

        OP2_LOCX1 = 450
        OP2_LOCY1 = 90
        OP2_LOCX2 = OP2_LOCX1 + OP_W
        OP2_LOCY2 = OP2_LOCY1 + OP_H

        OP3_LOCX1 = 80
        OP3_LOCY1 = 390
        OP3_LOCX2 = OP3_LOCX1 + OP_W
        OP3_LOCY2 = OP3_LOCY1 + OP_H

        OP4_LOCX1 = 450
        OP4_LOCY1 = 390
        OP4_LOCX2 = OP4_LOCX1 + OP_W
        OP4_LOCY2 = OP4_LOCY1 + OP_H

        # four coloured OP rectangles
        self.canvas.create_rectangle(OP1_LOCX1, OP1_LOCY1, OP1_LOCX2, OP1_LOCY2, fill='#FF1818', tag="route")
        self.canvas.create_rectangle(OP2_LOCX1, OP2_LOCY1, OP2_LOCX2, OP2_LOCY2, fill='#00FF00', tag="route")
        self.canvas.create_rectangle(OP3_LOCX1, OP3_LOCY1, OP3_LOCX2, OP3_LOCY2, fill='#2828FF', tag="route")
        self.canvas.create_rectangle(OP4_LOCX1, OP4_LOCY1, OP4_LOCX2, OP4_LOCY2, fill='#FFFF00', tag="route")

        # labels for the rectangles
        self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 40, anchor=tk.NW, text="OP1", fill='#000000', font=('Helvetica','48','bold'), tag="route")
        self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 40, anchor=tk.NW, text="OP2", fill='#000000', font=('Helvetica','48','bold'), tag="route")
        self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 40, anchor=tk.NW, text="OP3", fill='#000000', font=('Helvetica','48','bold'), tag="route")
        self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 40, anchor=tk.NW, text="OP4", fill='#000000', font=('Helvetica','48','bold'), tag="route")

        self.canvas.create_text(280, 640, anchor=tk.NW, text="Click anywhere to show/hide values", fill='#FFFFFF', font=('Helvetica','18'), tag="route")

        if controllist["OP1:Fixed"][0].getValue():
            self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP1:Freq"][0].getValue() * 100 + controllist["OP1:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP1:Ratio"][0].getValue() * 100 + controllist["OP1:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP1:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP1:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")
        
        if controllist["OP2:Fixed"][0].getValue():
            self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP2:Freq"][0].getValue() * 100 + controllist["OP2:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP2:Ratio"][0].getValue() * 100 + controllist["OP2:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP2:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP2:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")

        if controllist["OP3:Fixed"][0].getValue():
            self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP3:Freq"][0].getValue() * 100 + controllist["OP3:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP3:Ratio"][0].getValue() * 100 + controllist["OP3:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP3:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP3:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")

        if controllist["OP4:Fixed"][0].getValue():
            self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP4:Freq"][0].getValue() * 100 + controllist["OP4:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP4:Ratio"][0].getValue() * 100 + controllist["OP4:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP4:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP4:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")


        # the OP1 to OP2 route (horiz, red)
        self.canvas.create_line(OP1_LOCX2, OP1_LOCY1 + 20, OP2_LOCX1, OP1_LOCY1 + 20, fill='#FF1818', arrow=LAST, width=16, stipple=self.getStipple("OP2:OP1In"), tag="route")
        self.canvas.create_text(OP1_LOCX2 - 50, OP1_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP2:OP1In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP2 to OP1 route (horiz, green)
        self.canvas.create_line(OP1_LOCX2, OP1_LOCY1 + 50, OP2_LOCX1, OP1_LOCY1 + 50, fill='#00FF00', arrow=FIRST, width=16, stipple=self.getStipple("OP1:OP2In"), tag="route")
        self.canvas.create_text(OP2_LOCX1 + 5, OP1_LOCY1 + 50, anchor=tk.W, text=self.getDigits("OP1:OP2In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP3 to OP4 route (horiz, bllue)
        self.canvas.create_line(OP3_LOCX2, OP3_LOCY2 - 20, OP4_LOCX1, OP3_LOCY2 - 20, fill='#2828FF', arrow=LAST, width=16, stipple=self.getStipple("OP4:OP3In"), tag="route")
        self.canvas.create_text(OP3_LOCX2 - 50, OP3_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP4:OP3In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP4 to OP3 route (horiz, yellow)
        self.canvas.create_line(OP3_LOCX2, OP3_LOCY2 - 50, OP4_LOCX1, OP3_LOCY2 - 50, fill='#FFFF00', arrow=FIRST, width=16, stipple=self.getStipple("OP3:OP4In"), tag="route")
        self.canvas.create_text(OP4_LOCX1 + 5, OP3_LOCY2 - 50, anchor=tk.W, text=self.getDigits("OP3:OP4In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP1 to OP3 route (vert, red)
        self.canvas.create_line(OP1_LOCX1 + 20, OP1_LOCY2, OP1_LOCX1 + 20, OP3_LOCY1, fill='#FF1818', arrow=LAST, width=16, stipple=self.getStipple("OP3:OP1In"), tag="route")
        self.canvas.create_text(OP1_LOCX1 + 5, OP1_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP3:OP1In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP3 to OP1 route (vert, blue)
        self.canvas.create_line(OP1_LOCX1 + 50, OP1_LOCY2, OP1_LOCX1 + 50, OP3_LOCY1, fill='#2828FF', arrow=FIRST, width=16, stipple=self.getStipple("OP1:OP3In"), tag="route")
        self.canvas.create_text(OP3_LOCX1 + 30, OP3_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP1:OP3In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP2 to OP4 route (vert, green)
        self.canvas.create_line(OP4_LOCX2 - 20, OP2_LOCY2, OP4_LOCX2 - 20, OP4_LOCY1, fill='#00FF00', arrow=LAST, width=16, stipple=self.getStipple("OP4:OP2In"), tag="route")
        self.canvas.create_text(OP4_LOCX2 - 40, OP2_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP4:OP2In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP4 ot OP2 route (vert, yellow)
        self.canvas.create_line(OP4_LOCX2 - 50, OP2_LOCY2, OP4_LOCX2 - 50, OP4_LOCY1, fill='#FFFF00', arrow=FIRST, width=16, stipple=self.getStipple("OP2:OP4In"), tag="route")
        self.canvas.create_text(OP4_LOCX2 - 70, OP4_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP2:OP4In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP1 to OP4 route (diag, red)
        self.canvas.create_line(OP1_LOCX2 - 8, OP1_LOCY2 - 30, OP4_LOCX1 + 30, OP4_LOCY1, fill='#FF1818', arrow=LAST, width=16, stipple=self.getStipple("OP4:OP1In"), tag="route")
        self.canvas.create_text(OP1_LOCX2 - 50, OP1_LOCY2 - 30, anchor=tk.W, text=self.getDigits("OP4:OP1In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP4 to OP1 route (diag, yellow)
        self.canvas.create_line(OP1_LOCX2 - 30, OP1_LOCY2, OP4_LOCX1 + 8, OP4_LOCY1 + 30, fill='#FFFF00', arrow=FIRST, width=16, stipple=self.getStipple("OP1:OP4In"), tag="route")
        self.canvas.create_text(OP4_LOCX1 + 8 , OP4_LOCY1 + 30, anchor=tk.W, text=self.getDigits("OP1:OP4In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP3 to OP2 route (diag, blue)
        self.canvas.create_line(OP3_LOCX2 - 8, OP3_LOCY1 + 30, OP2_LOCX1 + 30, OP2_LOCY2, fill='#2828FF', arrow=LAST, width=16, stipple=self.getStipple("OP2:OP3In"), tag="route")
        self.canvas.create_text(OP3_LOCX2 - 50 , OP3_LOCY1 + 30, anchor=tk.W, text=self.getDigits("OP2:OP3In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP2 to OP3 route (diag, green)
        self.canvas.create_line(OP3_LOCX2 - 30, OP3_LOCY1, OP2_LOCX1 + 8, OP2_LOCY2 - 30, fill='#00FF00', arrow=FIRST, width=16, stipple=self.getStipple("OP3:OP2In"), tag="route")
        self.canvas.create_text(OP2_LOCX1 + 8 , OP2_LOCY2 - 30, anchor=tk.W, text=self.getDigits("OP3:OP2In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
      
        # the "OUTPUT" text label
        self.canvas.create_text(OP2_LOCX2 + 20, OP2_LOCY2 + 40, anchor=tk.NW, text="OUTPUT", fill='#FFFFFF', font=('Helvetica','30','bold'), tag="route")

        # the OP1 route to OUTPUT (red)
        stip = self.getStipple("OP1:Output")
        self.canvas.create_line(OP1_LOCX1 + (OP_W / 2), OP1_LOCY1, OP1_LOCX1 + (OP_W / 2), OP1_LOCY1 - 68, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 + (OP_W / 2), OP1_LOCY1 - 60, OP2_LOCX2 + 148, OP1_LOCY1 - 60, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 140, OP1_LOCY1 - 60, OP2_LOCX2 + 140, OP2_LOCY2 + 30, fill='#FF1818', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP1_LOCX1 + (OP_W / 2), OP1_LOCY1 + 20, anchor=tk.CENTER, text=self.getDigits("OP1:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP2 route to OUPUT (green)
        stip = self.getStipple("OP2:Output")
        self.canvas.create_line(OP2_LOCX2, OP2_LOCY1 + (OP_H / 2), OP2_LOCX2 + 58, OP2_LOCY1 + (OP_H / 2), fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 50, OP2_LOCY1 + (OP_H / 2), OP2_LOCX2 + 50, OP2_LOCY2 + 30, arrow=LAST, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP2_LOCX2 - 50, OP2_LOCY1 + (OP_H / 2), anchor=tk.W, text=self.getDigits("OP2:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP3 route to OUPUT (blue)
        stip = self.getStipple("OP3:Output")
        self.canvas.create_line(OP3_LOCX1 + (OP_W / 2), OP3_LOCY2, OP1_LOCX1 + (OP_W / 2), OP3_LOCY2 + 68, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 + (OP_W / 2), OP3_LOCY2 + 60, OP4_LOCX2 + 148, OP3_LOCY2 + 60, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 140, OP3_LOCY2 + 60, OP4_LOCX2 + 140, OP4_LOCY1 - 30, fill='#2828FF', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP3_LOCX1 + (OP_W / 2), OP3_LOCY2 - 20, anchor=tk.CENTER, text=self.getDigits("OP3:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP4 route to OUTPUT (yellow)
        stip = self.getStipple("OP4:Output")
        self.canvas.create_line(OP4_LOCX2, OP4_LOCY1 + (OP_H / 2), OP4_LOCX2 + 58, OP4_LOCY1 + (OP_H / 2), fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 50, OP4_LOCY1 + (OP_H / 2), OP4_LOCX2 + 50, OP4_LOCY1 - 30, arrow=LAST, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP4_LOCX2 - 50, OP4_LOCY1 + (OP_H / 2), anchor=tk.W, text=self.getDigits("OP4:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP1 feedback loop (red)
        op1fbk = controllist["OP1:Feedback"][0].getValue()
        wave_file = self.getWave(op1fbk)
        stip = self.getStipple("OP1:Feedback")
        self.canvas.create_line(OP1_LOCX1 + 50, OP1_LOCY1, OP1_LOCX1 + 50, OP1_LOCY1 - 38, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 + 50, OP1_LOCY1 - 30, OP1_LOCX1 - 38, OP1_LOCY1 - 30, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 - 30, OP1_LOCY1 - 30, OP1_LOCX1 - 30, OP1_LOCY1 + 30, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 - 38, OP1_LOCY1 + 30, OP1_LOCX1, OP1_LOCY1 + 30, fill='#FF1818', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP1_LOCX1 + 30, OP1_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP1:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op1fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP1_LOCX1 + 30, OP1_LOCY1 + 40, anchor=tk.NW, image = wave_file, tag="route")

        # the OP2 feedback loop (green)
        op2fbk = controllist["OP2:Feedback"][0].getValue()
        wave_file = self.getWave(op2fbk)
        stip = self.getStipple("OP2:Feedback")
        self.canvas.create_line(OP2_LOCX2 - 50, OP2_LOCY1, OP2_LOCX2 - 50, OP2_LOCY1 - 38, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 - 50, OP2_LOCY1 - 30, OP2_LOCX2 + 38, OP2_LOCY1 - 30, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 30, OP2_LOCY1 - 30, OP2_LOCX2 + 30, OP2_LOCY1 + 30, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 38, OP2_LOCY1 + 30, OP2_LOCX2, OP2_LOCY1 + 30, fill='#00FF00', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP2_LOCX2 - 70, OP2_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP2:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op2fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP2_LOCX2 - 70, OP2_LOCY1 + 40, anchor=tk.NW, image = wave_file, tag="route")

        # the OP3 feedback loop (blue)
        op3fbk = controllist["OP3:Feedback"][0].getValue()
        wave_file = self.getWave(op3fbk)
        stip = self.getStipple("OP3:Feedback")
        self.canvas.create_line(OP3_LOCX1 + 50, OP3_LOCY2, OP3_LOCX1 + 50, OP3_LOCY2 + 38, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 + 50, OP3_LOCY2 + 30, OP3_LOCX1 - 38, OP3_LOCY2 + 30, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 - 30, OP3_LOCY2 - 30, OP3_LOCX1 - 30, OP3_LOCY2 + 30, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 - 38, OP3_LOCY2 - 30, OP3_LOCX1, OP3_LOCY2 - 30, fill='#2828FF', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP3_LOCX1 + 30, OP3_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP3:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op3fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP3_LOCX1 + 30, OP3_LOCY2 - 70, anchor=tk.NW, image = wave_file, tag="route")

        # the OP4 feedback loop (yellow)
        op4fbk = controllist["OP4:Feedback"][0].getValue()
        wave_file = self.getWave(op4fbk)
        stip = self.getStipple("OP4:Feedback")
        self.canvas.create_line(OP4_LOCX2 - 50, OP4_LOCY2, OP4_LOCX2 - 50, OP4_LOCY2 + 38, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 - 50, OP4_LOCY2 + 30, OP4_LOCX2 + 38, OP4_LOCY2 + 30, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 30, OP4_LOCY2 + 30, OP4_LOCX2 + 30, OP4_LOCY2 - 30, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 38, OP4_LOCY2 - 30, OP4_LOCX2, OP4_LOCY2 - 30, fill='#FFFF00', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP4_LOCX2 - 70, OP4_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP4:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op4fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP4_LOCX2 - 70, OP4_LOCY2 - 70, anchor=tk.NW, image = wave_file, tag="route")

# The setup class draws a standalone window with its own user interaction where various functions can be performed.
# Two list boxes list the MIDI IN and OUT ports that Mido can "see". The user can then select one in each list box
# press a button to open that port. If just viewing only MIDI IN is needed but if planning to send the patch back
# to XFM then OUT must be set too.
# Beneath that is a check box. This selects whether the editor should automatically write a JSON copy of the patch
# data after each patch is received. 
# On the right the window has dump displays of the raw sysex each time new data is received and a secondary dump of
# that data after it has been through 7 to 8 bit conversion. The CRC calculated by the editor as well as the CRC that
# arrived in packet 3 are both shown (basically as debug to make sure it's beeing calculated right). Also sort of debug
# but possibly useful when there isn't an XFM to hand is the ability to load sysex (just packet 2) from a file on disk
class SetupWindow:
    def __init__(self):
        self.setupWin = Toplevel(window)
        self.setupWin.geometry("940x650")
        self.setupWin.title("Setup")
        self.setupWin.resizable(False, False)
        self.setupWin.protocol("WM_DELETE_WINDOW", self.toggle_window)
        self.canvas = Canvas(self.setupWin, width = 940, height = 650, bg='#313131')
        self.canvas.place(x = 0, y = 0)

        self.listbox = Listbox(self.setupWin, width = 50)
        self.listbox.place(x = 20, y = 50)
        self.midiButton = Button(self.setupWin, text = "Open MIDI IN port")
        self.midiButton.place(x = 120, y = 230)
        self.midiButton.bind('<Button>', self.openMIDI)
        self.midiLabel = Label(self.setupWin, text="MIDI IN port: NOT SET", bg='#313131', fg='#FFFFFF')
        self.midiLabel.place(x = 120, y = 20)

        self.listboxOut = Listbox(self.setupWin, width = 50)
        self.listboxOut.place(x = 20, y = 300)
        self.midiButtonOut = Button(self.setupWin, text = "Open MIDI OUT port")
        self.midiButtonOut.place(x = 120, y = 480)
        self.midiButtonOut.bind('<Button>', self.openMIDIOut)
        self.midiLabelOut = Label(self.setupWin, text="MIDI OUT port: NOT SET", bg='#313131', fg='#FFFFFF')
        self.midiLabelOut.place(x = 120, y = 270)

        self.dumpLabel = Label(self.setupWin, text = "Dump of RAW received sysex (red = changed)", bg='#313131', fg = '#FFFFFF')
        self.dumpLabel.place(x = 430, y = 20)
        self.LoadSyxButton = Button(self.setupWin, text = "Load SYX file")
        self.LoadSyxButton.place(x = 750, y = 20)
        self.LoadSyxButton.bind('<Button>', self.LoadSyx)
        self.dump8Label = Label(self.setupWin, text = "Dump of sysex after 7 to 8 bit conversion", bg='#313131', fg = '#FFFFFF')
        self.dump8Label.place(x = 430, y = 330)
        self.saveLoadState = IntVar()
        self.saveLoadState.set(0)
        self.saveLoad = Checkbutton(self.setupWin, text="Save JSON when patches received", variable=self.saveLoadState, bg='#313131', fg = '#FFFFFF', selectcolor='#313131' )
        self.saveLoad.place(x = 50, y = 580)
        self.showNums = True
        self.portsListed = False
        self.portsOutListed = False
        self.bytes = b''
        self.bytes8 = b''
        self.crchex = ""
        self.hide()

    def toggle_window(self):
        if self.Showing:
            self.hide()
        else:
            self.show()

    def show(self):
        self.setupWin.deiconify()
        self.Showing = True
        self.draw()

    def hide(self):
        self.setupWin.withdraw()
        self.Showing = False

    def draw(self):
        if not self.Showing:
            return
        # print("len of bytes = " + str(len(self.bytes)))
        if len(self.bytes) == 0:
            return
        if self.bytes[0x2A] == 4:
            offset = 0
            byteLimit = len(self.bytes) - 1
        else:
            offset = 5
            byteLimit = len(self.bytes) - 6
        self.canvas.delete("dump")
        for y in range(1, 14):
            Ypos = (y * 20) + 50
            addr = str(format(y * 16, '02X')) + " :"
            self.canvas.create_text(400, Ypos, anchor=tk.NW, text = addr, fill='#8080FF', tag="dump")
        for x in range(16):
            Xpos = x * 20 + 430
            addr = str(format(x, '02X'))
            self.canvas.create_text(Xpos, 50, anchor=tk.NW, text = addr, fill='#80FF80', tag="dump")
        for x in range(16, byteLimit):
            byt = self.bytes[x + offset]
            tx = str(format(byt, '02X'))
            Xoff = (x * 20) % 320
            Yoff = int(x / 16) * 20
            # because "ABCD" and "A.BC.D" type patches (dots or not) vary by 5 bytes in length then don't
            # compare received to old if the lenth just changed (coz everything will have moved!)
            if len(self.bytes) != len(self.oldBytes):
                self.canvas.create_text(430 + Xoff, 50 + Yoff, anchor=tk.NW, text = tx, fill='#FFFFFF', tag="dump")
            else:
                # but if this and previous are the same length then draw == bytes in black and changed in red
                if self.bytes[x + offset] == self.oldBytes[x + offset]:
                    self.canvas.create_text(430 + Xoff, 50 + Yoff, anchor=tk.NW, text = tx, fill='#FFFFFF', tag="dump")
                else:
                    self.canvas.create_text(430 + Xoff, 50 + Yoff, anchor=tk.NW, text = tx, fill='#FF8080', tag="dump")

        # now do all that again but for the bytes AFTER the 7 to 8 bit conversion...
        for y in range(0, 12):
            Ypos = (y * 20)
            addr = str(format(y * 16, '02X')) + " :"
            self.canvas.create_text(400, Ypos + 370, anchor=tk.NW, text = addr, fill='#8080FF', tag="dump")
        byteLimit = len(self.bytes8)
        col = 0
        chrtxt = ""
        for x in range(0, byteLimit):
            byt = self.bytes8[x]
            tx = str(format(byt, '02X'))
            if byt > 31 and byt < 128:
                chrtxt = chrtxt + chr(byt)
            else:
                chrtxt = chrtxt + '.'
            col = col + 1
            Xoff = (x * 20) % 320
            Yoff = int(x / 16) * 20
            # because "ABCD" and "A.BC.D" type patches (dots or not) vary by 5 bytes in length then don't
            # compare received to old if the lenth just changed (coz everything will have moved!)
            if len(self.bytes8) != len(self.old8bytes):
                self.canvas.create_text(430 + Xoff, 370 + Yoff, anchor=tk.NW, text = tx, fill='#FFFFFF', tag="dump")
            else:
                # but if this and previous are the same length then draw == bytes in black and changed in red
                if self.bytes8[x] == self.old8bytes[x]:
                    self.canvas.create_text(430 + Xoff, 370 + Yoff, anchor=tk.NW, text = tx, fill='#FFFFFF', tag="dump")
                else:
                    self.canvas.create_text(430 + Xoff, 370 + Yoff, anchor=tk.NW, text = tx, fill='#FF8080', tag="dump")
            if col == 16:
                self.canvas.create_text(760, 370 + Yoff, anchor=tk.NW, text = chrtxt, font=("Consolas", 10), fill = '#80FF80', tag="dump")
                col = 0
                chrtxt = ""
        if len(chrtxt):
            self.canvas.create_text(760, 370 + Yoff, anchor=tk.NW, text = chrtxt, font=("Consolas", 10), fill = '#80FF80', tag="dump")
        
        crctxt = "CRC32 (calculated) = " + str(format(self.crc, '08X')) + "   from XFM = " + self.crchex
        # show the calculated crc32 which will be key to sending this patch data back to XFM
        self.canvas.create_text(430, 350, anchor=tk.NW, text = crctxt, fill='#8080FF', font=("Consolas", 10), tag="dump")


    def setPorts(self, inports):
        if len(inports) > 0:
            for port in inports:
                self.listbox.insert(END, port)
            self.listbox.selection_anchor(0)
            self.portsListed = True

    def setOutPorts(self, outports):
        if len(outports) > 0:
            for port in outports:
                self.listboxOut.insert(END, port)
            self.listboxOut.selection_anchor(0)
            self.portsOutListed = True

    def openMIDI(self, event):
        if not self.portsListed:
            return
        global port
        global portOpen
        print("Opening input")
        if portOpen:
            port.close()
        print("going to open: " + self.listbox.get(ANCHOR))
        port = mido.open_input(self.listbox.get(ANCHOR), callback=rxmsg)
        self.midiLabel.config(text = "MIDI IN port: " + self.listbox.get(ANCHOR))
        portOpen = True
        window.title("Quick Edit for Liven XFM")

    def openMIDIOut(self, event):
        if not self.portsOutListed:
            return
        global portOut
        global portOutOpen
        print("Opening output")
        if portOutOpen:
            portOut.close()
        print("going to open: " + self.listboxOut.get(ANCHOR))
        portOut = mido.open_output(self.listboxOut.get(ANCHOR))
        self.midiLabelOut.config(text = "MIDI OUT port: " + self.listboxOut.get(ANCHOR))
        portOutOpen = True
        window.title("Quick Edit for Liven XFM")

    def setBytes(self, bytes):
        self.oldBytes = self.bytes
        self.bytes = bytes
        #self.draw()

    def set8bytes(self, bytes):
        self.old8bytes = self.bytes8
        self.bytes8 = bytes
        self.crc = crc32(0, bytes, len(bytes))

    def setCRC(self, hexdigs):
        self.crchex = hexdigs

    def LoadSyx(self, event):
        print("oof")
        filename = fd.askopenfilename(title="Load Sysex file", filetypes=[("Sysex files", "*.syx")])
        print(filename)
        with open(filename, 'rb') as f:
            bytes = f.read()
            loadRawBytes(bytes, False)

# This just writes a hex dump (including ASCII chars) to the console. It's pretty much the same as
# the hex dumps in the setup window  except that the copy at the console remains in the log and can
# be referred back to
def print_dump(bytes):
    txt = ""
    print("00 :", end=" ")
    for x in range(len(bytes)):
            byt = bytes[x]
            print(format(byt, '02x'), end = " ")
            if byt > 31 and byt < 128:
                txt = txt + chr(byt)
            else:
                txt = txt + '.'
            if x % 16 == 15:
                print(txt)
                txt = ""
                if x != (len(bytes) - 1):
                    print(format(x + 1, '02x'), ":", end=" ")
    if len(txt):
        left = 16 - len(txt)
        for i in range(left):
            print("   ", end="")
        print(txt)
    print()

# all valuse have to pack into the 128 steps from 0x00 to 0x7F but some are
# really "signed" values like -18..+18, -63..+63, -63..+64 so as soon as the
# dump is received convert such values to signed which basically means (as this
# is in 7 bits not 8 bits) that >64 should be -(128 - n)
def make_signed(byte):
    retval = int(byte)
    if byte > 127:
        retval = int (-1 * (256 - byte))
    return retval

# This is the second version of decode - it's MUCH easier after the 7 to 8 bit
# decode because the function does not need to worry about +128 shifts as all that has
# already been applied. Also, rather than using raw sysex offsets to find data items
# the offsets in this are based on 0 being the start of the TPDT payload after initial
# headers have been skipped so the routine can handle patches whether they have four or
# 8 byte names (that is no dots or with dots).
def decode_8bit(bytes, patch):
# Patch (after conversion to 8bit) has this layout
# 00: FMTC <u32 total_len> <u32 0> <u32 2>
# 10: FMNM <u32 len = 14 or 18> <u32 0> <u32 name_len> <u8 name characters (4 or 8)>
# 28/2C: TPDT <u32 len> <u32 0> <u32 1> <u8 payload>
    namelen = bytes[0x1C]
    txt = ""
    for n in range(namelen):
        txt += chr(bytes[0x20 + n])
    patch['Name'] = txt
    if bytes[0x14] == 0x14: # len of FMNM means it has has just 4 byte payload
        payload = bytes[0x34:]
    else: # len is 0x18 so TPDT and rest of patch is 4 bytes further on
        payload = bytes[0x38:]

    print_dump(payload)
    patch["OP1"]['Feedback'] = (make_signed(payload[0x5C]) * 10) + make_signed(payload[0])
    patch["OP1"]['OP2In'] = payload[0x5D]
    patch["OP1"]['OP3In'] = payload[0x5E]
    patch["OP1"]['OP4In'] = payload[0x5F]
    patch["OP1"]['Output'] = payload[0x6C]
    patch["OP1"]['PitchEnv'] = payload[0x78]
    patch["OP1"]['Fixed'] = payload[4]
    ratio = ((payload[0x15] * 256) + payload[0x14] )
    patch["OP1"]['Ratio'] = ratio
    freq = ((payload[7] * 65536) + (payload[6] * 256) + payload[5])
    patch["OP1"]["Freq"] = freq
    patch["OP1"]['Detune'] = make_signed(payload[0x17])
    patch["OP1"]['Level'] = payload[0x16]
    patch["OP1"]['VelSens'] = payload[0x70]
    patch["OP1"]['Time'] = payload[0x74]
    patch["OP1"]['UpCurve'] = make_signed(payload[0x7C])
    patch["OP1"]['DnCurve'] = make_signed(payload[0x7D])
    patch["OP1"]['Scale'] = payload[0x4F]
    patch["OP1"]['ALevel'] = payload[0x28]
    patch["OP1"]['ATime'] = payload[0x24]
    patch["OP1"]['DLevel'] = payload[0x29]
    patch["OP1"]['DTime'] = payload[0x25]
    patch["OP1"]['SLevel'] = payload[0x2A]
    patch["OP1"]['STime'] = payload[0x26]
    patch["OP1"]['RLevel'] = payload[0x2B]
    patch["OP1"]['RTime'] = payload[0x27]
    patch["OP1"]['LGain'] = make_signed(payload[0x4C])
    patch["OP1"]['RGain'] = make_signed(payload[0x4D])
    patch["OP1"]['LCurve'] = payload[0x4E] & 0x01
    patch["OP1"]['RCurve'] = 1 if payload[0x4E] & 0x10 else 0

    patch["OP2"]['Feedback'] = (make_signed(payload[0x61]) * 10) + make_signed(payload[1])
    patch["OP2"]['OP1In'] = payload[0x60]
    patch["OP2"]['OP3In'] = payload[0x62]
    patch["OP2"]['OP4In'] = payload[0x63]
    patch["OP2"]['Output'] = payload[0x6D]
    patch["OP2"]['PitchEnv'] = payload[0x79]
    patch["OP2"]['Fixed'] = payload[8]
    ratio = ((payload[0x19] * 256) + payload[0x18] )
    patch["OP2"]['Ratio'] = ratio
    freq = ((payload[0xB] * 65536) + (payload[0xA] * 256) + payload[9])
    patch["OP2"]["Freq"] = freq
    patch["OP2"]['Detune'] = make_signed(payload[0x1B])
    patch["OP2"]['Level'] = payload[0x1A]
    patch["OP2"]['VelSens'] = payload[0x71]
    patch["OP2"]['Time'] = payload[0x75]
    patch["OP2"]['UpCurve'] = make_signed(payload[0x7E])
    patch["OP2"]['DnCurve'] = make_signed(payload[0x7F])
    patch["OP2"]['Scale'] = payload[0x53]
    patch["OP2"]['ALevel'] = payload[0x30]
    patch["OP2"]['ATime'] = payload[0x2C]
    patch["OP2"]['DLevel'] = payload[0x31]
    patch["OP2"]['DTime'] = payload[0x2D]
    patch["OP2"]['SLevel'] = payload[0x32]
    patch["OP2"]['STime'] = payload[0x2E]
    patch["OP2"]['RLevel'] = payload[0x33]
    patch["OP2"]['RTime'] = payload[0x2F]
    patch["OP2"]['LGain'] = make_signed(payload[0x50])
    patch["OP2"]['RGain'] = make_signed(payload[0x51])
    patch["OP2"]['LCurve'] = payload[0x52] & 0x01
    patch["OP2"]['RCurve'] = 1 if payload[0x52] & 0x10 else 0

    #print("OP3 Fbck units =", hex(payload[0x66]), "frac =", hex(payload[2]), end="")
    #print("signed that is", hex(make_signed(payload[0x66])), "and ", hex(make_signed(payload[2])))
    patch["OP3"]['Feedback'] = (make_signed(payload[0x66]) * 10) + make_signed(payload[2])
    patch["OP3"]['OP1In'] = payload[0x64]
    patch["OP3"]['OP2In'] = payload[0x65]
    patch["OP3"]['OP4In'] = payload[0x67]
    patch["OP3"]['Output'] = payload[0x6E]
    patch["OP3"]['PitchEnv'] = payload[0x7A]
    patch["OP3"]['Fixed'] = payload[0xC]
    ratio = ((payload[0x1D] * 256) + payload[0x1C] )
    patch["OP3"]['Ratio'] = ratio
    freq = ((payload[0xF] * 65536) + (payload[0xE] * 256) + payload[0xD])
    patch["OP3"]["Freq"] = freq
    patch["OP3"]['Detune'] = make_signed(payload[0x1F])
    patch["OP3"]['Level'] = payload[0x1E]
    patch["OP3"]['VelSens'] = payload[0x72]
    patch["OP3"]['Time'] = payload[0x76]
    patch["OP3"]['UpCurve'] = make_signed(payload[0x80])
    patch["OP3"]['DnCurve'] = make_signed(payload[0x81])
    patch["OP3"]['Scale'] = payload[0x57]
    patch["OP3"]['ALevel'] = payload[0x38]
    patch["OP3"]['ATime'] = payload[0x34]
    patch["OP3"]['DLevel'] = payload[0x39]
    patch["OP3"]['DTime'] = payload[0x35]
    patch["OP3"]['SLevel'] = payload[0x3A]
    patch["OP3"]['STime'] = payload[0x36]
    patch["OP3"]['RLevel'] = payload[0x3B]
    patch["OP3"]['RTime'] = payload[0x37]
    patch["OP3"]['LGain'] = make_signed(payload[0x54])
    patch["OP3"]['RGain'] = make_signed(payload[0x55])
    patch["OP3"]['LCurve'] = payload[0x56] & 0x01
    patch["OP3"]['RCurve'] = 1 if payload[0x56] & 0x10 else 0

    patch["OP4"]['Feedback'] = (make_signed(payload[0x6B]) * 10) + make_signed(payload[3])
    patch["OP4"]['OP1In'] = payload[0x68]
    patch["OP4"]['OP2In'] = payload[0x69]
    patch["OP4"]['OP3In'] = payload[0x6A]
    patch["OP4"]['Output'] = payload[0x6F]
    patch["OP4"]['PitchEnv'] = payload[0x7B]
    patch["OP4"]['Fixed'] = payload[0x10]
    ratio = ((payload[0x21] * 256) + payload[0x20] )
    patch["OP4"]['Ratio'] = ratio
    freq = ((payload[0x13] * 65536) + (payload[0x12] * 256) + payload[0x11])
    patch["OP4"]["Freq"] = freq
    patch["OP4"]['Detune'] = make_signed(payload[0x23])
    patch["OP4"]['Level'] = payload[0x22]
    patch["OP4"]['VelSens'] = payload[0x73]
    patch["OP4"]['Time'] = payload[0x77]
    patch["OP4"]['UpCurve'] = make_signed(payload[0x82])
    patch["OP4"]['DnCurve'] = make_signed(payload[0x83])
    patch["OP4"]['Scale'] = payload[0x5B]
    patch["OP4"]['ALevel'] = payload[0x40]
    patch["OP4"]['ATime'] = payload[0x3C]
    patch["OP4"]['DLevel'] = payload[0x41]
    patch["OP4"]['DTime'] = payload[0x3D]
    patch["OP4"]['SLevel'] = payload[0x42]
    patch["OP4"]['STime'] = payload[0x3E]
    patch["OP4"]['RLevel'] = payload[0x43]
    patch["OP4"]['RTime'] = payload[0x3F]
    patch["OP4"]['LGain'] = make_signed(payload[0x58])
    patch["OP4"]['RGain'] = make_signed(payload[0x59])
    patch["OP4"]['LCurve'] = payload[0x5A] & 0x01
    patch["OP4"]['RCurve'] = 1 if payload[0x5A] & 0x10 else 0

    patch["Pitch"]['ALevel'] = make_signed(payload[0x48])
    patch["Pitch"]['ATime'] = payload[0x44]
    patch["Pitch"]['DLevel'] = make_signed(payload[0x49])
    patch["Pitch"]['DTime'] = payload[0x45]
    patch["Pitch"]['SLevel'] = make_signed(payload[0x4A])
    patch["Pitch"]['STime'] = payload[0x46]
    patch["Pitch"]['RLevel'] = make_signed(payload[0x4B])
    patch["Pitch"]['RTime'] = payload[0x47]

    patch["Mixer"]['Level'] = make_signed(payload[0x84])


# This has never been tested in anger because at the time this was written
# it wasn't possible to calculate CRC32. This will be changed to use 
# proper (0 based) offsets and to create the FMTC/FMNM/TPDT headers in msg2
def encode_bytes(patch):
    SOUND_LEGACY = 0
    SOUND_BANK = 1
    PATTERN = 2
    SOUND = 4
    
    if len(patch['Name']) == 4:
        size = 0xBC
        namelen = b'\x14\x00\x00\x00'
    else:
        # it has dots so there are 4 more bytes
        size = 0xC0
        namelen = b'\x18\x00\x00\x00'

    # start of is the fixed header (with 01/02/03 message type at end). This (incl 01/02/03) is the 
    # one bit that does not get put through 8 to 7 bit conversion
    hdr = b'\xF0\x00\x48\x04\x00\x00\x03\x60'
    fm_type_container = b'FMTC'
    fm_name = b'FMNM'
    the_patch_data = b'TPDT'
    u32_0_le = b'\x00\x00\x00\x00'
    u32_1_le = b'\x01\x00\x00\x00'
    u32_2_le = b'\x02\x00\x00\x00'
    u32_4_le = b'\x04\x00\x00\x00'

    msg2payload = bytearray(0x88) # payload is 0x88 because TPDT is always 0x98 bytes (from TPDT onwards) and header is 0x10

    # Feedback is tricky because it's split over two bytes with .0 .. .9 fraction stored in one
    # place and feedback/10 (0..64) in another - but it is signed so the high part is easy as -1..-63
    # is simply 0xFF .. 0xCD but the fractional part is also stored signed so -.1 to -.9 needs
    # special handling. The following strips the overall sign, converts to absolute then does the %10 to
    # split the fraction then re-applies the sign to the result and converts to 1 byte
    fbck = patch["OP1"]['Feedback']
    fbck_sign = 1
    if fbck < 0:
        fbck_sign = -1
    fbck_frac = ((abs(fbck) % 10) * fbck_sign) & 0xFF
    msg2payload[0] = fbck_frac                # -63.0 .. +64.0 (+1.0)
    msg2payload[0x5C] = int(fbck / 10) & 0xFF       # -63.0 .. +64.0 (+1.0)
    msg2payload[0x5D] = patch["OP1"]['OP2In']                    # 0 .. 127 (+1)
    msg2payload[0x5E] = patch["OP1"]['OP3In']
    msg2payload[0x5F] = patch["OP1"]['OP4In']
    msg2payload[0x6C] = patch["OP1"]['Output']                   # 0..127 (+1)
    msg2payload[0x78] = patch["OP1"]['PitchEnv']                      # OFF / ON
    msg2payload[4] = patch["OP1"]['Fixed']                    # OFF / ON
    ratio = patch["OP1"]['Ratio']
    msg2payload[0x14] = ratio & 0xFF           # 0.50 .. 32.00 (+.01) / 1 .. 9755 (+1)
    msg2payload[0x15] = int(ratio / 256)        # wonder why I'm not using >> 8 ??
    freq = patch["OP1"]["Freq"]
    msg2payload[5] = (freq & 0x0000FF)
    msg2payload[6] = (freq & 0x00FF00) >> 8
    msg2payload[7] = (freq & 0xFF0000) >> 16
    msg2payload[0x17] = patch["OP1"]['Detune'] & 0xFF                  # -63 .. 63 (+1)
    msg2payload[0x16] = patch["OP1"]['Level']                    # 0 .. 127 (+1)
    msg2payload[0x70] = patch["OP1"]['VelSens']                  # 0 .. 127 (+1)
    msg2payload[0x74] = patch["OP1"]['Time']                     # 0 .. 127 (+1)
    msg2payload[0x7C] = patch["OP1"]['UpCurve'] & 0xFF                  # -18 .. +18 (+1)
    msg2payload[0x7D] = patch["OP1"]['DnCurve'] & 0xFF                  # -18 .. +18 (+1)
    msg2payload[0x4F] = patch["OP1"]['Scale']                    # C1 .. C7
    msg2payload[0x28] = patch["OP1"]['ALevel']                   # 0 .. 127 (+1)
    msg2payload[0x24] = patch["OP1"]['ATime']
    msg2payload[0x29] = patch["OP1"]['DLevel']
    msg2payload[0x25] = patch["OP1"]['DTime']
    msg2payload[0x2A] = patch["OP1"]['SLevel']
    msg2payload[0x26] = patch["OP1"]['STime']
    msg2payload[0x2B] = patch["OP1"]['RLevel']
    msg2payload[0x27] = patch["OP1"]['RTime']
    msg2payload[0x4C] = patch["OP1"]['LGain'] & 0xFF                   # -63 .. +63 (+1)
    msg2payload[0x4D] = patch["OP1"]['RGain'] & 0xFF
    curves = (patch["OP1"]['LCurve']) | (patch["OP1"]['RCurve'])  # LINE / EXP
    msg2payload[0x4E] = curves

    fbck = patch["OP2"]['Feedback']
    fbck_sign = 1
    if fbck < 0:
        fbck_sign = -1
    fbck_frac = ((abs(fbck) % 10) * fbck_sign) & 0xFF
    msg2payload[1] = fbck_frac                # -63.0 .. +64.0 (+1.0)
    msg2payload[0x61] = int(fbck / 10) & 0xFF       # -63.0 .. +64.0 (+1.0)
    msg2payload[0x60] = patch["OP2"]['OP1In']
    msg2payload[0x62] = patch["OP2"]['OP3In']
    msg2payload[0x63] = patch["OP2"]['OP4In']
    msg2payload[0x6D] = patch["OP2"]['Output']
    msg2payload[0x79] = patch["OP2"]['PitchEnv']
    msg2payload[8] = patch["OP2"]['Fixed']
    ratio = patch["OP2"]['Ratio']
    msg2payload[0x18] = ratio & 0xFF
    msg2payload[0x19] = int(ratio / 256)
    freq = patch["OP2"]["Freq"]
    msg2payload[9]   = (freq & 0x0000FF)
    msg2payload[0xA] = (freq & 0x00FF00) >> 8
    msg2payload[0xB] = (freq & 0xFF0000) >> 16
    msg2payload[0x1B] = patch["OP2"]['Detune'] & 0xFF
    msg2payload[0x1A] = patch["OP2"]['Level']
    msg2payload[0x71] = patch["OP2"]['VelSens']
    msg2payload[0x75] = patch["OP2"]['Time']
    msg2payload[0x7E] = patch["OP2"]['UpCurve'] & 0xFF
    msg2payload[0x7F] = patch["OP2"]['DnCurve'] & 0xFF
    msg2payload[0x53] = patch["OP2"]['Scale']
    msg2payload[0x30] = patch["OP2"]['ALevel']
    msg2payload[0x2C] = patch["OP2"]['ATime']
    msg2payload[0x31] = patch["OP2"]['DLevel']
    msg2payload[0x2D] = patch["OP2"]['DTime']
    msg2payload[0x32] = patch["OP2"]['SLevel']
    msg2payload[0x2E] = patch["OP2"]['STime']
    msg2payload[0x33] = patch["OP2"]['RLevel']
    msg2payload[0x2F] = patch["OP2"]['RTime']
    msg2payload[0x50] = patch["OP2"]['LGain'] & 0xFF
    msg2payload[0x51] = patch["OP2"]['RGain'] & 0xFF
    curves = (patch["OP2"]['LCurve']) | (patch["OP2"]['RCurve'])
    msg2payload[0x52] = curves

    fbck = patch["OP3"]['Feedback']
    #print("fbck from control is", hex(fbck))
    fbck_sign = 1
    if fbck < 0:
        fbck_sign = -1
    #print("fbck sign = ", fbck_sign, "abs(fbck) is", abs(fbck), "and abs(fbck) % 10 is", abs(fbck) % 10)
    fbck_frac = ((abs(fbck) % 10) * fbck_sign) & 0xFF
    #print("fraction =", fbck_frac)
    msg2payload[2] = fbck_frac                # -63.0 .. +64.0 (+1.0)
    msg2payload[0x66] = int(fbck / 10) & 0xFF       # -63.0 .. +64.0 (+1.0)
    #print("so storing", hex(msg2payload[0x66]), "and", hex(msg2payload[2]))
    msg2payload[0x64] = patch["OP3"]['OP1In']
    msg2payload[0x65] = patch["OP3"]['OP2In']
    msg2payload[0x67] = patch["OP3"]['OP4In']
    msg2payload[0x6E] = patch["OP3"]['Output']
    msg2payload[0x7A] = patch["OP3"]['PitchEnv']
    msg2payload[0xC] = patch["OP3"]['Fixed']
    ratio = patch["OP3"]['Ratio']
    msg2payload[0x1C] = ratio & 0xFF
    msg2payload[0x1D] = int(ratio / 256)
    freq = patch["OP3"]["Freq"]
    msg2payload[0xD] = (freq & 0x0000FF)
    msg2payload[0xE] = (freq & 0x00FF00) >> 8
    msg2payload[0xF] = (freq & 0xFF0000) >> 16
    msg2payload[0x1F] = patch["OP3"]['Detune'] & 0xFF
    msg2payload[0x1E] = patch["OP3"]['Level']
    msg2payload[0x72] = patch["OP3"]['VelSens']
    msg2payload[0x76] = patch["OP3"]['Time']
    msg2payload[0x80] = patch["OP3"]['UpCurve'] & 0xFF
    msg2payload[0x81] = patch["OP3"]['DnCurve'] & 0xFF
    msg2payload[0x57] = patch["OP3"]['Scale']
    msg2payload[0x38] = patch["OP3"]['ALevel']
    msg2payload[0x34] = patch["OP3"]['ATime']
    msg2payload[0x39] = patch["OP3"]['DLevel']
    msg2payload[0x35] = patch["OP3"]['DTime']
    msg2payload[0x3A] = patch["OP3"]['SLevel']
    msg2payload[0x36] = patch["OP3"]['STime']
    msg2payload[0x3B] = patch["OP3"]['RLevel']
    msg2payload[0x37] = patch["OP3"]['RTime']
    msg2payload[0x54] = patch["OP3"]['LGain'] & 0xFF
    msg2payload[0x55] = patch["OP3"]['RGain'] & 0xFF
    curves = (patch["OP3"]['LCurve']) | (patch["OP3"]['RCurve'])
    msg2payload[0x56] = curves

    fbck = patch["OP4"]['Feedback']
    fbck_sign = 1
    if fbck < 0:
        fbck_sign = -1
    fbck_frac = ((abs(fbck) % 10) * fbck_sign) & 0xFF
    msg2payload[3] = fbck_frac                # -63.0 .. +64.0 (+1.0)
    msg2payload[0x6B] = int(fbck / 10) & 0xFF       # -63.0 .. +64.0 (+1.0)
    msg2payload[0x68] = patch["OP4"]['OP1In']
    msg2payload[0x69] = patch["OP4"]['OP2In']
    msg2payload[0x6A] = patch["OP4"]['OP3In']
    msg2payload[0x6F] = patch["OP4"]['Output']
    msg2payload[0x7B] = patch["OP4"]['PitchEnv']
    msg2payload[0x10] = patch["OP4"]['Fixed']
    ratio = patch["OP4"]['Ratio']
    msg2payload[0x20] = ratio & 0xFF
    msg2payload[0x21] = int(ratio / 256)
    freq = patch["OP4"]["Freq"]
    msg2payload[0x11] = (freq & 0x0000FF)
    msg2payload[0x12] = (freq & 0x00FF00) >> 8
    msg2payload[0x13] = (freq & 0xFF0000) >> 16
    msg2payload[0x23] = patch["OP4"]['Detune'] & 0xFF
    msg2payload[0x22] = patch["OP4"]['Level']
    msg2payload[0x73] = patch["OP4"]['VelSens']
    msg2payload[0x77] = patch["OP4"]['Time']
    msg2payload[0x82] = patch["OP4"]['UpCurve'] & 0xFF
    msg2payload[0x83] = patch["OP4"]['DnCurve'] & 0xFF
    msg2payload[0x5B] = patch["OP4"]['Scale']
    msg2payload[0x40] = patch["OP4"]['ALevel']
    msg2payload[0x3C] = patch["OP4"]['ATime']
    msg2payload[0x41] = patch["OP4"]['DLevel']
    msg2payload[0x3D] = patch["OP4"]['DTime']
    msg2payload[0x42] = patch["OP4"]['SLevel']
    msg2payload[0x3E] = patch["OP4"]['STime']
    msg2payload[0x43] = patch["OP4"]['RLevel']
    msg2payload[0x3F] = patch["OP4"]['RTime']
    msg2payload[0x58] = patch["OP4"]['LGain'] & 0xFF
    msg2payload[0x59] = patch["OP4"]['RGain'] & 0xFF
    curves = (patch["OP4"]['LCurve']) | (patch["OP4"]['RCurve'])
    msg2payload[0x5A] = curves

    msg2payload[0x48] = patch["Pitch"]['ALevel'] & 0xFF         # -48 .. +48 (+1)
    msg2payload[0x44] = patch["Pitch"]['ATime']          # 0 .. 127 (+1)
    msg2payload[0x49] = patch["Pitch"]['DLevel'] & 0xFF
    msg2payload[0x45] = patch["Pitch"]['DTime']
    msg2payload[0x4A] = patch["Pitch"]['SLevel'] & 0xFF
    msg2payload[0x46] = patch["Pitch"]['STime']
    msg2payload[0x4B] = patch["Pitch"]['RLevel'] & 0xFF
    msg2payload[0x47] = patch["Pitch"]['RTime']

    msg2payload[0x84] = patch["Mixer"]['Level'] & 0xFF           # -63 .. +63 (+1)
    # patch is padded to the end with 0xFF in the last 3 bytes
    msg2payload[0x85] = 255
    msg2payload[0x86] = 255
    msg2payload[0x87] = 255

    msg1 = hdr
    msg1 += b'\x01' # sequence number start=1, data=2, crc=3
    msg1 += SOUND.to_bytes(length = 4, byteorder = 'little')
    msg1 += size.to_bytes(length = 4, byteorder = 'little')
    print("msg1 =")
    print_dump(msg1)
    msg1_7bit = convert87(msg1) # this starts at byte 9 and splits into 7's with leading shift mask
    msg1_7bit += (0xF7).to_bytes(length = 1, byteorder = 'little')
    print("msg1 (7 bit)=")
    print_dump(msg1_7bit)

    # As noted above the sysex payload in message 2 consists of:
    # 00: FMTC <u32 total_len> <u32 0> <u32 2>
    # 10: FMNM <u32 len = 14 or 18> <u32 0> <u32 name_len> <u8 name characters (4 or 8)>
    # 28/2C: TPDT <u32 len> <u32 0> <u32 1> <u8 payload>
    msg2 = hdr
    msg2 += b'\x02' # sequence number start=1, data=2, crc=3
    msg2 += fm_type_container # 'FMTC'
    msg2 += size.to_bytes(length = 4, byteorder = 'little')
    msg2 += u32_0_le
    msg2 += u32_2_le
    msg2 += fm_name # 'FMNM'
    msg2 += namelen # 0x14 or 0x18 in le u32
    msg2 += u32_0_le
    msg2 += len(patch['Name']).to_bytes(length = 4, byteorder='little')
    msg2 += bytearray(patch['Name'].encode())
    if len(patch['Name']) > 4:
        # if it's a name with dots then pad with FF at the end if less than 4 dots
        for n in range(8 - len(patch['Name'])):
            msg2 += (0xFF).to_bytes(length = 1, byteorder = 'little')
    msg2 += the_patch_data # 'TPDT'
    msg2 += (0x98).to_bytes(length = 4, byteorder = 'little')
    msg2 += u32_0_le
    msg2 += u32_1_le
    msg2 += msg2payload
    print("msg2 =")
    print_dump(msg2)
    msg2_7bit = convert87(msg2)
    msg2_7bit += (0xF7).to_bytes(length = 1, byteorder = 'little')
    print("msg2 (7 bit)=")
    print_dump(msg2_7bit)
    # following is just debug (so what would be sent can be reloaded via setup to test) but could be useful...
    with open("test.syx", "wb") as f:
        f.write(msg2_7bit)

    msg3 = hdr
    msg3 += b'\x03' # sequence number start=1, data=2, crc=3
    # CRC is everything in messag2 from byt 9 onwards
    crc_out = crc32(0, msg2[9:], len(msg2[9:]))
    msg3 += crc_out.to_bytes(length = 4, byteorder = 'little')
    print("msg3 =")
    print_dump(msg3)
    msg3_7bit = convert87(msg3)
    msg3_7bit += (0xF7).to_bytes(length = 1, byteorder = 'little')
    print("msg3 (7 bit)=")
    print_dump(msg3_7bit)

def convert87_chunk(data):
    mask = 0
    chunk = list(data)
    for x in range(len(chunk)):
        #print("byte is ", hex(chunk[x]), "mask before is ", hex(mask), end="")
        mask = mask | ((chunk[x] & 0x80) >> (x + 1))
        #print(" mask after is", hex(mask))
        chunk[x] = chunk[x] & 0x7F
    retval = mask.to_bytes(length = 1, byteorder = 'little')
    #print("retval (mask) =", retval)
    retval += bytearray(chunk)
    #print("retval (all) =", retval)
    return retval

# When sending the body of the messages after the 9 byte header has to be grouped
# into 7 bytes at a time with a leading byte that shows any +128 shifts for the 7
# to follow (and that shift byte has to be in 7bits too - hence groups of 7 not 8)
def convert87(data):
    retval = data[:9]
    data = data[9:]
    for n in range(0, len(data), 7):
        #print("87 of ", len(data[n:n + 7]), "bytes: ", data[n:n + 7])
        retval += convert87_chunk(data[n:n + 7])
    return retval

# The patch is 8 bit but sysex can only carry 7 bit data so the patch is broken into
# groups of 7 bytes and each 7 byte group is preceded by a 7 bit mask where each bit
# says whether or not 0x80 (128) should be added to that byte within the 7
def convert78_chunk(shifts, data):
    if shifts == 0:
        return data
    result = []
    for n in range(0, len(data)):
        if (shifts << (n + 1)) & 0x80:
            result.append(0x80 | data[n])
        else:
            result.append(data[n])
    return result

# So this takes an entire sysex (from F0 to F7) and breaks it into 8 byte
# groups of 1 shift byte and 7 data bytes then passes each in turn to
# convert87 above and then concatentates all these into result[]
def convert78(data):
    result = []
    # first discard the front 9 bytes
    data = data[9:]
    while len(data):
        if data[-1] == 0xf7:
            # if we reached the last byte ditch it
            data = data[:-1]
        # what then follows is a byte holding possible 0x80 shifts for next 7 bytes
        shifts = data[0]
        # and then 7 bytes of data
        bytes = data[1 : 8]
        next7 = convert78_chunk(shifts, bytes)
        # now chop off the 8 bytes just processed ready to go again
        data = data[8:]
        # the 7 processed bytes are added to the result being built up
        result.extend(next7)
    print()
    return result

# This is the CRC32 that XFM uses. It is the widely used 0xEDB88320 polynomial which is
# the reveresed polynomial of 0x04C11DB7 which is used in MPEG2, Zlib, PKZip, PNG, Zmodem etc
#
# The seed passed in as "crc" to start is 0x00000000 to match what XFM uses.
def crc32(crc, p, len):
  crc = 0xffffffff & ~crc
  for i in range(len):
    crc = crc ^ p[i]
    for j in range(8):
      crc = (crc >> 1) ^ (0xedb88320 & -(crc & 1))
  return 0xffffffff & ~crc

# This has been broken out of rxmsg where it originally lived so it can be called both after
# sysex arrives in rxmsg and also after a SYX file has been loaded from disk - it basically loads
# the data into the editor controls (and also dumps data in various ways - both onscreen in "setup"
# and to the console log.
def loadRawBytes(bytes, possSaveJson):
    patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
    setupWin.setBytes(bytes)

    print("The raw 7bit sysex data")
    print_dump(bytes)

    # convert 7 to 8 bit using every 8th byte as 7 shift masks
    data8 = convert78(bytes)
    print("The converted 8bit data")
    print_dump(data8)

    setupWin.set8bytes(data8)

    setupWin.draw()

    decode_8bit(data8, patch)
    if setupWin.saveLoadState.get() == 1 and possSaveJson:
        saveJson(patch)

    # then load the patch (dict)
    loadCtrls(patch)
    routeWin.draw()


# This is the main interaction with Mido on message receipt. This will ignore
# anything that is not sysex and even if it is sysex it's only really interested in
# packet 2 (the payload) and packet 3 (the little endian CRC32)
def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    # sound dump comes in 3 messages - look for the middle one with sequence number 2 (from 1, 2, 3)
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        bytes = msg.bytes()
        # true means do save JSON if user has ticked the Setup box
        loadRawBytes(bytes, True)
        
    # Packet 3 has the CRC32
    if msg.type == 'sysex' and msg.bytes()[8] == 3:
        crc = convert78(msg.bytes())
        crchex = ""
        print("CRC from XFM = ", end="")
        for n in range(4):
            crchex = crchex + str(format(crc[3 - n], '02X'))
            print(hex(crc[3 - n]), end=" ")
        print()
        setupWin.setCRC(crchex)
        setupWin.draw()

# This loads a patch (dictionary / associative array) into the corresponding named
# controls ready to start editing.
def loadCtrls(data):
    for i in data:
        print("=====", i, "=====")
        if (i != "Name"):
            for j in data[i]:
                key = f'{i}:{j}'
                print(f'{key} = ', data[i][j])
                valToSet = data[i][j]
                if j == "Freq":
                    valToSet = (valToSet + 5) / 10 # so 4408 (for example) becomes 441
                if j == "Freq" or j == "Ratio":
                    controllist[key][0].setValue(int(valToSet / 100))
                    controllist[key][0].fraction = int(valToSet % 100)
                elif j == "Feedback":
                    controllist[key][0].setValue(int(valToSet / 10))
                    controllist[key][0].fraction = int(abs(valToSet) % 10)
                else:
                    controllist[key][0].setValue(valToSet)
                controllist[key][0].draw()
        else:
            charCount = 0
            n = 0
            while n < len(data[i]):
                withDot = False
                key = f'{i}:chr{charCount}'
                print(f'{key} =  {data[i][n]}', end="")
                chrnum = ord(data[i][n])
                if n < (len(data[i]) - 1):
                    if data[i][n + 1] == '.':
                        withDot = True
                        print(".")
                    else:
                        print()
                if chrnum >= ord('A'):
                    chrnum = chrnum - ord('A') + 11 # 11 not 10 because ' '
                elif chrnum == ord(' '):
                    chrnum = 10
                else:
                    chrnum = chrnum - ord('0')
                if withDot == True:
                    chrnum = chrnum + 100 # mark that a dot needs to be drawn
                    n = n + 1
                controllist[key][0].index = chrnum
                controllist[key][0].draw()
                charCount = charCount + 1
                n = n + 1
            print()
        for j in ['OP1:', 'OP2:', 'OP3:', 'OP4:', 'Pitch:']:
            adsrs[j].draw()

# this reads the values back out of the controls and creates a tagged dictionary from
# the values (which can be written as JSON or then passed further to create a binary
# payload to go back to XFM)
def readCtrls():
    patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
    nameList = list()
    for x in controllist:
        sect= x.split(':')[0]
        item = x.split(':')[1]
        if sect == "Name":
            dot  = False
            namechr = controllist[x][0].getValue()
            if namechr > 100:
                dot = True
                namechr = namechr - 100
            if namechr < 10:
                namechr = namechr + ord('0')
            elif namechr == 10:
                namechr = ord(' ')
            else:
                namechr = namechr - 11 + ord('A')
            nameList.append(chr(namechr))
            if dot:
                nameList.append('.')
            if item == "chr3":
                patch["Name"] = ''.join(nameList)
        elif item == "Freq":
            patch[sect][item] = ((controllist[x][0].getValue() * 100) + controllist[x][0].fraction) * 10
        elif item == "Ratio":
            patch[sect][item] = (controllist[x][0].getValue() * 100) + controllist[x][0].fraction
        elif item == "Feedback":
            if controllist[x][0].getValue() >= 0:
                patch[sect][item] = (controllist[x][0].getValue() * 10) + controllist[x][0].fraction
            else:
                patch[sect][item] = (controllist[x][0].getValue() * 10) - controllist[x][0].fraction
        else:
            patch[sect][item] = controllist[x][0].getValue()
    return patch

def loadJson(filename):
    with open(filename) as f:
        data = json.load(f)
        loadCtrls(data)

def loadInitJson():
    loadJson("initpatch.json")

def saveJson(patch):
    jsonpatch = json.dumps(patch, indent=4)
    with open("PATCH_" + patch['Name'] + ".json", 'w') as f:
        f.write(jsonpatch)

#============================= THE start ================================
portOpen = False
portOutOpen = False

# save current (install) directory
cur_dir = os.getcwd()
# switch to sub-dir where all the controls and logos are held while everything is loaded
os.chdir('./images_animations')

window = Tk()
window.geometry("1720x930")
window.title("Quick Edit for Liven XFM - no MIDI port open - use Setup!!")
window.iconbitmap("xicon.ico")
window.configure(bg='#313131')
window.resizable(False, False)

# There are only so many different types of control and each has an animated PNG
# The entries are filename and number of frames (so frame height is overall height / num frames)
anims = {
    "0to127" :  [ "ctrl_0_127.png", 128 ],
    "on_off" :  [ "ctrl_on_off.png", 2 ],
    "line_exp" :[ "ctrl_line_exp.png", 2 ],
    "_18to18" : [ "ctrl_-18_18.png", 37 ],
    "slideH" :  [ "ctrl_slide_H.png", 128],
    "slideV" :  [ "ctrl_slide_V.png", 128],
    "slideVbi" :[ "ctrl_slide_V-48_48.png", 97],
    "_63to63" : [ "ctrl_-63_63.png", 127 ],
    "C1toC7" :  [ "ctrl_C1_C7.png", 7 ],
    "chars" :   [ "lcd_chars.png", 38 ],
    "blk128" :  [ "ctrl_blank_128.png", 128 ],
    "blk33" :   [ "ctrl_blank_33.png", 33 ],
    "blk98" :   [ "ctrl_blank_98.png", 98 ],
    "op1_4" :   [ "op_logo.png", 4 ],
    "dig_d_99" :[ "digits_dot_0_99.png", 100 ],
    "dig_d_9" : [ "digits_dot_0_9.png", 10 ],
    "digits" :  [ "digits_0_127.png", 128 ],
    "digits0" : [ "digits_00_127.png", 128 ],
    "neg"    :  [ "digit_neg.png", 1],
    "litegrey" :[ "lightgrey.png", 1],
    "dot" :     [ "dot.png", 1]
}

# Given the above list open each PNG in turn and break them into N separate anim frames
ctrlimgs = {}
for anim in anims:
    fname = anims[anim][0]
    numFrame = anims[anim][1]
    img = Image.open(fname)
    width = img.size[0]
    # following is total height so if 7 frame anim and each frame is 32px high this is 224 e.g.
    height = img.size[1]
    # while this is the height of each frame (so 32 in this example)
    frameH = int(height / numFrame)
    # record everything about the multi-frames complete with empty list of frames
    ctrlimgs.update({ anim : { "type" : anim, "numframes" : numFrame, "width" : width, "height" : height, "frameH" : frameH, "frames" : []}})
    for n in range(numFrame):
        tup = (0, frameH * n, width, frameH * (n + 1))
        frame = ImageTk.PhotoImage(img.crop(tup))
        # having cropped each frame from PNG store it separatelt in "frames" list
        ctrlimgs[anim]["frames"].append(frame)

waveSineImage = ImageTk.PhotoImage(Image.open("sine.png").resize((32,32), Image.Resampling.LANCZOS))
waveSawImage = ImageTk.PhotoImage(Image.open("saw.png").resize((32,32), Image.Resampling.LANCZOS))
waveSquareImage = ImageTk.PhotoImage(Image.open("square.png").resize((32,32), Image.Resampling.LANCZOS))
waveNoiseImage = ImageTk.PhotoImage(Image.open("noise.png").resize((32,32), Image.Resampling.LANCZOS))

# Textured grey used as background for all 5 sub-windows
rawback = Image.open("dark-grey.jpg")
opback = rawback.resize((685, 460))
backimg = ImageTk.PhotoImage(opback)

# Background for pitch/master edit right - same image just resized
mstrback = rawback.resize((340, 928))
mstrimg = ImageTk.PhotoImage(mstrback)

# "Quick Edit for Sonicware Liven XFM logo"
rawlogo = Image.open("logo.png")
mainlogo = ImageTk.PhotoImage(rawlogo)

Backdrop("OP1", 0, 0, 684, 460, backimg, ctrlimgs["op1_4"]["frames"][0], 0, 8)
Backdrop("OP2", 688, 0, 684, 460, backimg, ctrlimgs["op1_4"]["frames"][1], 0, 8)
Backdrop("OP3", 0, 462, 684, 462, backimg, ctrlimgs["op1_4"]["frames"][2], 0, 8)
Backdrop("OP4", 688, 462, 684, 462, backimg, ctrlimgs["op1_4"]["frames"][3], 0, 8)
Backdrop("Master", 1375, 0, 340, 922, mstrimg, mainlogo, 15, 680)

adsrs = {}
# The five grey ADSR canvases
adsrs["OP1:"] = Adsr("OP1:", 210, 250)
adsrs["OP2:"] = Adsr("OP2:", 890, 250)
adsrs["OP3:"] = Adsr("OP3:", 210, 710)
adsrs["OP4:"] = Adsr("OP4:", 890, 710)
adsrs["Pitch:"] = Adsr("Pitch:", 1410, 270)

XOFF = 690
YOFF = 460
COL_RATIO = 500
COL_FEEDBACK = 590
COL_TIMESCALE = 10
COL_DETUNE = 100
TIME_SLIDE_Y = 400
LEVEL_SLIDE_Y = 70
SWITCH_X = 210
SWITCH_OFFX = 70
SWITCH_Y = 20

# following is list of all animated controls - a key name, a label, an anim to use and X/Y
controls = {
    "Name:chr0" :    [ "",          "chars",   1430, 10 ],
    "Name:chr1" :    [ "",          "chars",   1430 + 64 - 8, 10 ],
    "Name:chr2" :    [ "",          "chars",   1430 + ((64 - 8) * 2), 10 ],
    "Name:chr3":     [ "",          "chars",   1430 + ((64 - 8) * 3), 10 ],

    "OP1:Feedback" : [ "Feedback",  "blk128",    COL_FEEDBACK - 12, 10, -63 ],
    "OP1:OP2In" :    [ "OP2 Input", "0to127",    COL_RATIO, 130 ],
    "OP1:OP3In" :    [ "OP3 Input", "0to127",    COL_FEEDBACK, 130 ],
    "OP1:OP4In" :    [ "OP4 Input", "0to127",    COL_RATIO, 220 ],
    "OP1:Output" :   [ "Output",    "0to127",    COL_FEEDBACK, 220 ],
    "OP1:PitchEnv" : [ "Pitch Env",  "on_off",   SWITCH_X + (2 * SWITCH_OFFX), SWITCH_Y ],
    "OP1:Fixed" :    [ "Fixed",     "on_off",    SWITCH_X + (3 * SWITCH_OFFX), SWITCH_Y ],
    # two controls - one location - what's displayed depends on Fixed On/Off
    "OP1:Ratio" :    [ "Ratio",     "blk33",     COL_RATIO - 12, 10 ],#not 0to127 !
    "OP1:Freq" :     [ "Frequency", "blk98",     COL_RATIO - 12, 10 ],#not 0to127 !
    "OP1:Detune" :   [ "Detune",    "_63to63",   COL_DETUNE, 25, -63 ],
    "OP1:Level" :    [ "Level",     "0to127",    COL_RATIO, 310 ],
    "OP1:VelSens" :  [ "Velo Sens", "0to127",    COL_FEEDBACK, 310 ],
    "OP1:Time" :     [ "TimeScale", "0to127",    COL_TIMESCALE, 130 ],
    "OP1:UpCurve" :  [ "Up Curve",  "_18to18",   COL_DETUNE, 130, -18 ],
    "OP1:DnCurve" :  [ "Down Curve","_18to18",   COL_DETUNE, 220, -18 ],
    "OP1:Scale" :    [ "Scale Pos", "C1toC7",    COL_TIMESCALE, 220 ],
    "OP1:ALevel" :   [ "A Level",   "slideV",    210, LEVEL_SLIDE_Y ],
    "OP1:ATime" :    [ "A Time",    "slideH",    10, TIME_SLIDE_Y ],
    "OP1:DLevel" :   [ "D Level",   "slideV",    280, LEVEL_SLIDE_Y ],
    "OP1:DTime" :    [ "D Time",    "slideH",    180, TIME_SLIDE_Y ],
    "OP1:SLevel" :   [ "S Level",   "slideV",    350, LEVEL_SLIDE_Y ],
    "OP1:STime" :    [ "S Time",    "slideH",    350, TIME_SLIDE_Y ],
    "OP1:RLevel" :   [ "R Level",   "slideV",    420, LEVEL_SLIDE_Y ],
    "OP1:RTime" :    [ "R Time",    "slideH",    520, TIME_SLIDE_Y ],
    "OP1:LGain" :    [ "L Gain",    "_63to63",   COL_TIMESCALE, 310, -63 ],
    "OP1:RGain" :    [ "R Gain",    "_63to63",   COL_DETUNE, 310, -63 ],
    "OP1:LCurve" :   [ "L Curve",   "line_exp",  SWITCH_X, SWITCH_Y ],
    "OP1:RCurve" :   [ "R Curve",   "line_exp",  SWITCH_X + (1 * SWITCH_OFFX), SWITCH_Y ],

    "OP2:Feedback" : [ "Feedback",  "blk128",    XOFF + COL_FEEDBACK - 12, 10, -63 ],
    "OP2:OP1In" :    [ "OP1 Input", "0to127",    XOFF + COL_RATIO, 130 ],
    "OP2:OP3In" :    [ "OP3 Input", "0to127",    XOFF + COL_FEEDBACK, 130 ],
    "OP2:OP4In" :    [ "OP4 Input", "0to127",    XOFF + COL_RATIO, 220 ],
    "OP2:Output" :   [ "Output",    "0to127",    XOFF + COL_FEEDBACK, 220 ],
    "OP2:PitchEnv" : [ "Pitch Env",  "on_off",   XOFF + SWITCH_X + (2 * SWITCH_OFFX), SWITCH_Y ],
    "OP2:Fixed" :    [ "Fixed",     "on_off",    XOFF + SWITCH_X + (3 * SWITCH_OFFX), SWITCH_Y ],
    "OP2:Ratio" :    [ "Ratio",     "blk33",     XOFF + COL_RATIO - 12, 10 ],
    "OP2:Freq" :     [ "Frequency", "blk98",     XOFF + COL_RATIO - 12, 10 ],
    "OP2:Detune" :   [ "Detune",    "_63to63",   XOFF + COL_DETUNE, 25, -63 ],
    "OP2:Level" :    [ "Level",     "0to127",    XOFF + COL_RATIO, 310 ],
    "OP2:VelSens" :  [ "Velo Sens", "0to127",    XOFF + COL_FEEDBACK, 310 ],
    "OP2:Time" :     [ "TimeScale", "0to127",    XOFF + COL_TIMESCALE, 130 ],
    "OP2:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + COL_DETUNE, 130, -18 ],
    "OP2:DnCurve" :  [ "Down Curve","_18to18",   XOFF + COL_DETUNE, 220, -18 ],
    "OP2:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + COL_TIMESCALE, 220 ],
    "OP2:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, LEVEL_SLIDE_Y ],
    "OP2:ATime" :    [ "A Time",    "slideH",    XOFF + 10, TIME_SLIDE_Y ],
    "OP2:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, LEVEL_SLIDE_Y ],
    "OP2:DTime" :    [ "D Time",    "slideH",    XOFF + 180, TIME_SLIDE_Y ],
    "OP2:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, LEVEL_SLIDE_Y ],
    "OP2:STime" :    [ "S Time",    "slideH",    XOFF + 350, TIME_SLIDE_Y ],
    "OP2:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, LEVEL_SLIDE_Y ],
    "OP2:RTime" :    [ "R Time",    "slideH",    XOFF + 520, TIME_SLIDE_Y ],
    "OP2:LGain" :    [ "L Gain",    "_63to63",   XOFF + COL_TIMESCALE, 310, -63 ],
    "OP2:RGain" :    [ "R Gain",    "_63to63",   XOFF + COL_DETUNE, 310, -63 ],
    "OP2:LCurve" :   [ "L Curve",   "line_exp",  XOFF + SWITCH_X, SWITCH_Y ],
    "OP2:RCurve" :   [ "R Curve",   "line_exp",  XOFF + SWITCH_X + (1 * SWITCH_OFFX), SWITCH_Y ],

    "OP3:Feedback" : [ "Feedback",  "blk128",    COL_FEEDBACK - 12, YOFF + 10, -63 ],
    "OP3:OP1In" :    [ "OP1 Input", "0to127",    COL_RATIO, YOFF + 130 ],
    "OP3:OP2In" :    [ "OP2 Input", "0to127",    COL_FEEDBACK, YOFF + 130 ],
    "OP3:OP4In" :    [ "OP4 Input", "0to127",    COL_RATIO, YOFF + 220 ],
    "OP3:Output" :   [ "Output",    "0to127",    COL_FEEDBACK, YOFF + 220 ],
    "OP3:PitchEnv" : [ "Pitch Env",  "on_off",   SWITCH_X + (2 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP3:Fixed" :    [ "Fixed",     "on_off",    SWITCH_X + (3 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP3:Ratio" :    [ "Ratio",     "blk33",     COL_RATIO - 12, YOFF + 10 ],
    "OP3:Freq" :     [ "Frequency", "blk98",     COL_RATIO - 12, YOFF + 10 ],
    "OP3:Detune" :   [ "Detune",    "_63to63",   COL_DETUNE, YOFF + 25, -63 ],
    "OP3:Level" :    [ "Level",     "0to127",    COL_RATIO, YOFF + 310 ],
    "OP3:VelSens" :  [ "Velo Sens", "0to127",    COL_FEEDBACK, YOFF + 310 ],
    "OP3:Time" :     [ "TimeScale", "0to127",    COL_TIMESCALE, YOFF + 130 ],
    "OP3:UpCurve" :  [ "Up Curve",  "_18to18",   COL_DETUNE, YOFF + 130, -18 ],
    "OP3:DnCurve" :  [ "Down Curve","_18to18",   COL_DETUNE, YOFF + 220, -18 ],
    "OP3:Scale" :    [ "Scale Pos", "C1toC7",    COL_TIMESCALE, YOFF + 220 ],
    "OP3:ALevel" :   [ "A Level",   "slideV",    210, YOFF + LEVEL_SLIDE_Y ],
    "OP3:ATime" :    [ "A Time",    "slideH",    10, YOFF + TIME_SLIDE_Y ],
    "OP3:DLevel" :   [ "D Level",   "slideV",    280, YOFF + LEVEL_SLIDE_Y ],
    "OP3:DTime" :    [ "D Time",    "slideH",    180, YOFF + TIME_SLIDE_Y ],
    "OP3:SLevel" :   [ "S Level",   "slideV",    350, YOFF + LEVEL_SLIDE_Y ],
    "OP3:STime" :    [ "S Time",    "slideH",    350, YOFF + TIME_SLIDE_Y ],
    "OP3:RLevel" :   [ "R Level",   "slideV",    420, YOFF + LEVEL_SLIDE_Y ],
    "OP3:RTime" :    [ "R Time",    "slideH",    520, YOFF + TIME_SLIDE_Y ],
    "OP3:LGain" :    [ "L Gain",    "_63to63",   COL_TIMESCALE, YOFF + 310, -63 ],
    "OP3:RGain" :    [ "R Gain",    "_63to63",   COL_DETUNE, YOFF + 310, -63 ],
    "OP3:LCurve" :   [ "L Curve",   "line_exp",  SWITCH_X, YOFF + SWITCH_Y ],
    "OP3:RCurve" :   [ "R Curve",   "line_exp",  SWITCH_X + (1 * SWITCH_OFFX), YOFF + SWITCH_Y ],

    "OP4:Feedback" : [ "Feedback",  "blk128",    XOFF + COL_FEEDBACK - 12, YOFF + 10, -63 ],
    "OP4:OP1In" :    [ "OP1 Input", "0to127",    XOFF + COL_RATIO, YOFF + 130 ],
    "OP4:OP2In" :    [ "OP2 Input", "0to127",    XOFF + COL_FEEDBACK, YOFF + 130 ],
    "OP4:OP3In" :    [ "OP3 Input", "0to127",    XOFF + COL_RATIO, YOFF + 220 ],
    "OP4:Output" :   [ "Output",    "0to127",    XOFF + COL_FEEDBACK, YOFF + 220 ],
    "OP4:PitchEnv" : [ "Pitch Env",  "on_off",   XOFF + SWITCH_X + (2 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP4:Fixed" :    [ "Fixed",     "on_off",    XOFF + SWITCH_X + (3 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP4:Ratio" :    [ "Ratio",     "blk33",     XOFF + COL_RATIO - 12, YOFF + 10 ],
    "OP4:Freq" :     [ "Frequency", "blk98",     XOFF + COL_RATIO - 12, YOFF + 10 ],
    "OP4:Detune" :   [ "Detune",    "_63to63",   XOFF + COL_DETUNE, YOFF + 25, -63 ],
    "OP4:Level" :    [ "Level",     "0to127",    XOFF + COL_RATIO, YOFF + 310 ],
    "OP4:VelSens" :  [ "Velo Sens", "0to127",    XOFF + COL_FEEDBACK, YOFF + 310 ],
    "OP4:Time" :     [ "TimeScale", "0to127",    XOFF + COL_TIMESCALE, YOFF + 130 ],
    "OP4:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + COL_DETUNE, YOFF + 130, -18 ],
    "OP4:DnCurve" :  [ "Down Curve","_18to18",   XOFF + COL_DETUNE, YOFF + 220, -18 ],
    "OP4:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + COL_TIMESCALE, YOFF + 220 ],
    "OP4:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, YOFF + LEVEL_SLIDE_Y ],
    "OP4:ATime" :    [ "A Time",    "slideH",    XOFF + 10, YOFF + TIME_SLIDE_Y ],
    "OP4:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, YOFF + LEVEL_SLIDE_Y ],
    "OP4:DTime" :    [ "D Time",    "slideH",    XOFF + 180, YOFF + TIME_SLIDE_Y ],
    "OP4:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, YOFF + LEVEL_SLIDE_Y ],
    "OP4:STime" :    [ "S Time",    "slideH",    XOFF + 350, YOFF + TIME_SLIDE_Y ],
    "OP4:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, YOFF + LEVEL_SLIDE_Y ],
    "OP4:RTime" :    [ "R Time",    "slideH",    XOFF + 520, YOFF + TIME_SLIDE_Y ],
    "OP4:LGain" :    [ "L Gain",    "_63to63",   XOFF + COL_TIMESCALE, YOFF + 310, -63 ],
    "OP4:RGain" :    [ "R Gain",    "_63to63",   XOFF + COL_DETUNE, YOFF + 310, -63 ],
    "OP4:LCurve" :   [ "L Curve",   "line_exp",  XOFF + SWITCH_X, YOFF + SWITCH_Y ],
    "OP4:RCurve" :   [ "R Curve",   "line_exp",  XOFF + SWITCH_X + (1 * SWITCH_OFFX), YOFF + SWITCH_Y ],

    "Pitch:ALevel" : [ "A Level",   "slideVbi",    1410, 90, -48 ],
    "Pitch:ATime" :  [ "A Time",    "slideH",    1410, 410 ],
    "Pitch:DLevel" : [ "D Level",   "slideVbi",    1480, 90, -48 ],
    "Pitch:DTime" :  [ "D Time",    "slideH",    1410, 460 ],
    "Pitch:SLevel" : [ "S Level",   "slideVbi",    1550, 90, -48 ],
    "Pitch:STime" :  [ "S Time",    "slideH",    1410, 510 ],
    "Pitch:RLevel" : [ "R Level",   "slideVbi",    1620, 90, -48 ],
    "Pitch:RTime" :  [ "R Time",    "slideH",    1410, 560 ],

    "Mixer:Level" :  [ "Mixer Level","_63to63",   1600, 600, -63 ],
}

# For all the above controls simply create their anm objects but don't draw until inits set
controllist = {}
for key in controls:
    entry = controls[key]
    if len(entry) == 4:
        thisanim = Anim(key, title = entry[0], ctrl = entry[1], xpos = entry[2], ypos = entry[3])
    else:
        thisanim = Anim(key, title = entry[0], ctrl = entry[1], xpos = entry[2], ypos = entry[3], offset = entry[4])
    controllist.update({key : [thisanim]})

# following is a JSON experiment to load a file (when a canvas is clicked) and load all the
# values into the controls
def initJSON(event):
    loadInitJson()

def loadJSON(event):
    file = fd.askopenfilename(title="Load JSON patch", filetypes=[("JSON patches", "*.json")])
    if "json" in file:
        loadJson(file)

def saveJSON(event):
    patch = readCtrls()
    saveJson(patch)

def sendPatch(event):
    encode_bytes(readCtrls())

init = Canvas(width=32, height=32, highlightthickness=0)
init.place(x=1650, y=410)
init.create_rectangle(0,0, 31, 31, fill='#C00000')
init.create_text(0, 10, anchor=tk.NW, text="  Init", fill='#FFFFFF')
init.bind('<Button>', initJSON)

save = Canvas(width=32, height=32, highlightthickness=0)
save.place(x=1600, y=410)
save.create_rectangle(0,0, 31, 31, fill='#00C000')
save.create_text(0, 0, anchor=tk.NW, text=" Save\nJSON", fill='#FFFFFF')
save.bind('<Button>', saveJSON)

load = Canvas(width=32, height=32, highlightthickness=0)
load.place(x=1600, y=450)
load.create_rectangle(0,0, 31, 31, fill='#c0C000')
load.create_text(0, 0, anchor=tk.NW, text=" load\nJSON", fill='#FFFFFF')
load.bind('<Button>', loadJSON)

load = Canvas(width=32, height=32, highlightthickness=0)
load.place(x=1650, y=450)
load.create_rectangle(0,0, 31, 31, fill='#08c5cf')
load.create_text(0, 0, anchor=tk.NW, text=" Send", fill='#FFFFFF')
load.bind('<Button>', sendPatch)

routeWin = RouteWindow()

def routeButtonClick(event):
    if not routeWin.Showing:
        routeWin.show()
    else:
        routeWin.hide()

routeButton = Canvas(width=32, height=32, highlightthickness=0)
routeButton.place(x=1600, y=490)
routeButton.create_rectangle(0,0, 31, 31, fill='#0000C0')
route_label = routeButton.create_text(0, 10, anchor=tk.NW, text="Route", fill='#FFFFFF')
routeButton.bind('<Button>', routeButtonClick)

setupWin = SetupWindow()

def setupButtonClick(event):
    if not setupWin.Showing:
        setupWin.show()
    else:
        setupWin.hide()

setupButton = Canvas(width=32, height=32, highlightthickness=0)
setupButton.place(x=1650, y=490)
setupButton.create_rectangle(0,0, 31, 31, fill='#C000C0')
setupButton.create_text(0, 10, anchor=tk.NW, text="Setup", fill='#FFFFFF')
setupButton.bind('<Button>', setupButtonClick)

# now all images/logos loaded back to the install directory where patches/etc will be
os.chdir(cur_dir)

# load initpatch.json (which will default to an "init" patch.
loadInitJson()

# Now init values are set run throught the list and draw all animated controls
for entry in controllist:
    controllist[entry][0].draw()

inports = mido.get_input_names()
setupWin.setPorts(inports)
outports = mido.get_output_names()
setupWin.setOutPorts(outports)

if len(inports):
    print("MIDI IN ports:", inports)
if len(outports):
    print("MIDI OUT ports:", outports)

window.mainloop()
