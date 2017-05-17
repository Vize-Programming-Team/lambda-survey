import os
import urllib
import random

import boto3

from boto3.session import Session
from boto3.dynamodb.conditions import Key
from twilio.twiml.messaging_response import MessagingResponse

from question import get_next_question
from question_response import save_response

# Add S3 and DynamoDB session
s3 = boto3.resource('s3')
session = Session()

# Add Twilio credentials
account_sid = os.environ['ACCOUNT_SID']
auth_token = os.environ['AUTH_TOKEN']

# Add DynamoDB
dynamodb = boto3.resource('dynamodb','us-west-2')
table_users = dynamodb.Table('User_Data')

def lambda_handler(event, context):
    response = MessagingResponse()
    print('Event:', event)
    identify_key = 'Survey_Code'

    message = str(event['Body'])
    from_number = event['From']
    num_media = event['NumMedia']

    from_number = urllib.parse.unquote(from_number)

    # Checks for initial response from survey deployment. If responded with 'Yes' the survey will be sent
    if (table_users.get_item(Key={identify_key: from_number})['Item']['Responded'] == 0) and (message.lower() == 'yes'):
        table_users.update_item(Key={identify_key: from_number, }, UpdateExpression="set Responded = :r",
                                ExpressionAttributeValues={':r': 1}, ReturnValues="UPDATED_NEW")

    # Check the database for an existing user
    dynamo_response = table_users.query(KeyConditionExpression=Key('Survey_Code').eq(from_number))

    if dynamo_response['Count'] == 0:
        response.message("Error. We don't recognize your number")
        save_message = False
    else:
        save_message = True

    # Stores the response in the database
    if save_message:
        # Handles storing media sent via text
        if num_media != '0':
            pic_url = urllib.parse.unquote(event['MediaUrl0'])
            twilio_pic = urllib.request.Request(pic_url, headers={'User-Agent': "Magic Browser"})
            image = urllib.request.urlopen(twilio_pic)
            image_bucket = 'image-monster'
            key = "ingest-images/" + str(from_number.replace('+', '')) + "/" + str(random.getrandbits(50)) + ".png"
            store_url = "https://s3-us-west-2.amazonaws.com/{0}/{1}".format(image_bucket, str(key))
            meta_data = {'FromNumber': from_number, 'url': store_url}
            s3.Bucket(image_bucket).put_object(Key=key, Body=image.read(), ACL='public-read', ContentType='image/png',
                                               Metadata=meta_data)
            message = store_url
        save_response(from_number, message)

    # If the user wants to take the survey, the next question is received
    if table_users.get_item(Key={identify_key: from_number})['Item']['Responded']:
        question = get_next_question(from_number)
        response.message(question)

    return str(response)