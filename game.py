from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import re
import pgzrun, pygame
import time, random, math
import pickle
#################
### VARIABLES ###
#################
WIDTH = 900 # Window size
HEIGHT = 800
TILE_SIZE = 30 # Size of each tile
ROOM_SIZE = 20
ROOM_MAP_WIDTH = 3 # Number of rooms in the map (left to right)
ROOM_MAP_HEIGHT = 4 # Number of rooms in the map (top to bottom)
SHIFTED = list(")!@#$%^&*(") # Used for keyboard typing
ROBOT_NAME = "Vimal"
SHIP_NAME = "Jolene"
CHAT_DATA = "chat.txt"
MUSIC_CHOICES = ['kisstherain', 'merrygoroundoflife']
top_left_x = 0 
top_left_y = 60 # Shifts room down so that the top-most pillar is visible
x_shift, y_shift = 0, 0 # Shifts rooms in relation to player (player stays in the centre of the screen)
robot_speaking = False # Makes game decide whether to display speech bubble for the robot
robot_text = "" # Text to be displayed when robot_speaking is Trye
player_speaking = False # Same thing but for the player
player_text = ""
doors = {}
walls = {}
paused = False
mute = False
old_click = False

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

player_direction = "up" # The direction the player is facing
player_frame = 0 # Frame of animation
player_image = PLAYER[player_direction][player_frame] # Image of the player
player_offset_x, player_offset_y = 0, 0 # Player offset to fit animations and movement along the x and y axis (0.25 offset, frame 1, 0.5 offset, frame 2... 1 offset = x += 1, frame 0 again)
player_x, player_y = 30, 49 # Player position in relation to environment
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

player_image_shadow = PLAYER_SHADOW[player_direction][0]

#######################
### ROBOT VARIABLES ###
#######################
ROBOT = {
    "left": [images.drone, images.drone],
    "right": [images.drone, images.drone],
    "up": [images.drone, images.drone],
    "down": [images.drone, images.drone]
}
robot_direction = player_direction
robot_moving = 0
robot_image = ROBOT[robot_direction][robot_moving]
robot_offset_x, robot_offset_y = 0, 0
robot_x, robot_y = player_x, player_y + 1

