import gspread
from oauth2client.service_account import ServiceAccountCredentials
from espn_api.football import League
from datetime import datetime, timedelta
import pytz
import json
import requests

team_mapping = {
    "ARI": ("Arizona Cardinals", "Ari"),
    "ATL": ("Atlanta Falcons", "Atl"),
    "BAL": ("Baltimore Ravens", "Bal"),
    "BUF": ("Buffalo Bills", "Buf"),
    "CAR": ("Carolina Panthers", "Car"),
    "CHI": ("Chicago Bears", "Chi"),
    "CIN": ("Cincinnati Bengals", "Cin"),
    "CLE": ("Cleveland Browns", "Cle"),
    "DAL": ("Dallas Cowboys", "Dal"),
    "DEN": ("Denver Broncos", "Den"),
    "DET": ("Detroit Lions", "Det"),
    "GB": ("Green Bay Packers", "GB"),
    "HOU": ("Houston Texans", "Hou"),
    "IND": ("Indianapolis Colts", "Ind"),
    "JAX": ("Jacksonville Jaguars", "Jax"),
    "KC": ("Kansas City Chiefs", "KC"),
    "MIA": ("Miami Dolphins", "Mia"),
    "MIN": ("Minnesota Vikings", "Min"),
    "NE": ("New England Patriots", "NE"),
    "NO": ("New Orleans Saints", "NO"),
    "NYG": ("New York Giants", "NYG"),
    "NYJ": ("New York Jets", "NYJ"),
    "LV": ("Las Vegas Raiders", "LV"),
    "PHI": ("Philadelphia Eagles", "Phi"),
    "PIT": ("Pittsburgh Steelers", "Pit"),
    "LAC": ("Los Angeles Chargers", "LAC"),
    "SF": ("San Francisco 49ers", "SF"),
    "SEA": ("Seattle Seahawks", "Sea"),
    "LAR": ("Los Angeles Rams", "LAR"),
    "TB": ("Tampa Bay Buccaneers", "TB"),
    "TEN": ("Tennessee Titans", "Ten"),
    "WAS": ("Washington Commanders", "Was")
}

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("scenic-crossbar-399110-e8bbb8903198.json", scope)
client = gspread.authorize(creds)
sheet = client.open("White Water Fantasy All-Stars").worksheet("Eligible Players")

# ESPN API setup
LEAGUE_ID = 935464
YEAR = 2023
ESPN_S2 = "AEBkP1k%2BWZhyusCijcwUWRhJS8CHQ%2FW0J85u7TBqJKRDGMEfTKfP6Jtk32%2BHqs%2FbPW%2BLMhC9nPFekI4tIK8Dg49thEzBmdZlwzNP2%2F9i4kNAWPNRjKfuRdTPt3NXjloUDP7n774v91fJ1m0Bp0Q33exNw%2BHOQBxAH5iyakYZECV8XthEiGEeREjcBU7Fvnz5ue16XD78VXA07BzIIMSCi4yeK46FdPKWdCwwfzqMXGQGF990KtxKn60Qkx7Y45ns3KJn03LCJUgno1JUbwIcjNGCEVKCCJDvjgnfIQ%2BtyP%2BqLQ%3D%3D"
SWID = "{4CF33657-E49C-468C-A2C4-C91A262AFDF8}"
league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)

# Load the NFL schedule data from the GitHub repository
response = requests.get("https://raw.githubusercontent.com/alex-ackerman-greenberg/fantasy-all-stars/main/week_6_schedule.json")
response.raise_for_status()  # Raise an exception for HTTP errors
nfl_schedule_data = response.json()

# Extracting the schedule into a more accessible format
schedule = {}
for event in nfl_schedule_data["events"]:
    if " @ " in event["shortName"]:
        teams = event["shortName"].split(" @ ")
    elif " VS " in event["shortName"]:
        teams = event["shortName"].split(" VS ")
    else:
        print(f"Unexpected format in event shortName: {event['shortName']}")
        continue

    date = event["date"]
    weekNumber = event["weekNumber"]
    schedule[teams[0]] = {"opponent": teams[1], "date": date, "week": weekNumber}
    schedule[teams[1]] = {"opponent": teams[0], "date": date, "week": weekNumber}

# Convert UTC time to Pacific Time
def convert_to_pacific(utc_time_str):
    try:
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M%z")
    
    pacific_time = utc_time - timedelta(hours=7)
    return pacific_time

# Define the cell positions for each team
team_positions = {
    1: {"team_name": (3, 2), "position": (5, 2), "player_name": (5, 3), "opp": (5, 4), "game": (5, 5)},
    2: {"team_name": (3, 7), "position": (5, 7), "player_name": (5, 8), "opp": (5, 9), "game": (5, 10)},
    3: {"team_name": (22, 2), "position": (24, 2), "player_name": (24, 3), "opp": (24, 4), "game": (24, 5)},
    4: {"team_name": (22, 7), "position": (24, 7), "player_name": (24, 8), "opp": (24, 9), "game": (24, 10)},
    5: {"team_name": (41, 2), "position": (43, 2), "player_name": (43, 3), "opp": (43, 4), "game": (43, 5)},
    6: {"team_name": (41, 7), "position": (43, 7), "player_name": (43, 8), "opp": (43, 9), "game": (43, 10)},
    7: {"team_name": (60, 2), "position": (62, 2), "player_name": (62, 3), "opp": (62, 4), "game": (62, 5)},
    8: {"team_name": (60, 7), "position": (62, 7), "player_name": (62, 8), "opp": (62, 9), "game": (62, 10)},
    9: {"team_name": (79, 2), "position": (81, 2), "player_name": (81, 3), "opp": (81, 4), "game": (81, 5)},
    10: {"team_name": (79, 7), "position": (81, 7), "player_name": (81, 8), "opp": (81, 9), "game": (81, 10)},
    11: {"team_name": (98, 2), "position": (100, 2), "player_name": (100, 3), "opp": (100, 4), "game": (100, 5)},
    12: {"team_name": (98, 7), "position": (100, 7), "player_name": (100, 8), "opp": (100, 9), "game": (100, 10)},
    13: {"team_name": (117, 2), "position": (119, 2), "player_name": (119, 3), "opp": (119, 4), "game": (119, 5)},
    14: {"team_name": (117, 7), "position": (119, 7), "player_name": (119, 8), "opp": (119, 9), "game": (119, 10)}
}


