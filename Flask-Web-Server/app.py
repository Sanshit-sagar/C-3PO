from flask import Flask, request
from flask import jsonify
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

import os
import jsonpickle
import translate
import importlib
import datetime
import random
import json
import requests
import Functions
import time

from NLPHelpers import text_analysis
import psycopg2
from marshmallow_sqlalchemy import ModelSchema
import urllib.parse as urlparse

app = Flask(__name__)

minor_memory_span = 300
major_memory_span = 1000000

moods = ["angry", "annoyed", "curious", "upset", "sorry", "humorous", "frantic", "reflective", "sympathetic", "empathetic"]
sarcastic_intents = ["SuicidalHelp"]

major_intents = ["SuicidalHelp"]

happy_intents = ["SmalltalkInsult", "SmalltalkCompliment", "Greet", "FetchJoke", "FetchLiquidStudioInformation"]
sad_intents = ["Doubt", "Repeat", "SuicidalHelp"]

bing_entity_intents = ["GetCountryCapital", "IntroduceMyself"]

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
api = Api(app)

class Client(db.Model):
    id = db.Column(db.String(), primary_key=True)
    identifier = db.Column(db.String())
    device = db.Column(db.String(80))
    request = db.Column(db.String())
    entities = db.Column(db.String())
    time = db.Column(db.BigInteger())
    sentiment = db.Column(db.String())
    solved = db.Column(db.String())
    stored = db.Column(db.String())
    response = db.Column(db.String())
    isQuestion = db.Column(db.String())
    lastMood = db.Column(db.String())


    def __init__(self, id, identifier, device, request, entities, time, sentiment, solved, stored, response, isQuestion, lastMood):
        self.id = id
        self.identifier = identifier
        self.device = device
        self.request = request
        self.time = time
        self.sentiment = sentiment
        self.solved = solved
        self.stored = stored
        self.response = response
        self.isQuestion = isQuestion
        self.lastMood = lastMood

    def __repr__(self):
        return '<ClientId %r>' % self.id

class ClientSchema(ModelSchema):
    class Meta:
        model = Client

class ClientResource(Resource):
    def get(self, client_id):
        client = Client.query.get(client_id)
        return ClientSchema().dump(client)

    def put(self, client_id):
        client = Client.query.get(client_id)
        ClientSchema().load(request.form, instance=client, session=db.session)
        db.session.commit()
        return 'updated'

    def delete(self, client_id):
        client = Client.query.get(client_id)
        db.session.delete(client)
        db.session.commit()


class ClientListResource(Resource):
    def get(self):
        clients = Client.query.all()
        return ClientSchema(many=True).dump(clients)

    def post(self):
        client = ClientSchema().load(request.form, session=db.session).data
        db.session.add(client)
        db.session.commit()
        return 'created'

# db.drop_all()
# db.create_all()

@app.route('/')
def home():
    name = "hello"
    return name


