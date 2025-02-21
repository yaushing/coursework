import pickle, pgzrun, pygame

possible_keys = "ESCAPE BACKQUOTE K_1 K_2 K_3 K_4 K_5 K_6 K_7 K_8 K_9 K_0 MINUS EQUALS BACKSPACE TAB".split(
    " "
)
possible_keys += list("QWERTYUIOP")
possible_keys += "LEFTBRACKET RIGHTBRACKET BACKSLASH CAPSLOCK".split(" ")
possible_keys += list("ASDFGHJKL")
possible_keys += "SEMICOLON QUOTE RETURN LSHIFT".split(" ")
possible_keys += list("ZXCVBNM")
possible_keys += "COMMA PERIOD SLASH RSHIFT LCTRL LALT LGUI SPACE RGUI RALT LEFT UP RIGHT DOWN".split(
    " "
)
count = 0
temp = {}
data = {}


def on_key_up(key, mod):
    global count, temp, data
    print(key, count, f"""{key}:"keys.{possible_keys[count]}",""")
    temp[int(key)] = f"keys.{possible_keys[count]}"
    count += 1
    if count == len(possible_keys):
        print(temp)
        for k in range(len(list(temp.keys()))):
            key_ids = list(temp.keys())
            key_ids.sort()
            data[key_ids[k]] = temp[key_ids[k]]
        print(data)
        with open("savefile.txt", "w") as f:
            f.write("{\n\t")
            for k, v in data.items():
                f.write(f"{k}: '{v}',\n\t")
            f.write("}")


pgzrun.go()
