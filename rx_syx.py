import keyboard
import mido
import json
import os

inports = mido.get_input_names()
print(inports)

def print_dump(bytes):
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

def make_signed(byte):
    # all valuse have to pack into the 128 steps from 0x00 to 0x7F but some are
    # really "signed" values like -18..+18, -63..+63, -63..+64 so as soon as the
    # dump is received convert such values to signed which basically means (as this
    # is in 7 bits not 8 bits) that >64 should be -(128 - n)
    retval = int(byte)
    if byte > 64:
        retval = int (-1 * (128 - byte))
    return retval

def decode_bytes(bytes, patch):
    txt = ""
    txt += chr(bytes[0x2E])
    txt += chr(bytes[0x2F])
    txt += chr(bytes[0x30])
    txt += chr(bytes[0x32])
    patch['Name'] = txt

    patch["OP1"]['Feedback'] = make_signed(bytes[0x45])
    patch["OP1"]['OP2In'] = bytes[0xAF]
    patch["OP1"]['OP3In'] = bytes[0xB0]
    patch["OP1"]['OP4In'] = bytes[0xB2]
    patch["OP1"]['Output'] = bytes[0xC0]
    patch["OP1"]['PitchEnv'] = bytes[0xCE]
    patch["OP1"]['Fixed'] = bytes[0x4A]
    ratio = ((bytes[0x5D] * 256) + bytes[0x5C] )
    patch["OP1"]['Ratio'] = ratio
    patch["OP1"]['Detune'] = make_signed(bytes[0x5F])
    patch["OP1"]['Level'] = bytes[0x5E]
    patch["OP1"]['VelSens'] = bytes[0xC5]
    patch["OP1"]['Time'] = bytes[0xCA]
    patch["OP1"]['UpCurve'] = make_signed(bytes[0xD3])
    patch["OP1"]['DnCurve'] = make_signed(bytes[0xD4])
    patch["OP1"]['Scale'] = bytes[0x9F]
    patch["OP1"]['ALevel'] = bytes[0x73]
    patch["OP1"]['ATime'] = bytes[0x6E]
    patch["OP1"]['DLevel'] = bytes[0x74]
    patch["OP1"]['DTime'] = bytes[0x6F]
    patch["OP1"]['SLevel'] = bytes[0x75]
    patch["OP1"]['STime'] = bytes[0x70]
    patch["OP1"]['RLevel'] = bytes[0x76]
    patch["OP1"]['RTime'] = bytes[0x72]
    patch["OP1"]['LGain'] = make_signed(bytes[0x9C])
    patch["OP1"]['RGain'] = make_signed(bytes[0x9D])
    patch["OP1"]['LCurve'] = bytes[0x9E] & 0x01
    patch["OP1"]['RCurve'] = bytes[0x9E] & 0x10

    patch["OP2"]['Feedback'] = make_signed(bytes[0x46])
    patch["OP2"]['OP1In'] = bytes[0xB3]
    patch["OP2"]['OP3In'] = bytes[0xB5]
    patch["OP2"]['OP4In'] = bytes[0xB6]
    patch["OP2"]['Output'] = bytes[0xC2]
    patch["OP2"]['PitchEnv'] = bytes[0xCF]
    patch["OP2"]['Fixed'] = bytes[0x4E]
    ratio = ((bytes[0x61] * 256) + bytes[0x60] )
    patch["OP2"]['Ratio'] = ratio
    patch["OP2"]['Detune'] = make_signed(bytes[0x64])
    patch["OP2"]['Level'] = bytes[0x63]
    patch["OP2"]['VelSens'] = bytes[0xC6]
    patch["OP2"]['Time'] = bytes[0xCB]
    patch["OP2"]['UpCurve'] = make_signed(bytes[0xD5])
    patch["OP2"]['DnCurve'] = make_signed(bytes[0xD6])
    patch["OP2"]['Scale'] = bytes[0xA4]
    patch["OP2"]['ALevel'] = bytes[0x7C]
    patch["OP2"]['ATime'] = bytes[0x77]
    patch["OP2"]['DLevel'] = bytes[0x7D]
    patch["OP2"]['DTime'] = bytes[0x78]
    patch["OP2"]['SLevel'] = bytes[0x7E]
    patch["OP2"]['STime'] = bytes[0x7A]
    patch["OP2"]['RLevel'] = bytes[0x7F]
    patch["OP2"]['RTime'] = bytes[0x7B]
    patch["OP2"]['LGain'] = make_signed(bytes[0xA0])
    patch["OP2"]['RGain'] = make_signed(bytes[0xA2])
    patch["OP2"]['LCurve'] = bytes[0xA3] & 0x01
    patch["OP2"]['RCurve'] = bytes[0xA3] & 0x10

    patch["OP3"]['Feedback'] = make_signed(bytes[0x47])
    patch["OP3"]['OP1In'] = bytes[0xB7]
    patch["OP3"]['OP2In'] = bytes[0xB8]
    patch["OP3"]['OP4In'] = bytes[0xBB]
    patch["OP3"]['Output'] = bytes[0xC3]
    patch["OP3"]['PitchEnv'] = bytes[0xD0]
    patch["OP3"]['Fixed'] = bytes[0x53]
    ratio = ((bytes[0x66] * 256) + bytes[0x65] )
    patch["OP3"]['Ratio'] = ratio
    patch["OP3"]['Detune'] = make_signed(bytes[0x68])
    patch["OP3"]['Level'] = bytes[0x67]
    patch["OP3"]['VelSens'] = bytes[0xC7]
    patch["OP3"]['Time'] = bytes[0xCC]
    patch["OP3"]['UpCurve'] = make_signed(bytes[0xD7])
    patch["OP3"]['DnCurve'] = make_signed(bytes[0xD8])
    patch["OP3"]['Scale'] = bytes[0xA8]
    patch["OP3"]['ALevel'] = bytes[0x85]
    patch["OP3"]['ATime'] = bytes[0x80]
    patch["OP3"]['DLevel'] = bytes[0x86]
    patch["OP3"]['DTime'] = bytes[0x82]
    patch["OP3"]['SLevel'] = bytes[0x87]
    patch["OP3"]['STime'] = bytes[0x83]
    patch["OP3"]['RLevel'] = bytes[0x88]
    patch["OP3"]['RTime'] = bytes[0x84]
    patch["OP3"]['LGain'] = make_signed(bytes[0xA5])
    patch["OP3"]['RGain'] = make_signed(bytes[0xA6])
    patch["OP3"]['LCurve'] = bytes[0xA7] & 0x01
    patch["OP3"]['RCurve'] = bytes[0xA7] & 0x10

    patch["OP4"]['Feedback'] = make_signed(bytes[0x48])
    patch["OP4"]['OP1In'] = bytes[0xBC]
    patch["OP4"]['OP2In'] = bytes[0xBD]
    patch["OP4"]['OP3In'] = bytes[0xBE]
    patch["OP4"]['Output'] = bytes[0xC4]
    patch["OP4"]['PitchEnv'] = bytes[0xD2]
    patch["OP4"]['Fixed'] = bytes[0x57]
    ratio = ((bytes[0x6B] * 256) + bytes[0x6A] )
    patch["OP4"]['Ratio'] = ratio
    patch["OP4"]['Detune'] = make_signed(bytes[0x6D])
    patch["OP4"]['Level'] = bytes[0x6C]
    patch["OP4"]['VelSens'] = bytes[0xC8]
    patch["OP4"]['Time'] = bytes[0xCD]
    patch["OP4"]['UpCurve'] = make_signed(bytes[0xDA])
    patch["OP4"]['DnCurve'] = make_signed(bytes[0xDB])
    patch["OP4"]['Scale'] = bytes[0xAD]
    patch["OP4"]['ALevel'] = bytes[0x8E]
    patch["OP4"]['ATime'] = bytes[0x8A]
    patch["OP4"]['DLevel'] = bytes[0x8F]
    patch["OP4"]['DTime'] = bytes[0x8B]
    patch["OP4"]['SLevel'] = bytes[0x90]
    patch["OP4"]['STime'] = bytes[0x8C]
    patch["OP4"]['RLevel'] = bytes[0x92]
    patch["OP4"]['RTime'] = bytes[0x8D]
    patch["OP4"]['LGain'] = make_signed(bytes[0xAA])
    patch["OP4"]['RGain'] = make_signed(bytes[0xAB])
    patch["OP4"]['LCurve'] = bytes[0xAC] & 0x01
    patch["OP4"]['RCurve'] = bytes[0xAC] & 0x10

    patch["Pitch"]['ALevel'] = make_signed(bytes[0x97])
    patch["Pitch"]['ATime'] = bytes[0x93]
    patch["Pitch"]['DLevel'] = make_signed(bytes[0x98])
    patch["Pitch"]['DTime'] = bytes[0x94]
    patch["Pitch"]['SLevel'] = make_signed(bytes[0x9A])
    patch["Pitch"]['STime'] = bytes[0x95]
    patch["Pitch"]['RLevel'] = make_signed(bytes[0x9B])
    patch["Pitch"]['RTime'] = bytes[0x96]

    patch["Mixer"]['Level'] = make_signed(bytes[0xDC])

