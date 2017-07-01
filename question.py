import boto3

dynamodb = boto3.resource('dynamodb','us-east-1')
table = dynamodb.Table('user-data')

identify_key = 'ID'

question_list = table.get_item(Key={identify_key: 'Questions', })['Item']['Questions']

def get_next_question(number):
    user = table.get_item(Key={identify_key: number, })
    user_item = user['Item']
    user_question_list = user_item['Questions']
    user_completed = user_item['Completed']

    if len(user_question_list) == len(question_list):
        if user_completed:
            return 'You have already completed the survey'
        else:
            table.update_item(Key={identify_key: number, }, UpdateExpression="set Completed = :c",
                              ExpressionAttributeValues={':c': 1}, ReturnValues="UPDATED_NEW")
            return "That's the end of the survey. Thank you!"
    else:
        return question_list[len(user_question_list)]

def get_question(question_number):
    return question_list[question_number]

def get_previous_question(number):
    user_question_list = table.get_item(Key={identify_key: number})['Item']['Questions']
    if len(user_question_list)-1 >= 0:
        return question_list[len(user_question_list)-1]
    else:
        return question_list[0]

# Returns the number of questions in the survey
def total_questions():
    return len(question_list)