############################
### IMPORTS -- YAU SHING ###
############################
try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import START, MessagesState, StateGraph
    from langchain_core.messages import HumanMessage, SystemMessage, trim_messages, RemoveMessage
    from langchain_openai import ChatOpenAI
except:
    raise ModuleNotFoundError("Could not find required module {langchain}. Try re-running the install command.")
try:
    import pgzrun, pygame
except:
    raise ModuleNotFoundError("Could not find required module {pygame}. Try re-running the install command.")
try:
    from matplotlib import pyplot as plt
except:
    raise ModuleNotFoundError("Could not find required module {matplotlib}. Try re-running the install command.")
try:
    import numpy as np
except:
    raise ModuleNotFoundError("Could not find required module {numpy}. Try re-running the install command.")
try:
    import time, random, math, re, warnings, pickle, os
    from datetime import date
except:
    raise ModuleNotFoundError("Could not find built-in modules. Try re-installing python 3.9.12")
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
except:
    warnings.warn("Could not find built-in nltk sentiment analysis tools. App will run, but mood charts will not be generated.")
try:
    import password
    chatbot_on = True
except:
    warnings.warn("Configuration file for openAI API keys not found. Chatbot will be disabled")
    chatbot_on = False

##############################
### CONSTANTS -- YAU SHING ###
##############################
WIDTH = 900  # Window size
HEIGHT = 800
TILE_SIZE = 30  # Size of each tile
ROOM_SIZE = 20 # Size of the room 
ROOM_MAP_WIDTH = 3  # Number of rooms in the map (left to right)
ROOM_MAP_HEIGHT = 3  # Number of rooms in the map (top to bottom)
SHIFTED = list(")!@#$%^&*(")  # Used for keyboard typing
ROBOT_NAME = "Amy" # Name of the robot
MUSIC_CHOICES = ["kisstherain", "merrygoroundoflife"] # Music choices
LANGCHAIN_TRACING_V2 = True # Langchain API key
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com" # Langchain API key
LANGCHAIN_API_KEY = password.langchainapi # Langchain API key
LANGCHAIN_PROJECT = "coursework"
KEY_IDS = { # Made by Vimal, keymapping for keyboard which returns integers and not keys.A
    8: "keys.BACKSPACE",
    9: "keys.TAB",
    13: "keys.RETURN",
    27: "keys.ESCAPE",
    32: "keys.SPACE",
    39: "keys.QUOTE",
    44: "keys.COMMA",
    45: "keys.MINUS",
    46: "keys.PERIOD",
    47: "keys.SLASH",
    48: "keys.K_0",
    49: "keys.K_1",
    50: "keys.K_2",
    51: "keys.K_3",
    52: "keys.K_4",
    53: "keys.K_5",
    54: "keys.K_6",
    55: "keys.K_7",
    56: "keys.K_8",
    57: "keys.K_9",
    59: "keys.SEMICOLON",
    61: "keys.EQUALS",
    91: "keys.LEFTBRACKET",
    92: "keys.BACKSLASH",
    93: "keys.RIGHTBRACKET",
    96: "keys.BACKQUOTE",
    97: "keys.A",
    98: "keys.B",
    99: "keys.C",
    100: "keys.D",
    101: "keys.E",
    102: "keys.F",
    103: "keys.G",
    104: "keys.H",
    105: "keys.I",
    106: "keys.J",
    107: "keys.K",
    108: "keys.L",
    109: "keys.M",
    110: "keys.N",
    111: "keys.O",
    112: "keys.P",
    113: "keys.Q",
    114: "keys.R",
    115: "keys.S",
    116: "keys.T",
    117: "keys.U",
    118: "keys.V",
    119: "keys.W",
    120: "keys.X",
    121: "keys.Y",
    122: "keys.Z",
    1073741881: "keys.CAPSLOCK",
    1073741903: "keys.RIGHT",
    1073741904: "keys.LEFT",
    1073741905: "keys.DOWN",
    1073741906: "keys.UP",
    1073742048: "keys.LCTRL",
    1073742049: "keys.LSHIFT",
    1073742050: "keys.LALT",
    1073742051: "keys.LGUI",
    1073742053: "keys.RSHIFT",
    1073742054: "keys.RALT",
    1073742055: "keys.RGUI",
}

#################
### VARIABLES ###
#################
top_left_x = 0
top_left_y = 60  # Shifts room down so that the top-most pillar is visible
x_shift, y_shift = 0, 0 # Shifts rooms in relation to player (player stays in the centre of the screen)
robot_speaking = False  # Makes game decide whether to display speech bubble for the robot
robot_text = ""  # Text to be displayed when robot_speaking is Trye
player_speaking = False  # Same thing but for the player
player_text = "" # Text to be displayed when when the player is typing
doors = {} # Dictonary that will hold all the doors in a key:frame pair
walls = {} # Dictonary that will hold all the walls that alternate to be transclusent in a key:frame pair
paused = False # Whether the game is paused
exercise = False # Whether the exercise menu should be shown
mute = False # Whether the game is muted
old_click = False # Whether the user had clicked in the previous game looop
mood_hist = {} # History of the user's mood for plotting
displaying_chart = False # Whether to display the mood chart
modal = False # Whether the game should display the modal for pop-ups
modal_text = "" # Text inside pop-ups
delete_data = False # Whether the game should delete all player data
future_robot_text = "" # Text for the robot to continue speaking if the text is too long
text_hist = [] # History of previous messages for the robot to remember the user

# Exercises : Jolene
old_click2 = False 
exercise_menu = False
breathing_menu = False
breathing_menu_1 = False
cur_pg = 0
bodyscan_menu = False
pause_music = True
first_play = True

########################
### PLAYER VARIABLES ###
########################

# Player movement animations
PLAYER = {
    "left": [images.spacesuit_left,images.spacesuit_left_1,images.spacesuit_left_2,images.spacesuit_left_3,images.spacesuit_left_4,],
    "right": [images.spacesuit_right,images.spacesuit_right_1,images.spacesuit_right_2,images.spacesuit_right_3,images.spacesuit_right_4,],
    "up": [images.spacesuit_back,images.spacesuit_back_1,images.spacesuit_back_2,images.spacesuit_back_3,images.spacesuit_back_4,],
    "down": [images.spacesuit_front,images.spacesuit_front_1,images.spacesuit_front_2,images.spacesuit_front_3,images.spacesuit_front_4,]
}

player_direction = "up"  # The direction the player is facing
player_frame = 0  # Frame of animation
player_image = PLAYER[player_direction][player_frame]  # Image of the player
player_offset_x, player_offset_y = (0, 0)  # Player offset to fit animations and movement along the x and y axis (0.25 offset, frame 1, 0.5 offset, frame 2... 1 offset = x += 1, frame 0 again)
player_x, player_y = 30, 30  # Player position in relation to environment
current_room = 0  # The room the player is in

PLAYER_SHADOW = {
    "left": [images.spacesuit_left_shadow,images.spacesuit_left_1_shadow,images.spacesuit_left_2_shadow,images.spacesuit_left_3_shadow,images.spacesuit_left_4_shadow,],
    "right": [images.spacesuit_right_shadow,images.spacesuit_right_1_shadow,images.spacesuit_right_2_shadow,images.spacesuit_right_3_shadow,images.spacesuit_right_4_shadow,],
    "up": [images.spacesuit_back_shadow,images.spacesuit_back_1_shadow,images.spacesuit_back_2_shadow,images.spacesuit_back_3_shadow,images.spacesuit_back_4_shadow,],
    "down": [images.spacesuit_front_shadow,images.spacesuit_front_1_shadow,images.spacesuit_front_2_shadow,images.spacesuit_front_3_shadow,images.spacesuit_front_4_shadow,]
}