###############
### OBJECTS ###
###############
OBJECTS = {
    0: [images.void, None, "the empty void of space."],
    1: [images.floor, None, "the floor.", "It's shiny and clean."],
    2: [images.pillar, images.full_shadow, "a wall.", "Sterile, and devoid of contamination."],
    3: [[images.pillar, images.pillar_95, images.pillar_80, images.pillar_60, images.pillar_50], None, "a wall.", "Sterile, and devoid of contamination."],
    4: [images.soil, None, "soil, used for the farm.", "Surprisingly, it hasn't spilled onto the ground yet."],
    5: [[images.door, images.door1, images.door2, images.door3, images.door4], [images.door_shadow, images.door1_shadow, images.door3_shadow, images.door4_shadow], "a door.", "It opens and closes."],
    6: [images.pillar_low, images.half_shadow, "a shoft wall.", "Sterile and devoid of contamination."],
    7: [images.bed_left, images.half_shadow, "a bed.", "It's tidy and comfortable."],
    8: [images.bed_right, images.half_shadow, "a bed.", "It's tidy and comfortable."],
    9: [images.table, images.half_shadow, "a table.", "It's made of a strong plastic."],
    10: [images.chair_left, None, "a chair.", "Nice and comfy with a soft cushion."],
    11: [images.chair_right, None, "a chair.", "Nice and comfy with a soft cushion."],
    12: [images.bookcase_tall, images.full_shadow, "a bookshelf.", "It's stacked with reference books."],
    13: [images.bookcase_small, images.half_shadow, "a bookshelf.", "It's stacked with reference books."],
    14: [images.cabinet, images.half_shadow, "a small locker.", "It's used for storing personal items"],
    15: [images.desk_computer, images.half_shadow, "a computer.", "It has logs from over for over 2000 years."],
    16: [images.plant, images.plant_shadow, "a spaceberry plant.", "It's locally sourced, sustainable and healthy!"],
    17: [images.electrical1, images.half_shadow, "a part of the electrical system of the space shuttle.", ""],
    18: [images.electrical2, images.half_shadow, "a part of the electrical system of the space shuttle.", ""],
    19: [images.cactus, images.cactus_shadow, "a cactus.", "It's pretty sharp."],
    20: [images.shrub, images.shrub_shadow, "a space lettuce.", "It's a bit limp, but amazing it's growing here!"],
    21: [images.pipes1, images.pipes1_shadow, "a part of the water purification system of the space shuttle.", ""],
    22: [images.pipes2, images.pipes2_shadow, "a part of the life support systems.", "Don't touch thease."],
    23: [images.pipes3, images.pipes3_shadow, "a part of the life support systems.", "Don't touch thease."],
    25: [images.contraption, images.contraption_shadow, "a scientific experiment of one of the old astronauts.", "What's left, of it, anyways."],
    26: [images.robot_arm, images.robot_arm_shadow, "a robot arm.", "It was used for heavy lifting."],
    27: [images.toilet, images.half_shadow, "a toilet.", "It's sparkling clean."],
    28: [images.sink, None, "a sink, with clean running water recycled through the system.", "It's clean!"],
    29: [images.globe, images.globe_shadow, "a giant globe of the planet", "It gently glows from inside"],
    30: [images.science_lab_table, None, "a table of experiments.", "Martian soil and dust is on it."],
    31: [images.vending_machine, images.full_shadow, "a vending machine.", "Unfortunately, it needs a credit. And I used the last one."],
    33: [images.mission_control_desk, images.mission_control_desk_shadow, "computer station connected to Mission Control.", ""],
    34: [images.whiteboard, images.full_shadow, "a whiteboard.", "It used to be used for brainstorming and planning."],
    35: [images.window, images.full_shadow, "a window.", "It allows you to look out at space."],
    36: [images.robot, images.robot_shadow, "a cleaning robot.", "It's turned off right now to conserve power."],
    37: [images.robot2, images.robot2_shadow, "a robot for terrestial exploration.", "It's turned off right now to conserve power."],
    40: [images.drone, None, "a delivery drone", "They used to whizz through the corridors like nobody's business."],
    41: [images.computer, images.computer_shadow, "a computer workstation", "Used for managing space station systems."],
    42: [images.map, images.full_shadow, "a map charting the path of the ship.", "It's very in-depth."],
    255: [images.floor, None, "the floor.", "It's shiny and clean."],
    256: [images.floor, None, "the floor.", "It's shiny and clean."],
}

# Special tiles:
# 0: Transparent tile, used for space, and the space used up by wide objects which are on the wall furtherst from the screen, adjacent to space.
# 255: The space used up by wide objects, does not allow player to walk through.
# 256: The space used up by wide objects, however allows player to walk through.

#############
### ROOMS ###
#############
ROOMS = [
    [0, 0, False, False, False, False, "", ""],
    [14, 10, False, False, False, True, "the bridge.", "You used to be able to control your ship from here..."],
    [0, 0, False, False, False, False, "", ""],
    [4, 4, False, True, False, True, "an access corridor.", "Why would you come from here?"],
    [12, 10, True, True, True, True, "mission control.", "Back when comms worked, we could talk to Earth from here..."],
    [4, 4, True, False, False, True, "an access corridor.", "How did you get here?"],
    [16, 16, False, True, True, True, "the lab.", "The other astronauts used to run their experiments here."],
    [18, 18, True, True, True, True, "the one and only lounging area in the entire spaceship.", "It's pretty nice!"],
    [16, 16, True, False, True, True, "the garden.", "The plants grow here. Tomatoes grow surprisingly well!"],
    [14, 10, False, False, True, False, "the dorm.", "All the astronauts used to stay here at night."],
    [10, 10, False, False, True, False, "the toilet.", "Also, the only one."],
    [14, 10, False, False, True, False, "the life support system.", ""],
]

###############
### SCENERY ###
###############

