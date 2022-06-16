import tkinter as tk

window = tk.Tk()
window.title("Envelope")
window.geometry("560x480")

def update(val):
    plot.delete("all")
    ax = atVar.get()
    ay = 256 - (2 * alVar.get())

    dx = dtVar.get() + ax
    dy = 256 - (2 * dlVar.get())

    sx = stVar.get() + dx
    sy = 256 - (2 * slVar.get())

    rx = rtVar.get() + sx
    ry = 256 - (2 * rlVar.get())

    padding = 512 - (atVar.get() + dtVar.get() + stVar.get() + rtVar.get())

    plot.create_line(0, 256, ax, ay, width=3)
    plot.create_line(ax, ay, dx, dy, width=3)
    plot.create_line(dx, dy, sx, sy, width=3)
    plot.create_line(sx, sy, sx + padding, sy, width=3, dash=(3,1))
    plot.create_line(sx + padding, sy, 512, ry, width=3)

def sliders(label, xpos, varLevel, varTime):
    ypos=290
    lbl = tk.Label(text=label, font=("Arial", 24))
    lbl.place(x=xpos + 5, y=ypos)
    scale1 = tk.Scale(window, label="level", variable=varLevel, from_=127, to=0, command=update)
    scale1.place(x=xpos + 30, y=ypos)
    scale2 = tk.Scale(window, orient=tk.HORIZONTAL, label="time", variable=varTime, from_=0, to=127, command=update)
    scale2.place(x=xpos, y=ypos + 110)

plot = tk.Canvas(window, bg="#E0E0E0", width = 512, height = 256)
plot.place(x=10, y=10)

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

window.mainloop()