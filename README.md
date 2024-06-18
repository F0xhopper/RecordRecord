This Flask application allows users to manage and retrieve personal records (PRs) for squat, bench press, and deadlift via SMS commands. It integrates with Twilio for handling incoming messages and stores data in a Google Sheets document.

Tech Stack

- Flask
- Gspread
- Twilio

Features

- Capability to update personal records (PRs) for squat, bench press, and deadlift via SMS commands e.g. 'set squat 100kg'.
- Ability to retrieve the highest PRs for each exercise through SMS queries e.g.'get squat'.
- Storage and retrieval of PR data from a Google Sheets document.

Usage

Clone the repository:

git clone <repository_url>
cd <repository_directory>

Install dependencies using pip:

pip install Flask gspread oauth2client twilio

Obtain Google Service Account credentials:

Go to the Google Cloud Console and create a new project if you haven't already.
Enable the Google Sheets API for your project.
Create a service account, download the JSON key file, and save it securely.
Share your Google Sheets document with the service account email address.
Configure credentials:

Place your downloaded credentials.json file in the project directory.
Update the creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/credentials.json", scope) line in app.py with your actual credentials path.

Run app:

python main.py
