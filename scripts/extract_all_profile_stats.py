import re
import json
from collections import defaultdict

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Map of profile aliases to their stats
profile_stats = defaultdict(lambda: {
    'championships': 0,
    'runner_ups': 0,
    'playoff_wins': 0,
    'playoff_losses': 0,
    'playoff_appearances': set()
})

# Name to alias mapping
name_to_alias = {
    'JJ': 'jj',
    'JMar': 'jmar',
    'Masters': 'masters',
    'Lucas': 'lucas',
    'Jasper': 'jasper',
    'Sunny': 'sunny',
    'Hatter': 'hatter',
    'Cam': 'cam',
    'Drew': 'drew',
    'Kircher': 'kircher',
    'D-Lew': 'd-lew',
    'Baker': 'baker'
}

# Extract championships and runner-ups from champions table
champ_row_pattern = r'<div class="table-row">\s*<span class="col-year">(\d{4})</span>\s*<span class="col-champ">(?:<a href="profiles/([^"]+)\.html"[^>]*>([^<]+)</a>|([^<]+))</span>\s*<span class="col-runner">(?:<a href="profiles/([^"]+)\.html"[^>]*>([^<]+)</a>|([^<]+))</span>'

for match in re.finditer(champ_row_pattern, content):
    year = match.group(1)
    champ_alias = match.group(2) or None
    champ_name = match.group(3) or match.group(4)
    runner_alias = match.group(5) or None
    runner_name = match.group(6) or match.group(7)
    
    if champ_alias:
        profile_stats[champ_alias]['championships'] += 1
        profile_stats[champ_alias]['playoff_appearances'].add(year)
    
    if runner_alias:
        profile_stats[runner_alias]['runner_ups'] += 1
        profile_stats[runner_alias]['playoff_appearances'].add(year)

# Extract playoff bracket data - find each bracket section
# Look for "Championship Bracket" and extract the bracket div (exclude 3rd place games)
# Stop before any "3rd Place Game" section
bracket_sections = re.finditer(r'<h4 class="bracket-title">Championship Bracket</h4>\s*<div class="bracket">(.*?)</div>\s*(?=<h4 class="bracket-title">3rd Place|</div>\s*</div>\s*<!--)', content, re.DOTALL)

for bracket_match in bracket_sections:
    bracket_html = bracket_match.group(1)
    
    # Find all matchups in this bracket (only Championship Bracket, not 3rd place games)
    # Matchup pattern: two teams with names and scores
    matchup_pattern = r'<div class="matchup[^"]*">(.*?)</div>\s*</div>'
    matchups = re.findall(matchup_pattern, bracket_html, re.DOTALL)
    
    for matchup_html in matchups:
        # Skip BYE matchups
        if 'team bye' in matchup_html:
            continue
        
        # Extract both teams from the matchup
        team_pattern = r'<div class="team[^"]*">.*?<span class="name">([^<]+)</span>.*?<span class="score">([^<]+)</span>'
        teams = re.findall(team_pattern, matchup_html, re.DOTALL)
        
        if len(teams) != 2:
            continue
        
        team1_name = teams[0][0].strip()
        team1_score = teams[0][1].strip()
        team2_name = teams[1][0].strip()
        team2_score = teams[1][1].strip()
        
        # Skip BYE games
        if 'BYE' in team1_score or 'BYE' in team2_score:
            continue
        
        # Get aliases
        team1_alias = name_to_alias.get(team1_name)
        team2_alias = name_to_alias.get(team2_name)
        
        if not team1_alias or not team2_alias:
            continue
        
        # Determine winner by comparing scores (ignore 3rd place games are already excluded)
        try:
            score1 = float(team1_score)
            score2 = float(team2_score)
            
            if score1 > score2:
                profile_stats[team1_alias]['playoff_wins'] += 1
                profile_stats[team2_alias]['playoff_losses'] += 1
            elif score2 > score1:
                profile_stats[team2_alias]['playoff_wins'] += 1
                profile_stats[team1_alias]['playoff_losses'] += 1
        except ValueError:
            pass

# Convert playoff_appearances sets to counts
for alias in profile_stats:
    profile_stats[alias]['playoff_appearances'] = len(profile_stats[alias]['playoff_appearances'])

# Print results
print("Profile Statistics:")
for alias in sorted(profile_stats.keys()):
    stats = profile_stats[alias]
    print(f"{alias}:")
    print(f"  Championships: {stats['championships']}")
    print(f"  Runner-Ups: {stats['runner_ups']}")
    print(f"  Playoff Record: {stats['playoff_wins']}-{stats['playoff_losses']}")
    print(f"  Playoff Appearances: {stats['playoff_appearances']}")
    print()

# Save to JSON
output = {}
for alias, stats in profile_stats.items():
    output[alias] = {
        'championships': stats['championships'],
        'runner_ups': stats['runner_ups'],
        'playoff_record': f"{stats['playoff_wins']}-{stats['playoff_losses']}",
        'playoff_appearances': stats['playoff_appearances']
    }

with open('data/profile_stats_corrected.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print("Saved to data/profile_stats_corrected.json")
