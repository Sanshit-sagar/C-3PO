import datetime
import time
from time import sleep
from geopy.geocoders import Nominatim
import pyowm
import reverse_geocoder as rg
import random
import dateutil.parser as parser
import dateparser
import requests
from NLPHelpers import text_analysis

def WeatherGetForecast(params):

    entities = params["entities"]
    sentiment = params["sentiment"]
    request = params["request"]

    mood = params["mood"]


    ## TODO: Check if apis are online

    dates = text_analysis.find_entity_key(entities, "builtin.datetimeV2.date")

    if(dates[0]["entity"]=="Not found"):
            print("inside if")
            date = datetime.datetime.now().isoformat()
    else:
        try:
            date_dict = dates[0]["entity"]
            date = date_dict['value']
            date = parser.parse(date).isoformat()
        except Exception as e:
            #print(e)
            return {"response":"Oh man I'm terrible with days, what date is that?", "request": request, "follow_up":"false", "store":"false", "solved":"false"}
            #"true", "context":{"needs":["builtin.datetimeV2.date"], "entities":entities, "intent_name":"Weather.GetForecast"}}

    locations = text_analysis.find_entity_key(entities, "Weather.Location")
    if(locations[0]["entity"]=="Not found"):
        location = ""
        words = request.split(" ")
        if("in" in words or "on" in words or "at" in words):
            return {"response":"uhhhhhh, I'm going to blame not knowing this one on the obscurity of that location.", "request": request, "follow_up":"false", "store":
            "false", "solved":"false"}
    else:
        location = locations[0]["entity"]

    return GetTemperature(date, location, request)

def GetTemperature(date, location, request):
    owm = pyowm.OWM('f6afeb7ec6fbd385727c50ee1900aaab')
    geolocator = Nominatim()
    #print(date + ", " + location)
    if(location==""):
        #print("entering the correct for loop")
        observation = owm.weather_at_place("Singapore, Singapore")
        w = observation.get_weather()
        return returnTemp(w, request)
    else:
        g = geolocator.geocode(location, timeout=10)

    try:
        latitude = float(g.latitude)
        longitude = float(g.longitude)
    except(AttributeError):
        return {"response":"Hmmm I dont really recognize that place to be honest", "request": request, "follow_up":"false", "store":"false", "solved":"false"}

    curr_date = datetime.datetime.now().isoformat()[0:10]
    iso_date = date
    date = date[0:10]
    if(date==curr_date):
        observation = owm.weather_at_coords(latitude, longitude)
        w = observation.get_weather()
        return returnTemp(w, request)
    else:
        return GetForecast(iso_date, latitude, longitude, time, request)


def returnTemp(w, request):
    temp_stats = w.get_temperature('celsius')
    temp_return = get_temp(temp_stats)

    status = str(w.get_status())
    status_return = get_status(status)

    humidity_stats = str(w.get_humidity())
    hum_return = get_hum(humidity_stats)

    ## TODO: make a get_wind method
    #wind_stats = w.get_wind()
    #wind_speed = str(wind_stats['speed'])
    #wind_dir = str(wind_stats['deg'])
    #" percent and the wind is blowing at a speed of: " + wind_speed +
    #" at " + wind_dir + " degrees from North.")

    result = status_return + " " + temp_return + " " + hum_return
    return {"response":result, "request": request, "follow_up":"false", "store":"false"}

def get_temp(temp_stats):
    temp_high = str(round(temp_stats['temp_max'], 0))
    temp_low = str(round(temp_stats['temp_min'], 0))
    temp_now = str(round(temp_stats['temp'], 0))
    if(temp_stats['temp_max']-temp_stats['temp_min']<3):
        temp_return = ("The temperature is " + temp_now + " and it looks like its going to stay that way.")
    else:
        temp_return = ("The temperature is " + temp_now + " with a high today of " + temp_high + "and a low of " + temp_low + ".")
    return temp_return

def get_hum(humidity_stats):
    to_ret_hum = random.randint(0, 2)
    if(to_ret_hum == 0):
        hum_return = ("The current humidity levels are at: " + humidity_stats)
    else:
        hum_return = ""
    return hum_return

def get_status(status):
    clear_arr = ["oooh, looks like there is some clarity in the sky", "chance of some sunny sunshine, babe", "there ain't nothing to complain about, the skies are as clear as my mind.",
    ("50 percent chance of some sunshine, " + str(random.randint(75, 100)) + " chance of clear skies, and a hundred percent chance of me liking it."), "sunny, sunny, and some happiness."]
    rain_arr = ["it's pouring out there dawg, watch out!", "pitter patter pitter patter - that's morse code for rain.",
    "its coming down, looks like someone up there is crying their eyes out.", "rain, rain and more rain. no me gusta!"]
    wind_arr = ["oh wow, it's windy out there.", "be prepared to be blown away, literally, by the wind.", "some bold people are out there, but even bolder winds for sure.",
    "The winds might blow you away to neverland, be careful!", "winds here, winds there, winds everywhere."]
    snow_arr = ["brrrr. its chilly and snowy, I couldn't survive out there.", "oh my, looks like its weather for the polar bears, its snowing.",
    "You might be able to make some snowmen if youre adventurous enough.", "snow snow snow and more snow."]
    clouds_arr = ["I see some puffy clouds up in the sky.", "Some clouds are floating around, bonus points if you spot the sun.",
    "oh man, the clouds will be hiding your view.", "cloudy as can be."]

    status_response = {
        'Clear': clear_arr,
        'Rain': rain_arr,
        'Snow': snow_arr,
        'Wind': wind_arr,
        'Clouds': clouds_arr
        }

    custom_resp_statuses = ['Clear', 'Rain', 'Snow', 'Wind', 'Clouds']

    if(status in custom_resp_statuses):
        status_arr = status_response[status]
        rand_status_resp = random.randint(0, len(status_arr)-1)
        status_return = (status_arr[rand_status_resp])
    else:
        status_return = "I see some " + status

    return status_return

def GetForecast(date, latitude, longitude, time, request):
    API_KEY = "221b5387eb43aa94b3bcd2ee8bc3a24e"

    latitude = str(latitude)
    longitude = str(longitude)
    search_date = str(date)
    option_list = "exclude=currently,minutely,hourly,alerts&amp;units=si"

    response = requests.get("https://api.darksky.net/forecast/"+API_KEY+"/"+latitude+","+longitude+","+search_date+"?"+option_list)

    daily_dict = response.json()['daily']
    data = daily_dict['data'][0]
    sum = str(data['summary'])
    maxx = round(((data['apparentTemperatureMax']- 32) * 5.0/9.0), 0)
    minn = round(((data['apparentTemperatureMin']- 32) * 5.0/9.0), 0)
    temp_max = str(maxx)
    temp_min = str(minn)
    humidity = str(data['humidity'])

    to_ret = (sum + "," + "The temperature will range from " + temp_min + " to " + temp_max + ". The humidity levels are projected to be " + humidity + ".")
    return {"response":to_ret, "request": request, "follow_up":"false", "store": "false", "solved":"true"}
