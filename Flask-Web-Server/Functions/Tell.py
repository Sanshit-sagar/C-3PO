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
third_person_words = ["he", "she", "her", "his", "she", "they", "their", "himself", "herself" ]
second_person_words = ['you', "you", "your", "your", "you guys", "your", "yourself", "yourself"]

def Tell(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    person_name = text_analysis.find_entity_key(entities, "Tell.Person")[0]["entity"]
    tell_statement = text_analysis.find_entity_key(entities, "Tell.Statement")[0]["entity"]





    if person_name == "Not found":
        return {"follow_up":False, "response": "Who do you want to tell that to?", "store": False, "bing_entity_name":needed_from_bing, "request": request}

    elif tell_statement == "Not found":
        return {"follow_up":False, "response": "What do you want me to tell " + str(person_name), "store": False, "bing_entity_name":needed_from_bing, "request": request}
    else:
        #recieved all intents
        resp_string = "Yo " + person_name + ", " + second_person(tell_statement)
        return {"follow_up": False, "response": resp_string, "store" : True}



def second_person(third_person):

    t = third_person.lower()
    t = " " + t
    words = t.split(" ")

    second_person_array = []
    for word in words:
        if word in third_person_words:
            word_index = third_person_words.index(word)

            third_person_word_index = words.index(word)

            print(third_person_word_index)
            #because the arrays are same length
            second_person_array.append(second_person_words[word_index])

        else:
            second_person_array.append(word)

    second_person_setence = " ".join(second_person_array)


    replace = ["you is", "they are", " i "]
    replace_with = ["you are", "you guys are", " Steven "]

    for i in range(0, len(replace)):
        print(second_person_setence)
        second_person_setence = second_person_setence.replace(replace[i], replace_with[i])

    return second_person_setence