player_image_shadow = PLAYER_SHADOW[player_direction][0]

#######################
### ROBOT VARIABLES ###
#######################
ROBOT = {
    "left": [images.drone, images.drone],
    "right": [images.drone, images.drone],
    "up": [images.drone, images.drone],
    "down": [images.drone, images.drone],
}
robot_direction = player_direction
robot_moving = 0
robot_image = ROBOT[robot_direction][robot_moving]
robot_offset_x, robot_offset_y = 0, 0
robot_x, robot_y = player_x, player_y + 1

###############
### OBJECTS ###
###############
# [image, shadow, description] OR
# [[image frame 1, image frame 2, ...], [shaodw frame 1, shadow frame 2, ...], description]
OBJECTS = {
    0: [images.void, None, "the empty void of space."],
    1: [images.floor, None, "the floor.", "It's shiny and clean."],
    2: [images.pillar, images.full_shadow, "a wall.", "Sterile, and devoid of contamination."],
    3: [[images.pillar,images.pillar_95,images.pillar_80,images.pillar_60,images.pillar_50,],images.full_shadow,"a wall.","Sterile, and devoid of contamination.",],
    4: [images.soil,None,"soil, used for the farm.","Surprisingly, it hasn't spilled onto the ground yet.",],
    5: [[images.door, images.door1, images.door2, images.door3, images.door4],[images.door_shadow,images.door1_shadow,images.door3_shadow,images.door4_shadow,],"a door.","It opens and closes.",],
    6: [images.pillar_low,images.half_shadow,"a shoft wall.","Sterile and devoid of contamination.",],
    7: [images.bed_left, images.half_shadow, "a bed.", "It's tidy and comfortable."],
    8: [images.bed_right, images.half_shadow, "a bed.", "It's tidy and comfortable."],
    9: [images.table, images.half_shadow, "a table.", "It's made of a strong plastic."],
    10: [images.chair_left, None, "a chair.", "Nice and comfy with a soft cushion."],
    11: [images.chair_right, None, "a chair.", "Nice and comfy with a soft cushion."],
    12: [images.bookcase_tall,images.full_shadow,"a bookshelf.","It's stacked with reference books.",],
    13: [images.bookcase_small,images.half_shadow,"a bookshelf.","It's stacked with reference books.",],
    14: [images.cabinet,images.half_shadow,"a small locker.","It's used for storing personal items",],
    15: [images.desk_computer,images.half_shadow,"a computer.","It has logs from over for over 2000 years.",],
    16: [images.plant,images.plant_shadow,"a spaceberry plant.","It's locally sourced, sustainable and healthy!",],
    17: [images.electrical1,images.half_shadow,"a part of the electrical system of the space shuttle.","",],
    18: [images.electrical2,images.half_shadow,"a part of the electrical system of the space shuttle.","",],
    19: [images.cactus, images.cactus_shadow, "a cactus.", "It's pretty sharp."],
    20: [images.shrub,images.shrub_shadow,"a space lettuce.","It's a bit limp, but amazing it's growing here!",],
    21: [images.pipes1,images.pipes1_shadow,"a part of the water purification system of the space shuttle.","",],
    22: [images.pipes2,images.pipes2_shadow,"a part of the life support systems.","Don't touch thease.",],
    23: [images.pipes3,images.pipes3_shadow,"a part of the life support systems.","Don't touch thease.",],
    25: [images.contraption,images.contraption_shadow,"a scientific experiment of one of the old astronauts.","What's left, of it, anyways.",],
    26: [images.robot_arm,images.robot_arm_shadow,"a robot arm.","It was used for heavy lifting.",],
    27: [images.toilet, images.half_shadow, "a toilet.", "It's sparkling clean."],
    28: [images.sink,None,"a sink, with clean running water recycled through the system.","It's clean!",],
    29: [images.globe,images.globe_shadow,"a giant globe of the planet","It gently glows from inside",],
    30: [images.science_lab_table,None,"a table of experiments.","Martian soil and dust is on it.",],
    31: [images.vending_machine,images.full_shadow,"a vending machine.","Unfortunately, it needs a credit. And I used the last one.",],
    33: [images.mission_control_desk,images.mission_control_desk_shadow,"computer station connected to Mission Control.","",],
    34: [images.duckwall,images.full_shadow,"a whiteboard.","It used to be used for brainstorming and planning.",],
    35: [images.window,images.full_shadow,"a window.","It allows you to look out at space.",],
    36: [images.window_short,images.full_shadow,"a window","It allows you to look out at space.",],
    37: [images.robot,images.robot_shadow,"a cleaning robot.","It's turned off right now to conserve power.",],
    40: [images.drone,None,"a delivery drone","They used to whizz through the corridors like nobody's business.",],
    41: [images.computer,images.computer_shadow,"a computer workstation","Used for managing space station systems.",],
    42: [images.map,images.full_shadow,"a map charting the path of the ship.","It's very in-depth.",],
    43: [images.bottomfence,None,"a fence.","It stops you from walking onto the crops",],
    44: [images.topfence, None, "a fence.", "It stops you from walking onto the crops"],
    45: [images.leftfence,None,"a fence.","It stops you from walking onto the crops",],
    46: [images.rightfence,None,"a fence.","It stops you from walking onto the crops",],
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
    [14,10,False,False,False,True,"A wide, empty room","You can decorate this however you like!",],
    [0,0,False,False,False,False,"space.","As a developer, please tell me how you got out so I can patch this.",],
    [14,10,False,False,False,True,"The toilet","The only one.",],
    [4, 4, False, True, True, True, "an access corridor.", "How did you get here?"],
    [18,18,True,True,False,False,"the one and only lounging area in the entire cabin.","It's pretty nice!",],
    [4, 4, True, False, True, True, "an access corridor.", "How did you get here?"],
    [14,10,False,False,True,False,"the dorm.","It's a dorm.",],
    [0,0,False,False,False,False,"space.","As a developer, please tell me how you got out so I can patch this.",],
    [14,10,False,False,True,False,"the garden.","The plants grow here. Tomatoes grow surprisingly well!",],
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
    6: [[7, 0, 0],[14, 0, 2],[7, 0, 3],[8, 0, 7],[14, 0, 9],[8, 0, 10],[7, 2, 0],[14, 2, 2],[7, 2, 3],[8, 2, 7],[14, 2, 9],[8, 2, 10],[7, 5, 0],[14, 5, 2],[7, 5, 3],[8, 5, 7],[14, 5, 9],[8, 5, 10],[7, 7, 0],[14, 7, 2],[7, 7, 3],[8, 7, 7],[14, 7, 9],[8, 7, 10],[35, 8, 0],],8: [[35, 8, 0],[4, 1, 1],[4, 1, 2],[4, 1, 3],[4, 1, 4],[4, 1, 7],[4, 1, 8],[4, 1, 9],[4, 1, 10],[4, 2, 1],[4, 2, 2],[4, 2, 3],[4, 2, 4],[4, 2, 7],[4, 2, 8],[4, 2, 9],[4, 2, 10],[4, 4, 1],[4, 4, 2],[4, 4, 3],[4, 4, 4],[4, 4, 7],[4, 4, 8],[4, 4, 9],[4, 4, 10],[4, 5, 1],[4, 5, 2],[4, 5, 3],[4, 5, 4],[4, 5, 7],[4, 5, 8],[4, 5, 9],[4, 5, 10],[43, 6, 1],[43, 6, 2],[43, 6, 3],[43, 6, 4],[43, 6, 7],[43, 6, 8],[43, 6, 9],[43, 6, 10],[44, 0, 1],[44, 0, 2],[44, 0, 3],[44, 0, 4],[44, 0, 7],[44, 0, 7],[44, 0, 8],[44, 0, 9],[44, 0, 10],[43, 3, 1],[43, 3, 2],[43, 3, 3],[43, 3, 4],[43, 3, 7],[43, 3, 8],[43, 3, 9],[43, 3, 10],[43, 3, 1],[43, 3, 2],[43, 3, 3],[43, 3, 4],[43, 3, 7],[43, 3, 8],[43, 3, 9],[43, 3, 10],[45, 0, 0],[45, 1, 0],[45, 2, 0],[46, 0, 5],[46, 1, 5],[46, 2, 5],[45, 0, 6],[45, 1, 6],[45, 2, 6],[46, 0, 11],[46, 1, 11],[46, 2, 11],[45, 3, 0],[45, 4, 0],[45, 5, 0],[46, 3, 5],[46, 4, 5],[46, 5, 5],[45, 3, 6],[45, 4, 6],[45, 5, 6],[46, 3, 11],[46, 4, 11],[46, 5, 11]]
}

