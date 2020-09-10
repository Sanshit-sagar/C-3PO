import time

def Repeat(params):

    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]

    if len(context) > 0:
        last_request = context[-1]

        request_time = last_request["time"]
        ts = time.time()
        difference = ts - request_time

        if difference > 20:
            #no memory!
            return {"response": "What?", "follow_up": False, "store": False, "mood": "confused"}

        else:
            response = getRes(last_request["request"], last_request["response"])
            return {"response": response, "follow_up": False, "store": False}
        #{"id": r.id, "request":r.request, "time":r.time, "sentiment":r.sentiment, "solved":r.solved, "stored": r.stored}

    else:
        # response = getRes(last_request["request"])
        return {"response": "What??", "follow_up": False, "store": False}

def getRes(request, response):
    #RANDOMISE RESPONSES FOR DOUBT HERE
    response = "I said " + str(response) + ". Are you deaf?"
    return response
    # return {"response": response, "follow_up": False, "store": False}
