import re
from pathlib import Path
from collections import defaultdict
import json

# Read index.html to extract standings data
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract standings data for each year
# Find all tab content sections with standings tables
member_records = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0})
member_playoff_records = defaultdict(lambda: {'wins': 0, 'losses': 0})

# Find all standings tables
# Pattern: look for standings-table and extract rows
table_pattern = r'<table class="standings-table">(.*?)</table>'
tables = re.findall(table_pattern, content, re.DOTALL)

for table_html in tables:
    # Extract rows with member names and records
    # Pattern: profile link, then record in next td
    row_pattern = r'<a href="profiles/([^"]+)\.html"[^>]*>([^<]+)</a></td>\s*<td>(\d+)-(\d+)-(\d+)</td>'
    rows = re.findall(row_pattern, table_html)
    
    for profile_file, member_name, wins, losses, ties in rows:
        member_records[profile_file]['wins'] += int(wins)
        member_records[profile_file]['losses'] += int(losses)
        member_records[profile_file]['ties'] += int(ties)

# Extract playoff records from bracket data
# Look for playoff matchups - winners and losers
bracket_pattern = r'<div class="bracket">(.*?)</div>\s*</div>\s*</div>\s*</div>'
brackets = re.findall(bracket_pattern, content, re.DOTALL)

for bracket_html in brackets:
    # Find winners (team winner class)
    winner_pattern = r'<div class="team winner">.*?<span class="name">([^<]+)</span>'
    winners = re.findall(winner_pattern, bracket_html, re.DOTALL)
    
    # Find all matchups to count wins/losses
    matchup_pattern = r'<div class="matchup">(.*?)</div>\s*</div>'
    matchups = re.findall(matchup_pattern, bracket_html, re.DOTALL)
    
    for matchup in matchups:
        # Find both teams in matchup
        teams = re.findall(r'<span class="name">([^<]+)</span>', matchup)
        scores = re.findall(r'<span class="score">([^<]+)</span>', matchup)
        
        if len(teams) == 2 and len(scores) == 2:
            # Check which team won (has higher score or "BYE")
            if 'BYE' in scores[0] or 'BYE' in scores[1]:
                continue
            
            try:
                score1 = float(scores[0])
                score2 = float(scores[1])
                
                # Map team names to profile files (need to normalize)
                team1 = teams[0].strip()
                team2 = teams[1].strip()
                
                # Winner gets a win, loser gets a loss
                if score1 > score2:
                    # Find profile file for team1
                    for profile_file in member_records.keys():
                        if profile_file.replace('-', '').lower() in team1.lower() or team1.lower() in profile_file.lower():
                            member_playoff_records[profile_file]['wins'] += 1
                        if profile_file.replace('-', '').lower() in team2.lower() or team2.lower() in profile_file.lower():
                            member_playoff_records[profile_file]['losses'] += 1
                elif score2 > score1:
                    for profile_file in member_records.keys():
                        if profile_file.replace('-', '').lower() in team2.lower() or team2.lower() in profile_file.lower():
                            member_playoff_records[profile_file]['wins'] += 1
                        if profile_file.replace('-', '').lower() in team1.lower() or team1.lower() in profile_file.lower():
                            member_playoff_records[profile_file]['losses'] += 1
            except ValueError:
                pass

print("Extracted season records:")
for member, records in sorted(member_records.items()):
    season_record = f"{records['wins']}-{records['losses']}-{records['ties']}"
    playoff_record = f"{member_playoff_records[member]['wins']}-{member_playoff_records[member]['losses']}"
    print(f"{member}: {season_record} (Playoff: {playoff_record})")

# Save to a file
output = {}
for member in member_records.keys():
    output[member] = {
        'season_record': f"{member_records[member]['wins']}-{member_records[member]['losses']}-{member_records[member]['ties']}",
        'playoff_record': f"{member_playoff_records[member]['wins']}-{member_playoff_records[member]['losses']}"
    }

with open('data/member_season_records.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to data/member_season_records.json")

