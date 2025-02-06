###############
### IMPORTS ###
###############
try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import START, MessagesState, StateGraph
    from langchain_core.messages import HumanMessage, SystemMessage, trim_messages, RemoveMessage
    from langchain_openai import ChatOpenAI
except: raise ModuleNotFoundError('Could not find required module {langchain}. Try re-running the install command.')
try: import pgzrun, pygame
except: raise ModuleNotFoundError('Could not find required module {pygame}. Try re-running the install command.')
#try: 
from matplotlib import pyplot as plt
#except: raise ModuleNotFoundError('Could not find required module {matplotlib}. Try re-running the install command.')
try: import numpy as np
except: raise ModuleNotFoundError('Could not find required module {numpy}. Try re-running the install command.')
try:
    import time, random, math, re, warnings, pickle, os
    from datetime import date
except: raise ModuleNotFoundError('Could not find built-in modules. Try re-installing python 3.9.12')
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
except: warnings.warn('Could not find built-in nltk sentiment analysis tools. App will run, but mood charts will not be generated.')
try: 
    import password
    chatbot_on = True
except: 
    warnings.warn('Configuration file for openAI API keys not found. Chatbot will be disabled')
    chatbot_on = False

#################
### CONSTANTS ###
#################
WIDTH = 900 # Window size
HEIGHT = 800
TILE_SIZE = 30 # Size of each tile
ROOM_SIZE = 20
ROOM_MAP_WIDTH = 3 # Number of rooms in the map (left to right)
ROOM_MAP_HEIGHT = 3 # Number of rooms in the map (top to bottom)
SHIFTED = list(")!@#$%^&*(") # Used for keyboard typing
ROBOT_NAME = "Vimal"
SHIP_NAME = "Jolene"
MUSIC_CHOICES = ['kisstherain', 'merrygoroundoflife']
LANGCHAIN_TRACING_V2=True
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=password.langchainapi
LANGCHAIN_PROJECT="coursework"

#################
### VARIABLES ###
#################
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
mood_hist = {}
displaying_chart = False
modal = False
modal_text = ""
delete_data = False
future_robot_text = ""
text_hist = []

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
player_x, player_y = 30, 30 # Player position in relation to environment
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
    3: [[images.pillar, images.pillar_95, images.pillar_80, images.pillar_60, images.pillar_50], images.full_shadow, "a wall.", "Sterile, and devoid of contamination."],
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
    34: [images.duckwall, images.full_shadow, "a whiteboard.", "It used to be used for brainstorming and planning."],
    35: [images.window, images.full_shadow, "a window.", "It allows you to look out at space."],
    36: [images.window_short, images.full_shadow, "a window", "It allows you to look out at space."],
    37: [images.robot, images.robot_shadow, "a cleaning robot.", "It's turned off right now to conserve power."],
    40: [images.drone, None, "a delivery drone", "They used to whizz through the corridors like nobody's business."],
    41: [images.computer, images.computer_shadow, "a computer workstation", "Used for managing space station systems."],
    42: [images.map, images.full_shadow, "a map charting the path of the ship.", "It's very in-depth."],
    43: [images.bottomfence, None, "a fence.", "It stops you from walking onto the crops"],
    44: [images.topfence, None, "a fence.", "It stops you from walking onto the crops"],
    45: [images.leftfence, None, "a fence.", "It stops you from walking onto the crops"],
    46: [images.rightfence, None, "a fence.", "It stops you from walking onto the crops"],
    255: [images.floor, None, "the floor.", "It's shiny and clean."],
    256: [images.floor, None, "the floor.", "It's shiny and clean."]
}

# Special tiles:
# 0: Transparent tile, used for space, and the space used up by wide objects which are on the wall furtherst from the screen, adjacent to space.
# 255: The space used up by wide objects, does not allow player to walk through.
# 256: The space used up by wide objects, however allows player to walk through.

