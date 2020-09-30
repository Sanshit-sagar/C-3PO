
import time

def Doubt(params):

    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]

    if len(context) > 0:
        last_request = context[-1]
        if(last_request["isQuestion"]==False):
            response = "Is that a question, an answer? Babe youre confusing me haha"
            return {"response": response, "follow_up": False, "store": False}
        request_time = last_request["time"]
        ts = time.time()
        difference = ts - request_time

        if difference > 20:
            #no memory!
            return {"response": "What?", "follow_up": False, "store": False, "mood": "confused"}

        else:
            response = getRes(last_request["request"])
            return {"response": response, "follow_up": False, "store": False}
        #{"id": r.id, "request":r.request, "time":r.time, "sentiment":r.sentiment, "solved":r.solved, "stored": r.stored}

    else:

        return {"response": "What?", "follow_up": False, "store": False}

def getRes(request):
    #RANDOMISE RESPONSES FOR DOUBT HERE
    response = "Ummm...I am pretty sure about that"
    return response
    # return {"response": response, "follow_up": False, "store": False}
