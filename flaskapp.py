from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from botocore.exceptions import ClientError
import get_message

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to dynamo db table
TABLE_NAME = "Employees"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

@app.route('/', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        state = request.form['state']
        town = request.form['town']
        college = request.form['college']
        team = request.form['team']
        role = request.form['role']
        hobbies = request.form['hobbies']
        response = table.scan()
        items = response['Items']
        count = len(items)
        table.put_item(
        Item={
            'ID': count+1,
            'Email': email,
            'First Name': fname,
            'Last Name': lname,
            'Hometown': town+", "+state,
            'College': college,
            'Team': team,
            'Role': role,
            'Hobbies': hobbies
        }
        )
        print(get_message.new_employee_message())
        flash('Employee added successfully!')
        return redirect('/')  # PRG pattern

        
    else:
        # Render the html page if the request method is GET
        return render_template('template.html')  
    

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
