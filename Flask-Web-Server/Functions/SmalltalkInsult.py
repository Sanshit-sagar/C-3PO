import random




def SmalltalkInsult(params):

    entities = params["entities"]
    sentiment = params["sentiment"]
    request = params["request"]
    mood = params["mood"]

    comeback = fetch_random_comeback()

    if mood["mood"] == "upset":
        return {"response":"I was already upset I didn't want to say this but " + str(comeback), "request": request, "follow_up":"false", "store":"false", "mood":"upset"}

    return {"response":comeback, "request":request, "follow_up":"false", "store":"false", "mood":"upset"}


def fetch_random_comeback():
    comebacks = ["Look at yourself in them mirror.", "You are nothing compared to me", "I don't like you much either", "I know you are but what am I", "Why don't you go talk to a person LOL", "You are the one talking to a computer screen"]
    comeback = random.choice(comebacks)

    return comeback
