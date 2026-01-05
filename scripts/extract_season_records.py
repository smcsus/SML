import re
from pathlib import Path
from collections import defaultdict

# Read index.html to extract standings data
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract standings data for each year
# Pattern: year tab -> standings table -> rows with member names and records
standings_pattern = r'<div class="tab-content[^>]*data-year="(\d+)"[^>]*>.*?<table class="standings-table">(.*?)</table>'
standings_matches = re.findall(standings_pattern, content, re.DOTALL)

member_records = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0, 'playoff_wins': 0, 'playoff_losses': 0})

# Process each year's standings
for year, table_html in standings_matches:
    # Extract rows with member names and records
    row_pattern = r'<td><a href="profiles/([^"]+)\.html"[^>]*>([^<]+)</a></td>\s*<td>(\d+)-(\d+)-(\d+)</td>'
    rows = re.findall(row_pattern, table_html)
    
    for profile_file, member_name, wins, losses, ties in rows:
        member_records[profile_file]['wins'] += int(wins)
        member_records[profile_file]['losses'] += int(losses)
        member_records[profile_file]['ties'] += int(ties)

# Extract playoff records from bracket data
# Look for playoff matchups and track wins/losses
playoff_pattern = r'<div class="team (?:winner|)">.*?<span class="name">([^<]+)</span>.*?<span class="score">([^<]+)</span>'
# This is more complex, let's just extract from history for now

print("Extracted season records:")
for member, records in sorted(member_records.items()):
    season_record = f"{records['wins']}-{records['losses']}-{records['ties']}"
    print(f"{member}: {season_record}")

# Save to a file for use in fixing profiles
import json
with open('data/member_season_records.json', 'w') as f:
    json.dump(dict(member_records), f, indent=2)

print("\nSaved to data/member_season_records.json")

