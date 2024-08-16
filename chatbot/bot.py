###############
### IMPORTS ###
###############
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import re

#################
### FUNCTIONS ###
#################
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

#################
### VARIABLES ###
#################
CHAT_CORPUS = "chatbot/chat.txt"
chatbot = ChatBot("Chatpot")
trainer = ListTrainer(chatbot)
cleaned_corpus = remove_non_message_text(remove_chat_metadata(CHAT_CORPUS))

################
### TRAINING ###
################
trainer.train(cleaned_corpus)

##############################
### CHATBOT INITIALIZATION ###
##############################
exit_conditions = (":q", "quit", "exit")
print(f"🪴 Hi!!! Type :q, quit or exit to quit!")
while True:
    query = input("> ")
    if query in exit_conditions:
        break
    else:
        ans = chatbot.get_response(query)
        print(f"🪴 {ans}")