#############
### ROOMS ###
#############
ROOMS = [
    # [width, height, left exit, right exit, top exit, bottom exit, title, description.]
    [14, 10, False, False, False, True, "BETA", "BETABETA"],
    [0, 0, False, False, False, False, "space.", "As a developer, please tell me how you got out so I can patch this."],
    [14, 10, False, False, False, True, "mission control.", "Back when comms worked, we could talk to Earth from here..."],
    [4, 4, False, True, True, True, "an access corridor.", "How did you get here?"],
    [18, 18, True, True, False, False, "the one and only lounging area in the entire spaceship.", "It's pretty nice!"],
    [4, 4, True, False, True, True, "an access corridor.", "How did you get here?"],
    [14, 10, False, False, True, False, "the dorm.", "All the astronauts used to stay here at night."],
    [0, 0, False, False, False, False, "space.", "As a developer, please tell me how you got out so I can patch this."],
    [14, 10, False, False, True, False, "the garden.", "The plants grow here. Tomatoes grow surprisingly well!"]
]

###############
### SCENERY ###
###############

# Screnery:
# [[item, y, x]]
SCENERY = {
    0: [[35, -1, 0]],
    2: [[35, -1, 0]],
    4: [[36, -1, 0], [34, -1, 4], [36, -1, 12]],
    6: [[7, 0, 0], [14, 0, 2], [7, 0, 3], [8, 0, 7], [14, 0, 9], [8, 0, 10], [7, 2, 0], [14, 2, 2], [7, 2, 3], [8, 2, 7], [14, 2, 9], [8, 2, 10], [7, 5, 0], [14, 5, 2], [7, 5, 3], [8, 5, 7], [14, 5, 9], [8, 5, 10], [7, 7, 0], [14, 7, 2], [7, 7, 3], [8, 7, 7], [14, 7, 9], [8, 7, 10], [35, 8, 0]],
    8: [[35, 8, 0], [4, 1, 1], [4, 1, 2], [4, 1, 3], [4, 1, 4], [4, 1, 7], [4, 1, 8], [4, 1, 9], [4, 1, 10], [4, 2, 1], [4, 2, 2], [4, 2, 3], [4, 2, 4], [4, 2, 7], [4, 2, 8], [4, 2, 9], [4, 2, 10], [4, 4, 1], [4, 4, 2], [4, 4, 3], [4, 4, 4], [4, 4, 7], [4, 4, 8], [4, 4, 9], [4, 4, 10], [4, 5, 1], [4, 5, 2], [4, 5, 3], [4, 5, 4], [4, 5, 7], [4, 5, 8], [4, 5, 9], [4, 5, 10], [43, 6, 1], [43, 6, 2], [43, 6, 3], [43, 6, 4], [43, 6, 7], [43, 6, 8], [43, 6, 9], [43, 6, 10], [44, 0, 1], [44, 0, 2], [44, 0, 3], [44, 0, 4], [44, 0, 7], [44, 0, 7], [44, 0, 8], [44, 0, 9], [44, 0, 10], [43, 3, 1], [43, 3, 2], [43, 3, 3], [43, 3, 4], [43, 3, 7], [43, 3, 8], [43, 3, 9], [43, 3, 10], [43, 3, 1], [43, 3, 2], [43, 3, 3], [43, 3, 4], [43, 3, 7], [43, 3, 8], [43, 3, 9], [43, 3, 10], [45, 0, 0], [45, 1, 0], [45, 2, 0], [46, 0, 5], [46, 1, 5], [46, 2, 5], [45, 0, 6], [45, 1, 6], [45, 2, 6], [46, 0, 11], [46, 1, 11], [46, 2, 11], [45, 3, 0], [45, 4, 0], [45, 5, 0], [46, 3, 5], [46, 4, 5], [46, 5, 5], [45, 3, 6], [45, 4, 6], [45, 5, 6], [46, 3, 11], [46, 4, 11], [46, 5, 11]]
}

checksum = 0
check_counter = 0
for key, room_scenery_list in SCENERY.items():
    for scenery_item_list in room_scenery_list:
        checksum += (scenery_item_list[0] * key
                     + scenery_item_list[1] * (key + 1) 
                     + scenery_item_list[2] * (key + 2))
        check_counter += 1