checksum = 0
check_counter = 0
for key, room_scenery_list in SCENERY.items():
    for scenery_item_list in room_scenery_list:
        checksum += (
            scenery_item_list[0] * key
            + scenery_item_list[1] * (key + 1)
            + scenery_item_list[2] * (key + 2)
        )
        check_counter += 1
assert check_counter == 120, f"Expected 120 scenery items, got {check_counter}."
assert checksum == 32523, f"Expected checksum of 32523, got {checksum}."

ITEMS_PLAYER_MAY_STAND_ON = [1, 5, 34, 43, 44, 45, 46, 256] # The items that the player can walk through
ITEMS_PLAYER_MAY_INTERACT_WITH = [15, 33, 41] # Computers that cause the mood chart to show 

#######################################################
### LANGCHAIN AND OPENAI API -- Yau Shing and Vimal ###
#######################################################

### Initialize
model = ChatOpenAI(model="gpt-4o-mini", api_key=password.api_key, temperature=0.5)

def call_model(state: MessagesState):
    global text_hist
    ### Make the messages
    system_prompt = f"Your name is {ROBOT_NAME}, and you are a therapist, who gives emotional support to the user no matter what, and uses quick and concise replies to help your clients improve their mental health. The provided history includes a summary of the earler conversation."
    system_message = SystemMessage(content=system_prompt)
    message_history = state["messages"][:-1]  # The message history are the messages - the most recent user input
    text_hist = message_history[:] # Copy the local var into the global, saved var
    # Summarize the messages if the chat history >= 5
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

# Workflow for LangGraph
workflow = StateGraph(state_schema=MessagesState)

# define the node in the graph
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}

# Queries the AI for an answer, including the text history and the user request.
def get_answer(query):
    output = app.invoke({"messages": text_hist + [HumanMessage(content=query)]}, config)
    print(text_hist)
    return output["messages"][-1].content # Returns the most recent message in the list


