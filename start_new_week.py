#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 13:40:55 2023

@author: alexag
"""

import pygsheets
from schedule_checker import save_schedule_files
from fetch_eligible_players import fetch_eligible_players
from common_functions import get_week_number

#STEP 0: Auth and open the spreadsheet
# Authenticate and create a client to interact with the Google Drive API
gc = pygsheets.authorize(service_file='scenic-crossbar-399110-e8bbb8903198.json')

# Open the spreadsheet by its title
sheet = gc.open("White Water Fantasy All-Stars")

#STEP 1: CREATE NEW "CURRENT MATCHUP" TAB.

# Rename old matchup tab to "Week X - Matchup"
old_matchup_worksheet = sheet.worksheet_by_title("Current Matchup")
current_week_number = get_week_number()
new_title = f"Week {current_week_number} - Matchup"
old_matchup_worksheet.title = new_title

# Re-fetch the worksheet with its new title
old_matchup_worksheet = sheet.worksheet_by_title(new_title)

# Duplicate it
new_matchup_worksheet = sheet.add_worksheet(title="Current Matchup", src_worksheet=old_matchup_worksheet)

# Increment N1 by 1 in the "Current Matchup" worksheet
new_week_number = current_week_number + 1
new_matchup_worksheet.update_value('N1', new_week_number)  # N1 corresponds to row 1, column 14

#Step 2: Archive the team pages
# Get all the worksheets
all_worksheets = sheet.worksheets()

for worksheet in all_worksheets:
    # If it's a "Team Page"
    if "Team Page" in worksheet.title and "Template" not in worksheet.title:
        team_name = worksheet.title.replace(" Team Page", "")
        
        # Find the corresponding "Team Archive"
        team_archive_ws = sheet.worksheet_by_title(f"{team_name} Team Archive")
        
        # Insert 153 new rows at the top of the archive
        team_archive_ws.insert_rows(row=1, number=154)

        # Copy the data from "Team Page" to "Team Archive"
        df_source = worksheet.get_as_df(start='A1', end='K153')
        team_archive_ws.set_dataframe(df_source, start='A1', overwrite=True)

#Step 3: Save out the old week's eligible players, and run the eligible player script for this week.

#create new schedule files for upcoming week
save_schedule_files()

# save out the old week's player page
all_worksheets = sheet.worksheets()
source_sheet = sheet.worksheet_by_title("Eligible Players")
new_sheet_name_base = f"Eligible Players - Week {current_week_number}"
new_sheet_name = new_sheet_name_base
counter = 1

while True:
    try:
        duplicated_sheet = sheet.add_worksheet(new_sheet_name, src_worksheet=source_sheet)
        break  # If the sheet is added successfully, exit the loop
    except pygsheets.exceptions.WorksheetTitleTaken:
        # If the title already exists, increment the title and try again
        new_sheet_name = f"{new_sheet_name_base} ({counter})"
        counter += 1

#create new eligible player page
fetch_eligible_players()

#Step 4: Put eligible players into team template page
all_worksheets = sheet.worksheets()
source_sheet = sheet.worksheet_by_title("Eligible Players")
eligible_player_data = source_sheet.get_as_df(start='A1')

for worksheet in all_worksheets:
    if "Team Page Template" in worksheet.title:
        worksheet.set_dataframe(eligible_player_data, start='A18', overwrite=True)
        
#Step 5: Copy team page template into the team pages . This is going to use google APIs directly to maintain formatting.
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('scenic-crossbar-399110-e8bbb8903198.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# open spreadsheet
spreadsheet_id = '1f0AhQpZzG_16u0QWuyGvZ7LYZ4ddHuCOo9T_xblPL8Q'
source_sheet_id = 302540256

# Step 1: List all sheets in the spreadsheet
response = service.spreadsheets().get(spreadsheetId=spreadsheet_id, fields="sheets.properties").execute()
sheets = response.get('sheets', [])

# Step 2: Filter the sheets
target_sheet_ids = [sheet['properties']['sheetId'] for sheet in sheets if "Team Page" in sheet['properties']['title'] and sheet['properties']['title'] != "Team Page Template"]

# Step 3: Copy data from the source sheet to each target sheet
for target_sheet_id in target_sheet_ids:
    request = {
        "copyPaste": {
            "source": {
                "sheetId": source_sheet_id,
                "startRowIndex": 0,
                "startColumnIndex": 0,
                "endRowIndex": 153,  # Assuming the source sheet has 153 rows
                "endColumnIndex": 11  # Change this to your source sheet's last column
            },
            "destination": {
                "sheetId": target_sheet_id,
                "startRowIndex": 0,
                "startColumnIndex": 0,
            },
            "pasteType": "PASTE_NORMAL"
        }
    }

    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [request]}).execute()

print(f"Data copied from source sheet to {len(target_sheet_ids)} target sheets.")




#OLD WAY OF COPYING ELIGIBLE PLAYERS THAT DOESNT PRESERVE FORMATTING

# all_worksheets = sheet.worksheets()

# template_ws = sheet.worksheet_by_title("Team Page Template")

# # Fetch data and formatting from the template
# df_template = template_ws.get_as_df()

# for worksheet in all_worksheets:
#     # If it's a "Team Page"
#     if "Team Page" in worksheet.title:
#         # Overwrite the data in the Team Page with the template's data
#         worksheet.set_dataframe(df_template, start='A1', overwrite=True)