"""
assert check_counter == 93, f"Expected 93 scenery items, got {check_counter}."
assert checksum == 21422, f"Expected checksum of 21422, got {checksum}."
"""

ITEMS_PLAYER_MAY_STAND_ON = [1, 5, 34, 43, 44, 45, 46, 256]
ITEMS_PLAYER_MAY_INTERACT_WITH = [15, 33, 41]

################################
### LANGCHAIN AND OPENAI API ###
################################

### Initialize
model = ChatOpenAI(
    model = 'gpt-4o-mini', 
    api_key = password.api_key,
    temperature = 0.5
)

### Prompt template

def call_model(state: MessagesState):
    global text_hist
    system_prompt = (f"Your name is {ROBOT_NAME}, and you are a conselour, who gives emotional support to the user no matter what, and uses quick and concise replies to help your clients. The provided history includes a summary of the earler conversation.")
    system_message = SystemMessage(content=system_prompt)
    message_history = state["messages"][:-1]  # exclude the most recent user input
    text_hist = message_history[:]
    # Summarize the messages if the chat history reaches a certain size
    if len(message_history) >= 4:
        last_human_message = state["messages"][-1]
        # Invoke the model to generate conversation summary
        summary_prompt = (
            "Distill the above chat messages into a single summary message. "
            "Include as many specific details as you can."
        )
        summary_message = model.invoke(
            message_history + [HumanMessage(content=summary_prompt)]
        )

        # Delete messages that we no longer want to show up
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"]]
        # Re-add user message
        human_message = HumanMessage(content=last_human_message.content)
        # Call the model with summary & response
        response = model.invoke([system_message, summary_message, human_message])
        message_updates = [summary_message, human_message, response] + delete_messages
    else:
        message_updates = model.invoke([system_message] + state["messages"])

    return {"messages": message_updates}

workflow = StateGraph(state_schema=MessagesState)

# define the (single) node in the graph
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}


def get_answer(query):
    output = app.invoke(
            {"messages": text_hist + [HumanMessage(content=query)]}, config)
    print(text_hist)
    return output['messages'][-1].content

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
    assert trans_wall_count == 50, f"Expected 50 transparent walls, got {trans_wall_count}."
    return final

def adjust_wall_transparency():
    global walls
    # Basically a key
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
    global old_click, mute, paused, modal, modal_text, delete_data
    clicked = any(pygame.mouse.get_pressed())
    if clicked and not old_click:
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        #print(pygame.mouse.get_pressed())
        #print(f"Clicked at position {pygame.mouse.get_pos()}")
        if not modal and paused:
            if 270 <= mouse_x <= 630 and 250 <= mouse_y <= 340:
                clock.schedule_interval(game_loop, 0.02)
                clock.schedule_interval(robot_interactions, 0.05)
                paused = False
            if 270 <= mouse_x <= 630 and 390 <= mouse_y <= 480:
                modal = True
                modal_text = "Are you sure you want to quit?"
            if 270 <= mouse_x <= 360 and 530 <= mouse_y <= 620: 
                mute = not mute
                if mute: music.pause()
                else: music.unpause()
            if 540 <= mouse_x <= 630 and 530 <= mouse_y <= 620: 
                modal = True
                modal_text = "Are you sure you want to delete all your save files? The game will automatically stop after you confirm."
                delete_data = True
        elif modal:
            if 285 <= mouse_x <= 465 and 480 <= mouse_y <= 570:  
                if delete_data:
                    try:
                        os.remove("savefile.dat")
                        os.remove("images/moodchart.png")
                    except: pass
                exit()
            if 435 <= mouse_x <= 615 and 480 <= mouse_y <= 570: 
                modal = False
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
    if not player_speaking and key_id == "C" and chatbot_on == True: # If the chatbot hasn't started, start the chatbot, pausing the gameloop and other interactions
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        start_chatbot()
    if player_speaking: # Typing
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
    global player_speaking, mood_hist
    player_speaking = False
    if player_text == ":q": 
        clock.schedule_interval(robot_interactions, 0.05)
        clock.schedule_interval(game_loop, 0.02)
        pass
    elif player_text == "/p_debug":
        mood_to_disp = [sum(mood_hist[i])/(len(mood_hist[i])) for i in mood_hist.keys()]
        plt.plot(list(mood_hist.keys()), mood_to_disp, marker='x')
        plt.xlabel('Date')
        plt.ylabel('Mood')
        plt.title('Mood chart')
        plt.grid(True)
        plt.ylim(-1.1, 1.1)
        plt.plot(list(mood_hist.keys()), [0 for _ in range(len(mood_hist))], color="lightgray", linestyle="--", label="Baseline")
        plt.savefig("images/moodchart.png")
    else: 
        print(get_sentiment(player_text))
        today_date = np.datetime64(date.today())
        if today_date not in mood_hist: mood_hist[today_date] = [get_sentiment(player_text)]
        else: mood_hist[today_date].append(get_sentiment(player_text))
        print(mood_hist)
        get_reply(player_text)