#############################
### MAKE MAP -- Yau Shing ###
#############################
def create_room(room_number, width, height, left=False, right=False, up=False, down=False):
    ### Validations
    assert 0 <= room_number <= ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH, f"Room number is invalid. Expected 0 ≤ room number ≤ {ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH - 1}, got {room_number}"
    assert width % 2 == 0, "Width must be even"
    assert height % 2 == 0, "Height must be even"
    assert 0 <= width < ROOM_SIZE, f"Width ({width}) must between 0 and ROOM_SIZE ({ROOM_SIZE}), inclusive."
    assert 0 <= height < ROOM_SIZE, f"Height ({height}) must be between 0 and ROOM_SIZE ({ROOM_SIZE}), inclusive."
    if width == 0 or height == 0:
        return [[0 for _ in range(ROOM_SIZE)] for _ in range(ROOM_SIZE)]  # if width or height of room is zero, return a void
    # Generates borders for empty void of space
    lr_borders = (ROOM_SIZE - width) // 2
    ud_borders = (ROOM_SIZE - height) // 2
    room = [[2 for _ in range(width)]] + [[2] + [1 for _ in range(width - 2)] + [2] for _ in range(height - 2)] + [[2] + [3 for _ in range(width - 2)] + [2]] # Generate walls around the room
    if left: # If there is a left exit, create the gap to the left
        sections = height // 2
        room[sections - 1][0] = 1
        room[sections][0] = 1
    if right: # If there is a right exit, create the gap to the right
        sections = height // 2
        room[sections - 1][-1] = 1
        room[sections][-1] = 1
    if up: # If there is a up exit, create the gap to the top
        sections = width // 2
        room[0][sections - 1] = 1
        room[0][sections] = 1
    if down: # If there is a down exit, create the gap to the bottom
        sections = width // 2
        room[-1][sections - 1] = 1
        room[-1][sections] = 1
    if room_number in SCENERY:
        scenery_items_in_room = SCENERY[room_number] # Local var of the scenery items in each room
        for scenery_object in scenery_items_in_room: # Loops through each scenery item
            # Validations
            assert 0 <= scenery_object[1] + 1 <= len(room), f"Error in scenery placement: Expected -1 ≤ y ≤ {len(room) - 1}, got {scenery_object[1]}"
            assert 0 <= scenery_object[2] + 1 <= len(room[0]), f"Error in scenery placement: Expected -1 ≤ x ≤ {len(room[0]) - 1}, got {scenery_object[2]}"
            # Loops through the tiles that the scenery object is meant to take up
            for i in range(OBJECTS[scenery_object[0]][0].get_width() // 30):
                if scenery_object[1] == -1: # If the y is -1 (if the scenery is the top border of the room, remove the walls there)
                    room[scenery_object[1] + 1][scenery_object[2] + 1 + i] = 0
                else: # Otherwise, replace it with the floor block that's for the area taken by wide objects.
                    room[scenery_object[1] + 1][scenery_object[2] + 1 + i] = 255 
            room[scenery_object[1] + 1][scenery_object[2] + 1] = scenery_object[0] # At the leftmost corner of the scemery item, replace the floor with the scenery object
    room = [[0 for _ in range(width)] for _ in range(ud_borders)] + room + [[0 for _ in range(width)] for _ in range(ud_borders)]
    # Generate the empty blocks around the room
    for i in range(ROOM_SIZE):
        room[i] = [0 for _ in range(lr_borders)] + room[i] + [0 for _ in range(lr_borders)]
    if left:
        # Generate the corridor on the left side of the room
        sections = height // 2
        room[sections - 2 + ud_borders][:lr_borders] = [2 for _ in range(lr_borders)]
        room[sections - 1 + ud_borders][:lr_borders] = [1 for _ in range(lr_borders)]
        room[sections + ud_borders][:lr_borders] = [1 for _ in range(lr_borders)]
        room[sections + 1 + ud_borders][:lr_borders] = [3 for _ in range(lr_borders)]
    if right:
        # Generate the corridor on the right side of the room
        sections = height // 2
        room[sections - 2 + ud_borders][-lr_borders:] = [2 for _ in range(lr_borders)]
        room[sections - 1 + ud_borders][-lr_borders:] = [1 for _ in range(lr_borders)]
        room[sections + ud_borders][-lr_borders:] = [1 for _ in range(lr_borders)]
        room[sections + 1 + ud_borders][-lr_borders:] = [3 for _ in range(lr_borders)]
    if up:
        # Generate the corridor on the top side of the room
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
        # Generate the corridor on the bottom side of the room
        sections = width // 2
        for i in range(ud_borders):
            room[-i - 1][sections - 2 + lr_borders] = 2
            room[-i - 1][sections + 1 + lr_borders] = 2
            room[-i - 1][sections - 1 + lr_borders] = 1
            room[-i - 1][sections + lr_borders] = 1
            if i == ud_borders - 1:
                room[-i - 2][sections - 1 + lr_borders] = 5
                room[-i - 1][sections + lr_borders] = 256
    return room # A 2D array of the room with scenery objects

def generate_rooms(rooms):
    room_data = [] #  Local var - will be a 2D array of the entire cabin with scenery objects
    # Validation
    assert len(rooms) == ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH, f"Expected {ROOM_MAP_HEIGHT * ROOM_MAP_WIDTH} rooms, got {len(rooms)}."
    for i in range(len(rooms)): # Loops through each room
        if i % ROOM_MAP_WIDTH == 0: # If the room number should be a new row of rooms, create a new row
            row_data = create_room(i, rooms[i][0], rooms[i][1], rooms[i][2], rooms[i][3], rooms[i][4], rooms[i][5])
            # ROW of ROOMS, not a single row of tiles
            if i != len(rooms) - 1: continue # If the room is not the last room, skip to the next iteration
        # If the room is the last room and last room, create another temporary room and add it to the row_data
        temp_room = create_room(i, rooms[i][0], rooms[i][1], rooms[i][2], rooms[i][3], rooms[i][4], rooms[i][5],)
        for j in range(ROOM_SIZE): # For each row of tiles, add the room row data to row_data
            row_data[j] += temp_room[j]
        if i == (len(rooms) - 1): # If the room is the last room
            if i % ROOM_MAP_WIDTH != ROOM_MAP_WIDTH - 1: # If the last room isn't aligned to the other rooms, pad the end of the row with empty space
                for _ in range((ROOM_MAP_WIDTH - 1) - (i % ROOM_MAP_WIDTH)):
                    for j in range(ROOM_SIZE):
                        row_data[j] += [0 for _ in range(ROOM_SIZE)]
        # If the room is the last room in the row, add the row data to room_data
        if (i % ROOM_MAP_WIDTH) == (ROOM_MAP_WIDTH - 1) or i == len(rooms) - 1:
            room_data += row_data
    # Trnasparent wall validations
    for y in range(len(room_data)):
        for x in range(len(room_data[y])):
            # If the tile is a wall that has a floor above it and empty space beneath it, it should be a wall that will change transparency
            if room_data[y][x] == 2 and room_data[y + 1][x] == 0 and room_data[y - 1][x] == 1:
                room_data[y][x] = 3
            # If the tile was initialised to be a wall with transparency but it ground beneath it is not empty space, it should not be a wall with transparency
            if room_data[y][x] == 3 and room_data[y + 1][x] != 0:
                room_data[y][x] = 2
    final = [] # Final room data
    trans_wall_count = 0 # For assertion check
    # If the length of each row is greater than 0, add it to the final array (Presence check)
    for row in room_data: 
        if len(row) > 0:
            final.append(row)
    # Checks if the height of the total tile is what it should be
    assert len(final) == ROOM_MAP_HEIGHT * ROOM_SIZE, f"Expected height to be {ROOM_MAP_HEIGHT * ROOM_SIZE}, got {len(room_data)}"
    for i in range(len(final)):
        # Checks if the width of the row i is what it should be
        assert len(final[i]) == ROOM_MAP_WIDTH * ROOM_SIZE, f"Expected width of row {i} to be {ROOM_MAP_WIDTH * ROOM_SIZE}, got {len(final[i])}"
        trans_wall_count += final[i].count(3) # Add the number of transparent walls in the row to the count of transparent walls
    assert trans_wall_count == 50, f"Expected 50 transparent walls, got {trans_wall_count}." # Final check of transparent walls
    return final

def adjust_wall_transparency():
    global walls
    # Basically a key
    # Checked tiles = {[2xy-x²]: tile}
    # The key is 2xy-x²
    checked_tiles = { # The tiles around the player, in a key: tile-type pair
        (player_x - 1) * 2 * (player_y) - (player_x - 1) ** 2: room_map[player_y][player_x - 1],
        (player_x - 1) * 2 * (player_y + 1) - (player_x - 1) ** 2: room_map[player_y + 1][player_x - 1],
        (player_x - 1) * 2 * (player_y + 2) - (player_x - 1) ** 2: room_map[player_y + 2][player_x - 1],
        (player_x) * 2 * (player_y) - (player_x) ** 2: room_map[player_y][player_x],
        (player_x) * 2 * (player_y + 1) - (player_x) ** 2: room_map[player_y + 1][player_x],
        (player_x) * 2 * (player_y + 2) - (player_x) ** 2: room_map[player_y + 2][player_x],
        (player_x + 1) * 2 * (player_y) - (player_x + 1) ** 2: room_map[player_y][player_x + 1],
        (player_x + 1) * 2 * (player_y + 1) - (player_x + 1) ** 2: room_map[player_y + 1][player_x + 1],
        (player_x + 1) * 2 * (player_y + 2) - (player_x + 1) ** 2: room_map[player_y + 2][player_x + 1],
    }
    for k, v in checked_tiles.items():
        # If there's a wall with transparency in checked_tiles, and the frame of the wall is < 4, add a frame to the wall
        if v == 3 and walls[k] < 4:
            walls[k] += 1 
    for k in list(walls.keys()):
        # If there's a wall with transparency in walls, and the frame of the wall is > 0, and it is not in checked_tiles (i.e. NOT in the radius of the player), remove a frame to the wall
        if not k in list(checked_tiles.keys()) and walls[k] > 0:
            walls[k] -= 1

def open_doors():
    # EVERYTHING WORKS THE SAME AS THE WALL TRANSPARENCY SEE COMMENTS THERE
    global doors
    checked_tiles = {
        (player_x - 1) * 2 * (player_y - 2) - (player_x - 1) ** 2: room_map[player_y - 2][player_x - 1],
        (player_x - 1) * 2 * (player_y - 1) - (player_x - 1) ** 2: room_map[player_y - 1][player_x - 1],
        (player_x - 1) * 2 * (player_y) - (player_x - 1) ** 2: room_map[player_y][player_x - 1],
        (player_x - 1) * 2 * (player_y + 1) - (player_x - 1) ** 2: room_map[player_y + 1][player_x - 1],
        (player_x - 1) * 2 * (player_y + 2) - (player_x - 1) ** 2: room_map[player_y + 2][player_x - 1],
        (player_x) * 2 * (player_y - 2) - (player_x) ** 2: room_map[player_y - 2][player_x],
        (player_x) * 2 * (player_y - 1) - (player_x) ** 2: room_map[player_y - 1][player_x],
        (player_x) * 2 * (player_y) - (player_x) ** 2: room_map[player_y][player_x],
        (player_x) * 2 * (player_y + 1) - (player_x) ** 2: room_map[player_y + 1][player_x],
        (player_x) * 2 * (player_y + 2)- (player_x) ** 2: room_map[player_y + 2][player_x],
    }
    for k, v in checked_tiles.items():
        if v == 5 and doors[k] < 3:
            doors[k] += 1
    for k in list(doors.keys()):
        if not k in checked_tiles and doors[k] > 0:
            doors[k] -= 1


def draw_image(image, y, x):
    screen.blit(image, (top_left_x + ((x + x_shift) * TILE_SIZE), top_left_y + ((y + y_shift) * TILE_SIZE) - image.get_height()))
    # Draws the image, taking the y and x tile and drawing them including the relative shift to the player position and the height of the image and offset of the screen and the size of the tile

def draw_shadow(image, y, x):
    screen.blit(image, (top_left_x + ((x + x_shift) * TILE_SIZE), top_left_y + ((y + y_shift) * TILE_SIZE)))
    # Draws the image, taking the y and x tile and drawing them including the relative shift to the player position and offset of the screen and the size of the tile

def draw_player():
    player_image = PLAYER[player_direction][player_frame]
    screen.blit(player_image, (top_left_x + 15 * TILE_SIZE, top_left_y + 15 * TILE_SIZE - player_image.get_height()))
    # Blits the player image always at the middle of the screen (see draw_image (line 540) for explanation of how this line is derived)
    player_image_shadow = PLAYER_SHADOW[player_direction][player_frame]
    screen.blit(player_image_shadow, (top_left_x + 15 * TILE_SIZE, top_left_y + 15 * TILE_SIZE))
    # Blits the player shadow always at the middle of the screen (see draw_image (line 544) for explanation of how this line is derived)

def draw_robot():
    robot_image = ROBOT[robot_direction][robot_moving]
    screen.blit(robot_image, (top_left_x + (robot_x + x_shift + robot_offset_x) * TILE_SIZE, top_left_y + (robot_y + y_shift + robot_offset_y) * TILE_SIZE - robot_image.get_height()))
    # Blits the robot image at the robot's position, taking into account the relative shift to the player position and the height of the image and offset of the screen and the size of the robot
    # Robot_offset_x and Robot_offset_y takes into account the old position of the player and uses that as the where the robot should

###########################
### PAUSE MENU -- Vimal ###
###########################
def pause_loop():
    global old_click, mute, paused, modal, modal_text, delete_data
    clicked = any(pygame.mouse.get_pressed()) # Is the mouse clicked?
    if clicked and not old_click: # If it was clicked and it wasn't clicked in the last frame (i.e., it was clicked but not held)
        mouse_x = pygame.mouse.get_pos()[0] # Get mouse x of there it was clicked
        mouse_y = pygame.mouse.get_pos()[1] # Get mouse y of there it was clicked
        if not modal and paused: # If there is no modal popping up but the game is paused
            if 270 <= mouse_x <= 630 and 250 <= mouse_y <= 340: # Continue button, continues the game
                clock.schedule_interval(game_loop, 0.02)
                clock.schedule_interval(robot_interactions, 0.05)
                paused = False
            if 270 <= mouse_x <= 630 and 390 <= mouse_y <= 480: # Quit button, starts the modal
                modal = True
                modal_text = "Are you sure you want to quit?" 
            if 270 <= mouse_x <= 360 and 530 <= mouse_y <= 620: # Mute music button
                mute = not mute # Inverts mute so that the icon is drawn correctly and the music plays properly
                if mute: music.pause()
                else: music.unpause()
            if 540 <= mouse_x <= 630 and 530 <= mouse_y <= 620: # Delete data button
                modal = True
                modal_text = "Are you sure you want to delete all your data? The game will automatically stop after you confirm."
                delete_data = True
        elif modal: # If there is modal popping up, it is either that the user clicked delete or quit
            if 285 <= mouse_x <= 465 and 480 <= mouse_y <= 570: # The left button which is confirm
                if delete_data: # If the user clicked delete this will be true
                    try:
                        os.remove("savefile.dat")
                        os.remove("images/moodchart.png")
                    except:
                        pass
                # No matter what the game will exit
                exit()
            if 435 <= mouse_x <= 615 and 480 <= mouse_y <= 570: # Cancel
                modal = False # Removes the modal
                delete_data = False # Sets the popup to delete data back to False
    old_click = clicked # Updates old_click

##############################
### CHATBOT  -- Yau Shing ###
##############################
# On_key_up is a built-in function into pgzero that is called everytime a key is released on the keyboard. We use release to prevent tracking a press and held key.
def on_key_up(key, mod): 
    # Key **should** be in the format keys.F, keys.Q, keys.K_1, keys.SPACE, .etc, BUT for vimal it didn't work like that and gave integers, which is the fix in line 609
    # Mod is if the shift or caps key is toggled
    global player_speaking, player_text, paused, exercise_menu, breathing_menu, cur_pg, bodyscan_menu, pause_music
    try: key_id = str(key)[str(key).index(".") + 1:] # Gets the part of keys.F that's pass the period
    except: key_id = KEY_IDS[key][str(KEY_IDS[key]).index(".") + 1 :] #When the keys doesn't return in the correct format, take it from KEYS_IDS and get the part that's pass the period
    # If the escape key was pressed, and the player is not typing, and the robot is not speaking, and the exercise menu is not on, and the game is not paused, pause the game.
    if not paused and key_id == "ESCAPE" and not player_speaking and not robot_speaking and not exercise_menu: 
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        paused = True
    # If the escape key was pressed and the game is paused, unpause the game
    elif paused and key_id == "ESCAPE":
        clock.schedule_interval(game_loop, 0.02)
        clock.schedule_interval(robot_interactions, 0.05)
        paused = False
    # If the I key was pressed, and the player is not typing, and the robot is not speaking, and the exercise menu is not on, and the game is not paused, turn on the exercise menu
    if not exercise_menu and not paused and key_id == "I" and not player_speaking and not robot_speaking:
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        exercise_menu = True
    elif exercise_menu and key_id == "I":
        clock.schedule_interval(game_loop, 0.02)
        clock.schedule_interval(robot_interactions, 0.05)
        music.play(random.choice(MUSIC_CHOICES))
        exercise_menu = breathing_menu = bodyscan_menu = False
    # exercises go to next step
    if breathing_menu and key_id == "RIGHT":
        if cur_pg < 5:
            cur_pg += 1
    elif breathing_menu and key_id == "LEFT":
        if cur_pg > 0:
            cur_pg -= 1
    # pause body scan track
    if bodyscan_menu and key_id == "SPACE" and pause_music == False:
        pause_music = True
    elif bodyscan_menu and key_id == "SPACE":
        pause_music = False
    
    if not player_speaking and key_id == "C" and chatbot_on == True and not paused and not robot_speaking and not exercise_menu:  
        # If the C key was pressed, and the player is not typing, and the robot is not speaking, and the exercise menu is not on, and the game is not paused, and the chatbot is activated by the API key, start the chatbot
        clock.unschedule(robot_interactions)
        clock.unschedule(game_loop)
        start_chatbot()
    if player_speaking:  # Typing
        print(player_text)
        if len(key_id) == 1: # If the key_id is length is 1, that means a letter key was pressed, so add the key_id
            if mod: player_text += key_id
            else: player_text += key_id.lower()
        if len(key_id) == 3 and not key_id == "TAB": # If the key_id is length is 3 and not TAB, that means a number key was pressed (K_x), so add the key_id's last character
            if mod: player_text += SHIFTED[int(key_id[-1])]
            else: player_text += key_id[-1]
        # The rest is pretty self-explanatory
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
        if key_id == "TAB":
            if mod: player_text += "    "
        if key_id == "SPACE":
            player_text += " "
        if key_id == "BACKSPACE":
            player_text = player_text[:-1]
        if key_id == "RETURN": # If the enter key is pressed, call the function
            end_player_message()


def end_player_message():  
    # When the player is done typing, close the popup. If the player_text is an exit query (currently :q), stop the chatbot and resume game parts. Else, get the reply from the chatbot
    global player_speaking, mood_hist
    player_speaking = False # Remove player's ability to type
    if player_text == ":q": # Stop chatbot
        clock.schedule_interval(robot_interactions, 0.05)
        clock.schedule_interval(game_loop, 0.02)
        pass
    elif player_text == ":h": # Show help message
            display_message(
                f"Hi! I'm {ROBOT_NAME}, your AI companion. If you need any help, press 'T'. If you want to chat, press 'C'. For breathing exercisies, press 'I'! While chatting, type :q to exit, :mood to show your mood chart or :h to display this message again. Now, use WASD to move!"
            )
            clock.schedule_unique(end_message, 20.0)
    elif player_text == ":mood": # If the player queries for the mood chart, plot the chart and show it
        mood_to_disp = [
            sum(mood_hist[i]) / (len(mood_hist[i])) for i in mood_hist.keys()
        ]
        plt.plot(list(mood_hist.keys()), mood_to_disp, marker="x")
        plt.xlabel("Date")
        plt.ylabel("Mood")
        plt.title("Mood chart")
        plt.grid(True)
        plt.ylim(-1.1, 1.1)
        plt.plot(
            list(mood_hist.keys()),
            [0 for _ in range(len(mood_hist))],
            color="lightgray",
            linestyle="--",
            label="Baseline",
        )
        plt.savefig("images/moodchart.png")
        show_mood_chart()
    else: # Otherwise, get the sentiment form the text, add it to the history, get the reply from the chatbot
        today_date = np.datetime64(date.today())
        if today_date not in mood_hist:
            mood_hist[today_date] = [get_sentiment(player_text)]
        else:
            mood_hist[today_date].append(get_sentiment(player_text))
        get_reply(player_text)

def get_reply(text):
    display_robot_message(get_answer(text))
    # Sends the chatbot the query and sends the reult to the text splitter


def display_robot_message_cont():
    global future_robot_text, robot_text
    split_text = [future_robot_text[i : i + 200] for i in range(0, len(future_robot_text), 200)] # Splits the text into blocks of 200 characters each
    future_robot_text = "".join(split_text[1:])
    # Set the global text that cannot fit to the textbox as a list, including all of the segments except the first one
    if len(future_robot_text) > 0: # If there is more than zero segments, set the global robot text to the first segment and schedule the next messages
        robot_text = split_text[0]
        clock.schedule(display_robot_message_cont, max(6.0, round(len(robot_text) * 0.15, 1)))
    else: # Otherwise, just show the robot_text
        clock.schedule_unique(end_robot_message, max(6.0, round(len(robot_text) * 0.15, 1)))


def display_robot_message(text):
    global robot_speaking, robot_text, future_robot_text
    robot_speaking = True # Sets the robot textbox to appear
    robot_text = text # Sets the global robot text to the parameter
    if len(robot_text) > 205: # If the length of the message is too long to fit in one textbox, call the continued function
        not_yet_done = robot_text[201:] # Text that cannot fit
        robot_text = robot_text[:201] # Text that fits
        future_robot_text = not_yet_done # Global text that cannot fit
        clock.schedule(display_robot_message_cont, max(6.0, round(len(robot_text) * 0.15, 1))) # Schedules the next segment of the message
    clock.schedule_unique(end_robot_message, max(6.0, round(len(robot_text) * 0.15, 1))) # Otherwise schedule the end of the message (minimum 6 seconds, or it scales with the message length)


def end_robot_message():
    global robot_speaking
    robot_speaking = False # Turns of the robot textbox
    get_player_text() # Get player query


def get_player_text():
    global player_speaking, player_text
    player_text = "" 
    player_speaking = True # Allows the player to start typing


def start_chatbot():
    clock.unschedule(robot_interactions)
    get_player_text() # Pause the robot's other functions and allows the player to start typing


################################
### MOOD CHARTS -- Yau Shing ###
################################
def preprocess_text(text):
    # Throws the query through a tokenizer, filter the stopwords, and a lemmatizer
    tokens = word_tokenize(text.lower())
    filtered = [token for token in tokens if token not in stopwords.words("english")]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered]
    processed_text = " ".join(lemmatized_tokens)
    return processed_text


