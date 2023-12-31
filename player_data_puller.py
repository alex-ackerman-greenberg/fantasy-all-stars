import gspread
from oauth2client.service_account import ServiceAccountCredentials
from espn_api.football import League
import pytz
import time
from datetime import datetime

# ESPN League Details
LEAGUE_ID = 935464
YEAR = 2023
ESPN_S2 = "AEBkP1k%2BWZhyusCijcwUWRhJS8CHQ%2FW0J85u7TBqJKRDGMEfTKfP6Jtk32%2BHqs%2FbPW%2BLMhC9nPFekI4tIK8Dg49thEzBmdZlwzNP2%2F9i4kNAWPNRjKfuRdTPt3NXjloUDP7n774v91fJ1m0Bp0Q33exNw%2BHOQBxAH5iyakYZECV8XthEiGEeREjcBU7Fvnz5ue16XD78VXA07BzIIMSCi4yeK46FdPKWdCwwfzqMXGQGF990KtxKn60Qkx7Y45ns3KJn03LCJUgno1JUbwIcjNGCEVKCCJDvjgnfIQ%2BtyP%2BqLQ%3D%3D"
SWID = "{4CF33657-E49C-468C-A2C4-C91A262AFDF8}"

# Google Sheets Details
CREDENTIALS_FILE = "scenic-crossbar-399110-e8bbb8903198.json"
SHEET_NAME = "White Water Fantasy All-Stars"
TAB_NAME = "Week 6 - Matchup"

# Initialize ESPN League
league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)

player_data_cache = {}

# Fetch player data
def get_player_data(player_name, week):
    # Check if data is in cache
    if player_name in player_data_cache:
        cached_data = player_data_cache[player_name]
        if cached_data[1] is None:  # If the cached team value is None, skip this player
            return cached_data
    
    retries = 3  # specify the number of retries you want to allow
    for _ in range(retries):
        try:
            player = league.player_info(name=player_name)
            if player:
                points = player.stats.get(week, {}).get('points')
                team_names = [team.team_name for team in league.teams if player.playerId in [p.playerId for p in team.roster]]
                team_name = team_names[0] if team_names else None
                if not team_name:
                    print(f"Warning: No team found for player: {player_name}")
                    player_data_cache[player_name] = (None, None)  # Cache players with no teams
                
                # Save the data to cache ONLY if points and team_name are not None
                if points is not None and team_name is not None:
                    player_data_cache[player_name] = (points, team_name)
                return points, team_name
            else:
                print(f"Warning: No data found for player: {player_name}")
                return None, None
        except Exception as e:
            print(f"Error encountered while fetching player data: {str(e)}. Retrying...")
            time.sleep(5)  # wait for 5 seconds before retrying
    print(f"Failed to retrieve data for player {player_name} after {retries} attempts.")
    return None, None  # return None values if data fetch fails even after retries

# Update Google Sheet
def update_sheet():
    #empty the player points data from the cache before starting the run again. Leaves the player names and teams intact.
    for player in player_data_cache:
        player_data_cache[player]["points"] = None
    
    # Setup Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    
    # Open the sheet and specific tab
    sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
    
    # Fetch all data from the sheet at once
    all_data = sheet.get_all_values()
    
    # Get the week number from cell N1
    week = int(all_data[0][13])  # 13 corresponds to column N
    
    # Collect updates here
    all_updates = []

    # Iterate over the fetched data
    for row_idx, row in enumerate(all_data):
        for col_idx, cell_value in enumerate(row):
            if cell_value == "Player Name":
                player_row = row_idx + 1
                while player_row < len(all_data) and all_data[player_row][col_idx] != "Team Score:":
                    player_name = all_data[player_row][col_idx]
                    points, team_name = get_player_data(player_name, week)
                    if points is not None and team_name is not None:
                        cell_points = gspread.Cell(row=player_row + 1, col=col_idx + 2, value=points)
                        cell_team = gspread.Cell(row=player_row + 1, col=col_idx + 3, value=team_name)
                        all_updates.extend([cell_points, cell_team])
                    elif not team_name:
                        # Highlight the cell in red if the player is not found on a team
                        format_cell_range = f"{gspread.utils.rowcol_to_a1(player_row + 1, col_idx + 1)}:{gspread.utils.rowcol_to_a1(player_row + 1, col_idx + 1)}"
                        sheet.format(format_cell_range, {"backgroundColor": {"red": 1, "green": 0, "blue": 0}})
                    player_row += 1

    # Update the timestamp in cell D1
    pacific = pytz.timezone('US/Pacific')
    current_time = datetime.now(pacific).strftime('%-I:%M%p (%-m/%-d)').lower()
    sheet.update_cell(1, 4, current_time)

    # Batch update the sheet
    if all_updates:
        sheet.update_cells(all_updates)
        print("Sheet updated successfully at ",current_time)
    else:
        print("No updates found.")

#Main function that allows for manual sheet updates, if this script is run directly. If it is imported, this will not run.
if __name__ == "__main__":
    update_sheet()
