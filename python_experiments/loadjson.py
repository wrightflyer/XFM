import json

# test program to try loading JSON patch file but converting fields
# to internal key names used in RX and ANIM

with open("mypatch.json") as f:
    data = json.load(f)
    
    for i in data:
        print("=====", i, "=====")
        if (i != "Name"):
            for j in data[i]:
                key = f'{i}:{j}'
                print(f'{key} = ', data[i][j])
        else:
            for n in range(4):
                key = f'{i}:chr{n}'
                print(f'{key} = ', data[i][n])