SCENERY = {
    1: [[35, -1, 0], [41, 1, 3], [41, 1, 7] ,[15, 3, 0], [15, 3, 3], [15, 3, 7], [15, 3, 10], [15, 6, 0], [15, 6, 3], [15, 6, 7], [15, 6, 10]],
    4: [[33, 2, 0], [33, 2, 6], [33, 5, 0], [33, 5, 6]],
    9: [[7, 0, 0], [14, 0, 2], [7, 0, 3], [8, 0, 7], [14, 0, 9], [8, 0, 10], [7, 2, 0], [14, 2, 2], [7, 2, 3], [8, 2, 7], [14, 2, 9], [8, 2, 10], [7, 5, 0], [14, 5, 2], [7, 5, 3], [8, 5, 7], [14, 5, 9], [8, 5, 10], [7, 7, 0], [14, 7, 2], [7, 7, 3], [8, 7, 7], [14, 7, 9], [8, 7, 10], [35, 8, 0]],
    6: [[12, 0, 0], [13, 0, 1], [13, 0, 2], [25, 0, 10], [26, 2, 3], [11, 5, 2], [10, 5, 11], [30, 5, 3], [11, 9, 2], [10, 9, 11], [30, 9, 3], [26, 10, 3]]
}

checksum = 0
check_counter = 0
for key, room_scenery_list in SCENERY.items():
    for scenery_item_list in room_scenery_list:
        checksum += (scenery_item_list[0] * key
                     + scenery_item_list[1] * (key + 1) 
                     + scenery_item_list[2] * (key + 2))
        check_counter += 1
assert check_counter == 52, f"Expected 52 scenery items, got {check_counter}."
assert checksum == 7906, f"Expected checksum of 7906, got {checksum}."

items_player_may_stand_on = [1, 4, 5, 256]

########################
### CHATBOT TRAINING ###
########################
def remove_chat_metadata(chat_export_file):
    date_time = r"(\d+\/\d+\/\d+,\s\d+:\d+)"  # e.g. "9/16/22, 06:34"
    dash_whitespace = r"\s-\s"  # " - "
    username = r"([\w\s]+)"  # e.g. "Martin"
    metadata_end = r":\s"  # ": "
    pattern = date_time + dash_whitespace + username + metadata_end

    with open(chat_export_file, "r") as corpus_file:
        content = corpus_file.read()
    cleaned_corpus = re.sub(pattern, "", content)
    return tuple(cleaned_corpus.split("\n"))

def remove_non_message_text(export_text_lines):
    messages = export_text_lines[1:-1]

    filter_out_msgs = ("<Media omitted>",)
    return tuple((msg for msg in messages if msg not in filter_out_msgs))

chatbot = ChatBot("Chatpot")
trainer = ListTrainer(chatbot)
cleaned_data = remove_non_message_text(remove_chat_metadata(CHAT_DATA))
trainer.train(cleaned_data)
def get_answer(query):
    return chatbot.get_response(query)
################
### MAKE MAP ###
################

