from NLPHelpers import text_analysis


def HelpWithLuggage(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]

    language_code = text_analysis.find_entity_key(entities, "language")[0]["entity"]
    luggage_states = text_analysis.find_entity_key(entities, "TravelAssistent.LuggageType")


    main_state = None
    for state in luggage_states:
        if state["entity"] == "Not found":
            pass
        else:
            main_state = state["entity"]


    if main_state is None:
        #user did not put in a state of luggage
        if language_code == "Not found":
            return {"response": "I need to know if your luggage is lost or broken", "follow_up": True,  "store": False}
        else:
            return {"response": "I need to know if your luggage is lost or broken", "language":language_code, "follow_up": True,  "store": False}

    else:
        if language_code == "Not found":

            return {"response": "I can help you with your " + main_state + " luggage. Do you have a baggage tag?", "follow_up": True, "next_step":"CheckBaggageTag", "store": False}

        else:
            return {"response": "I can help you with your " + main_state + " luggage. Do you have a baggage tag?",  "language":language_code, "follow_up": True, "next_step":"CheckBaggageTag",  "store": False}
