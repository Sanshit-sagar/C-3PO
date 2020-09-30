import wolframalpha
import wikipedia
import requests

appId = 'APER4E-58XJGHAVAK'
client = wolframalpha.Client(appId)
needed_from_bing = []

def search_wiki(keyword=''):
    searchResults = wikipedia.search(keyword)
    if not searchResults:
        result = "No result from Wikipedia"
        return result
    try:
        page = wikipedia.page(searchResults[0])
    except (wikipedia.DisambiguationError, err):
        page = wikipedia.page(err.options[0])

    wikiTitle = str(page.title.encode('utf-8'))
    wikiSummary =  str(page.summary.encode('utf-8'))
    result = wikiSummary
    return result

def SearchWolfram(params):
  entities = params["entities"]
  request = params["request"]
  sentiment = params["sentiment"]
  context = params["context"]
  text = request
  res = client.query(text)
  if res['@success'] == 'false':

     print('Question cannot be resolved')
     return {"response":"unsure", "user_request":text, "follow_up":"false", "bing_entity_name":needed_from_bing, "request": request}
  else:
    result = ''
    pod0 = res['pod'][0]
    pod1 = res['pod'][1]
    if (('definition' in pod1['@title'].lower()) or ('result' in  pod1['@title'].lower()) or (pod1.get('@primary','false') == 'true')):
      result = resolveListOrDict(pod1['subpod'])
      question = resolveListOrDict(pod0['subpod'])
      question = removeBrackets(question)
      return {"response":result,  "user_request":text, "follow_up":"false", "store":"false", "bing_entity_name":needed_from_bing, "request": request}
    elif((len(pod0['subpod']['plaintext']))>0):
      result = pod0['subpod']['plaintext']
      return {"response":result,  "user_request":text, "follow_up":"false", "store":"false", "bing_entity_name":needed_from_bing, "request": request}
    else:
      question = resolveListOrDict(pod0['subpod'])
      question = removeBrackets(question)
      result = search_wiki(question)
      return {"response":result,  "user_request":text, "follow_up":"false", "store":"false", "bing_entity_name":needed_from_bing, "request": request}

def removeBrackets(variable):
  return variable.split('(')[0]

def resolveListOrDict(variable):
  if isinstance(variable, list):
    return variable[0]['plaintext']
  else:
    return variable['plaintext']