def create_room(room_number, width, height, left=False, right=False, up=False, down=False):
    ### Validations
    assert 0 <= room_number <= ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH, f"Room number is invalid. Expected 0 ≤ room number ≤ {ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH - 1}, got {room_number}"
    assert width % 2 == 0, "Width must be even"
    assert height % 2 == 0, "Height must be even"
    assert 0 <= width < ROOM_SIZE, f"Width ({width}) must between 0 and ROOM_SIZE ({ROOM_SIZE}), inclusive."
    assert 0 <= height < ROOM_SIZE, f"Height ({height}) must be between 0 and ROOM_SIZE ({ROOM_SIZE}), inclusive."
    if width == 0 or height == 0: return [[0 for _ in range(ROOM_SIZE)] for _ in range(ROOM_SIZE)] # if width or height of room is zero, return a void
    # Generates borders for empty void of space
    lr_borders = (ROOM_SIZE - width) // 2
    ud_borders = (ROOM_SIZE - height) // 2
    room = [[2 for _ in range(width)]] + [[2] + [1 for _ in range(width - 2)] + [2] for _ in range(height-2)] + [[2] + [3 for _ in range(width - 2)] + [2]]
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
    if room_number in SCENERY:
        scenery_items_in_room = SCENERY[room_number]
        for scenery_object in scenery_items_in_room:
            assert 0 <= scenery_object[1] + 1 <= len(room), f"Error in scenery placement: Expected -1 ≤ y ≤ {len(room) - 1}, got {scenery_object[1]}"
            assert 0 <= scenery_object[2] + 1 <= len(room[0]), f"Error in scenery placement: Expected -1 ≤ x ≤ {len(room[0]) - 1}, got {scenery_object[2]}"
            for i in range(OBJECTS[scenery_object[0]][0].get_width() // 30):
                if scenery_object[1] == -1:
                    room[scenery_object[1] + 1][scenery_object[2] + 1 + i] = 0
                else: room[scenery_object[1] + 1][scenery_object[2] + 1 + i] = 255
            room[scenery_object[1] + 1][scenery_object[2] + 1] = scenery_object[0]
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
            room[i][sections + 1 + lr_borders] = 2
            room[i][sections - 1 + lr_borders] = 1
            room[i][sections + lr_borders] = 1
            if i == ud_borders - 1:
                room[i + 1][sections - 1 + lr_borders] = 5
                room[i + 1][sections + lr_borders] = 256
    if down:
        sections = width // 2
        for i in range(ud_borders):
            room[-i - 1][sections - 2 + lr_borders] = 2
            room[-i - 1][sections + 1 + lr_borders] = 2
            room[-i - 1][sections - 1 + lr_borders] = 1
            room[-i - 1][sections + lr_borders] = 1
            if i == ud_borders - 1:
                room[-i - 2][sections - 1 + lr_borders] = 5
                room[-i - 1][sections + lr_borders] = 256
    return room

def generate_rooms(rooms):
    room_data = []
    assert len(rooms) == ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH, f"Expected {ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH} rooms, got {len(rooms)}."
    for i in range(len(rooms)):
        if i % ROOM_MAP_WIDTH == 0:
            ROW_DATA = create_room(i, rooms[i][0], rooms[i][1], rooms[i][2], rooms[i][3], rooms[i][4], rooms[i][5])
            if i != (len(rooms) - 1): continue
        temp_room = create_room(i, rooms[i][0], rooms[i][1], rooms[i][2], rooms[i][3], rooms[i][4], rooms[i][5])
        for j in range(ROOM_SIZE):
            ROW_DATA[j] += temp_room[j]
        if i == (len(rooms) - 1):
            if i % ROOM_MAP_WIDTH != ROOM_MAP_WIDTH - 1:
                for _ in range((ROOM_MAP_WIDTH - 1) - (i % ROOM_MAP_WIDTH)):
                    for j in range(ROOM_SIZE):
                        ROW_DATA[j] += [0 for _ in range(ROOM_SIZE)]
        if (i % ROOM_MAP_WIDTH) == (ROOM_MAP_WIDTH - 1) or i == len(rooms) - 1:
            room_data += ROW_DATA
    # Validations:
    for y in range(len(room_data)):
        for x in range(len(room_data[y])):
            if room_data[y][x] == 2 and room_data[y + 1][x] == 0 and room_data[y - 1][x] == 1:
                room_data[y][x] = 3
            if room_data[y][x] == 3 and room_data[y + 1][x] != 0:
                room_data[y][x] = 2
    final = []
    trans_wall_count = 0
    for row in room_data:
        if len(row) > 0: final.append(row)
    assert len(final) == ROOM_MAP_HEIGHT * ROOM_SIZE, f"Expected height to be {ROOM_MAP_HEIGHT * ROOM_SIZE}, got {len(room_data)}" 
    for i in range(len(final)):
        assert len(final[i]) == ROOM_MAP_WIDTH * ROOM_SIZE, f"Expected width of row {i} to be {ROOM_MAP_WIDTH * ROOM_SIZE}, got {len(final[i])}" 
        trans_wall_count += final[i].count(3)
    assert trans_wall_count == 96, f"Expected 96 transparent walls, got {trans_wall_count}."
    return final

def adjust_wall_transparency():
    global walls
    checked_tiles = {
        (player_x - 1) * 2 * (player_y) - (player_x - 1)**2: room_map[player_y][player_x - 1],
        (player_x - 1) * 2 * (player_y + 1) - (player_x - 1)**2: room_map[player_y + 1][player_x - 1],
        (player_x - 1) * 2 * (player_y + 2) - (player_x - 1)**2: room_map[player_y + 2][player_x - 1],
        (player_x) * 2 * (player_y) - (player_x)**2: room_map[player_y][player_x],
        (player_x) * 2 * (player_y + 1) - (player_x)**2: room_map[player_y + 1][player_x],
        (player_x) * 2 * (player_y + 2) - (player_x)**2: room_map[player_y + 2][player_x],
        (player_x + 1) * 2 * (player_y) - (player_x + 1)**2: room_map[player_y][player_x + 1],
        (player_x + 1) * 2 * (player_y + 1) - (player_x + 1)**2: room_map[player_y + 1][player_x + 1],
        (player_x + 1) * 2 * (player_y + 2) - (player_x + 1)**2: room_map[player_y + 2][player_x + 1],
    }
    for k, v in checked_tiles.items():
        if v == 3 and walls[k] < 4:
            walls[k] += 1
    for k in list(walls.keys()):
        if not k in list(checked_tiles.keys()) and walls[k] > 0:
            walls[k] -= 1

def open_doors():
    global doors
    checked_tiles = {
        (player_x - 1) * 2 * (player_y - 2) - (player_x - 1)**2: room_map[player_y - 2][player_x - 1],
        (player_x - 1) * 2 * (player_y - 1) - (player_x - 1)**2: room_map[player_y - 1][player_x - 1],
        (player_x - 1) * 2 * (player_y) - (player_x - 1)**2: room_map[player_y][player_x - 1],
        (player_x - 1) * 2 * (player_y + 1) - (player_x - 1)**2: room_map[player_y + 1][player_x - 1],
        (player_x - 1) * 2 * (player_y + 2) - (player_x - 1)**2: room_map[player_y + 2][player_x - 1],
        (player_x) * 2 * (player_y - 2) - (player_x)**2: room_map[player_y - 2][player_x],
        (player_x) * 2 * (player_y - 1) - (player_x)**2: room_map[player_y - 1][player_x],
        (player_x) * 2 * (player_y) - (player_x)**2: room_map[player_y][player_x],
        (player_x) * 2 * (player_y + 1) - (player_x)**2: room_map[player_y + 1][player_x],
        (player_x) * 2 * (player_y + 2) - (player_x)**2: room_map[player_y + 2][player_x],
    }
    for k, v in checked_tiles.items():
        if v == 5 and doors[k] < 3:
            doors[k] += 1
    for k in list(doors.keys()):
        if not k in checked_tiles and doors[k] > 0:
            doors[k] -= 1

def draw_image(image, y, x):
    screen.blit(image, (top_left_x + ((x + x_shift) * TILE_SIZE), top_left_y + ((y + y_shift) * TILE_SIZE) - image.get_height()) )

def draw_shadow(image, y, x):
    screen.blit(image,(top_left_x + ((x + x_shift) * TILE_SIZE), top_left_y + ((y + y_shift) * TILE_SIZE)))

def draw_player():
    player_image = PLAYER[player_direction][player_frame]
    screen.blit(player_image, (top_left_x + 15 * TILE_SIZE, top_left_y + 15 * TILE_SIZE - player_image.get_height()))
    player_image_shadow = PLAYER_SHADOW[player_direction][player_frame]
    screen.blit(player_image_shadow, (top_left_x + 15 * TILE_SIZE, top_left_y + 15 * TILE_SIZE))

def draw_robot():
    robot_image = ROBOT[robot_direction][robot_moving]
    screen.blit(robot_image, (top_left_x + (robot_x + x_shift + robot_offset_x) * TILE_SIZE, top_left_y + (robot_y + y_shift + robot_offset_y) * TILE_SIZE - robot_image.get_height()))

##################
### PAUSE MENU ###
##################
def pause_loop():
    global old_click
    if not paused: return
    clicked = any(pygame.mouse.get_pressed())
    if clicked and not old_click:
        mouse_x = pygame.mouse.get_pos()[0] // 30
        mouse_y = pygame.mouse.get_pos()[1] // 30
        print(pygame.mouse.get_pressed())
        print(f"Clicked at position {pygame.mouse.get_pos()}, tile {mouse_x, mouse_y}")
    old_click = clicked    

###############
### CHATBOT ###
###############
def on_key_up(key, mod):
    global player_speaking, player_text, paused
    key_id = str(key)[str(key).index(".") + 1:]
    if not paused and key_id == "ESCAPE":
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        paused = True
    elif paused and key_id == "ESCAPE":
        clock.schedule_interval(game_loop, 0.02)
        clock.schedule_interval(robot_interactions, 0.05)
        paused = False
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
        clock.schedule_interval(game_loop, 0.02)
        pass
    else: get_reply(player_text)

def get_reply(text):
    robot_reply = get_answer(text)
    display_robot_reply(robot_reply)

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
            if room_map[y][x] in items_player_may_stand_on and not room_map[y][x] == 5:
                draw_image(OBJECTS[room_map[y][x]][0], y, x)
            if room_map[y][x] != 0 and room_map[y][x] != 4:
                draw_image(OBJECTS[1][0], y, x)
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE):
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            item_here = room_map[y][x]
            # Player cannot walk on 255: it marks spaces used by wide objects.
            if item_here not in items_player_may_stand_on + [255] or item_here == 5:
                image = OBJECTS[item_here][0]
                if item_here == 3:
                    image = OBJECTS[item_here][0][walls[2 * x * y - x**2]]
                if item_here == 5:
                    image = OBJECTS[item_here][0][doors[2 * x * y - x**2]]
                draw_image(image, y, x) 
                if OBJECTS[item_here][1] is not None and room_map[y + 1][x] != 0: # If object has a shadow, and the tile below it is not space
                    shadow_image = OBJECTS[item_here][1]
                    if item_here == 5:
                        shadow_image = OBJECTS[item_here][1][doors[2 * x * y - x**2]]
                    # if shadow might need horizontal tiling
                    if shadow_image in [images.half_shadow, images.full_shadow]:
                        shadow_width = int(image.get_width() / TILE_SIZE)
                        # Use shadow across width of object.
                        for z in range(0, shadow_width):
                            draw_shadow(shadow_image, y, x+z)
                    else:
                        draw_shadow(shadow_image, y, x)
        if (robot_y == y):
            draw_robot()
        if (player_y == y):
            draw_player()
    if robot_speaking:
        screen.blit(images.textbox, (30, 650))
        screen.draw.text(f"{ROBOT_NAME}", (60, 670), color="black", fontname="biorhyme", width=780, lineheight=1)
        screen.draw.text(robot_text, (60, 700), color="black", fontname="biorhyme", width=780, lineheight=1, fontsize=15)
        screen.blit(images.drone_text, (30, 600))
    if player_speaking:
        screen.blit(images.textbox, (30, 650))
        screen.draw.text("You", (60, 670), color="black", fontname="biorhyme", width=780, lineheight=1)
        screen.draw.text(player_text, (60, 700), color="black", fontname="biorhyme", width=780, lineheight=1, fontsize = 15)
        screen.blit(images.player_text, (30, 600))
    if paused:
        s = pygame.Surface((WIDTH, HEIGHT)) # Creates a surface the height and width of the window
        s.set_alpha(128) # To create a semi-opaque overlay
        s.fill((0, 0, 0)) # Makes the overlay black (rgba(0, 0, 0, 128))
        screen.blit(s, (0,0)) # Blits the surface onto the screen