def get_sentiment(text):
    # Uses nltk's Vader SentimentIntensityAnalyzer to get the sentiment
    # Only want the compound score from -1 to 1
    processed = preprocess_text(text)
    scores = SentimentIntensityAnalyzer().polarity_scores(text)
    return scores["compound"]

def show_mood_chart():
    global displaying_chart # Set the global chart to display to true 
    displaying_chart = True
    clock.schedule_unique(hide_mood_chart, 10.0) # Schedule to hide the chart after 10 seconds

def hide_mood_chart():
    global displaying_chart
    displaying_chart = False # Hides the chart
    end_robot_message() # Calls to end the robot message 

"""
def player_interact():
    Only for scenery that we didn't add into this demo yet
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
        mood_to_disp = [
            sum(mood_hist[i]) / (len(mood_hist[i]) - mood_hist[i].count(0))
            for i in mood_hist.keys()
        ]
        plt.plot(
            list(mood_hist.keys()), mood_to_disp, marker="x", color="blue", label="Mood"
        )
        plt.xlabel("Date")
        plt.ylabel("Mood")
        plt.title("Mood chart")
        plt.grid(True)
        plt.ylim(-1.1, 1.1)
        plt.plot(
            list(mood_hist.keys()),
            [0 for _ in range(len(mood_hist))],
            color="lightgray",
            linestyle="--",
            label="Baseline",
        )
        plt.savefig("images/moodchart.png")
        show_mood_chart()
    else:
        pass
"""

