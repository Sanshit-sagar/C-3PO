from bs4 import BeautifulSoup
import random
import requests

from inspect import getsourcefile
import os.path
import sys
current_path = os.path.abspath(getsourcefile(lambda:0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]

sys.path.insert(0, parent_dir)

from NLPHelpers import text_analysis
needed_from_bing = []

def Greet(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    question_word = text_analysis.find_entity_key(entities, "question_word")[0]["entity"]


    if question_word == "Not found":
        voice_response = "Hello."
    elif question_word == "what":
        voice_response = "I'm just sitting here, waiting to help you."
    elif question_word == "how":
        voice_response = "I am well. And you?"
    # stop_listening()
    elif question_word is None:
        voice_response = "Greetings."


    return {"follow_up":False, "response":voice_response, "store":False, "store": False, "bing_entity_name":needed_from_bing, "request": request}
    # voice.speak_text(voice_response)