def display_message(text):
    global robot_speaking, robot_text
    robot_speaking = True
    robot_text = text
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
    global robot_x, robot_y
    global robot_moving
    global robot_offset_x, robot_offset_y
    if mute:
        music.pause()
    if not mute:
        music.unpause()
    current_room = player_x // ROOM_SIZE + (player_y // ROOM_SIZE) * 3
    if player_frame > 0:
        player_frame += 1
        time.sleep(0.02)
        if player_frame == 5:
            player_frame = 0
            player_offset_x = 0
            player_offset_y = 0
            robot_moving = 0
            robot_offset_x = 0
            robot_offset_y = 0

# save player's current position
    old_player_x = player_x
    old_player_y = player_y

# move if key is pressed
    if player_frame == 0:
        if keyboard.left or keyboard.a: 
            from_player_x = player_x
            from_player_y = player_y
            player_x -= 1
            player_direction = "left"
            player_frame = 1
            update_robot_pos(old_player_x, old_player_y)
        elif keyboard.right or keyboard.d: #elif stops player making diagonal movements
            from_player_x = player_x
            from_player_y = player_y
            player_x += 1
            player_direction = "right"
            player_frame = 1
            update_robot_pos(old_player_x, old_player_y)
        elif keyboard.up or keyboard.w:
            from_player_x = player_x
            from_player_y = player_y
            player_y -= 1
            player_direction = "up"
            player_frame = 1
            update_robot_pos(old_player_x, old_player_y)
        elif keyboard.down or keyboard.s:
            from_player_x = player_x
            from_player_y = player_y
            player_y += 1
            player_direction = "down"
            player_frame = 1
            update_robot_pos(old_player_x, old_player_y)
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
    if robot_direction == "right" and robot_moving > 0:
        robot_offset_x = -1 + (0.25 * player_frame)
    if robot_direction == "left" and robot_moving > 0:
        robot_offset_x = 1 - (0.25 * player_frame)
    if robot_direction == "up" and robot_moving > 0:
        robot_offset_y = 1 - (0.25 * player_frame)
    if robot_direction == "down" and robot_moving > 0:
        robot_offset_y = -1 + (0.25 * player_frame)
    x_shift, y_shift = - (player_x + player_offset_x - 15), -(player_y + player_offset_y - 15)
    with open('savefile.dat', 'wb') as f:
        pickle.dump([STARTED, player_x, player_y, x_shift, y_shift, robot_x, robot_y, player_direction, robot_direction], f, protocol=2)

