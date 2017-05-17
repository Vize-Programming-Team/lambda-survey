import boto3

dynamodb = boto3.resource('dynamodb','us-west-2')
table = dynamodb.Table('User_Data')

identify_key = 'Survey_Code'

def get_next_question(number):
    questions = table.get_item(Key={identify_key: 'Questions', })
    questions_item = questions['Item']
    question_list = questions_item['Questions']

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

# Returns the number of questions in the survey
def total_questions():
    questions = table.get_item(Key={identify_key: 'Questions', })
    questions_item = questions['Item']
    question_list = questions_item['Questions']

    return len(question_list)