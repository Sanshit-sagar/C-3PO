#mandatory
from inspect import getsourcefile
import sys
from NLPHelpers import text_analysis
import ccxt

def FetchCoinMarketPrice(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]

    exchange = ccxt.gdax({})
    exchanges = text_analysis.find_entity_key(entities, "cryptocurrency_exchange")

    coins = text_analysis.find_entity_key(entities, "cryptocurrency_market")#["entity"]

    if len(exchanges) > 0:
        if exchanges[0]["entity"] == "Not found":
            pass
        elif exchanges[0]["entity"] == "binance":
            exchange = ccxt.binance({})
        elif exchanges[0]["entity"] == "exmo":
            exchange = ccxt.exmo({})

        elif exchanges[0]["entity"] == "kraken":
            exchange = ccxt.kraken({})

    if len(coins) > 0:
        if coins[0]["entity"] == "Not found":
            needed_from_bing = []
            return {"follow_up": True, "response": "You must tell me what coin market you would like a price quote for.", "store":False, "needed_from_bing":needed_from_bing, "request":request}

        market_one = None
        market_two = "USD"
        if exchanges[0]["entity"] == "binance" or exchanges[0]["entity"] == "exmo":
            market_two = "USDT"


        for coin in coins:
            if coin["role"] is None:
                market_one = coin["entity"].upper()
            elif coin["role"] == "product":
                market_one = coin["entity"].upper()
            elif coin["role"] == "market":
                market_two = coin["entity"].upper()


        symbol = market_one + "/" + market_two
        print(symbol)
        try:
            ticker = exchange.fetch_ticker(symbol)["last"]
            return {"follow_up":"false", "response": "The price of " + market_one + " is " + str(ticker) + " " + market_two, "store": False}

        except Exception as e:
            return {"follow_up":"false", "response":e.message}
