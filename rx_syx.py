import keyboard
import mido
import json

inports = mido.get_input_names()
print(inports)

#sysex data=(0,72,4,0,0,3,96,2,4,70,77,84,67
def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        patch = { "name" : "LOAD", "Mixer" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}}
        bytes = msg.bytes()
        txt = ""
        print("10 :", end=" ")
        for x in range(16, len(bytes) - 1):
                byt = bytes[x]
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
        txt = ""
        txt += chr(bytes[0x2E])
        txt += chr(bytes[0x2F])
        txt += chr(bytes[0x30])
        txt += chr(bytes[0x32])
        patch['name'] = txt

        patch["OP1"]['feedback'] = bytes[0x45]
        patch["OP1"]['OP2 input'] = bytes[0xAF]
        patch["OP1"]['OP3 input'] = bytes[0xB0]
        patch["OP1"]['OP4 input'] = bytes[0xB2]
        patch["OP1"]['Output to Mixer'] = bytes[0xC0]
        peq = True if bytes[0xCE] == 1 else False
        fixed = True if bytes[0x4A] == 1 else False
        patch["OP1"]['Fixed='] = fixed
        ratio = ((bytes[0x5D] * 256) + bytes[0x5C] )
        patch["OP1"]['Ratio/Fixed'] = ratio
        patch["OP1"]['Detune'] = bytes[0x5F]
        patch["OP1"]['Level'] = bytes[0x5E]
        patch["OP1"]['Velocity Sensitivity'] = bytes[0xC5]
        patch["OP1"]['Timescale'] = bytes[0xCA]
        patch["OP1"]['Up Curve'] = bytes[0xD3]
        patch["OP1"]['Down Curve'] = bytes[0xD4]
        patch["OP1"]['ScalePos (C4=3)'] = bytes[0x9F]
        patch["OP1"]['A level '] = bytes[0x73]
        patch["OP1"]['A time '] = bytes[0x6E]
        patch["OP1"]['D level '] = bytes[0x74]
        patch["OP1"]['D time '] = bytes[0x6F]
        patch["OP1"]['S level '] = bytes[0x75]
        patch["OP1"]['S time '] = bytes[0x70]
        patch["OP1"]['R level '] = bytes[0x76]
        patch["OP1"]['R time '] = bytes[0x72]
        patch["OP1"]['L gain '] = bytes[0x9C]
        patch["OP1"]['R gain '] = bytes[0x9D]
        patch["OP1"]['L curve'] = "Line" if bytes[0x9E] & 0x01 else "Exp"
        patch["OP1"]['R curve'] = "Line" if bytes[0x9E] & 0x10 else "Exp"

        patch["OP2"]['feedback'] = bytes[0x46]
        patch["OP2"]['OP1 input'] = bytes[0xB3]
        patch["OP2"]['OP3 input'] = bytes[0xB5]
        patch["OP2"]['OP4 input'] = bytes[0xB6]
        patch["OP2"]['Output to Mixer'] = bytes[0xC2]
        peq = True if bytes[0xCF] == 1 else False
        patch["OP2"]['Pitch EQ'] = peq
        fixed = True if bytes[0x4E] == 1 else False
        patch["OP2"]['Fixed='] = fixed
        ratio = ((bytes[0x61] * 256) + bytes[0x60] )
        patch["OP2"]['Ratio/Fixed'] = ratio
        patch["OP2"]['Detune'] = bytes[0x64]
        patch["OP2"]['Level'] = bytes[0x63]
        patch["OP2"]['Velocity Sensitivity'] = bytes[0xC6]
        patch["OP2"]['Timescale'] = bytes[0xCB]
        patch["OP2"]['Up Curve'] = bytes[0xD5]
        patch["OP2"]['Down Curve'] = bytes[0xD6]
        patch["OP2"]['ScalePos (C4=3)'] = bytes[0xA4]
        patch["OP2"]['A level '] = bytes[0x7C]
        patch["OP2"]['A time '] = bytes[0x77]
        patch["OP2"]['D level '] = bytes[0x7D]
        patch["OP2"]['D time '] = bytes[0x78]
        patch["OP2"]['S level '] = bytes[0x7E]
        patch["OP2"]['S time '] = bytes[0x7A]
        patch["OP2"]['R level '] = bytes[0x7F]
        patch["OP2"]['R time '] = bytes[0x7B]
        patch["OP2"]['L gain '] = bytes[0xA0]
        patch["OP2"]['R gain '] = bytes[0xA2]
        patch["OP2"]['L curve'] = "Line" if bytes[0xA3] & 0x01 else "Exp"
        patch["OP2"]['R curve'] = "Line" if bytes[0xA3] & 0x10 else "Exp"
        print(json.dumps(patch, indent=4))

if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)

while True:
    if keyboard.is_pressed("q"):
        break
    pass

port.close()

