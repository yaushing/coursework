from bot import get_answer
import pgzrun
import time, random, math

###############
## VARIABLES ##
###############

WIDTH = 900 # Window size
HEIGHT = 800
TILE_SIZE = 30 # Size of each tile
ROOM_SIZE = 20
ROOM_MAP_WIDTH = 3 # Number of rooms in the map (left to right)
ROOM_MAP_HEIGHT = 3 # Number of rooms in the map (top to bottom)
TRANSPARENT_WALL_HEIGHTS = [] # The rows of rooms that have a transparent  wall (populated later)
top_left_x = 0 
top_left_y = 60 # Shifts room down so that the top-most pillar is visible
x_shift, y_shift = 0, 0 # Shifts rooms in relation to player (player stays in the centre of the screen)
robot_speaking = False
robot_text = ""
player_speaking = False
player_text = ""
SHIFTED = list(")!@#$%^&*(")

########################
### PLAYER VARIABLES ###
########################

# Player movement animations
PLAYER = {
    "left": [images.spacesuit_left, images.spacesuit_left_1,
            images.spacesuit_left_2, images.spacesuit_left_3,
            images.spacesuit_left_4
            ], 
    "right": [images.spacesuit_right, images.spacesuit_right_1,
            images.spacesuit_right_2, images.spacesuit_right_3,
            images.spacesuit_right_4
            ],
    "up": [images.spacesuit_back, images.spacesuit_back_1,
            images.spacesuit_back_2, images.spacesuit_back_3,
            images.spacesuit_back_4 
            ],
    "down": [images.spacesuit_front, images.spacesuit_front_1,
            images.spacesuit_front_2, images.spacesuit_front_3,
            images.spacesuit_front_4
            ]
    }

player_direction = "right" # The direction the player is facing
player_frame = 0 # Frame of animation
player_image = PLAYER[player_direction][player_frame] # Image of the player
player_offset_x, player_offset_y = 0, 0 # Player offset to fit animations and movement along the x and y axis (0.25 offset, frame 1, 0.5 offset, frame 2... 1 offset = x += 1, frame 0 again)
player_x, player_y = 9, 9 # Player position in relation to environment
current_room = 0 # The room the player is in

PLAYER_SHADOW = {
    "left": [images.spacesuit_left_shadow, images.spacesuit_left_1_shadow,
            images.spacesuit_left_2_shadow, images.spacesuit_left_3_shadow,
            images.spacesuit_left_4_shadow
            ],
    "right": [images.spacesuit_right_shadow, images.spacesuit_right_1_shadow,
            images.spacesuit_right_2_shadow,
            images.spacesuit_right_3_shadow, images.spacesuit_right_4_shadow
            ],
    "up": [images.spacesuit_back_shadow, images.spacesuit_back_1_shadow,
            images.spacesuit_back_2_shadow, images.spacesuit_back_3_shadow,
            images.spacesuit_back_4_shadow
            ],
    "down": [images.spacesuit_front_shadow, images.spacesuit_front_1_shadow,
            images.spacesuit_front_2_shadow, images.spacesuit_front_3_shadow,
            images.spacesuit_front_4_shadow
            ]
    }

player_image_shadow = PLAYER_SHADOW["down"][0]

wall_transparency_frame = 0

OBJECTS = [
    [images.void, None, "The empty void of space"],
    [images.floor, None, "The floor is shiny and clean"],
    [images.pillar, images.full_shadow, "The wall is smooth and cold"],
    [[images.pillar, images.pillar_95, images.pillar_80, images.pillar_60, images.pillar_50], None, "The wall is smooth and cold"],
    [images.soil, None, "It's like a desert. Or should that be dessert?"],
    [images.pillar_low, images.half_shadow, "The wall is smooth and cold"]
]

items_player_may_stand_on = [1, 4]

################
### MAKE MAP ###
################

