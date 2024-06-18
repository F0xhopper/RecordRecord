import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("RecordRecord").sheet1

@app.route("/sms", methods=['POST'])
def sms_reply():
    """
    Respond to incoming messages with a simple text message.
    Commands:
    - 'set squat lift': Set a new squat lift.
    - 'set bench lift': Set a new bench press lift.
    - 'set deadlift lift': Set a new deadlift lift.
    - 'get squat': Get the highest squat PR.
    - 'get bench': Get the highest bench press PR.
    - 'get deadlift': Get the highest deadlift PR.
    """
    body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    
    try:
        if body.startswith('set squat'):
            lift = float(body.split()[-1])
            message = update_pr('squat', lift)
            resp.message(message)
        elif body.startswith('set bench'):
            lift = float(body.split()[-1])
            message = update_pr('bench', lift)
            resp.message(message)
        elif body.startswith('set deadlift'):
            lift = float(body.split()[-1])
            message = update_pr('deadlift', lift)
            resp.message(message)
        elif body.startswith('get squat'):
            pr = get_pr('squat')
            resp.message(f"Your highest squat is {pr} kg.")
        elif body.startswith('get bench'):
            pr = get_pr('bench')
            resp.message(f"Your highest bench press is {pr} kg.")
        elif body.startswith('get deadlift'):
            pr = get_pr('deadlift')
            resp.message(f"Your highest deadlift is {pr} kg.")
        else:
            resp.message("Unknown command. Please use 'set' or 'get' followed by the exercise and lift.")
    except Exception as e:
        resp.message(f"An error occurred: {str(e)}")
    
    return Response(str(resp), mimetype="application/xml")

def update_pr(exercise, lift):
    """
    Update the personal record (PR) for a specific exercise.
    Args:
    - exercise (str): Name of the exercise ('squat', 'bench', 'deadlift').
    - lift (float): Weight lifted in kilograms.
    Returns:
    - str: Confirmation message of the update.
    """
    column = {
        'squat': 1,
        'bench': 2,
        'deadlift': 3
    }
    col = sheet.col_values(column[exercise])
    
    if 'x' in str(lift).lower():
        weight_lifted = parse_and_calculate_1rm(str(lift))
    elif lift.endswith("kg"): 
        weight_lifted = float(lift[:-2])  # Remove 'kg' and convert to float
    else:
        weight_lifted = float(lift)
    
    # Find the current max PR
    if len(col) > 1:  # Check if there are existing PRs, ignoring header
        max_pr = max(col[1:], key=lambda x: float(x))
    else:
        max_pr = 0
    
    # Append the new PR to the column
    next_row = len(col) + 1
    sheet.update_cell(next_row, column[exercise], weight_lifted)
    
    # Compare the new PR with the current max PR
    if float(lift) > float(max_pr):
        return f"New {exercise} PR! You beat the previous PR of {max_pr} kg by {float(lift) - float(max_pr)} kg."
    else:
        return f"Your new {exercise} lift of {lift} kg has been added. You were {float(max_pr) - lift} kg away from beating your best."

def get_pr(exercise):
    """
    Get the highest personal record (PR) for a specific exercise.
    Args:
    - exercise (str): Name of the exercise ('squat', 'bench', 'deadlift').
    Returns:
    - str: Highest PR for the exercise.
    """
    column = {
        'squat': 1,
        'bench': 2,
        'deadlift': 3
    }
    col = sheet.col_values(column[exercise])
    if len(col) > 1:
        pr = max(col[1:], key=lambda x: float(x))  # Skip the header and find the max value
        return pr
    else:
        return "No PR recorded."

def parse_and_calculate_1rm(input_str):
    """
    Parse and calculate estimated 1-rep max (1RM) using Epley formula.
    Args:
    - input_str (str): Input string containing repetitions and weight lifted (e.g., '5x100kg').
    Returns:
    - float: Estimated 1RM.
    """
    parts = input_str.strip().split('x')
    reps = int(parts[0])
    weight_str = parts[1].strip()
    if weight_str.endswith("kg"):
        weight_lifted = float(weight_str[:-2])  # Remove 'kg' and convert to float
    else:
        weight_lifted = float(weight_str)

    # Calculate estimated 1RM using Epley formula
    estimated_1rm = weight_lifted * (1 + reps / 30)

    return estimated_1rm

if __name__ == "__main__":
    app.run(debug=True)