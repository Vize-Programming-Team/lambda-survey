import boto3

from question import total_questions

dynamodb = boto3.resource('dynamodb','us-west-2')
table = dynamodb.Table('User_Data')

identify_key = 'Survey_Code'

def save_response(number,body):
    user_response_list = table.get_item(Key={identify_key: number, })['Item']['Questions']

    if len(user_response_list) < total_questions():
        user_response_list.append(body)
        table.update_item(Key={identify_key: number, }, UpdateExpression="set Questions = :m",
                          ExpressionAttributeValues={':m': user_response_list}, ReturnValues="UPDATED_NEW")

def get_response(number,question):
    user_responses = table.get_item(Key={identify_key: number, })['Item']['Questions']
    if (question >= 0) and (question < len(user_responses)):
        return user_responses[question]
    else:
        return None

def update_response(number,question,message):
    user_responses = table.get_item(Key={identify_key: number, })['Item']['Questions']

    if (question >= 0) and (question < len(user_responses)):
        user_responses[question] = user_responses[question] + '\n' + message
        table.update_item(Key={identify_key: number, }, UpdateExpression="set Questions = :m",
                          ExpressionAttributeValues={':m': user_responses}, ReturnValues="UPDATED_NEW")