def encode_bytes(patch, bytes):
    bytes[0x2E] = ord(patch['Name'][0])
    bytes[0x2F] = ord(patch['Name'][1])
    bytes[0x30] = ord(patch['Name'][2])
    bytes[0x32] = ord(patch['Name'][3])

    bytes[0x45] = patch["OP1"]['Feedback']                 # -63.0 .. +64.0 (+1.0)
    bytes[0xAF] = patch["OP1"]['OP2In']                    # 0 .. 127 (+1)
    bytes[0xB0] = patch["OP1"]['OP3In']
    bytes[0xB2] = patch["OP1"]['OP4In']
    bytes[0xC0] = patch["OP1"]['Output']                   # 0..127 (+1)
    bytes[0xCE] = patch["OP1"]['PitchEnv']                      # OFF / ON
    bytes[0x4A] = patch["OP1"]['Fixed']                    # OFF / ON
    bytes[0x5C] = (patch["OP1"]['Ratio']) & 0xFF           # 0.50 .. 32.00 (+.01) / 1 .. 9755 (+1)
    bytes[0x5D] = int((patch["OP1"]['Ratio']) / 256)
    bytes[0x5F] = patch["OP1"]['Detune']                   # -63 .. 63 (+1)
    bytes[0x5E] = patch["OP1"]['Level']                    # 0 .. 127 (+1)
    bytes[0xC5] = patch["OP1"]['VelSens']                  # 0 .. 127 (+1)
    bytes[0xCA] = patch["OP1"]['Time']                     # 0 .. 127 (+1)
    bytes[0xD3] = patch["OP1"]['UpCurve']                   # -18 .. +18 (+1)
    bytes[0xD4] = patch["OP1"]['DnCurve']                   # -18 .. +18 (+1)
    bytes[0x9F] = patch["OP1"]['Scale']                    # C1 .. C7
    bytes[0x73] = patch["OP1"]['ALevel']                   # 0 .. 127 (+1)
    bytes[0x6E] = patch["OP1"]['ATime']
    bytes[0x74] = patch["OP1"]['DLevel']
    bytes[0x6F] = patch["OP1"]['DTime']
    bytes[0x75] = patch["OP1"]['SLevel']
    bytes[0x70] = patch["OP1"]['STime']
    bytes[0x76] = patch["OP1"]['RLevel']
    bytes[0x72] = patch["OP1"]['RTime']
    bytes[0x9C] = patch["OP1"]['LGain']                    # -63 .. +63 (+1)
    bytes[0x9D] = patch["OP1"]['RGain']
    curves = (patch["OP1"]['LCurve']) | (patch["OP1"]['RCurve'])  # LINE / EXP
    bytes[0x9E] = curves

    bytes[0x46] = patch["OP2"]['Feedback']
    bytes[0xB3] = patch["OP2"]['OP1In']
    bytes[0xB5] = patch["OP2"]['OP3In']
    bytes[0xB6] = patch["OP2"]['OP4In']
    bytes[0xC2] = patch["OP2"]['Output']
    bytes[0xCF] = patch["OP2"]['PitchEnv']
    bytes[0x4E] = patch["OP2"]['Fixed']
    bytes[0x60] = (patch["OP2"]['Ratio']) & 0xFF
    bytes[0x61] = int((patch["OP2"]['Ratio']) / 256)
    bytes[0x64] = patch["OP2"]['Detune']
    bytes[0x63] = patch["OP2"]['Level']
    bytes[0xC6] = patch["OP2"]['VelSens']
    bytes[0xCB] = patch["OP2"]['Time']
    bytes[0xD5] = patch["OP2"]['UpCurve']
    bytes[0xD6] = patch["OP2"]['DnCurve']
    bytes[0xA4] = patch["OP2"]['Scale']
    bytes[0x7C] = patch["OP2"]['ALevel']
    bytes[0x77] = patch["OP2"]['ATime']
    bytes[0x7D] = patch["OP2"]['DLevel']
    bytes[0x78] = patch["OP2"]['DTime']
    bytes[0x7E] = patch["OP2"]['SLevel']
    bytes[0x7A] = patch["OP2"]['STime']
    bytes[0x7F] = patch["OP2"]['RLevel']
    bytes[0x7B] = patch["OP2"]['RTime']
    bytes[0xA0] = patch["OP2"]['LGain']
    bytes[0xA2] = patch["OP2"]['RGain']
    curves = (patch["OP2"]['LCurve']) | (patch["OP2"]['RCurve'])
    bytes[0xA3] = curves

    bytes[0x47] = patch["OP3"]['Feedback']
    bytes[0xB7] = patch["OP3"]['OP1In']
    bytes[0xB8] = patch["OP3"]['OP2In']
    bytes[0xBB] = patch["OP3"]['OP4In']
    bytes[0xC3] = patch["OP3"]['Output']
    bytes[0xD0] = patch["OP3"]['PitchEnv']
    bytes[0x53] = patch["OP3"]['Fixed']
    bytes[0x65] = (patch["OP3"]['Ratio']) & 0xFF
    bytes[0x66] = int((patch["OP3"]['Ratio']) / 256)
    bytes[0x68] = patch["OP3"]['Detune']
    bytes[0x67] = patch["OP3"]['Level']
    bytes[0xC7] = patch["OP3"]['VelSens']
    bytes[0xCC] = patch["OP3"]['Time']
    bytes[0xD7] = patch["OP3"]['UpCurve']
    bytes[0xD8] = patch["OP3"]['DnCurve']
    bytes[0xA8] = patch["OP3"]['Scale']
    bytes[0x85] = patch["OP3"]['ALevel']
    bytes[0x80] = patch["OP3"]['ATime']
    bytes[0x86] = patch["OP3"]['DLevel']
    bytes[0x82] = patch["OP3"]['DTime']
    bytes[0x87] = patch["OP3"]['SLevel']
    bytes[0x83] = patch["OP3"]['STime']
    bytes[0x88] = patch["OP3"]['RLevel']
    bytes[0x84] = patch["OP3"]['RTime']
    bytes[0xA5] = patch["OP3"]['LGain']
    bytes[0xA6] = patch["OP3"]['RGain']
    curves = (patch["OP3"]['LCurve']) | (patch["OP3"]['RCurve'])
    bytes[0xA7] = curves

    bytes[0x48] = patch["OP4"]['Feedback']
    bytes[0xBC] = patch["OP4"]['OP1In']
    bytes[0xBD] = patch["OP4"]['OP2In']
    bytes[0xBE] = patch["OP4"]['OP3In']
    bytes[0xC4] = patch["OP4"]['Output']
    bytes[0xD2] = patch["OP4"]['PitchEnv']
    bytes[0x57] = patch["OP4"]['Fixed']
    bytes[0x6A] = (patch["OP4"]['Ratio']) & 0xFF
    bytes[0x6B] = int((patch["OP4"]['Ratio']) / 256)
    bytes[0x6D] = patch["OP4"]['Detune']
    bytes[0x6C] = patch["OP4"]['Level']
    bytes[0xC8] = patch["OP4"]['VelSens']
    bytes[0xCD] = patch["OP4"]['Time']
    bytes[0xDA] = patch["OP4"]['UpCurve']
    bytes[0xDB] = patch["OP4"]['DnCurve']
    bytes[0xAD] = patch["OP4"]['Scale']
    bytes[0x8E] = patch["OP4"]['ALevel']
    bytes[0x8A] = patch["OP4"]['ATime']
    bytes[0x8F] = patch["OP4"]['DLevel']
    bytes[0x8B] = patch["OP4"]['DTime']
    bytes[0x90] = patch["OP4"]['SLevel']
    bytes[0x8C] = patch["OP4"]['STime']
    bytes[0x92] = patch["OP4"]['RLevel']
    bytes[0x8D] = patch["OP4"]['RTime']
    bytes[0xAA] = patch["OP4"]['LGain']
    bytes[0xAB] = patch["OP4"]['RGain']
    curves = (patch["OP4"]['LCurve']) | (patch["OP4"]['RCurve'])
    bytes[0xAC] = curves

    bytes[0x97] = patch["Pitch"]['ALevel']         # -48 .. +48 (+1)
    bytes[0x93] = patch["Pitch"]['ATime']          # 0 .. 127 (+1)
    bytes[0x98] = patch["Pitch"]['DLevel']
    bytes[0x94] = patch["Pitch"]['DTime']
    bytes[0x9A] = patch["Pitch"]['SLevel']
    bytes[0x95] = patch["Pitch"]['STime']
    bytes[0x9B] = patch["Pitch"]['RLevel']
    bytes[0x96] = patch["Pitch"]['RTime']

    bytes[0xDC] = patch["Mixer"]['Level']           # -63 .. +63 (+1)

def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    # sound dump comes in 3 messages - look for the middle one with sequence number 2 (from 1, 2, 3)
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
        bytes = msg.bytes()

        print_dump(bytes)

        decode_bytes(bytes, patch)

        print(json.dumps(patch, indent=4))
        
        newbytes = [0 for _ in range(0xE0)]
        encode_bytes(patch, newbytes)
        print_dump(newbytes)

if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)
else:
    # this is just test code when no MIDI available - create random byte array as message and create JSON
    bytes = bytearray(os.urandom(260))
    for n in range(len(bytes)):
        if bytes[n] > 127:
            bytes[n] = bytes[n] & 0x7F
    patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
    print_dump(bytes)
    decode_bytes(bytes, patch)
    with open("mypatch.json", 'w') as f:
        f.write(json.dumps(patch, indent=4))
    print(json.dumps(patch, indent=4))

while True:
    if keyboard.is_pressed("q"):
        break
    pass

port.close()