@app.route("/follow_up", methods=["POST"])
def follow_up():

    past_requests = Client.query.filter_by(identifier = request.args["identifier"]).all()
    db.session.delete(past_requests[-1])
    db.session.commit()
    query = request.args["query"]
    intent_name = request.args["intent"]
    identifier = request.args["identifier"]

    if intent_name in bing_entity_intents:
        form_data = request.args#form.to_dict()
        print(30*"8")
        print(form_data)
        bing_entity_types = form_data["needed_from_bing"].split(",")
        print(bing_entity_types)
        print("got hrere 3")
        old_request = form_data["request"]
        entities = []
        new_entities = {}#request.body["current_entities"]
        words_in_query = query.split(" ")
        valid_entity = None

        if len(bing_entity_types) > 0:
            for word in words_in_query:
                print("Looking at word: " + word)
                try:
                    r = requests.get("https://api.cognitive.microsoft.com/bing/v7.0/entities?mkt=en-US",
                    headers={"Ocp-Apim-Subscription-Key":"98cd9906396946bd89dfa377ada8f767"}, params={"q": word})
                    resp = json.loads(r.text)
                    entities = resp["entities"]
                    values = entities["value"]

                    for value in values:
                        entity_type = value["entityPresentationInfo"]["entityTypeHints"][0]
                        for t in bing_entity_types:
                            print("Checking " + str(t) + " against " + str(entity_type))
                            if t == entity_type:
                                print("FOUND....")
                                # old_request = old_request + " " + word
                                valid_entity = word
                                new_e = {"entity":word, "role":None}
                                if entity_type in new_entities:
                                    new_entities[entity_type].append(new_e)
                                else:
                                    new_entities[entity_type] = [new_e]

                                break
                except Exception as e:
                    print(e)

        print("Found entity : " + str(valid_entity))
        if valid_entity is None:
            analysis = text_analysis.analyze_text(old_request)
            intent_name = analysis.best_intent().intent
            score = float(analysis.best_intent().score)
            sentiment = analysis.sentimentAnalysis
            question_words = text_analysis.find_entity_key(analysis.entities, "question_words")
            question = False
            if len(question_words) > 0:
                first_question_word = question_words[0]["entity"]
                if first_question_word is None or first_question_word == "Not found":
                    question = True

            if score < 0.3 and question is True:
                intent_name = "SearchWolfram"

            past_requests = Client.query.filter_by(identifier = request.args["identifier"]).all()
            print(30*"-")
            mood = calculate_mood(past_requests)
            name = 'Functions.' + intent_name.replace(".", "")
            imp = importlib.import_module(name)
            handle_function = getattr(imp, intent_name.replace(".", ""))
            params = {"entities": analysis.entities, "request":request.args["query"], "mood":mood, "sentiment": sentiment, "context": past_requests}
            result = handle_function(params)


            if "store" in result:
                pass
            else:
                result["store"] = False
            if "solved" in result:
                pass
            else:
                result["solved"] = True

            iddd = str(random.randint(0, 100000000))
            last_mood = mood
            if "mood" in result:
                last_mood["mood"] = result["mood"]

            if "next_step" in result:
                intent_name = result["next_step"]

            new_request = Client(iddd, request.args["identifier"], 'postman', intent_name, analysis.entities,
            int(time.time()), sentiment["score"], str(result["solved"]), str(result["store"]), str(result["response"]),
            str(question), str(last_mood) )
            db.session.add(new_request)
            db.session.commit()
            final_response = jsonify({"result":["", result["response"]], "store": result["store"], "solved": result["solved"], "follow_up":result["follow_up"], "mood": last_mood, "isQuestion": question, "sentiment_average": "N/A", "intent":intent_name,
            "needed_from_bing":result["bing_entity_name"], "request":result["request"]})
            final_response.headers.add('Access-Control-Allow-Origin', '*')
            final_response.headers.add("Access-Control-Allow-Credentials", "true");
            final_response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT");
            final_response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers");
            return final_response

        else:
            print("Running " + str(intent_name))
            past_requests = Client.query.filter_by(identifier = identifier).all()
            mood = calculate_mood(past_requests)
            name = 'Functions.' + intent_name.replace(".", "")
            imp = importlib.import_module(name)
            handle_function = getattr(imp, intent_name.replace(".", ""))
            params = {"entities": new_entities, "parsed_entities":True, "request":query, "mood":mood, "sentiment": "N/A", "context": past_requests}

            result = handle_function(params)
            if "solved" in result:
                pass
            else:
                result["solved"] = True# result["follow_up"]
            iddd = str(random.randint(0, 100000000))
            last_mood = mood
            response_prefix = ""
            if "mood" in result:
                last_mood["mood"] = result["mood"]
            if "next_step" in result:
                intent_name = result["next_step"]

            new_request = Client(iddd, identifier, 'postman', intent_name, new_entities, int(time.time()),
            0.0, str(result["solved"]), str(result["store"]), str(result["response"]), str("false"), str(last_mood) )
            db.session.add(new_request)
            db.session.commit()
            final_response = jsonify({"result":[response_prefix, result["response"]], "store": result["store"],
            "solved": result["solved"], "follow_up":result["follow_up"], "mood": last_mood, "isQuestion": False,
            "sentiment_average": 0.0, "intent":intent_name,
            "needed_from_bing":result["bing_entity_name"], "request":result["request"]})
            final_response.headers.add('Access-Control-Allow-Origin', '*')
            final_response.headers.add("Access-Control-Allow-Credentials", "true");
            final_response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT");
            final_response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers");
            return final_response
    else:
            analysis = text_analysis.analyze_text(query)
            intent_name = intent_name
            score = 1
            sentiment = analysis.sentimentAnalysis
            question_words = text_analysis.find_entity_key(analysis.entities, "question_words")

            past_requests = Client.query.filter_by(identifier = identifier).all()
            mood = calculate_mood(past_requests)
            name = 'Functions.' + intent_name.replace(".", "")
            imp = importlib.import_module(name)
            handle_function = getattr(imp, intent_name.replace(".", ""))


            params = {"entities": analysis.entities, "request":query, "mood":mood, "sentiment": sentiment,
            "context": past_requests}
            result = handle_function(params)
            if "solved" in result:
                pass
            else:
                result["solved"] = True# result["follow_up"]
            iddd = str(random.randint(0, 100000000))
            last_mood = mood
            if "mood" in result:
                last_mood["mood"] = result["mood"]

            if "next_step" in result:
                intent_name = result["next_step"]

            new_request = Client(iddd, identifier, 'postman', intent_name, analysis.entities,
            int(time.time()), sentiment["score"], str(result["solved"]), str(result["store"]),
            str(result["response"]), str("False"), str(last_mood) )
            db.session.add(new_request)
            db.session.commit()
            final_response = jsonify({"result":["", result["response"]], "store": result["store"],
            "solved": result["solved"], "follow_up":result["follow_up"], "mood": last_mood,
            "isQuestion": "False", "sentiment_average": "", "intent":intent_name,
            "needed_from_bing":[], "request":""})
            return final_response


