from datetime import datetime

def GetTime(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    t = TimeInWords2()
    return t.caltime()

class TimeInWords2():
    def __init__(self):
        self.words=["one", "two", "three", "four", "five", "six", "seven", "eight","nine",
       "ten", "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen",
       "seventeen", "eighteen", "nineteen", "twenty", "twenty one",
       "twenty two", "twenty three", "twenty four", "twenty five",
       "twenty six", "twenty seven", "twenty eight", "twenty nine", "thirty", "thirty one", "thirty two", "thirty three", "thirty four", "thirty five", "thirty six", "thirty seven", "thirty eight",
       "thirty nine", "forty", "forty one", "forty two", "forty three", "forty four", "forty five", "forty six", "forty seven", "forty eight", "forty nine",
       "fifty", "fifty one", "fifty two", "fifty three", "fifty four", "fifty five", "fifty six", "fifty seven", "fifty eight", "fifty nine"]




    def caltime(self):
        dd=datetime.now()
        hrs = dd.hour
        mins = dd.minute
        header="It is "
        msg=""
        ampm = "AM"
        if (hrs > 12):
            ampm = "PM"
            hrs=hrs-12
        if (mins == 0):
            hr = self.words[hrs-1]
            msg=header + hr + " o'clock " + ampm + "."
        else:
            hr = self.words[hrs-1]
            mn =self.words[mins-1]
            msg = header + hr + " " + mn + " " + ampm + "."
        needed_from_bing = []
        return {"follow_up": False, "response": msg, "store": False, "bing_entity_name":needed_from_bing}
# print(GetTime())
