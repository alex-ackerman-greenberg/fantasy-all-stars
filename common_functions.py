#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 15:02:25 2023

@author: alexag
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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