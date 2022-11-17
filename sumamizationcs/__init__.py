import logging
import azure.functions as func
import json, requests, time, os, logging
from http.client import HTTPConnection

#I am not using python SDK azure-ai-textanalytics because Abstractive Summarization is not yet available as of Nov22

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )

def compose_response(json_data):
    values = json.loads(json_data)['values']

    # Prepare the Output before the loop
    results = {}
    results["values"] = []

    for value in values:
        outputRecord = transform_value(value)
        if outputRecord != None:
            results["values"].append(outputRecord)
    return json.dumps(results, ensure_ascii=False)

def transform_value(value):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('text' in data), "'text' corpus field is required in 'data' object."
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "data":{},
            "errors": [ { "message": "Error:" + error.args[0] }   ]
            })

    try:
        result = get_summary (value)

    except:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Could not complete operation for record." }   ]
            })

    return ({
            "recordId": recordId,
            "data": {
                "text": result
                    }
            })

# Function to submit the analysis job towards the Text Analytics (TA) API
def get_summary (value):
    # # Debug logging, useful if you struggle with the body sent to the endpoint. Uncomment from http.client too 
    # log = logging.getLogger('urllib3')
    # log.setLevel(logging.DEBUG)
    # # logging from urllib3 to console
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # log.addHandler(ch)
    # # print statements from `http.client.HTTPConnection` to console/stdout
    # HTTPConnection.debuglevel = 1 

    endpoint = os.environ["TA_ENDPOINT"] # This will look like 'https://westeurope.api.cognitive.microsoft.com/text/analytics/v3.2-preview.2/analyze' to be updated once product goes GA
    key = os.environ["TA_KEY"]

    corpus = str(value['data']['text'])
    # chunk corpus string into equally sized chunks of 80000 characters
    chunks = [corpus[i:i+80000] for i in range(0, len(corpus), 80000)]
    finalsummary = ''
    partialsummary = ''
    # loop through the chunks
    for chunk in chunks:
        body = {'analysisInput': {'documents': [{'id': '1', 'text': chunk,'language':'en' }]}, 'tasks': [{'kind':'AbstractiveSummarization','taskName':'Doc summarization','parameters': {'sentenceCount':6}}]}
        header = {'Ocp-Apim-Subscription-Key': key}
        body_json = json.dumps(body)
        #TA API works in two steps, first you post the job, afterwards you get the result
        response_job = requests.post(endpoint, data = body_json, headers = header)
        jobid = response_job.headers["operation-location"]
        time.sleep(1) 
        response = requests.get(jobid, None, headers=header)
        dict=json.loads(response.text)
        #sometimes the TA processing time will be longer, in that case we need to try again after a while. You can probably add a more sophisticated retry policy here
        # Wait until status is succeeded or failed
        while dict['status'] != 'succeeded' and dict['status'] != 'failed':
            time.sleep(1)
            response = requests.get(jobid, None, headers=header)
            dict=json.loads(response.text)  
        summary=dict['tasks']['items'][0]['results']['documents'][0]['summaries']
        #TA API returns a list of sentences, we need to concatenate them
        for sentence in summary:
            partialsummary = partialsummary + sentence['text'] + " "
        finalsummary = finalsummary + partialsummary + ' '
    return finalsummary
