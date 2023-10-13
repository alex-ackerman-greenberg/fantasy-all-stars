#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 11:19:23 2023

@author: alexag
"""

import json
from datetime import datetime, timedelta
from schedule_checker import get_week_number
import pytz
from player_data_puller import update_sheet

#function that saves the first game time, and last game time to be referenced elsewhere
def get_next_game_time_and_last_game_time(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    now = datetime.utcnow()
    
    start_times = [datetime.fromisoformat(event['date'].replace('Z', '')) for event in events]
    if not start_times:
        return None, None
    
    next_game_time = next((time for time in start_times if time > now), None)
    last_game_time = max(start_times)

    return next_game_time, last_game_time

#get current week from schedule checker
current_week = get_week_number()

#set filename based on current week
filename = f"week_{current_week}_sunday_schedule.json"

# Get next game time and last game time
next_game_time, last_game_time = get_next_game_time_and_last_game_time(filename)

print(next_game_time)
print(last_game_time)

#Commented out as I'm still working on this section to actually run the sheet updater function at the right times'
# =============================================================================
# # If it's not yet time for the first game or if all games for the day have been played, exit the script.
# if next_game_time is None or datetime.utcnow() > last_game_time + timedelta(hours=4):
#     print("No active games. Exiting...")
#     exit()
# 
# # If it's game day but not yet time for the first game, wait until the first game starts.
# if datetime.utcnow() < next_game_time:
#     wait_time = (next_game_time - datetime.utcnow()).total_seconds()
#     print(f"Waiting {wait_time} seconds for the first game to start at {next_game_time} UTC...")
#     time.sleep(wait_time)
# 
# # Main loop: retrieve data while games are being played.
# while datetime.utcnow() <= last_game_time + timedelta(hours=4):
#     update_sheet()  # Fetches player data and updates the Google Sheet
#     time.sleep(15 * 60)  # wait 15 minutes before fetching again
#     
# print("Games are finished for today. Exiting...")
# =============================================================================

