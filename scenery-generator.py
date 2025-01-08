floormap = """11111111111111
10000000000001
10444400444401
10444400444401
10000000000001
10444400444401
10444400444401
10000000000001
10444400444401
11111111111111"""
final = ""
split_map = [[int(j) for j in list(i)] for i in floormap.split("\n")]
for y in range(len(split_map)):
    for x in range(len(split_map[y])):
        if split_map[y][x] != 0 and split_map[y][x] != 1:
            scenery = f"[{split_map[y][x]}, {y - 1}, {x - 1}]"
            final += scenery + ", "
print(final[:-2])