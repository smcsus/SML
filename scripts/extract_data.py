"""
Extract all data from index.html into JSON format.
This creates the foundation for a data-driven architecture.
"""

import re
import json
from collections import defaultdict
from pathlib import Path

# Create data directories
Path("data/drafts").mkdir(parents=True, exist_ok=True)
Path("data/seasons").mkdir(parents=True, exist_ok=True)

# Read HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize player names for consistent IDs
def normalize_player_id(name):
    """Create a consistent player ID from name"""
    # Remove suffixes
    name = re.sub(r'\s+[JS]r\.?$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+III?$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+II$', '', name, flags=re.IGNORECASE)
    # Remove punctuation and spaces, lowercase
    name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return name

# Normalize team abbreviations
def normalize_team(team):
    """Normalize team abbreviation to standard format"""
    team_map = {
        "KC": "KAN", "KAN": "KAN",
        "SF": "SFO", "SFO": "SFO",
        "GB": "GNB", "GNB": "GNB",
        "NO": "NOR", "NOR": "NOR",
        "TB": "TAM", "TAM": "TAM",
        "WSH": "WAS", "WAS": "WAS", "Wsh": "WAS",
        "LV": "LVR", "LVR": "LVR",
        "NE": "NWE", "NWE": "NWE",
        "BAL": "BAL", "Bal": "BAL",
        "CIN": "CIN", "Cin": "CIN",
        "ATL": "ATL", "Atl": "ATL",
        "BUF": "BUF", "Buf": "BUF",
        "IND": "IND", "Ind": "IND",
        "LAR": "LAR",
        "NYJ": "NYJ",
        "DAL": "DAL", "Dal": "DAL",
        "MIA": "MIA", "Mia": "MIA",
        "DET": "DET", "Det": "DET",
        "PHI": "PHI", "Phi": "PHI",
        "ARI": "ARI", "Ari": "ARI",
        "HOU": "HOU", "Hou": "HOU",
        "JAX": "JAX", "Jax": "JAX",
        "MIN": "MIN", "Min": "MIN",
        "TEN": "TEN", "Ten": "TEN",
        "CAR": "CAR", "Car": "CAR",
        "CLE": "CLE", "Cle": "CLE",
        "PIT": "PIT", "Pit": "PIT",
        "DEN": "DEN", "Den": "DEN",
        "CHI": "CHI", "Chi": "CHI",
        "SEA": "SEA", "Sea": "SEA",
        "LAC": "LAC",
        "2TM": "2TM", "3TM": "3TM", "FA": "FA"
    }
    return team_map.get(team, team_map.get(team.upper(), team.upper()))

# Extract value icon class
def extract_value_class(value_html):
    """Extract value class from HTML span"""
    match = re.search(r'class="value-([^"]+)"', value_html)
    if match:
        return match.group(1)
    return None

# Find all draft sections
draft_years = ['2025', '2024', '2023', '2022', '2021']

# Store all players with their teams by year
players_db = {}
drafts_data = {}
seasons_data = {}

