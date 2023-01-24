import tkinter as tk
from tkinter import *

window = tk.Tk()
window.title("Envelope")
window.geometry("680x480")

envelopes = [
[ 0,0,0,0,0,0,0,0 ],
[ 0,0,0,0,0,0,0,0 ],
[ 0,0,0,0,0,0,0,0 ],
[ 0,0,0,0,0,0,0,0 ]
]

def setcanvas():
    global activecanvas
    val = active.get()
    if val == 1:
        activecanvas = plot1
    if val == 2:
        activecanvas = plot2
    if val == 3:
        activecanvas = plot3
    if val == 4:
        activecanvas = plot4
    print(id(activecanvas))

def update(val):
    activecanvas.delete("all")
    ax = atVar.get()
    ay = 128 - alVar.get()

    dx = dtVar.get() + ax
    dy = 128 - dlVar.get()

    sx = stVar.get() + dx
    sy = 128 - slVar.get()

    rx = rtVar.get() + sx
    ry = 128 - rlVar.get()

    padding = 256 - (atVar.get() + dtVar.get() + stVar.get() + rtVar.get())

    activecanvas.create_line(0, 128, ax, ay, width=3)
    activecanvas.create_line(ax, ay, dx, dy, width=3)
    activecanvas.create_line(dx, dy, sx, sy, width=3)
    activecanvas.create_line(sx, sy, sx + padding, sy, width=3, dash=(3,1))
    activecanvas.create_line(sx + padding, sy, 256, ry, width=3)

def sliders(label, xpos, varLevel, varTime):
    ypos=310
    lbl = tk.Label(text=label, font=("Arial", 24))
    lbl.place(x=xpos + 5, y=ypos)
    scale1 = tk.Scale(window, label="level", variable=varLevel, from_=127, to=0, command=update)
    scale1.place(x=xpos + 30, y=ypos)
    scale2 = tk.Scale(window, orient=tk.HORIZONTAL, label="time", variable=varTime, from_=0, to=127, command=update)
    scale2.place(x=xpos, y=ypos + 110)

plot1 = tk.Canvas(window, bg="#E0E0E0", width = 256, height = 128)
plot1.place(x=10, y=25)
plot2 = tk.Canvas(window, bg="#E0E0E0", width = 256, height = 128)
plot2.place(x=280, y=25)
plot3 = tk.Canvas(window, bg="#E0E0E0", width = 256, height = 128)
plot3.place(x=10, y=180)
plot4 = tk.Canvas(window, bg="#E0E0E0", width = 256, height = 128)
plot4.place(x=280, y=180)

activecanvas = plot1

alVar = tk.IntVar()
atVar = tk.IntVar()
sliders("A", 10, alVar, atVar)

dlVar = tk.IntVar()
dtVar = tk.IntVar()
sliders("D", 140, dlVar, dtVar)

slVar = tk.IntVar()
stVar = tk.IntVar()
sliders("S", 270, slVar, stVar)

rlVar = tk.IntVar()
rtVar = tk.IntVar()
sliders("R", 400, rlVar, rtVar)

active = tk.IntVar()
r1 = tk.Radiobutton(window, text="Op 1", variable=active, value=1, command=setcanvas)
r2 = tk.Radiobutton(window, text="Op 2", variable=active, value=2, command=setcanvas)
r3 = tk.Radiobutton(window, text="Op 3", variable=active, value=3, command=setcanvas)
r4 = tk.Radiobutton(window, text="Op 4", variable=active, value=4, command=setcanvas)
r1.place(x=10, y=0)
r2.place(x=280, y=0)
r3.place(x=10, y=155)
r4.place(x=280, y=155)

def feedcall():
    #print(fooVar.get())
    pass

feedVar = tk.StringVar(value = 64)
feed = tk.Spinbox(from_=0, to=127, textvariable=feedVar, wrap=True, width=5, command=feedcall)
feed.place(x=620, y=30)
tk.Label(text="Feedback:").place(x=550, y=30)

window.mainloop()