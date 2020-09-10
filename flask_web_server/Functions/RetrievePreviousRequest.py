from bs4 import BeautifulSoup
import random
import requests

from inspect import getsourcefile
import os.path
import sys
import datetime
current_path = os.path.abspath(getsourcefile(lambda:0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]
import dateutil.parser as parser

sys.path.insert(0, parent_dir)

from NLPHelpers import text_analysis

epoch = datetime.datetime(1970, 1, 1)


def RetrievePreviousRequest(params):

    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    print(30*"--")
    print(context)

    dates = text_analysis.find_entity_key(entities, "builtin.datetimeV2.datetime")
    numbers = text_analysis.find_entity_key(entities, "builtin.number")
    number = None
    timestamp = None
    if dates[0]["entity"] == "Not found":
        if numbers[0]["entity"] == "Not found":
            pass
        else:
            number = numbers[0]["entity"]
    else:
        timestamp = parser.parse(dates[0]["entity"]).isoformat()
        myformat = "%Y-%m-%dT%H:%M:%S"
        mydt = datetime.datetime.strptime(timestamp, myformat)
        val = (mydt - epoch).total_seconds()
        timestamp = val


    if timestamp is not None:
        smallest_time_from = 10000000
        closest_request = None
        for r in context:
            looking_For = timestamp
            request_time = r.time
            difference = ts - request_time
            # if (difference * difference) < 100
            time_from = difference * difference

            if time_from < smallest_time_from:
                closest_request = r

    elif number is not None:
        try:
            closest_request = context[-1]
        except Exception as e:
            response = "You have asked no questions yet."
            return {"follow_up":False, "response":response, "store":False, "solved":False}

    else:
        try:
            closest_request = context[-1]
        except Exception as e:
            response = "You have asked no questions yet."
            return {"follow_up":False, "response":response, "store":False, "solved":False}
        #neither

    if closest_request["solved"] == "true":
        response = "Your closest request to that time was asking for " + closest_request["request"] + ". And I was able to solve this request."
    else:
        response = "Your closest request to that time was asking for " + closest_request["request"] + ". And I was unable to solve this request."

    return {"follow_up":False, "response":response, "store":False, "solved":True}
    # voice.speak_text(voice_response)
