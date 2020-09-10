from google_tool import GoogleSearch
import requests
from bs4 import BeautifulSoup
import json


question = "Why does god exist?"
response = GoogleSearch().search(question)

for result in response.results:
    multi = False
    print(result.url)
    skip = False
    with open("../JSONData/question_answer.json") as json_file:
        request_history = json.load(json_file)
        for obj in request_history:
            if result.url == obj["url"]:
                skip = True

    if skip is True:
        print("Already looked at " + str(result.url) + " skipping.")
        continue
    request = requests.get(result.url)
    response = request.text
    soup = BeautifulSoup(response, "lxml")
    paragraphs = soup.find_all('p')
    ideal = ""
    combine = ""
    bad = False
    for p in paragraphs:
        text = p.text
        print(text)
        if len(combine) < 1:
            i = input("\nIs this a good initial part of an answer?\n")
        elif len(combine) > 1:
            i = input("\nIs this a good second part of answer?\n")

        if i == "bad":
            bad = True
            break
        if len(i) < 1:
            combine = combine + "\n" + text
            continue
            # break
            i = input("Press enter to finish at this part, or something else to keep adding to the answer.")
            if len(i) < 1:
                break
            multi = True
        else:
            #enter key pressed
            if len(combine) < 1:
                pass
            else:
                break


    if bad == True:
        continue

    with open("../JSONData/question_answer.json") as json_file:
        request_h = json.load(json_file)
        new_request = {
            "question":question,
            "answer":combine,
            "multi": multi,
            "url": result.url
        }
        request_h.append(new_request)
        json.dump(request_h, open("../JSONData/question_answer.json",'w'))

    print("Answer: " + str(combine))
