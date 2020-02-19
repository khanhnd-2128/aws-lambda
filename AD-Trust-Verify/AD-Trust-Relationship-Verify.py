import json
import logging
import os
import boto3
import random
import time
from urllib2 import Request, urlopen, URLError, HTTPError

# Read all the environment variables
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
SLACK_USER = os.environ['SLACK_USER']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
TRUST_ID = os.environ['TRUST_ID']
DIRECTORY_ID = os.environ['DIRECTORY_ID']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Event: " + str(event))

    logger.info("Trust verify")
    try:
        client = boto3.client('ds')
        res = client.verify_trust(TrustId=TRUST_ID)
        logger.info("HTTP Status Code: %s" % (res['ResponseMetadata']['HTTPStatusCode']))
    except Exception as e:
        message = "\nError trust api. Code return: %s" % (str(e.message))
    
    logger.info("Get trust AD describe")
    try:
        time.sleep(30)
        client = boto3.client('ds')
        res = client.describe_trusts(
            DirectoryId=DIRECTORY_ID,
            TrustIds=[TRUST_ID])
        trust_stt = res['Trusts'][0]['TrustState']
        res_code = 1 if trust_stt.lower() == 'verified' else 0
        message = "Trust AD status: %s" % (trust_stt)
    except Exception as e:
        res_code= 0
        message += "\nError describe api. Code return: %s" % (str(e.message))
    logger.info("Message: " + str(message))
    
   
    try:
        cloudwatch = boto3.client('cloudwatch')
        response = cloudwatch.put_metric_data(
            MetricData = [
                {
                    'MetricName': 'trust_api',
                    'Dimensions': [
                        {
                            'Name': 'TrustState',
                            'Value': 'Trust State'
                        }
                    ],
                    'Unit': 'None',
                    'Value': res_code
                },
            ],
            Namespace = 'AD'
        )
    except Exception as e:
        logger.info("Error: %s" % (str(e.message)))
        
    
    if int(res_code) == 1:
        logger.info("Trusted, not send message to slack")
        return "Trusted, not send message to slack"
    
    slack_message = {
        'channel': SLACK_CHANNEL,
        'username': SLACK_USER,
        'text': "%s" % (message)
    }

    req = Request(SLACK_WEBHOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
    return message
