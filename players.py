import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
import time

# Function to process a single match
def process_match(match_url, gameweek):
    while True:
        response = requests.get(match_url)
        if response.status_code == 429:
            print(f"Rate limited. Waiting before retrying {match_url}...")
            time.sleep(60)  # Wait for 1 minute before retrying (adjust as needed)
            continue
        elif response.status_code != 200:
            print(f"Failed to retrieve {match_url}. Status code: {response.status_code}")
            return None
        break

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all relevant divs that contain the player stats tables
    switcher_divs = soup.find_all('div', class_='switcher_content')

    home_team_table = None
    away_team_table = None

    for div in switcher_divs:
        table = div.find('table', {'class': 'stats_table'})
        if table:
            caption = table.find('caption')
            if caption:
                print(f"Found table: {caption.text.strip()}")
                if "Player Stats Table" in caption.text:
                    if home_team_table is None:
                        home_team_table = table  # First matching table is the home team
                    elif away_team_table is None:
                        away_team_table = table  # Second matching table is the away team
                        break  # We have both tables, no need to continue

    if not home_team_table or not away_team_table:
        print(f"Warning: Could not find the necessary tables on page: {match_url}")
        return None
    
    # Process the home and away team tables
    match_data = process_team_table(home_team_table, gameweek)
    match_data += process_team_table(away_team_table, gameweek)
    
    return match_data

# Function to process a team's stats table
def process_team_table(team_table, gameweek):
    team_data = []
    for row in team_table.find('tbody').find_all('tr'):
        player_cell = row.find('th', {'data-stat': 'player'})
        if player_cell:
            player_name = player_cell.text.strip()
            npxg_cell = row.find('td', {'data-stat': 'npxg'})
            xag_cell = row.find('td', {'data-stat': 'xag'})
            
            npxg = npxg_cell.text.strip() if npxg_cell else "0.0"
            xag = xag_cell.text.strip() if xag_cell else "0.0"

            try:
                npxg = float(npxg) if npxg else 0.0
                xag = float(xag) if xag else 0.0
                total = npxg + xag
            except ValueError:
                total = 0.0

            result = "likelyReturn" if total > 0.7 else "blank"
            team_data.append({'Player': player_name, f'GW{gameweek}': result})
    
    return team_data

def main():
    # Ask for user input
    match_id = int(input("Enter the match ID (1 for the first match, 2 for the second, etc.): "))
    csv_file = input("Enter the CSV file name (e.g., match_urls.csv): ")

    # Load match URLs from CSV
    match_urls_df = pd.read_csv(csv_file)
    match_urls = match_urls_df['Match URL'].tolist()

    if match_id < 1 or match_id > len(match_urls):
        print(f"Invalid match ID. Please enter a number between 1 and {len(match_urls)}.")
        return

    match_url = match_urls[match_id - 1]
    gameweek = (match_id // 10) + 1

    print(f"Processing match {match_id} for GW{gameweek}: {match_url}")
    
    # Process the match
    match_data = process_match(match_url, gameweek)
    
    if match_data:
        # Convert to DataFrame
        match_df = pd.DataFrame(match_data).set_index('Player')
        
        # Save the result to a CSV file
        output_file = f'match_{match_id}_data.csv'
        match_df.to_csv(output_file)
        print(f"Match data saved to {output_file}")
    else:
        print("No data was processed.")

if __name__ == "__main__":
    main()
