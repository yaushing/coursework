text = """2222222222222222
2455111111111162
2111111111111112
2111111111111112
2111111111111112
2111111111111112
2111111111111112
1111111111111111
1111111111111111
2111111111111112
2111111111111112
2111111111111112
2111111111111112
2111111111111112
2111111111111112
2333332112333332"""

data = text.split("\n")
final = []
for row in data:
    final.append(list(map(int, list(row))))
for y in range(len(final)):
    for x in range(len(final[y])):
        if final[y][x] == 4:
            print(f"[12, {y - 1}, {x - 1}]", end = ", ")
        elif final[y][x] == 5:
            print(f"[13, {y - 1}, {x - 1}]", end = ", ")
        elif final[y][x] == 6:
            print(f"[25, {y - 1}, {x - 1}]", end = ", ")
        elif final[y][x] == 7:
            print(f"[11, {y - 1}, {x - 1}]", end = ", ")