def get_reply(text):
    robot_reply = get_answer(text)
    print(robot_reply)
    display_robot_message(robot_reply)

def display_robot_message_cont():
    global future_robot_text, robot_text
    split_text = [future_robot_text[i:i+200] for i in range(0, len(future_robot_text), 200)]
    future_robot_text = ''.join(split_text[1:])
    if len(split_text) > 0:
        robot_text = split_text[0]
        clock.schedule(display_robot_message_cont, max(6.0, round(len(robot_text) * 0.8, 1)))

def display_robot_message(text):
    global robot_speaking, robot_text, future_robot_text
    robot_speaking = True
    robot_text = text
    if len(robot_text) > 205:
        not_yet_done = robot_text[201:]
        robot_text = robot_text[:201]
        future_robot_text = not_yet_done
        clock.schedule(display_robot_message_cont, max(6.0, round(len(robot_text) * 0.8, 1)))
    clock.schedule_unique(end_robot_message, max(6.0, round(len(text) * 0.8, 1)))

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

####################
### MOOD CHARTS ###
###################
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered = [token for token in tokens if token not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered]
    processed_text = ' '.join(lemmatized_tokens)
    #print(tokens, filtered, lemmatized_tokens, processed_text)
    return processed_text

def get_sentiment(text):
    processed = preprocess_text(text)
    scores = SentimentIntensityAnalyzer().polarity_scores(text)
    return scores['compound']

def player_interact():
    global displaying_chart
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
    if facing in ITEMS_PLAYER_MAY_INTERACT_WITH:
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        mood_to_disp = [sum(mood_hist[i])/(len(mood_hist[i]) - mood_hist[i].count(0)) for i in mood_hist.keys()]
        plt.plot(list(mood_hist.keys()), mood_to_disp, marker='x', color="blue", label="Mood")
        plt.xlabel('Date')
        plt.ylabel('Mood')
        plt.title('Mood chart')
        plt.grid(True)
        plt.ylim(-1.1, 1.1)
        plt.plot(list(mood_hist.keys()), [0 for _ in range(len(mood_hist))], color="lightgray", linestyle="--", label="Baseline")
        plt.savefig("images/moodchart.png")
        displaying_chart = True
    else:
        pass
