import subprocess
import time

def run_players_script(num_runs):
    for i in range(1, num_runs + 1):
        print(f"Running players.py with match ID {i}")
        subprocess.run(["python", "players.py", str(i), "match_urls.csv"])
        print(f"Completed run {i}")
        print("-" * 40)
        time.sleep(1)  # Add a 1-second delay between runs

if __name__ == "__main__":
    num_runs = 380
    run_players_script(num_runs)
