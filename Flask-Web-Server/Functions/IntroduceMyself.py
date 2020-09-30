from app import db
def IntroduceMyself(params):
    entities = params["entities"]
    print(entities)
    if "parsed_entities" in params:
        #do not use find by key if already parsed entities so just find in dictionary
        name = entities["Person"][0]["entity"]
        return {"follow_up":False, "response":"What a pleasure to know you, " + str(name) + ". Thanks for taking the time to meet me", "store": False, "bing_entity_name":[], "request": params["request"]}

    else:
        return {"follow_up":False, "respon":"Something went wrong.", "store":False, "bing_entity_name":[], "request":params["request"]}