def create_room(width, height, left=False, right=False, up=False, down=False):
    assert width % 2 == 0, "Width must be even"
    assert height % 2 == 0, "Height must be even"
    assert 0 <= width < ROOM_SIZE, f"Width ({width}) must between 0 and ROOM_SIZE ({ROOM_SIZE}), inclusive."
    assert 0 <= height < ROOM_SIZE, f"Height ({height}) must be between 0 and ROOM_SIZE ({ROOM_SIZE}), inclusive."
    if width == 0 or height == 0: return [[0 for _ in range(ROOM_SIZE)] for _ in range(ROOM_SIZE)]
    lr_borders = (ROOM_SIZE - width) // 2
    ud_borders = (ROOM_SIZE - height) // 2
    room = [[2 for _ in range(width)]] + [[2] + [1 for _ in range(width - 2)] + [2] for _ in range(height-2)] + [[3 for _ in range(width)]]
    if left:
        sections = height // 2
        room[sections - 1][0] = 1
        room[sections][0] = 1
    if right:
        sections = height // 2
        room[sections - 1][-1] = 1
        room[sections][-1] = 1
    if up:
        sections = width // 2
        room[0][sections - 1] = 1
        room[0][sections] = 1
    if down: 
        sections = width // 2
        room[-1][sections - 1] = 1
        room[-1][sections] = 1
    room = [[0 for _ in range(width)] for _ in range(ud_borders)] + room + [[0 for _ in range(width)] for _ in range(ud_borders)]
    for i in range(ROOM_SIZE):
        room[i] = [0 for _ in range(lr_borders)] + room[i] + [0 for _ in range(lr_borders)]
    if left:
        sections = height // 2
        room[sections - 2 + ud_borders][:lr_borders] = [2 for _ in range(lr_borders)]
        room[sections - 1 + ud_borders][:lr_borders] = [1 for _ in range(lr_borders)]
        room[sections + ud_borders][:lr_borders] = [1 for _ in range(lr_borders)]
        room[sections + 1 + ud_borders][:lr_borders] = [3 for _ in range(lr_borders)]
    if right:
        sections = height // 2
        room[sections - 2 + ud_borders][-lr_borders:] = [2 for _ in range(lr_borders)]
        room[sections - 1 + ud_borders][-lr_borders:] = [1 for _ in range(lr_borders)]
        room[sections + ud_borders][-lr_borders:] = [1 for _ in range(lr_borders)]
        room[sections + 1 + ud_borders][-lr_borders:] = [3 for _ in range(lr_borders)]
    if up:
        sections = width // 2
        for i in range(ud_borders):
            room[i][sections - 2 + lr_borders] = 2
            room[i][sections - 1 + lr_borders] = 1
            room[i][sections + lr_borders] = 1
            room[i][sections + 1 + lr_borders] = 2
    if down:
        sections = width // 2
        for i in range(ud_borders):
            room[-i - 1][sections - 2 + lr_borders] = 2
            room[-i - 1][sections - 1 + lr_borders] = 1
            room[-i - 1][sections + lr_borders] = 1
            room[-i - 1][sections + 1 + lr_borders] = 2
    return room

def generate_rooms(rooms):
    room_data = []
    for i in range(len(rooms)):
        if i % ROOM_MAP_WIDTH == 0:
            ROW_DATA = create_room(rooms[i][0], rooms[i][1], rooms[i][2], rooms[i][3], rooms[i][4], rooms[i][5])
            if i != (len(rooms) - 1): continue
        for j in range(ROOM_SIZE):
            temp_room = create_room(rooms[i][0], rooms[i][1], rooms[i][2], rooms[i][3], rooms[i][4], rooms[i][5])
            ROW_DATA[j] += temp_room[j]
        if i == (len(rooms) - 1):
            if i % ROOM_MAP_WIDTH != ROOM_MAP_WIDTH - 1:
                for _ in range((ROOM_MAP_WIDTH - 1) - (i % ROOM_MAP_WIDTH)):
                    for j in range(ROOM_SIZE):
                        ROW_DATA[j] += [0 for _ in range(ROOM_SIZE)]
        if (i % ROOM_MAP_WIDTH) == (ROOM_MAP_WIDTH - 1) or i == len(rooms) - 1:
            room_data += ROW_DATA
    # Validations:
    final = []
    for row in room_data:
        if len(row) > 0: final.append(row)
    assert len(final) == ROOM_MAP_HEIGHT * ROOM_SIZE, f"Expected height to be {ROOM_MAP_HEIGHT * ROOM_SIZE}, got {len(room_data)}" 
    for i in range(len(final)):
        assert len(final[i]) == ROOM_MAP_WIDTH * ROOM_SIZE, f"Expected width of row {i} to be {ROOM_MAP_WIDTH * ROOM_SIZE}, got {len(final[i])}" 
    return final

def adjust_wall_transparency():
    global wall_transparency_frame
    HEIGHT_TRIGGERS = [i - 1 for i in TRANSPARENT_WALL_HEIGHTS] # y values where the transparent walls will be called
    HEIGHT_TRIGGERS += [i - 2 for i in TRANSPARENT_WALL_HEIGHTS]
    if player_y in HEIGHT_TRIGGERS and room_map[player_y + 2][player_x] == 3 and wall_transparency_frame < 4:
        wall_transparency_frame += 1 # Fade wall in.
    if player_y not in HEIGHT_TRIGGERS and wall_transparency_frame > 0:
        wall_transparency_frame -= 1 # Fade wall out.