# Fetch all teams and their players
teams = league.teams
cells_to_color = []  # List to collect cells that need coloring
cells_to_center = []  # List to collect cells that need centering

for team_index, team in enumerate(teams, start=1):
    print(f"Team Name: {team.team_name}")
    sheet.update_cell(team_positions[team_index]["team_name"][0], team_positions[team_index]["team_name"][1], team.team_name)
    
    player_data = []
    start_row = team_positions[team_index]["position"][0]
    start_col = team_positions[team_index]["position"][1]

    for player_index, player in enumerate(team.roster, start=0):
        player_team = player.proTeam
        
        # Extracting game details
        if player_team in schedule:
            opp_team_all_caps = schedule[player_team]["opponent"]
            _, opp_team = team_mapping.get(opp_team_all_caps, (opp_team_all_caps, opp_team_all_caps))
            game_date_utc = schedule[player_team]["date"]
            game_date_pacific = convert_to_pacific(game_date_utc)
            game_time_str = game_date_pacific.strftime("%a %-I:%M%p").capitalize()
            if player_team < opp_team_all_caps:
                opp = "@ " + opp_team
            else:
                opp = "vs " + opp_team
        else:
            opp = "BYE"
            game_time_str = "BYE"
        
        player_data.append((player.position, player.name, opp, game_time_str))

    # Update the sheet in batches for each team
    start_row = team_positions[team_index]["position"][0]
    start_col = team_positions[team_index]["position"][1]
    end_row = start_row + len(player_data) - 1
    end_col = start_col + 3
    cell_range = sheet.range(start_row, start_col, end_row, end_col)

    for i, (position, name, opp, game) in enumerate(player_data):
        cell_range[i * 4].value = position
        cell_range[i * 4 + 1].value = name
        cell_range[i * 4 + 2].value = opp
        cell_range[i * 4 + 3].value = game

    for i, (position, name, opp, game) in enumerate(player_data):
        # Check the "Opp" column for "BYE"
        if opp == "BYE":
            opp_col = start_col + 1  # Adjusted column index for "Opp"
            cells_to_center.append(f"{chr(65 + opp_col)}{start_row + i}")

        # Check the "Game" column for "BYE"
        if game == "BYE":
            game_col = start_col + 2  # Adjusted column index for "Game"
            cells_to_center.append(f"{chr(65 + game_col)}{start_row + i}")

    sheet.update_cells(cell_range)  # Update the sheet with player data

    for i in range(len(player_data)):
        opp_value = player_data[i][2]
        game_value = player_data[i][3]

        if opp_value == "BYE" or "Mon" in game_value or "Sat" in game_value or "Thu" in game_value:
            # Collect all four cells corresponding to the player
            for j in range(4):
                cells_to_color.append(f"{chr(65 + start_col + j - 1)}{start_row + i}")  # Adjusted column index by subtracting 1  

# After updating all teams, set horizontal alignment for BYE cells
alignment_requests = [{
    "repeatCell": {
        "range": {
            "sheetId": sheet.id,
            "startRowIndex": int(cell_address[1:]) - 1,
            "endRowIndex": int(cell_address[1:]),
            "startColumnIndex": ord(cell_address[0]) - 65,
            "endColumnIndex": ord(cell_address[0]) - 64
        },
        "cell": {
            "userEnteredFormat": {
                "horizontalAlignment": "CENTER"
            }
        },
        "fields": "userEnteredFormat(horizontalAlignment)"
    }
} for cell_address in cells_to_center]

sheet.spreadsheet.batch_update({"requests": alignment_requests})

# Batch update the colors for cells that need coloring
format_requests = [{
    "repeatCell": {
        "range": {
            "sheetId": sheet.id,
            "startRowIndex": int(cell_address[1:]) - 1,
            "endRowIndex": int(cell_address[1:]),
            "startColumnIndex": ord(cell_address[0]) - 65,
            "endColumnIndex": ord(cell_address[0]) - 64
        },
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {
                    "red": 1,
                    "green": 0,
                    "blue": 0
                }
            }
        },
        "fields": "userEnteredFormat(backgroundColor)"
    }
} for cell_address in cells_to_color]

sheet.spreadsheet.batch_update({"requests": format_requests})

# Record script run timestamp
current_time = datetime.now(pytz.timezone('US/Pacific'))
formatted_time = current_time.strftime("%-I:%M%p (%-m/%-d)").lower()
sheet.update_cell(136, 3, formatted_time)

print("Script completed successfully!")
