import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

def process_match(match_url, gameweek, home_team, away_team, players_stats):
    while True:
        response = requests.get(match_url)
        if response.status_code == 429:
            print(f"Rate limited. Waiting before retrying {match_url}...")
            time.sleep(60)  # Wait for 1 minute before retrying (adjust as needed)
            continue
        elif response.status_code != 200:
            print(f"Failed to retrieve {match_url}. Status code: {response.status_code}")
            return
        break

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all tables that might be "Summary" tables based on the presence of "summary" in their class or id
    summary_tables = soup.find_all('table', id=lambda x: x and 'summary' in x)

    if not summary_tables:
        print(f"No 'Summary' tables found on page: {match_url}")
        return

    home_team_table = None
    away_team_table = None

    # Identify the home and away team tables based on the caption
    for table in summary_tables:
        caption = table.find('caption').text.strip()
        if home_team in caption:
            home_team_table = table
        elif away_team in caption:
            away_team_table = table

    if not home_team_table or not away_team_table:
        print(f"Warning: Could not find both 'Summary' tables on page: {match_url}")
        return

    # Process the home and away team tables
    process_team_table(home_team_table, gameweek, players_stats)
    process_team_table(away_team_table, gameweek, players_stats)

def process_team_table(team_table, gameweek, players_stats):
    for row in team_table.find('tbody').find_all('tr'):
        player_name = row.find('th', {'data-stat': 'player'}).text.strip()

        # Attempt to find the xG and xAG cells
        npxg_cell = row.find('td', {'data-stat': 'npxg'})
        xag_cell = row.find('td', {'data-stat': 'xg_assist'})

        # Extract xG and xAG values, handling cases where data is missing or non-numeric
        try:
            npxg = float(npxg_cell.text.strip()) if npxg_cell and npxg_cell.text.strip() else 0.0
        except ValueError:
            npxg = 0.0

        try:
            xag = float(xag_cell.text.strip()) if xag_cell and xag_cell.text.strip() else 0.0
        except ValueError:
            xag = 0.0

        # Initialize player's entry if not present
        if player_name not in players_stats:
            players_stats[player_name] = {f'GW{i+1} npxG': 0.0 for i in range(38)}
            players_stats[player_name].update({f'GW{i+1} xAG': 0.0 for i in range(38)})

        # Store the values in the corresponding gameweek
        players_stats[player_name][f'GW{gameweek} npxG'] = npxg
        players_stats[player_name][f'GW{gameweek} xAG'] = xag

        # Debugging: Confirm storage
        print(f"Stored npxG for GW{gameweek}: {players_stats[player_name][f'GW{gameweek} npxG']}")
        print(f"Stored xAG for GW{gameweek}: {players_stats[player_name][f'GW{gameweek} xAG']}")
        print("-" * 40)  # Separator for readability

def main():
    # Ask for user input
    match_id = int(input("Enter the match ID (1 for the first match, 2 for the second, etc.): "))
    csv_file = input("Enter the CSV file name (e.g., match_urls.csv): ")

    # Load match URLs and team names from CSV
    match_urls_df = pd.read_csv(csv_file)
    match_urls = match_urls_df['Match URL'].tolist()
    home_teams = match_urls_df['Home Team'].tolist()
    away_teams = match_urls_df['Away Team'].tolist()

    if match_id < 1 or match_id > len(match_urls):
        print(f"Invalid match ID. Please enter a number between 1 and {len(match_urls)}.")
        return

    match_url = match_urls[match_id - 1]
    home_team = home_teams[match_id - 1]
    away_team = away_teams[match_id - 1]
    gameweek = (match_id // 10) + 1

    print(f"Processing match {match_id} for GW{gameweek}: {match_url}")
    
    # Initialize the players' stats dictionary
    players_stats = {}

    # Process the match
    process_match(match_url, gameweek, home_team, away_team, players_stats)
    
    if players_stats:
        # Convert to DataFrame
        players_df = pd.DataFrame.from_dict(players_stats, orient='index')
        
        # Print the DataFrame to inspect the data
        print("Data to be saved:")
        print(players_df)
        
        # Save the result to a CSV file
        try:
            output_file = os.path.join(os.getcwd(), f'match_{match_id}_data.csv')
            players_df.to_csv(output_file)
            print(f"Match data saved to {output_file}")
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")
    else:
        print("No data was processed.")

if __name__ == "__main__":
    main()