#####################################
#### MAIN GAME LOOPS -- Yau Shing ###
#####################################
def draw():
    # Inbuilt to be called by pgzero
    mouse_x = pygame.mouse.get_pos()[0] # Get mouse x
    mouse_y = pygame.mouse.get_pos()[1] # Get mouse y
    screen.blit(images.backdrop, (top_left_x + ((-15 + x_shift) * TILE_SIZE), top_left_y + ((-15 + y_shift) * TILE_SIZE))) # Draw the backdrop
    # Draws the map
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE):
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE):
            if room_map[y][x] in ITEMS_PLAYER_MAY_STAND_ON and not room_map[y][x] in [5, 43, 45, 46]: # Basically if the tile is a tile that will act as the floor, draw it, unless it is a door
                draw_image(OBJECTS[room_map[y][x]][0], y, x)
            if room_map[y][x] not in [0, 4, 34, 35, 36]: # If the tile is not a void, not a wall or not a scenery item that acts like a wall, draw a floor there
                draw_image(OBJECTS[1][0], y, x)
    for y in range(ROOM_MAP_HEIGHT * ROOM_SIZE):
        # For actual scenery stuff
        for x in range(ROOM_MAP_WIDTH * ROOM_SIZE): 
            item_here = room_map[y][x]
            # Player cannot walk on 255: it marks spaces used by wide objects.
            if item_here not in ITEMS_PLAYER_MAY_STAND_ON + [255] or item_here in [5, 43, 45, 46]: # For the rest of the times that was not drawn, it's drawn here
                image = OBJECTS[item_here][0]
                if item_here == 3: # For a wall with transparency, draw the frame saved in the walls dict
                    image = OBJECTS[item_here][0][walls[2 * x * y - x**2]]
                if item_here == 5: # For a door, draw the frame saved in the doors dict (Key is 2xy-x²)
                    image = OBJECTS[item_here][0][doors[2 * x * y - x**2]]
                draw_image(image, y, x) # Draws image
                if OBJECTS[item_here][1] is not None:  # If object has a shadow
                    shadow_image = OBJECTS[item_here][1]
                    if item_here == 5: # Draw the shadow of the door with the frame in the doors dict
                        shadow_image = OBJECTS[item_here][1][doors[2 * x * y - x**2]]
                    # If shadow needs horizontal tiling
                    if shadow_image in [images.half_shadow, images.full_shadow]:
                        shadow_width = int(image.get_width() / TILE_SIZE)
                        # Use shadow across width of object.
                        for z in range(0, shadow_width):
                            draw_shadow(shadow_image, y, x + z)
                    else:
                        draw_shadow(shadow_image, y, x)
        if robot_y == y: # If the robot is at this y, draw the robot (This is for z-indexing so that the robot is always above the other scenery except stuff like walls)
            draw_robot() 
        if player_y == y: # If the player is at this y, draw the player (This is for z-indexing so that the player is always above the other scenery except stuff like walls)
            draw_player()
    # If the item is a fence that should be in front of the player draw it here
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
        screen.draw.text(player_text, (60, 700), color="black", fontname="biorhyme", width=780, lineheight=1, fontsize=15)
        screen.blit(images.player_text, (30, 600))

    ## Stress Management Exercises -- Jolene
    if exercise_menu and not paused:
        s = pygame.Surface((WIDTH-70, HEIGHT-70), pygame.SRCALPHA) # Creates a surface
        colour = (255, 255, 255)
        pygame.draw.rect(s, colour, pygame.Rect(0, 0, WIDTH-70, HEIGHT-70),  0, 50)
        screen.blit(s, (35, 35))
        screen.draw.text("MINDFULNESS EXERCISES", ((WIDTH/2-640/2), 140), color="dodgerblue4", width=640, fontname="biorhyme", lineheight=1, fontsize = 40)
        screen.draw.text("press [I] to quit", ((WIDTH/2-160/2), 200), color="dimgrey", width=160, fontname="biorhyme", lineheight=1, fontsize = 20)
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        if 120 <= mouse_x <= 780 and 280 <= mouse_y <= 420: screen.blit(images.breathing_button_hover, (120, 280))
        else: screen.blit(images.breathing_button, (120, 280))
        if 120 <= mouse_x <= 780 and 460 <= mouse_y <= 600: screen.blit(images.bodyscan_button_hover, (120, 460))
        else: screen.blit(images.bodyscan_button, (120, 460))
    if breathing_menu and not paused:
        s = pygame.Surface((WIDTH-70, HEIGHT-70), pygame.SRCALPHA) # Creates a surface over exercise menu
        colour = (255, 255, 255)
        pygame.draw.rect(s, colour, pygame.Rect(0, 0, WIDTH-70, HEIGHT-70),  0, 50)
        screen.blit(s, (35, 35))
        screen.draw.text("BREATHING EXERCISE", ((WIDTH/2-550/2), 140), color="dodgerblue4", width=550, fontname="biorhyme", lineheight=1, fontsize = 40)
        screen.draw.text("press key [RIGHT] to go to the next stage.", ((WIDTH/2-485/2), 200), color="dimgrey", width=485, fontname="biorhyme", lineheight=1, fontsize = 20)
        if cur_pg < 1:
            screen.draw.text("Deep breathing helps to relieve symptoms of anxiety. ", ((WIDTH/2-485/2), 270), color="black", width=485, fontname="biorhyme", lineheight=1, fontsize = 20)
            screen.draw.text("INSTRUCTIONS: Lean back or lie down in a comfortable position. Close your eyes if you'd like. When starting out, try placing a hand on your stomach. If you breathe deeply enough, you should feel it rise and fall with each breath. ", ((WIDTH/2-485/2), 340), color="black", width=485, fontname="biorhyme", lineheight=1, fontsize = 20)
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        #back button hover
        if 90 <= mouse_x <= 200 and 80 <= mouse_y <= 115: screen.blit(images.exercise_back_hover, (90,80))
        else: screen.blit(images.exercise_back, (90,80))
        if cur_pg >= 1:
            screen.draw.text("Step 1 of 4", (170, 260), color="black", width=550, fontname="biorhyme", lineheight=1, fontsize = 25)
            screen.draw.text("Inhale. Slowly breathe in through your nose for 4 seconds.", (170, 290), color="dimgrey", width=550, fontname="biorhyme", lineheight=1, fontsize = 17)
        if cur_pg >= 2:
            screen.draw.text("Step 2 of 4", (170, 310), color="black", width=550, fontname="biorhyme", lineheight=1, fontsize = 25)
            screen.draw.text("Pause. Hold your breath for 4 seconds.", (170, 340), color="dimgrey", width=550, fontname="biorhyme", lineheight=1, fontsize = 17)
        if cur_pg >= 3:
            screen.draw.text("Step 3 of 4", (170, 359), color="black", width=550, fontname="biorhyme", lineheight=1, fontsize = 25)
            screen.draw.text("Exhale. Gently release your breath through your mouth for 6 seconds.", (170, 388), color="dimgrey", width=550, fontname="biorhyme", lineheight=1, fontsize = 17)
            screen.draw.text("Tip: Purse your lips as if blowing through a straw to slow the exhale.", (170, 446), color="dimgrey", width=550, fontname="biorhyme", lineheight=1, fontsize = 17)
        if cur_pg >= 4:
            screen.draw.text("Step 4 of 4", (170, 505), color="black", width=550, fontname="biorhyme", lineheight=1, fontsize = 25)
            screen.draw.text("Repeat. Continue for at least 2 minutes, ideally 5 to 10 minutes.", (170, 535), color="dimgrey", width=550, fontname="biorhyme", lineheight=1, fontsize = 17)
            screen.draw.text("You'll likely feel calmer after this exercise, but if not, don't worry—it takes practice.", ((WIDTH/2-485/2), 630), color="black", width=485, fontname="biorhyme", lineheight=1, fontsize = 20)
    if bodyscan_menu and not paused:
        global first_play
        s = pygame.Surface((WIDTH-70, HEIGHT-70), pygame.SRCALPHA) # Creates a surface over exercise menu
        colour = (255, 255, 255)
        pygame.draw.rect(s, colour, pygame.Rect(0, 0, WIDTH-70, HEIGHT-70),  0, 50)
        screen.blit(s, (35, 35))
        screen.draw.text("BODY SCAN EXERCISE", ((WIDTH/2-550/2), 140), color="dodgerblue4", width=550, fontname="biorhyme", lineheight=1, fontsize = 40)
        screen.draw.text("press key [SPACE] to start, pause and resume the audio track.", ((WIDTH/2-485/2), 200), color="dimgrey", width=485, fontname="biorhyme", lineheight=1, fontsize = 20)
        screen.draw.text("For this exercise, you will focus on the physical sensations in your body. Simply observe these sensations through listening to the audio track.", ((WIDTH/2-485/2), 275), color="black", width=485, fontname="biorhyme", lineheight=1, fontsize = 20)
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        #back button hover
        if 90 <= mouse_x <= 200 and 80 <= mouse_y <= 115: screen.blit(images.exercise_back_hover, (90,80))
        else: screen.blit(images.exercise_back, (90,80))
        if not music.is_playing("body_scan_audio") and first_play:
            music.play_once("body_scan_audio")
            first_play = False
        if pause_music:
            music.pause()
        else:
            music.unpause()
        if music.is_playing('body_scan_audio'):
            screen.blit(images.audio_playing, (350, 450))
        else:
            screen.blit(images.audio_paused, (350, 450))
        cur_time = music.get_pos()/143000 * 660
        screen.draw.line((120,560), (780,560), (128, 128, 128))
        screen.draw.line((120,560), (120+cur_time,560), (0, 0, 0)) 
        screen.draw.line((120,561), (780,561), (128, 128, 128)) #for more thickness
        screen.draw.line((120,561), (120+cur_time,561), (0, 0, 0)) 

    ## Pause menu -- Vimal
    if paused:
        s = pygame.Surface((WIDTH, HEIGHT)) # Creates a surface the height and width of the window
        s.set_alpha(128) # To create a semi-opaque overlay
        s.fill((0, 0, 0)) # Makes the overlay black (rgba(0, 0, 0, 128))
        screen.blit(s, (0,0)) # Blits the surface onto the screen
        mouse_x = pygame.mouse.get_pos()[0] # Get mouse x
        mouse_y = pygame.mouse.get_pos()[1] # Get mouse y
        screen.blit(images.pausesign, (230, 50)) # Paused symbol
        # If the mouse is hovering over the continue button show the hovered button otherwise show the proper button
        # Same for the quit button, mute button, and delete data button
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
    ## Paused modals -- Yau Shing
    if modal:
        screen.blit(images.modal, (270, 315)) # Show the modals
        screen.draw.text("Warning", (285, 325), color="black", fontname="biorhyme", width=330, lineheight=1, fontsize = 30) # Title
        screen.draw.text(modal_text, (285, 370), color="black", fontname="biorhyme", width=330, lineheight=1, fontsize = 20) # Modal text
        # If the mouse is hovering over the continue button show the hovered button otherwise show the proper button
        # Same for the cancel button
        if 285 <= mouse_x <= 465 and 520 <= mouse_y <= 570: screen.blit(images.modalcontinuehover, (285, 520)) 
        else: screen.blit(images.modalcontinue, (285, 520)) 
        if 465 <= mouse_x <= 615 and 520 <= mouse_y <= 570: screen.blit(images.modalcancelhover, (465, 520))
        else: screen.blit(images.modalcancel, (465, 520)) 
    ## Mood Chart -- Yau Shing
    if displaying_chart:
        screen.blit(images.moodchart, (110, 190))


