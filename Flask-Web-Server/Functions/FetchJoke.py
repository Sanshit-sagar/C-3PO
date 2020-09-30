import requests
import random
from bs4 import BeautifulSoup


from inspect import getsourcefile
import os.path
import sys
from NLPHelpers import text_analysis


host = "https://top-funny-jokes.com/"

def FetchJoke(params):
    
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    joke_type = text_analysis.find_entity_key(entities, "joke_type")[0]["entity"]
    if joke_type == "Not found" or joke_type is None:
        joke_type = "bad"


    r = requests.get(host)
    soup = BeautifulSoup(r.text, "lxml")
    list = soup.find_all("a")
    href = ""
    keyword2 = joke_type

    for a in list:
        category = a.text.lower()
        keyword1 = "jokes"
        if keyword1 and keyword2 in category:
            href = a.get("href")
            break
    if keyword2.lower() in href.lower() and keyword1.lower() in href.lower():
        r = requests.get(href)
        soup = BeautifulSoup(r.text, "lxml")
        lis = soup.find_all("li")
        candidate = []
        for li in lis:
            if li.has_key('class'):
                pass
            else:
                candidate.append(li.text)
        return {"response": random.choice(candidate), "follow_up": False, "store": False}

    else:
        return {"response": "I couldn't find a " + str(joke_type) + " joke. Pick another genre.", "follow_up": False, "store": False}