def robot_interactions():
    global robot_speaking
    if keyboard.t:
        clock.unschedule(robot_interactions)
        display_help_message()
        clock.schedule_unique(end_message, 5.0)

def update_robot_pos(old_x, old_y):
    global robot_x, robot_y
    global robot_direction, robot_moving
    change_x = old_x - robot_x
    change_y = old_y - robot_y
    robot_moving = 1
    if change_y == 1:
        robot_direction = "down"
    elif change_y == -1:
        robot_direction = "up"
    elif change_x == -1:
        robot_direction = "left"
    elif change_x == 1:
        robot_direction = "right"
    robot_x, robot_y = old_x, old_y

def display_help_message():
    if player_direction == "right":
        facing = room_map[player_y][player_x + 1]
        checked = player_y, player_x + 1
    elif player_direction == "left":
        facing = room_map[player_y][player_x - 1]
        checked = player_y, player_x - 1
    elif player_direction == "up":
        facing = room_map[player_y - 1][player_x]
        checked = player_y - 1, player_x
    else:
        facing = room_map[player_y + 1][player_x]
        checked = player_y + 1, player_x
    checking_x_shift = 0
    while facing == 255 or facing == 0 or facing == 256:
        facing = room_map[checked[0]][checked[1] - checking_x_shift]
        checking_x_shift += 1
    if facing != 1:
        display_message(f"That is {OBJECTS[facing][2]} {OBJECTS[facing][3]}")
    else:
        display_message(f"This is {ROOMS[current_room][6]} {ROOMS[current_room][7]}")

