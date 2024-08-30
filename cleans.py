import pandas as pd
import requests
from bs4 import BeautifulSoup

# URL of the page containing fixtures and results
url = 'https://fbref.com/en/comps/9/2023-2024/schedule/2023-2024-Premier-League-Scores-and-Fixtures'

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all tables on the page
tables = soup.find_all('table')

if not tables:
    raise ValueError("No tables found on the page. The structure might have changed.")

# Try to identify the correct table by looking for one with the relevant columns
target_table = None
for table in tables:
    headers = [th.text for th in table.find_all('th')]
    if 'xG' in headers and 'Home' in headers:  # Checking for relevant headers
        target_table = table
        break

if target_table is None:
    raise ValueError("The table containing xG data was not found on the page.")

# Initialize an empty list to store the data
data = []

# Iterate over each row in the table body
for row in target_table.find('tbody').find_all('tr'):
    try:
        team_1 = row.find('td', {'data-stat': 'home_team'}).text.strip()  # Replace with correct attribute
        team_2 = row.find('td', {'data-stat': 'away_team'}).text.strip()  # Replace with correct attribute
        
        # Safely extract and convert xG values
        xg_1_str = row.find('td', {'data-stat': 'home_xg'}).text.strip()  # Replace with correct attribute
        xg_2_str = row.find('td', {'data-stat': 'away_xg'}).text.strip()  # Replace with correct attribute

        # Convert to float if not empty, else set to None
        xg_1 = float(xg_1_str) if xg_1_str else None
        xg_2 = float(xg_2_str) if xg_2_str else None

        # Only add data if xG values are valid
        if xg_1 is not None and xg_2 is not None:
            expected_clean_1 = 1 if xg_2 <= 0.7 else 0
            expected_clean_2 = 1 if xg_1 <= 0.7 else 0

            # Append to the data list
            data.append([team_1, expected_clean_1])
            data.append([team_2, expected_clean_2])

    except AttributeError:
        # Handle rows without data
        continue

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=['Team', 'Expected_Clean'])

# Calculate total games and expected cleans per team
result = df.groupby('Team').agg(Total_Games=('Expected_Clean', 'count'), 
                                Expected_Cleans=('Expected_Clean', 'sum')).reset_index()

# Display the result
print(result)

# Save the result to a CSV file
result.to_csv('expected_cleans.csv', index=False)