ROOMS = [
    [14, 10, False, True, False, False, "your bedroom.", ""],
    [16, 16, True, True, False, True, "the lounging area.", "Astronauts chill in this area."],
    [4, 4, True, False, False, True, "an access corridor.", "Why would you come from here?"],
    [0, 0, False, False, False, False, "the void of space.", "How did you even get out here?"],
    [18, 18, False, True, True, True, "mission control.", "You used to be able to communicate with your officers from here."],
    [6, 10, True, False, True, True, "the bridge.", "You used to be able to control your ship from here..."],
    [14, 10, False, True, False, False, "the life support system.", ""],
    [16, 16, True, True, True, False, "the garden.", "The plants grow here. Tomatoes grow surprisingly well!"],
    [4, 4, True, False, True, False, "an access corridor.", "How did you get here?"],
]

def draw_image(image, y, x):
    screen.blit(image, (top_left_x + ((x + x_shift) * TILE_SIZE), top_left_y + ((y + y_shift) * TILE_SIZE) - image.get_height()) )

def draw_shadow(image, y, x):
    screen.blit(image,(top_left_x + ((x + x_shift) * TILE_SIZE), top_left_y + ((y + y_shift) * TILE_SIZE)))

def draw_player():
    player_image = PLAYER[player_direction][player_frame]
    screen.blit(player_image, (top_left_x + 15 * TILE_SIZE, top_left_y + 15 * TILE_SIZE - player_image.get_height()))
    player_image_shadow = PLAYER_SHADOW[player_direction][player_frame]
    screen.blit(player_image_shadow, (top_left_x + 15 * TILE_SIZE, top_left_y + 15 * TILE_SIZE))

room_map = generate_rooms(ROOMS)
for row in room_map:
    print("".join(list(map(str, row))))

###############
### CHATBOT ###
###############

def on_key_up(key, mod):
    global player_speaking, player_text
    key_id = str(key)[str(key).index(".") + 1:]
    if not player_speaking and key_id == "C": # If the chatbot hasn't started, start the chatbot, pausing the gameloop and other interactions
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        start_chatbot()
    else: # Typing
        if len(key_id) == 1: 
            if mod: player_text += key_id
            else: player_text += key_id.lower()
        if len(key_id) == 3:
            if mod: player_text += SHIFTED[int(key_id[-1])]
            else: player_text += key_id[-1]
        if key_id == "BACKQUOTE":
            if mod: player_text += "~"
            else: player_text += "`"
        if key_id == "MINUS":
            if mod: player_text += "_"
            else: player_text += "-"
        if key_id == "EQUALS":
            if mod: player_text += "+"
            else: player_text += "="
        if key_id == "LEFTBRACKET":
            if mod: player_text += "{"
            else: player_text += "["
        if key_id == "RIGHTBRACKET":
            if mod: player_text += "}"
            else: player_text += "]"
        if key_id == "BACKSLASH":
            if mod: player_text += "|"
            else: player_text += "\\"
        if key_id == "SEMICOLON":
            if mod: player_text += ":"
            else: player_text += ";"
        if key_id == "QUOTE":
            if mod: player_text += '"'
            else: player_text += "'"
        if key_id == "COMMA":
            if mod: player_text += "<"
            else: player_text += ","
        if key_id == "PERIOD":
            if mod: player_text += ">"
            else: player_text += "."
        if key_id == "SLASH":
            if mod: player_text += "?"
            else: player_text += "/"
        if key_id == "SPACE": player_text += " "
        if key_id == "BACKSPACE": player_text = player_text[:-1]
        if key_id == "RETURN": end_player_message()

def end_player_message(): # When the player is done typing, close the popup. If the player_text is an exit query (currently only :q), stop the chatbot and resume game parts. Else, get the reply from the chatbot
    global player_speaking
    player_speaking = False
    if player_text == ":q": 
        clock.schedule_interval(robot_interactions, 0.05)
        clock.schedule_interval(game_loop, 0.01)
        pass
    else: get_reply(player_text)

def get_reply(text):
    robot_reply = get_answer(text)
    display_robot_reply(robot_reply)
    print(robot_reply)

def display_robot_reply(text):
    global robot_speaking, robot_text
    robot_speaking = True
    robot_text = text
    clock.schedule_unique(end_robot_message, 5.0)

def end_robot_message():
    global robot_speaking
    robot_speaking = False
    get_player_text()

def get_player_text():
    global player_speaking, player_text
    player_text = ""
    player_speaking = True

def start_chatbot():
    clock.unschedule(robot_interactions)
    get_player_text()