########################
#### MAIN GAME LOOPS ###
########################
def draw():
    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]
    screen.blit(images.backdrop, (top_left_x + ((-15 + x_shift) * TILE_SIZE), top_left_y + ((-15 + y_shift) * TILE_SIZE)))
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE): 
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            if room_map[y][x] in ITEMS_PLAYER_MAY_STAND_ON and not room_map[y][x] == 5:
                draw_image(OBJECTS[room_map[y][x]][0], y, x)
            if room_map[y][x] not in [0, 4, 34, 35, 36]:
                draw_image(OBJECTS[1][0], y, x)
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE):
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            item_here = room_map[y][x]
            # Player cannot walk on 255: it marks spaces used by wide objects.
            if item_here not in ITEMS_PLAYER_MAY_STAND_ON + [255] or item_here in [5, 43, 45, 46]:
                image = OBJECTS[item_here][0]
                if item_here == 3:
                    image = OBJECTS[item_here][0][walls[2 * x * y - x**2]]
                if item_here == 5:
                    image = OBJECTS[item_here][0][doors[2 * x * y - x**2]]
                draw_image(image, y, x) 
                if OBJECTS[item_here][1] is not None: # If object has a shadow
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
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE):
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            if (room_map[y][x] == 43 and y == 49) or room_map[y][x] == 44:
                image = OBJECTS[44][0]
                draw_image(image, y, x) 
                
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
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        screen.blit(images.pausesign, (230, 50))
        if 270 <= mouse_x <= 630 and 250 <= mouse_y <= 340 and not modal: screen.blit(images.maincontinuehover, (270, 250))
        else: screen.blit(images.maincontinue, (270, 250))
        if 270 <= mouse_x <= 630 and 390 <= mouse_y <= 480 and not modal: screen.blit(images.mainquithover, (270, 390))
        else: screen.blit(images.mainquit, (270, 390))
        if not mute:
            if 270 <= mouse_x <= 360 and 530 <= mouse_y <= 620 and not modal: screen.blit(images.mutehover, (270, 530))
            else: screen.blit(images.mute, (270, 530))
        else:
            if 270 <= mouse_x <= 360 and 530 <= mouse_y <= 620 and not modal: screen.blit(images.unmutehover, (270, 530))
            else: screen.blit(images.unmute, (270, 530))
        if 540 <= mouse_x <= 630 and 530 <= mouse_y <= 620 and not modal: screen.blit(images.deldatahover, (540, 530))
        else: screen.blit(images.deldata, (540, 530))
    if modal:
        screen.blit(images.modal, (270, 315))
        screen.draw.text("Warning", (285, 325), color="black", fontname="biorhyme", width=330, lineheight=1, fontsize = 30)
        screen.draw.text(modal_text, (285, 370), color="black", fontname="biorhyme", width=330, lineheight=1, fontsize = 20)
        if 285 <= mouse_x <= 465 and 520 <= mouse_y <= 570: screen.blit(images.modalcontinuehover, (285, 520))
        else: screen.blit(images.modalcontinue, (285, 520)) 
        if 465 <= mouse_x <= 615 and 520 <= mouse_y <= 570: screen.blit(images.modalcancelhover, (465, 520))
        else: screen.blit(images.modalcancel, (465, 520)) 
    if displaying_chart:
        screen.blit(images.moodchart, (110, 190))

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
    if keyboard.e:
        player_interact()
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
    if room_map[player_y][player_x] not in ITEMS_PLAYER_MAY_STAND_ON:
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
        pickle.dump([started, player_x, player_y, x_shift, y_shift, robot_x, robot_y, player_direction, robot_direction, mood_hist, text_hist], f, protocol=2)

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
        started, player_x, player_y, x_shift, y_shift, robot_x, robot_y, player_direction, robot_direction, mood_hist, text_hist = pickle.load(f)
except:
    started = False
if not mute:
    music.play(random.choice(MUSIC_CHOICES))
if not started:
    clock.unschedule(robot_interactions)
    display_message(f"Hi! I'm {ROBOT_NAME}, your AI companion (and last functioning robot) aboard the {SHIP_NAME}. If you need any help, just face what you want to find out more about and press 'T'. If you want to chat, just press 'C'. Now, use WASD or the arrow keys to move!")
    clock.schedule_unique(end_message, 20.0)
    started = True
room_map = generate_rooms(ROOMS)
for y in range(len(room_map)):
    for x in range(len(room_map[y])):
        if room_map[y][x] == 5:
            doors[2 * x * y - x**2] = 0 
        if room_map[y][x] == 3:
            walls[2 * x * y - x**2] = 0
        # the 2 * x * y - x**2 allows me to keep track of where the object is, for a unique key. (x + y would not work as that would cause (2, 3) to function trigger for (3, 2))
clock.schedule_interval(game_loop, 0.02)
clock.schedule_interval(robot_interactions, 0.05)
clock.schedule_interval(adjust_wall_transparency, 0.05)
clock.schedule_interval(open_doors, 0.05)
clock.schedule_interval(pause_loop, 0.05)
pgzrun.go()