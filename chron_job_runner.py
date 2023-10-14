#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 11:19:23 2023

@author: alexag
"""

import json
from datetime import datetime, timedelta
from schedule_checker import get_week_number
from player_data_puller import update_sheet
import time
import pytz

#function to convert UTC to PT to use when displaying/printing times. All calcuations/program logic done in UTC.
def format_time_as_pt(dt_utc):
    """Converts a UTC datetime object to a string in PT format."""
    if dt_utc.tzinfo is None:  # if dt_utc is naive
        dt_utc = pytz.utc.localize(dt_utc)
    dt_pt = dt_utc.astimezone(pytz.timezone('America/Los_Angeles'))
    return dt_pt.strftime('%Y-%m-%d %H:%M:%S %Z')

#IN THIS SECTION, WE ARE FINDING AND SAVING THE GAME TIMES FOR THE GIVEN DAY TO RUN THE SCHEDULED UPDATE SHEET SCRIPT
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
    last_game_time = max(start_times, default=None)

    return next_game_time, last_game_time

#get current week from schedule checker
current_week = get_week_number()

#set filename based on current week
filename = f"week_{current_week}_sunday_schedule.json"

# Get next game time and last game time
next_game_time, last_game_time = get_next_game_time_and_last_game_time(filename)

print(f"Next Game Time: {format_time_as_pt(next_game_time)}")
print(f"Last Game Time: {format_time_as_pt(last_game_time)}")

#IN THIS SECTION, WE ARE ACTUALLY TRYING TO UPDATE THE GOOGLE SHEET WITH LIVE PLAYER DATA, BUT ONLY WHEN GAMES ARE LIVE.
#WE SHOULD BE ABLE TO RUN THIS AT ANY TIME, AND HAVE IT WAIT TO MAKE ANY CALLS UNTIL GAME TIME SUNDAY.

# Configuration Section
MODE = 'TEST'  # Set to 'TEST' or 'PROD'
#No need to edit the fake time if you're using PROD mode.
FAKE_TIME_PT = datetime.datetime(2023, 10, 16, 12, 0)  # If using TEST mode, input a fake time here (Year, Month, Day, Hour, Minute, using military hours.
POST_GAME_WAIT_HOURS = 4  # Time to wait after the last game has started, in hours
UPDATE_INTERVAL_MINUTES = 15  # Interval between data updates during games, in minutes

# Convert FAKE_TIME to UTC
FAKE_TIME_UTC = pytz.timezone('America/Los_Angeles').localize(FAKE_TIME_PT).astimezone(pytz.utc)

# Function to get current time, respecting MODE
def get_current_time():
    return FAKE_TIME_UTC if MODE == 'TEST' else datetime.datetime.utcnow()

# Set player data update start and end times
player_data_update_start_time = next_game_time
player_data_update_end_time = None if last_game_time is None else last_game_time + timedelta(hours=POST_GAME_WAIT_HOURS)

# If there are no upcoming games and the last game (if any) is past the post-game wait period, exit the script.
if next_game_time is None and (last_game_time is None or get_current_time() > last_game_time + timedelta(hours=POST_GAME_WAIT_HOURS)):
    print("No active games. Exiting...")
    exit()

# If there's an upcoming game, wait until it starts, regardless of how far in the future it is.
if get_current_time() < player_data_update_start_time:
    wait_time = (player_data_update_start_time - get_current_time()).total_seconds()
    # Convert wait_time into hours, minutes, and seconds
    hours, remainder = divmod(wait_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Print the waiting time
    print(f"Waiting {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds for the next game to start at {format_time_as_pt(player_data_update_start_time)}..")
    time.sleep(wait_time)

# Main loop, once there is no wait time: retrieve data while games are being played.
#NOTE: the logic of the script does not take into account games that start late or were cancelled. Don't think that matters.
while get_current_time() <= player_data_update_end_time:
    update_sheet()  # Fetches player data and updates the Google Sheet
    time.sleep(UPDATE_INTERVAL_MINUTES * 60)  # wait before fetching again
    
print(f"Games are finished for today. Exiting at {format_time_as_pt(get_current_time())}")