########################
#### MAIN GAME LOOPS ###
########################
def draw():
    screen.blit(images.backdrop, (0 + min(x_shift, 0), 0 + min(y_shift, 0)))
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE): 
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            if room_map[y][x] in items_player_may_stand_on: 
                draw_image(OBJECTS[room_map[y][x]][0], y, x)
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE):
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            item_here = room_map[y][x]
            # Player cannot walk on 255: it marks spaces used by wide objects.
            if item_here not in items_player_may_stand_on + [255]:
                image = OBJECTS[item_here][0]
                if item_here == 3:
                    image = OBJECTS[item_here][0][wall_transparency_frame]
                draw_image(image, y, x) 
                if OBJECTS[item_here][1] is not None: # If object has a shadow
                    shadow_image = OBJECTS[item_here][1]
                    # if shadow might need horizontal tiling
                    if shadow_image in [images.half_shadow, images.full_shadow]:
                        shadow_width = int(image.get_width() / TILE_SIZE)
                        # Use shadow across width of object.
                        for z in range(0, shadow_width):
                            draw_shadow(shadow_image, y, x+z)
                    else:
                        draw_shadow(shadow_image, y, x)
        if (player_y == y):
            draw_player()
    if robot_speaking:
        screen.blit(images.textbox, (30, 650))
        screen.draw.text("Robot Name", (60, 670), color="black", fontname="biorhyme", width=780, lineheight=1)
        screen.draw.text(robot_text, (60, 700), color="black", fontname="biorhyme", width=780, lineheight=1, fontsize=15)
    if player_speaking:
        screen.blit(images.textbox, (30, 650))
        screen.draw.text("You", (60, 670), color="black", fontname="biorhyme", width=780, lineheight=1)
        screen.draw.text(player_text, (60, 700), color="black", fontname="biorhyme", width=780, lineheight=1, fontsize = 15)

def display_message(text):
    global robot_speaking, robot_text
    robot_speaking = True
    robot_text = text
    print(text)

def end_message():
    global robot_speaking
    robot_speaking = False
    clock.schedule_interval(robot_interactions, 0.05)

def game_loop():
    global player_x, player_y
    global from_player_x, from_player_y
    global player_image, player_image_shadow 
    global player_offset_x, player_offset_y
    global player_frame, player_direction
    global x_shift, y_shift
    global current_room

    current_room = player_x // ROOM_SIZE + (player_y // ROOM_SIZE) * 3
    if player_frame > 0:
        player_frame += 1
        time.sleep(0.05)
        if player_frame == 5:
            player_frame = 0
            player_offset_x = 0
            player_offset_y = 0

# save player's current position
    old_player_x = player_x
    old_player_y = player_y

# move if key is pressed
    if player_frame == 0:
        if keyboard.right:
            from_player_x = player_x
            from_player_y = player_y
            player_x += 1
            player_direction = "right"
            player_frame = 1
        elif keyboard.left: #elif stops player making diagonal movements
            from_player_x = player_x
            from_player_y = player_y
            player_x -= 1
            player_direction = "left"
            player_frame = 1
        elif keyboard.up:
            from_player_x = player_x
            from_player_y = player_y
            player_y -= 1
            player_direction = "up"
            player_frame = 1
        elif keyboard.down:
            from_player_x = player_x
            from_player_y = player_y
            player_y += 1
            player_direction = "down"
            player_frame = 1      
    if room_map[player_y][player_x] not in items_player_may_stand_on:
        player_x = old_player_x
        player_y = old_player_y
        player_frame = 0
    if player_direction == "right" and player_frame > 0:
        player_offset_x = -1 + (0.25 * player_frame)
    if player_direction == "left" and player_frame > 0:
        player_offset_x = 1 - (0.25 * player_frame)
    if player_direction == "up" and player_frame > 0:
        player_offset_y = 1 - (0.25 * player_frame)
    if player_direction == "down" and player_frame > 0:
        player_offset_y = -1 + (0.25 * player_frame)
    x_shift, y_shift = - (player_x + player_offset_x - 15), -(player_y + player_offset_y - 15)

def robot_interactions():
    global robot_speaking
    if keyboard.t:
        clock.unschedule(robot_interactions)
        display_message(f"This is {ROOMS[current_room][6]} {ROOMS[current_room][7]} ")
        clock.schedule_unique(end_message, 5.0)


#############
### START ###
#############
for i in range(len(room_map)):
    if 3 in room_map[i]: TRANSPARENT_WALL_HEIGHTS.append(i) # Populates the list of rows in the room map which has walls which may need to be transparent

clock.schedule_interval(game_loop, 0.03)
clock.schedule_interval(adjust_wall_transparency, 0.05)
clock.schedule_interval(robot_interactions, 0.05)
pgzrun.go()
