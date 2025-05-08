import json
import boto3

# SES and Dynamo setup
ses = boto3.client('ses', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
table = dynamodb.Table('Employees')

SENDER = "gabe.meier@drake.edu"  # Change to YOUR email
CHARSET = "UTF-8"

def get_var(ID, var):
    response = table.get_item(Key={'ID': ID})
    user = response.get("Item")
    return user[var]

def hobby_list(hobbies):
    hobby_dicts = json.loads(hobbies)
    hobbies = [item["value"] for item in hobby_dicts]
    if len(hobbies)==1:
        hobbies = hobbies[0]
    elif len(hobbies)==0:
        hobbies = "no hobbies"
    elif len(hobbies)==2:
        hobbies = hobbies[0]+" and "+hobbies[1]
    else:
        h=""
        for i in range(len(hobbies)):
            h+=hobbies[i]
            if i == len(hobbies)-1:
                h=h
            elif i == len(hobbies)-2:
                h+= ", and "
            else:
                h+= ", "
        hobbies=h
    return hobbies

def create_message(ID):
    fname = get_var(ID, "First Name")
    lname = get_var(ID, "Last Name")
    hometown = get_var(ID, "Hometown")
    college = get_var(ID, "College")
    team = get_var(ID, "Team")
    role = get_var(ID, "Role")
    hobbies = get_var(ID, "Hobbies")
    hobbies = hobby_list(hobbies)
    message='Join me in welcoming ' + fname + ' ' + lname + ' to the team! '
    message+=(fname + ' is from ' + hometown + ' and attended '+college + '.')
    message+=(' They will be joining the '+team+ ' team as an '+role)
    message+=('. Some of their hobbies include '+hobbies+'.')
    return message


def lambda_handler(event, context):
    print("EVENT RECEIVED:", json.dumps(event))
    table = dynamodb.Table('Employees')

    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_item = record['dynamodb']['NewImage']
            new_employee = int(new_item["ID"]["N"])

            # Build message
            message = create_message(new_employee)

            # Get list of recipient emails from table
            response = table.scan()
            employees = response.get('Items', [])
            recipient_emails = [emp['Email'] for emp in employees if 'Email' in emp]

            # Send email to each recipient
            for email in recipient_emails:
                if email != SENDER:
                    send_email(email, message)
                else:
                    send_email(email, message)

    return {
        'statusCode': 200,
        'body': json.dumps('Notification emails sent.')
    }

def send_email(recipient, message):
    ses.send_email(
        Source=SENDER,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': 'A New Employee Has Joined the Team!', 'Charset': CHARSET},
            'Body': {
                'Text': {'Data': message, 'Charset': CHARSET}
            }
        }
    )
