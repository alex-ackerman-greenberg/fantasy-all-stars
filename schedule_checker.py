#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 11:18:17 2023

@author: alexag
"""

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import pytz
from datetime import datetime
import json
import subprocess

# Google Sheets Details
CREDENTIALS_FILE = "scenic-crossbar-399110-e8bbb8903198.json"
SHEET_NAME = "White Water Fantasy All-Stars"
TAB_NAME = "Week 6 - Matchup"

#function to get week number from google sheet, to use in the URL to get this week's schedule
def get_week_number():
    # Setup Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    
    # Open the sheet and specific tab
    sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
    
    # Fetch all data from the sheet at once
    all_data = sheet.get_all_values()
    
    # Get the week number from cell N1
    current_week = int(all_data[0][13])  # 13 corresponds to column N
    return current_week

#function to get json from URL, to be used later
def fetch_json_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if there's an error
    return response.json()

#set current week variable to be used globally
current_week = get_week_number()

#set URL for current week to get schedule data
weekly_schedule_url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?limit=1000&year=2023&week={current_week}"

# Fetch data directly from the URL
original_data = fetch_json_from_url(weekly_schedule_url)

#function to strip and clean the original data into a simpler format to work with
def transform_event_data(original_data):
    events_list = original_data.get("events", [])
    transformed_data = {"events": []}

    for event in events_list:
        transformed_event = {
            "name": event.get("name", ""),
            "shortName": event.get("shortName", ""),
            "date": event.get("date", ""),
            "weekNumber": event.get("week", {}).get("number", ""),
            "gameState": event.get("status", {}).get("type", {}).get("state", ""),
            "id": event.get("id", "")
        }
        transformed_data["events"].append(transformed_event)

    return transformed_data

# Transform the data
transformed_data = transform_event_data(original_data)

# Print or save the transformed data
print(json.dumps(transformed_data, indent=4))

def save_to_file(data, filename):
    """Save the provided data to a JSON file."""
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)

# ... [rest of your code, including the fetching and transformation]

# Save the transformed data to a file in current directory, and store the filename
save_to_file(transformed_data, f"week_{current_week}_schedule.json")

print("Data saved successfully!")

#FOR LATER
# =============================================================================
# #function to push new weekly schedule to github
# def commit_and_push_to_github(filename, commit_message):
#     try:
#         # Add file to Git
#         subprocess.check_call(['git', 'add', filename])
# 
#         # Commit the file
#         subprocess.check_call(['git', 'commit', '-m', commit_message])
# 
#         # Push the commit
#         subprocess.check_call(['git', 'push'])
# 
#         print(f"File {filename} has been committed and pushed to GitHub!")
#     except subprocess.CalledProcessError as e:
#         print(f"Error committing the file to GitHub: {e}")
#         return
# 
# #set some variables to use in the github push function
# filename = f"week_{current_week}_schedule.json"
# commit_message = f"Adding week {current_week} schedule json from schedule checker script"
# 
# # Actually push weekly schedule to github
# commit_and_push_to_github(filename, commit_message)
# =============================================================================

