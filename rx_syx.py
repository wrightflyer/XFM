import keyboard
import mido

inports = mido.get_input_names()
print(inports)

#sysex data=(0,72,4,0,0,3,96,2,4,70,77,84,67
def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        txt = ""
        print("10 :", end=" ")
        for x in range(16, len(msg.bytes()) - 1):
                byt = msg.bytes()[x]
                print(format(byt, '02x'), end = " ")
                if byt > 31 and byt < 128:
                    txt = txt + chr(byt)
                else:
                    txt = txt + '.'
                if x % 16 == 15:
                    print(txt)
                    print(format(x + 1, '02x'), ":", end=" ")
                    txt = ""
        print()

if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)

while True:
    if keyboard.is_pressed("q"):
        break
    pass

port.close()