#############
### START ###
#############
try:
    with open('savefile.dat', 'rb') as f:
        STARTED, player_x, player_y, x_shift, y_shift, robot_x, robot_y, player_direction, robot_direction = pickle.load(f)
except:
    STARTED = False

if not mute:
    music.play(random.choice(MUSIC_CHOICES))
if not STARTED:
    clock.unschedule(robot_interactions)
    display_message(f"Hi! I'm {ROBOT_NAME}, your AI companion (and last functioning robot) aboard the {SHIP_NAME}. If you need any help, just face what you want to find out more about and press 'T'. If you want to chat, just press 'C'. Now, use WASD or the arrow keys to move!")
    clock.schedule_unique(end_message, 20.0)
    STARTED = True
room_map = generate_rooms(ROOMS)
for y in range(len(room_map)):
    for x in range(len(room_map[y])):
        if room_map[y][x] == 5:
            doors[2 * x * y - x**2] = 0 
        if room_map[y][x] == 3:
            walls[2 * x * y - x**2] = 0
        # the 2 * x * y - x**2 allows me to keep track of where the object is, for a unique key. (x + y would not work as that would cause (2, 3) to function trigger for (3, 2))
clock.schedule_interval(game_loop, 0.02)
clock.schedule_interval(adjust_wall_transparency, 0.05)
clock.schedule_interval(open_doors, 0.05)
clock.schedule_interval(robot_interactions, 0.05)
clock.schedule_interval(pause_loop, 0.05)
pgzrun.go()