@app.route("/translate", methods=["POST"])
def translate_now():

    to_language = request.args["to_language"]
    translations = translate.get_translation(request.args["query"], [to_language])
    translations = json.loads(translations)
    translated_text = translations[0]["translations"][0]["text"]
    response_prefix = ""
    final_response = jsonify({"result":[response_prefix, translated_text], "follow_up":False})

    return final_response

@app.route("/payload", methods=['POST'])
def show_payload():
    english_text = request.args["query"]
    if request.args["language"] != "en":
        translations = translate.get_translation(request.args["query"], ["en"])
        translations = json.loads(translations)
        english_text = translations[0]["translations"][0]["text"]

    if "voice_id" in request.args:
        if request.args["voice_id"] == "00000000-0000-0000-0000-000000000000":
            iddd = str(random.randint(0, 100000000))
            new_request = Client(iddd, request.args["identifier"], 'postman', "N/A", "",
            int(time.time()), 0.0, str("false"), str("false"),
            str("I am sorry, I don't believe we have met. What is your name?"), str(""), str(""))
            db.session.add(new_request)
            db.session.commit()
            final_response = jsonify({"result":["I am sorry, I don't believe we have met. What is your name?"],
            "store": False, "follow_up":True, "isQuestion": True, "needed_from_bing":["Person"], "intent":"IntroduceMyself",
            "needed_from_bing":["Person"], "request":english_text})
            return final_response

    analysis = text_analysis.analyze_text(english_text)

    intent_name = analysis.best_intent().intent
    score = float(analysis.best_intent().score)
    sentiment = analysis.sentimentAnalysis
    question_words = text_analysis.find_entity_key(analysis.entities, "question_words")
    question = False

    if len(question_words) > 0:
        first_question_word = question_words[0]["entity"]
        if first_question_word is None or first_question_word == "Not found":
            question = True

    if score < 0.3 and question is True:
        intent_name = "SearchWolfram"

    past_requests = Client.query.filter_by(identifier = request.args["identifier"]).all()
    mood_info = calculate_mood(past_requests)
    name = 'Functions.' + intent_name.replace(".", "")
    imp = importlib.import_module(name)
    handle_function = getattr(imp, intent_name.replace(".", ""))
    params = {"entities": analysis.entities, "request":english_text,
    "mood":mood_info, "sentiment": sentiment, "context": past_requests}
    result = handle_function(params)

    if "solved" in result:
        pass
    else:
        result["solved"] = True# result["follow_up"]

    iddd = str(random.randint(0, 100000000))
    response_language = request.args["language"]
    full_language_code = request.args["language"]
    last_mood = mood_info

    if "mood" in result:
        last_mood["mood"] = result["mood"]
    if "bing_entity_name" in result:
        pass
    else:
        result["bing_entity_name"] = []
    if "request" in result:
        pass
    else:
        result["request"] = ""
    if "store" in result:
        pass
    else:
        result["store"] = False

    if "language" in result:
        response_language = result["language"].split("-")[0]
        full_language_code = result["language"]

    new_request = Client(iddd, request.args["identifier"], 'postman', intent_name,
    analysis.entities, int(time.time()), sentiment["score"], str(result["solved"]),
    str(result["store"]), str(result["response"]), str(question), str(last_mood) )

    db.session.add(new_request)
    db.session.commit()
    response_prefix = ""
    resp_text = result["response"]

    if response_language != "en":
        translations = translate.get_translation(result["response"], [response_language])
        translations = json.loads(translations)
        native_tounge = translations[0]["translations"][0]["text"]
        resp_text = native_tounge

    final_response = jsonify({"result":[response_prefix, resp_text],
    "language": full_language_code, "store": result["store"], "solved": result["solved"],
    "follow_up":result["follow_up"], "mood": last_mood, "isQuestion": question,
    "sentiment_average": last_mood["avg_sentiment"], "intent":intent_name,
    "needed_from_bing":result["bing_entity_name"], "request":result["request"]})

    return final_response

