import http.client, urllib.parse, uuid, json

# **********************************************
# *** Update or verify the following values. ***
# **********************************************

# Replace the subscriptionKey string value with your valid subscription key.


def get_translation(text, to):
    subscriptionKey = '' #MS translate translation key REMOVED for github

    host = 'api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'

    # Translate to German and Italian.
    params = ""

    for obj in to:
        params = params + "&to=" + obj

    def translate (content):

        headers = {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        conn = http.client.HTTPSConnection(host)
        conn.request ("POST", path + params, content, headers)
        response = conn.getresponse ()
        return response.read ()

    requestBody = [{
        'Text' : text,
    }]
    content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')
    result = translate (content)

    output = json.dumps(json.loads(result), indent=4, ensure_ascii=False)

    return output
