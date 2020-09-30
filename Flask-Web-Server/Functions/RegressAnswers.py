import json

from itertools import chain
from nltk.corpus import wordnet

# synonyms = wordnet.synsets(text)
# lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))

def count_occurrences(params):
    entities = params["entities"]
    request = params["request"]
    sentiment = params["sentiment"]
    context = params["context"]
    return sentence.lower().split().count(word)



with open("../JSONData/question_answer.json") as json_file:
    history = json.load(json_file)

questions = {}
for q in history:
    question_init = q["question"].lower().replace("why", "").replace("what", "").replace("who", "")
    if question_init in questions.keys():
        continue

    questions[question_init] = []
    for r in history:

        question = r["question"].lower().replace("why", "").replace("what", "").replace("who", "")
        if question == question_init:
            answer = r["answer"].lower()
            multi = r["multi"]
            url = r["url"]

            answers = []
            if multi is True:
                answers = answer.split("\n")


            t_number = 0
            for word in question.split(" "):
                number_times = count_occurrences(word, answer)
                t_number += number_times

            questions[question].append(number_times)
        else:
            continue
        #print("For " + "'" + question + "', the words totaled " + str(number_times) + " occurrences in the answer")

        # = .append({"question": question,"occurances":number_times})

print(questions)
