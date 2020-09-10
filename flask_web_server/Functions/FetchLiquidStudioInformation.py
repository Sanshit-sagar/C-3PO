from inspect import getsourcefile
import os.path
import sys

from NLPHelpers import text_analysis

def FetchLiquidStudioInformation(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    exhibit = text_analysis.find_entity_key(entities, "liquid_studio_exhibits")["entity"][0]

    if exhibit["entity"] == "Not found":
        return {"follow_up":True, "store": True, "response": "Which exhibit would you like to know more about?"}
    else:
        return {"follow_up":False, "store": True, "response": "I can tell you all there is to know about " + exhibit + ". Don't worry."}
