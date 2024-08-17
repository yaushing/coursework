import pgzrun

WIDTH = 800
HEIGHT = 800
player_x = 400 - (images.astronaut.get_width() / 2)
player_y = 400  - (images.astronaut.get_height() / 2)
top_left_x = 200
top_left_y = 200
x_shift = 0
y_shift = 0

OBJECTS = [images.floor, images.pillar]
def create_room(width, height, left):
    room = [[1 for _ in range(width)]] + [[1] + [0 for _ in range(width - 2)] + [1] for _ in range(height-2)] + [[1 for _ in range(width)]]
    if left:
        sections = height // 2
        if height % 2 == 0:
            room[sections - 1][0] = 0
            room[sections][0] = 0
    return room
room_map = create_room(20, 8, True)

def draw():
    screen.blit(images.backdrop, (0, 0))
    for y in range(len(room_map)):
        for x in range(len(room_map[y])):
            image_to_draw = OBJECTS[room_map[y][x]]
            screen.blit(image_to_draw, (
                top_left_x + (x*30) + x_shift, top_left_y + (y*30) - image_to_draw.get_height() + y_shift))
    screen.blit(images.astronaut,(player_x, player_y))


def game_loop():
    global x_shift, y_shift
    if keyboard.right:
        x_shift -= 5
    elif keyboard.left:
        x_shift += 5
    elif keyboard.up:
        y_shift += 5
    elif keyboard.down:
        y_shift -= 5

clock.schedule_interval(game_loop, 0.03)
pgzrun.go()
