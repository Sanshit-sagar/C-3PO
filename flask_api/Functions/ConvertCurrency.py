from forex_python.converter import CurrencyRates

def ConvertCurrency(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]

    
    print(entities)
    print("yoohooo")
    if "currency-name" in entities and "currency-name1" in entities:
        if entities["currency-name1"] is None and entities["currency-name"] is not None:
             return {"user_request":reqest,  "response":"Which currency do you want to convert " + str(entities["currency-name"]) + " to?", "follow_up":"true"}

        elif entities["currency-name"] is None and entities["currency-name1"] is not None:
            return {"user_request":request,  "response":"Which currency do you want to convert " + str(entities["currency-name1"]) + " to?", "follow_up":"true"}

        elif entities["currency-name"] is None and entities["currency-name1"] is None:
            return {"user_request":request,  "response":"Which currencies do you want to convert?" + str(entities["currency-name1"]) + " to?", "follow_up":"true"}

        else:
            c = CurrencyRates()
            rate = c.get_rate(entities["currency-name"], entities["currency-name1"])
            amount = 1
            if "amount" in entities:
                if len(entities["amount"]) > 0:
                    amount = float(entities["amount"])

            conversion = amount * rate
            return {"response": str(amount) + " " + entities["currency-name"] + " is " + str(conversion) + " " + entities["currency-name1"], "user_request": request, "follow_up" : False}

    else:
        return {"user_request":request,  "response":"Uh oh, something went wrong.", "follow_up":"false"}