###############################
### EXERCISE MENU -- JOLENE ###
###############################
def exercise_loop():
    global old_click2, exercise_menu, breathing_menu, bodyscan_menu, paused, cur_pg, first_play
    clicked = any(pygame.mouse.get_pressed())
    if clicked and not old_click2:
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        # print(pygame.mouse.get_pressed())
        print(f"Clicked at position {pygame.mouse.get_pos()}")

        if (
            exercise_menu
            and (120 <= mouse_x <= 780 and 280 <= mouse_y <= 420)
            and not breathing_menu
            and not bodyscan_menu
        ):  # breathing menu
            breathing_menu = True
        if (
            exercise_menu
            and (120 <= mouse_x <= 780 and 460 <= mouse_y <= 600)
            and not breathing_menu
            and not bodyscan_menu
        ):  # body scan menu
            bodyscan_menu = True
            first_play = True
        if exercise_menu and (
            90 <= mouse_x <= 200 and 80 <= mouse_y <= 115
        ):  # back button
            breathing_menu = bodyscan_menu = False
            cur_pg = 0
    old_click2 = clicked

###############################
### Text boxes -- Yau Shing ###
###############################
def display_message(text):
    global robot_speaking, robot_text
    robot_speaking = True
    robot_text = text

def end_message():
    global robot_speaking
    robot_speaking = False
    clock.schedule_interval(robot_interactions, 0.05)

