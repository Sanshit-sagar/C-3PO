from NLPHelpers import text_analysis


def CheckBaggageTag(params):
    entities = params["entities"]

    ack = text_analysis.find_entity_key(entities, "acknowledgements")[0]["entity"]
    if ack == "Not found":
        return {"response": "I need to know if your luggage has a tag", "follow_up": False,  "store": False}


    elif ack == "confirm":
        return {"response": "Okay, your baggage has a tag! Great!", "follow_up": False,  "store": False}

    elif ack == "cancel":
        return {"response": "You need your tag.", "follow_up": False,  "store": False}
