import pycountry
from inspect import getsourcefile
import os.path
import sys
import json
from NLPHelpers import text_analysis
# import countries_python

def GetCountryCapital(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]

    with open('JSONData/countries.json') as f:
        country_data = json.load(f)
    countries_requested = []
    needed = []
    if(len(countries_requested)):
        return {"follow_up" : True, "response": response_string, "solved": False, "store": True, "bing_entity_name":needed_from_bing, "request": request}
    for country in pycountry.countries:
        if country.name.lower() in request.lower():
            countries_requested.append(country.name)
    capitals = []
    for country in countries_requested:
        for country_info in country_data:
            if country.lower() == country_info["name"]["common"].lower():
                capitals.append(country_info["capital"][0])
            if country_info == country_data[-1]:
                capitals.append("N/A")
    response_string = ""
    loop = 0
    for country in countries_requested:
        if capitals[loop] == "N/A":
            response_string = response_string + " I could not find the capital for " + str(country) + "."
        else:
            response_string = response_string + " The capital of " + str(country) + " is " + capitals[loop]

    needed_from_bing = []
    if len(response_string) < 1:
        needed_from_bing.append("Country")
        response_string = "Capital of which country?"
        return {"follow_up" : True, "response": response_string, "solved": False, "store": True, "bing_entity_name":needed_from_bing, "request": request}

    return {"follow_up" : False, "response": response_string, "solved": True, "store": True, "bing_entity_name":needed_from_bing, "request": request}