##########################################
### MAIN GAME LOOP -- VIMAL, YAU SHING ###
##########################################
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
    """
    Only for computer scenery devices to show mood chart - not built into this demo
    if keyboard.e:
        player_interact()
    """
    # Music
    if mute:
        music.pause()
    if not mute:
        music.unpause()

    # Tracks the room the player is currently in
    current_room = player_x // ROOM_SIZE + (player_y // ROOM_SIZE) * 3
    # Animates the player's movement
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

    # Saves player's current position (For robot)
    old_player_x = player_x
    old_player_y = player_y

    # Move if key is pressed, only if there is no animation playing
    if player_frame == 0:
        if keyboard.left or keyboard.a:
            from_player_x = player_x
            from_player_y = player_y
            player_x -= 1
            player_direction = "left"
            player_frame = 1
            update_robot_pos(old_player_x, old_player_y)
        elif keyboard.right or keyboard.d:  # Elif stops player making diagonal movements
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
    # If the player attempts to move onto a tile they shouldn't be standing on, move them back
    if room_map[player_y][player_x] not in ITEMS_PLAYER_MAY_STAND_ON:
        player_x = old_player_x
        player_y = old_player_y
        player_frame = 0
    # Animates the frames to the movement on the tiles (Frame 1 = 0, Frame 2 = 0.25, Frame 3 = 0.5, Frame 4 = 0.75, Frame 5 = 1)
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
    # Calculates the relative position of the map compared to the player, who is always at x tile = 15, y tile = 15
    x_shift, y_shift = -(player_x + player_offset_x - 15), -(player_y + player_offset_y - 15)
    with open("savefile.dat", "wb") as f:
        # Saves player data
        pickle.dump([started, player_x, player_y, x_shift, y_shift, robot_x, robot_y, player_direction, robot_direction, mood_hist, text_hist], f,protocol=2)

########################################
### ROBOT INTERACTIONS -- YAU SHING ####
########################################
def robot_interactions():
    # Shows help messages
    global robot_speaking
    if keyboard.t:
        clock.unschedule(robot_interactions)
        display_help_message()
        clock.schedule_unique(end_message, 5.0)


def update_robot_pos(old_x, old_y):
    # Moves the robot according to the move the player made last
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
    # Checks what the player is facing and displays what it is accordingly
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
    # If the player is facing a wide object, facing will return 255 or 256, or 0, so it checks the tile to the left of what the player is facing until it finds something
    checking_x_shift = 0
    while facing == 255 or facing == 0 or facing == 256:
        facing = room_map[checked[0]][checked[1] - checking_x_shift]
        checking_x_shift += 1
    if facing != 1: # If it is facing an object, return the object title and description
        display_message(f"That is {OBJECTS[facing][2]} {OBJECTS[facing][3]}")
    else: # Otherwise return the room title and description
        display_message(f"This is {ROOMS[current_room][6]} {ROOMS[current_room][7]}")

#############
### START ###
#############
try:
    with open("savefile.dat", "rb") as f:
        started, player_x, player_y, x_shift, y_shift, robot_x, robot_y, player_direction, robot_direction, mood_hist, text_hist = pickle.load(f)
        # Loads saved data
except:
    started = False # Otherwise the user didn't use it before
if not mute:
    music.play(random.choice(MUSIC_CHOICES)) # Start music
if not started: # If it's the first time the user is using it, show the help message
    clock.unschedule(robot_interactions)
    display_message(
        f"Hi! I'm {ROBOT_NAME}, your AI companion. If you need any help, press 'T'. If you want to chat, press 'C'. For breathing exercisies, press 'I'! While chatting, type :q to exit, :mood to show your mood chart or :h to display this message again. Now, use WASD to move!"
    )
    clock.schedule_unique(end_message, 20.0)
    started = True
# Generate the rooms
room_map = generate_rooms(ROOMS)
# Create the doors and walls dictionary and initialize all frames to 0
for y in range(len(room_map)):
    for x in range(len(room_map[y])):
        if room_map[y][x] == 5:
            doors[2 * x * y - x**2] = 0
        if room_map[y][x] == 3:
            walls[2 * x * y - x**2] = 0
        # The 2xy-x² allows us to keep track of where the object is, for a unique key. (x + y would not work as that would cause (2, 3) to function trigger for (3, 2))

# Schedules the different loops to run 
clock.schedule_interval(game_loop, 0.02)
clock.schedule_interval(robot_interactions, 0.05)
clock.schedule_interval(adjust_wall_transparency, 0.05)
clock.schedule_interval(open_doors, 0.05)
clock.schedule_interval(exercise_loop, 0.05)
clock.schedule_interval(pause_loop, 0.05)
pgzrun.go()
