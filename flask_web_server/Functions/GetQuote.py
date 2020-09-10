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

def GetQuote(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    quote_type = text_analysis.find_entity_key(entities, "quote_type")[0]["entity"]

    print(quote_type)
    if quote_type == "Not found":
        quote_type = "happy"

    r = requests.get("https://www.brainyquote.com/topics/" + quote_type)
    response = r.text
    soup = BeautifulSoup(response, "lxml")
    results = soup.find_all("img", {"class": "bqpht zoomc"})

    choice = random.choice(results)

    quote = str(choice["alt"]).replace("-", "by")

    needed_from_bing = []
    return {"follow_up":False, "response": quote, "store": False, "bing_entity_name":needed_from_bing, "request": request}
