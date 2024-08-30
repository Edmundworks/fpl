import os
import pandas as pd

def process_match_files(num_matches):
    player_data = {}

    for i in range(1, num_matches + 1):
        match_file = f'match_{i}_data.csv'
        
        if not os.path.exists(match_file):
            print(f"File {match_file} does not exist, skipping.")
            continue

        print(f"Processing {match_file}...")

        match_df = pd.read_csv(match_file, index_col=0)

        for player in match_df.index:
            if player not in player_data:
                player_data[player] = {f'GW{j+1}': '' for j in range(38)}

            for gw in match_df.columns:
                if 'xG' in gw or 'xAG' in gw:
                    gw_number = int(gw.split()[0][2:])  # Extract the gameweek number

                    npxg = match_df.at[player, f'GW{gw_number} xG'] if f'GW{gw_number} xG' in match_df.columns else 0.0
                    xag = match_df.at[player, f'GW{gw_number} xAG'] if f'GW{gw_number} xAG' in match_df.columns else 0.0

                    total_value = npxg + xag

                    if total_value > 0.7:
                        player_data[player][f'GW{gw_number}'] = 'likelyReturn'
                    else:
                        player_data[player][f'GW{gw_number}'] = ''  # Keep it blank if not a likelyReturn

    return player_data

def save_likely_returns(player_data):
    likely_returns_df = pd.DataFrame.from_dict(player_data, orient='index')
    likely_returns_df.to_csv('likelyReturns.csv')
    print("likelyReturns.csv has been created successfully.")

def main():
    num_matches = 380  # You can adjust this number if you have fewer or more matches
    player_data = process_match_files(num_matches)
    save_likely_returns(player_data)

if __name__ == "__main__":
    main()
