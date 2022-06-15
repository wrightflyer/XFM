import tkinter as tk

window = tk.Tk()
window.title("Envelope")
window.geometry("560x480")

def alChange(val):
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

plot = tk.Canvas(window, bg="#E0E0E0", width = 512, height = 256)
plot.place(x=10, y=10)

albl = tk.Label(text="A", font=("Arial", 24))
albl.place(x=15, y=290)
alVar = tk.IntVar()
alevel = tk.Scale(window, label="level", variable = alVar, from_=127, to=0, command=alChange)
alevel.place(x=40, y=290)

atVar = tk.IntVar()
atime = tk.Scale(window, orient=tk.HORIZONTAL, label="time", variable = atVar, from_=0, to=127, command=alChange)
atime.place(x=10, y=400)

dlbl = tk.Label(text="D", font=("Arial", 24))
dlbl.place(x=135, y=290)
dlVar = tk.IntVar()
dlevel = tk.Scale(window, label="level", variable = dlVar, from_=127, to=0, command=alChange)
dlevel.place(x=160, y=290)

dtVar = tk.IntVar()
dtime = tk.Scale(window, orient=tk.HORIZONTAL, label="time", variable = dtVar, from_=0, to=127, command=alChange)
dtime.place(x=130, y=400)

slbl = tk.Label(text="S", font=("Arial", 24))
slbl.place(x=255, y=290)
slVar = tk.IntVar()
slevel = tk.Scale(window, label="level", variable = slVar, from_=127, to=0, command=alChange)
slevel.place(x=280, y=290)

stVar = tk.IntVar()
stime = tk.Scale(window, orient=tk.HORIZONTAL, label="time", variable = stVar, from_=0, to=127, command=alChange)
stime.place(x=250, y=400)

rlbl = tk.Label(text="R", font=("Arial", 24))
rlbl.place(x=365, y=290)
rlVar = tk.IntVar()
rlevel = tk.Scale(window, label="level", variable = rlVar, from_=127, to=0, command=alChange)
rlevel.place(x=400, y=290)

rtVar = tk.IntVar()
rtime = tk.Scale(window, orient=tk.HORIZONTAL, label="time", variable = rtVar, from_=0, to=127, command=alChange)
rtime.place(x=370, y=400)


window.mainloop()