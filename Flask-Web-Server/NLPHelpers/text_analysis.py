from NLPHelpers import custom_luis as luis
import string
import requests
import json
import time
import os

app_key = ""
sub_key = ""

def train():

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": sub_key#""
    }

    url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/" + str(app_key) + "/versions/0.1/train"

    r = requests.post(url, headers=headers)
    # print(r.content)
    print("Trained Data: " + str(r.content))

def add_intent_utterence(utterance, intent):
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": sub_key#"
    }

    url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/" + str(app_key) + "/versions/0.1/examples"
    # POST the request
    data = [
	{
		"text": utterance,
		"intentName": intent
	}
    ]
    r = requests.post(url, data=json.dumps(data), headers=headers)
    # print(r.content)
    print("added new utterance with response: " + str(r.content) + "... training now")
    train()

def find_entity_key(entities_array, key):
    entities = entities_array
    # start_index = None
    for entity in entities:
        if str(entity.type) == "builtin.currency":
            start_index = entity.start_index
            end_index = entity.end_index

            for entity2 in entities:
                if str(entity2.type) == "builtin.number" and (int(entity2.start_index) == int(start_index) or int(entity2.end_index) == int(end_index)):
                    del entities[entities.index(entity2)]


        if str(entity.type) == "builtin.percentage":
            start_index = entity.start_index
            end_index = entity.end_index

            for entity2 in entities:
                if str(entity2.type) == "builtin.number" and (int(entity2.start_index) == int(start_index) or int(entity2.end_index) == int(end_index)):
                    del entities[entities.index(entity2)]

    return_array = []
    for entity in entities:
        if str(entity.type) == str(key):
            # print(entity.resolution["values"])
            print(entity)
            # if key == "builtin.number" or key == "builtin.currency" or key == "builtin.percentage" or key == "restaurantReservation.Cuisin":
            if entity.resolution is None or key == "builtin.number":
                return_array.append({"entity": entity.entity, "role": entity.role})
                # return entity.resolution["value"]
            else:
                if entity.resolution is None:
                    return_array.append({"entity": entity.resolution["values"][0], "role": entity.role})
                    # return {"entity": entity.entity, "role":entity.role}#entity.entity
                else:
                    return_array.append({"entity": entity.resolution["values"][0], "role": entity.role})
                    # return {"entity": entity.entity, "role":entity.role}#entity.resolution["values"][0]
        #
        # if entity == entities[-1]:
        #     return "Not found"

    if len(return_array) < 1:
        return [{"entity": "Not found", "role":None}]
    else:
        return return_array

    return [{"entity": "Not found", "role":None}]

def find_entity_roles_for_key(entities_array, key):
    entities = entities_array
    # start_index = None
    for entity in entities:
        if str(entity.type) == "builtin.currency":
            start_index = entity.start_index
            end_index = entity.end_index

            for entity2 in entities:
                if str(entity2.type) == "builtin.number" and (int(entity2.start_index) == int(start_index) or int(entity2.end_index) == int(end_index)):
                    del entities[entities.index(entity2)]


        if str(entity.type) == "builtin.percentage":
            start_index = entity.start_index
            end_index = entity.end_index

            for entity2 in entities:
                if str(entity2.type) == "builtin.number" and (int(entity2.start_index) == int(start_index) or int(entity2.end_index) == int(end_index)):
                    del entities[entities.index(entity2)]

    for entity in entities:
        if str(entity.type) == str(key):
            # print(entity.resolution["values"])

            if key == "builtin.number" or key == "builtin.currency" or key == "builtin.percentage":
                return entity.resolution["value"]
            else:
                if entity.resolution is None:
                    return entity.entity
                else:
                    return entity.resolution["values"][0]
        if entity == entities[-1]:
            return "Not found"

    return "Not found"


def analyze_text(query):
    l = luis.Luis(url='https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/' + str(app_key) + '?subscription-key=' + str(sub_key) + '&verbose=true&timezoneOffset=0&q=')

    user_request = query#input("What do you want to do? ")
    r = l.analyze(user_request)

    return r
    
    #
    # if r.best_intent().intent == "None":
    #     add_to = "No strong corrolation, highest found: " + str(r.best_intent().intent) + " for query: '" + str(user_request) + "'. Press enter, or say cancel to ignore this")
    #
    #     if add_to == "cancel":
    #         pass
    #
    #     elif len(add_to) < 1:
    #         add_intent_utterence(user_request, str(r.best_intent().intent))
    #     else:
    #         add_intent_utterence(user_request, add_to)
