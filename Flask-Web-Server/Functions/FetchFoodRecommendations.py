import googlemaps
from datetime import datetime
import random
from inspect import getsourcefile
import os.path
import sys


from NLPHelpers import text_analysis

def FetchFoodRecommendations(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    cuisine = text_analysis.find_entity_key(entities, "RestaurantReservation.Cuisine")[0]["entity"]

    query = ""
    if cuisine == "Not found":
        cuisine = ""
        query = "restaurant"
    else:
        query = cuisine + " restaurant"



    gmaps = googlemaps.Client(key='AIzaSyArwvSObBGbUyLtagHAiI8Xv_rfdrcNzaQ')

    # Geocoding an address
    # geocode_result = gmaps.geocode('50 ')

    # Look up an address with reverse geocoding
    # reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

    # Request directions via public transit
    places = gmaps.places(query, location=(51.5033640, -0.1276250), radius=1000)
    #
    # location=None, radius=None, language=None,
    #            min_price=None, max_price=None, open_now=False, type=None, region=None,
    #            page_token=None


    if places["status"] == "ZERO_RESULTS":
        return {"follow_up":False, "response":"I could not find any " + str(cuisine) + " places to eat within 1000 meters of you.", "store":False }
    else:
        results = places["results"]

        random_result = None
        while True:

            random_result = random.choice(results)
            rating = float(random_result["rating"])
            if float(sentiment["score"]) < 0.2:
                if rating > 3:
                    continue
                else:
                    response = "Okay, I found a pretty poor " + query+" rated only" + str(random_result["rating"]) + " stars called " + random_result["name"] + " not too far from you."

            else:
                if rating < 3:
                    continue
                else:
                    response = "Okay, I found a "+ query+" rated " + str(random_result["rating"]) + " stars called " + random_result["name"] + " not too far from you."

            break



    return {"follow_up" : False, "response" :response, "store": False}