def calculate_avg_sentiment(past_requests):
    if(len(past_requests)==0):
        return 0.5
    num_requests = len(past_requests)
    total_sentiment_score = 0
    for individual_request in past_requests:
        total_sentiment_score = total_sentiment_score + float(individual_request.sentiment)

    average_sentiment = float(float(total_sentiment_score)/(float(num_requests)))
    return average_sentiment

def calculate_solved_ratio(past_requests):
    if len(past_requests) == 0:
        return {"num_correct":0, "num_incorrect":0, "ratio":1}
    num_requests = len(past_requests)
    num_solved = 0
    for individual_request in past_requests:
        if(str(individual_request.solved).lower()=="true"):
            num_solved = num_solved + 1
    solved_ratio = float(float(num_solved)/float(num_requests))
    return {"num_correct":num_solved, "num_incorrect":(num_requests-num_solved), "ratio":solved_ratio}

def calculate_max_intent_hit(past_requests, time_frame):
    if len(past_requests) == 0:
        return {"name":None, "count": 0}
    intent_dict = {}
    for individual_request in past_requests:
        ts = time.time()
        request_time = individual_request.time
        difference = ts - request_time
        if(difference < time_frame):
            current_intent = individual_request.request
            if current_intent in intent_dict:
                intent_dict[current_intent] = intent_dict[current_intent] + 1
            else:
                intent_dict[current_intent] = 1

    max_intent_hits = 0
    max_intent_name = ''
    for intent_hits_key in intent_dict:
        intent_hits_item = intent_dict[intent_hits_key]
        if(intent_hits_item > max_intent_hits):
            max_intent_hits = intent_hits_item
            max_intent_name = intent_hits_key

    return {"name": max_intent_name, "count": max_intent_hits}

def calculate_mood(context):
        past_requests = context
        remembered_requests = []

        for r in past_requests:
            ts = time.time()
            request_time = r.time
            difference = ts - request_time
            intent_name = r.request
            if intent_name in major_intents:
                if difference < major_memory_span:
                    remembered_requests.append(r)
            else:
                if difference < minor_memory_span:
                    remembered_requests.append(r)

        avg_sentiment = calculate_avg_sentiment(remembered_requests)
        solved_ratio = calculate_solved_ratio(remembered_requests)
        max_intent = calculate_max_intent_hit(remembered_requests, 60)

        mood = "relaxed"
        if solved_ratio["ratio"] < 0.68:
            mood = "disapointed"
        num_correct = solved_ratio["num_correct"]
        num_incorrect = solved_ratio["num_incorrect"]


        if max_intent["count"] > 3:
            mood = "annoyed"

        return {"mood": mood, "correct": num_correct, "avg_sentiment": avg_sentiment,
        "incorrect": num_incorrect, "intent_hits":max_intent, "ratio":solved_ratio["ratio"]}


api.add_resource(ClientListResource, '/clients/')
api.add_resource(ClientResource, '/clients/<id>/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5432)
