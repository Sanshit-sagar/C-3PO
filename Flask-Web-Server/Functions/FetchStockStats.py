import requests
from datetime import date, timedelta

base_url = "https://www.alphavantage.co/query?"

def FetchStockStats(params):
    entities = params["entities"]
    request = params["request"]

    stock_symbol = text_analysis.find_entity_key(entities, stock_symbol)
    indicator = text_analysis.find_entity_key(entities, indicator)
    if(indicator=="RSI"):
        result = get_rsi(stock_symbol)
    if(indicator=="SMA"):
        result = get_sma(stock_symbol)
    if(indicator=="STOCH"):
        result = get_stoch(stock_symbol)
    if(indicator=="ADX"):
        result = get_adx(stock_symbol)
    if(indicator=="MOM"):
        result = get_mom(stock_symbol)
    if(indicator=="MACD"):
        result = get_macd(stock_symbol)
    if(indicator=="ROC"):
        result = get_roc(stock_symbol)
    if(indicator=="BBANDS"):
        result = get_bbands(stock_symbol)

    return {"response":result, "user_request": request, "follow_up":"false", "store": "false"}


def tech_anal(r, method_name):
    try:
        data = r.json()
        tech_analysis = data[str('Technical Analysis: ' + method_name)]
        yesterday = date.today() - timedelta(1)
        return tech_analysis[yesterday.isoformat()[0:10]]
    except Exception as e:
        print("Servers are being refreshed...try again")

def get_rsi(company_name):
    method_name = "RSI"
    function_name = "function=RSI"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    time_period = "&time_period=14"
    series_type = "&series_type=close"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + time_period + series_type + api_key)
    current_rsi = tech_anal(r, method_name)
    rsi = current_rsi['RSI']
    to_ret = ("Simple Moving Average for " + company_name + " is " + rsi)
    return to_ret

def get_sma(company_name):
    method_name = "SMA"
    function_name = "function=SMA"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    time_period = "&time_period=14"
    series_type = "&series_type=close"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"

    r = requests.get(base_url + function_name + company_list + interval + time_period + series_type + api_key)
    current_sma = tech_anal(r, method_name)
    sma = current_sma['SMA']
    to_ret = ("Relative Strenght index for " + company_name + " is " + sma)
    return to_ret

def get_stoch(company_name):
    method_name = "STOCH"
    function_name = "function=STOCH"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + api_key) #time_period + series_type + api_key)
    current_stoch = tech_anal(r, method_name)
    slowk = current_stoch['SlowK']
    slowd = current_stoch['SlowD']
    to_ret = ("Stochastic Oscillator Slowk Value for " + company_name + " is " + slowk + " and the SlowD Value is " + slowd)
    return to_ret

def get_adx(company_name):
    method_name = "ADX"
    function_name = "function=ADX"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    time_period = "&time_period=14"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + time_period + api_key)
    current_adx = tech_anal(r, method_name)
    adx = current_adx['ADX']
    to_ret = ("Average Directional Movement Index for " + company_name + " is " + adx)
    return to_ret

def get_mom(company_name):
    method_name = "MOM"
    function_name = "function=MOM"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    time_period = "&time_period=14"
    series_type = "&series_type=close"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + time_period + series_type + api_key)
    current_mom = tech_anal(r, method_name)
    mom = current_mom['MOM']
    to_ret = ("Momentum value for " + company_name + " is " + mom)
    return to_ret

def get_macd(company_name):
    method_name = "MACD"
    function_name = "function=MACD"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    series_type = "&series_type=close"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + series_type + api_key)
    current_macd = tech_anal(r, method_name)
    macd = current_macd['MACD']
    to_ret = ("Moving Average Convergence / Divergence value for " + company_name + " is " + macd)
    return to_ret

def get_roc(company_name):
    method_name = "ROC"
    function_name = "function=ROC"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    time_period = "&time_period=14"
    series_type = "&series_type=close"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + time_period + series_type + api_key)
    current_roc = tech_anal(r, method_name)
    roc = current_roc['ROC']
    to_ret = ("Rate of Change for " + company_name + " is " + roc)
    return to_ret

def get_bbands(company_name):
    method_name = "BBANDS"
    function_name = "function=BBANDS"
    company_list = "&symbol=" + company_name
    interval = "&interval=daily"
    time_period = "&time_period=14"
    series_type = "&series_type=close"
    api_key = "&apikey=" + "8B0ZCK5PZWP3QME9"
    r = requests.get(base_url + function_name + company_list + interval + time_period + series_type + api_key)
    current_bbands = tech_anal(r, method_name)
    lower_bband = current_bbands['Real Lower Band']
    middle_bband = current_bbands['Real Middle Band']
    upper_bband = current_bbands['Real Upper Band']
    to_ret = ("The Bollinger Bands for ACN are, Lower band: " + lower_bband + " Middle band: " + middle_bband + " Upper Band: " + upper_bband)
    return to_ret