for year in draft_years:
    print(f"\nExtracting {year} draft data...")
    
    # Find draft section
    start_tag = f'id="draft-{year}"'
    start_index = content.find(start_tag)
    if start_index == -1:
        print(f"  {year} draft section not found, skipping...")
        continue
    
    # Find the opening div
    start_index = content.rfind('<div', 0, start_index)
    
    # Find the end (next draft section or end of drafts)
    if year != '2021':
        next_year = str(int(year) - 1)
        end_tag = f'id="draft-{next_year}"'
    else:
        end_tag = 'id="draft-'
    
    end_index = content.find(end_tag, start_index)
    if end_index == -1:
        end_index = content.find('</section>', start_index)
    
    draft_section = content[start_index:end_index]
    
    # Pattern for rows with full data (2023, 2024, 2025)
    full_row_pattern = re.compile(
        r'<tr><td>(\d+)</td><td>(\d+)</td><td>([^<]+) \(([^,]+), ([^)]+)\)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>(<span[^>]*>[^<]+</span>|[^<]+)</td></tr>'
    )
    
    # Pattern for rows without full data (2021, 2022)
    basic_row_pattern = re.compile(
        r'<tr><td>(\d+)</td><td>(\d+)</td><td>([^<]+) \(([^,]+), ([^)]+)\)</td><td>([^<]+)</td></tr>'
    )
    
    picks = []
    season_rankings = defaultdict(list)
    
    # Try full pattern first
    matches = full_row_pattern.findall(draft_section)
    if matches:
        for match in matches:
            round_num, pick_num, player_name_full, team_abbr, position, owner, draft_pos, season_finish, points, value_html = match
            
            player_name = player_name_full.strip()
            player_id = normalize_player_id(player_name)
            team_normalized = normalize_team(team_abbr)
            
            # Store player in database
            if player_id not in players_db:
                players_db[player_id] = {
                    "name": player_name,
                    "positions": [],
                    "teams_by_year": {}
                }
            
            if position not in players_db[player_id]["positions"]:
                players_db[player_id]["positions"].append(position)
            
            players_db[player_id]["teams_by_year"][year] = team_normalized
            
            # Store draft pick
            pick_data = {
                "round": int(round_num),
                "pick": int(pick_num),
                "player_id": player_id,
                "owner": owner.strip(),
                "draft_pos": draft_pos.strip() if draft_pos.strip() else None
            }
            picks.append(pick_data)
            
            # Store season data if available
            if season_finish.strip() != "—" and points.strip() != "—":
                try:
                    points_float = float(points.strip())
                    # Extract rank from season_finish (e.g., "RB 8" -> 8)
                    rank_match = re.search(r'(\w+)\s+(\d+)', season_finish.strip())
                    if rank_match:
                        pos = rank_match.group(1)
                        rank = int(rank_match.group(2))
                        
                        season_rankings[pos].append({
                            "player_id": player_id,
                            "ppr": points_float,
                            "rank": rank
                        })
                except (ValueError, AttributeError):
                    pass
    
    # Try basic pattern for older years
    if not matches:
        matches = basic_row_pattern.findall(draft_section)
        for match in matches:
            round_num, pick_num, player_name_full, team_abbr, position, owner = match
            
            player_name = player_name_full.strip()
            player_id = normalize_player_id(player_name)
            team_normalized = normalize_team(team_abbr)
            
            # Store player in database
            if player_id not in players_db:
                players_db[player_id] = {
                    "name": player_name,
                    "positions": [],
                    "teams_by_year": {}
                }
            
            if position not in players_db[player_id]["positions"]:
                players_db[player_id]["positions"].append(position)
            
            players_db[player_id]["teams_by_year"][year] = team_normalized
            
            # Store draft pick
            pick_data = {
                "round": int(round_num),
                "pick": int(pick_num),
                "player_id": player_id,
                "owner": owner.strip(),
                "draft_pos": None
            }
            picks.append(pick_data)
    
    # Sort picks by round, then pick number
    picks.sort(key=lambda x: (x["round"], x["pick"]))
    
    # Store draft data
    drafts_data[year] = {
        "year": int(year),
        "picks": picks
    }
    
    # Sort season rankings by rank and store
    for pos in season_rankings:
        season_rankings[pos].sort(key=lambda x: x["rank"])
    
    if season_rankings:
        seasons_data[year] = {
            "year": int(year),
            "ppr_rankings": dict(season_rankings)
        }
    
    print(f"  Extracted {len(picks)} picks for {year}")
    if season_rankings:
        total_players = sum(len(rankings) for rankings in season_rankings.values())
        print(f"  Extracted {total_players} season rankings for {year}")

# Write players database
players_output = {
    "players": {}
}
for player_id, player_data in players_db.items():
    players_output["players"][player_id] = player_data

with open('data/players.json', 'w', encoding='utf-8') as f:
    json.dump(players_output, f, indent=2, ensure_ascii=False)

print(f"\n✓ Created data/players.json with {len(players_db)} players")

# Write draft data
for year, draft_data in drafts_data.items():
    filename = f'data/drafts/{year}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(draft_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Created {filename}")

# Write season data
for year, season_data in seasons_data.items():
    filename = f'data/seasons/{year}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(season_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Created {filename}")

print("\n" + "="*50)
print("Data extraction complete!")
print("="*50)
print(f"\nTotal players: {len(players_db)}")
print(f"Draft years extracted: {len(drafts_data)}")
print(f"Season years extracted: {len(seasons_data)}")

# Show example of player with multiple teams
print("\nExample: Players with teams across multiple years:")
for player_id, player_data in list(players_db.items())[:5]:
    if len(player_data["teams_by_year"]) > 1:
        print(f"  {player_data['name']}: {player_data['teams_by_year']}")

