from bs4 import BeautifulSoup
import random
import requests

from inspect import getsourcefile

from NLPHelpers import text_analysis


def OnDeviceAreYouListening(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    # question_word = text_analysis.find_entity_key(entities, "question_word")["entity"]
    #
    #
    # if question_word == "Not found":
    #     voice_response = "Hello."
    # elif question_word == "what":
    #     voice_response = "I'm just sitting here, waiting to help you."
    # elif question_word == "how":
    #     voice_response = "I am well. And you?"
    # # stop_listening()
    # elif question_word is None:
    #     voice_response = "Greetings."
    #

    return {"follow_up":False, "response":"What's up? I can hear you.", "store":True}
    # voice.speak_text(voice_response)
