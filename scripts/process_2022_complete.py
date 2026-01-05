"""Complete 2022 PPR processing - parse, rank, create JSON, update HTML"""

import json
import re
from collections import defaultdict

def normalize_name(name):
    name = re.sub(r'\s+[JS]r\.?$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+III?$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+II$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[*+]', '', name)
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def normalize_team(team):
    team_map = {
        "KC": "KAN", "KAN": "KAN", "SF": "SFO", "SFO": "SFO",
        "GB": "GNB", "GNB": "GNB", "NO": "NOR", "NOR": "NOR",
        "TB": "TAM", "TAM": "TAM", "WSH": "WAS", "WAS": "WAS",
        "LV": "LVR", "LVR": "LVR", "NE": "NWE", "NWE": "NWE",
        "BAL": "BAL", "CIN": "CIN", "ATL": "ATL", "BUF": "BUF",
        "IND": "IND", "LAR": "LAR", "NYJ": "NYJ", "DAL": "DAL",
        "MIA": "MIA", "DET": "DET", "PHI": "PHI", "ARI": "ARI",
        "HOU": "HOU", "JAX": "JAX", "MIN": "MIN", "TEN": "TEN",
        "CAR": "CAR", "CLE": "CLE", "PIT": "PIT", "DEN": "DEN",
        "CHI": "CHI", "SEA": "SEA", "LAC": "LAC",
        "2TM": "2TM", "3TM": "3TM", "FA": "FA"
    }
    return team_map.get(team, team_map.get(team.upper(), team.upper()))

def calculate_value_icon(draft_pos_str, season_finish_str):
    if season_finish_str == '—':
        return '<span class="value-miss">✗</span>'
    try:
        draft_pos_num = int(draft_pos_str.split(' ')[1])
        season_finish_num = int(season_finish_str.split(' ')[1])
        diff = draft_pos_num - season_finish_num
        if diff >= 30:
            return '<span class="value-super-hit">💎</span>'
        elif diff >= 15:
            return '<span class="value-extreme-hit">✓</span>'
        elif diff >= 6:
            return '<span class="value-hit">✓</span>'
        elif abs(diff) <= 5:
            return '<span class="value-push">≈</span>'
        else:
            return '<span class="value-miss">✗</span>'
    except (ValueError, IndexError):
        return '<span class="value-miss">✗</span>'

print("="*70)
print("PROCESSING 2022 PPR DATA - COMPLETE")
print("="*70)

# Load data
with open('data/players.json', 'r', encoding='utf-8') as f:
    players_data = json.load(f)['players']

with open('data/drafts/2022.json', 'r', encoding='utf-8') as f:
    draft_2022 = json.load(f)

# Create player lookup
player_id_lookup = {}
for player_id, player_info in players_data.items():
    normalized = normalize_name(player_info['name'])
    player_id_lookup[normalized] = (player_id, player_info['name'])

# Parse PPR data from file
# The data format: tab-separated, PPR is column 27 (0-indexed)
# Player is column 1, Team is column 2, Position is column 3

print("\n📊 Parsing PPR data...")

ppr_entries = []
try:
    # Read from the raw data file
    with open('data/2022_ppr_raw.txt', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) < 28:
                continue
            
            # Skip header rows - look for lines that start with "Rk" or don't have numeric first column
            try:
                first_col = parts[0].strip()
                # Skip if first column is not a number (header rows)
                int(first_col)
            except (ValueError, IndexError):
                continue
            
            try:
                # Format: Rank, Player, Team, Position, ...stats..., PPR (col 27)
                player_name = parts[1].strip().rstrip('*+')
                team = normalize_team(parts[2].strip())
                position = parts[3].strip()
                ppr = float(parts[27].strip())
                ppr_entries.append({
                    'name': player_name,
                    'team': team,
                    'position': position,
                    'ppr': ppr
                })
            except (ValueError, IndexError) as e:
                continue
except FileNotFoundError:
    print("  ⚠️  data/2022_ppr_raw.txt not found")
    print("  💡 Please save the full 2022 PPR data to this file")
    exit(1)

print(f"  ✅ Parsed {len(ppr_entries)} players")

# Group by position and rank
position_rankings = defaultdict(list)

for entry in ppr_entries:
    pos = entry['position']
    if pos in ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']:
        # Try to find player_id
        normalized_name = normalize_name(entry['name'])
        player_id = None
        if normalized_name in player_id_lookup:
            player_id = player_id_lookup[normalized_name][0]
        else:
            # Try fuzzy matching
            for norm_name, (pid, orig_name) in player_id_lookup.items():
                if normalized_name in norm_name or norm_name in normalized_name:
                    player_id = pid
                    break
        
        if player_id:
            position_rankings[pos].append({
                'player_id': player_id,
                'ppr': entry['ppr'],
                'name': entry['name'],
                'team': entry['team']
            })

# Sort by PPR descending and assign ranks
season_2022 = {
    "year": 2022,
    "ppr_rankings": {}
}

for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']:
    if pos in position_rankings:
        sorted_players = sorted(position_rankings[pos], key=lambda x: x['ppr'], reverse=True)
        season_2022['ppr_rankings'][pos] = [
            {
                'player_id': p['player_id'],
                'ppr': p['ppr'],
                'rank': i
            }
            for i, p in enumerate(sorted_players, 1)
        ]
        print(f"  ✅ {pos}: {len(sorted_players)} players ranked")

# Save season data
with open('data/seasons/2022.json', 'w', encoding='utf-8') as f:
    json.dump(season_2022, f, indent=2, ensure_ascii=False)

print(f"\n✅ Created data/seasons/2022.json")

# Create lookup for season data
season_lookup = {}
for pos, rankings in season_2022['ppr_rankings'].items():
    for entry in rankings:
        season_lookup[entry['player_id']] = {
            'finish': f"{pos} {entry['rank']}",
            'points': entry['ppr']
        }

# Update HTML
print("\n📝 Updating HTML...")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find 2022 draft section
start_tag = 'id="draft-2022"'
start_index = html.find(start_tag)
if start_index == -1:
    print("  ❌ 2022 draft section not found!")
    exit(1)

section_start = html.rfind('<div', 0, start_index)
section_end = html.find('id="draft-2021"', section_start)
if section_end == -1:
    section_end = html.find('</section>', section_start)

draft_section = html[section_start:section_end]

# Pattern to match rows
row_pattern = re.compile(
    r'<tr><td>(\d+)</td><td>(\d+)</td><td>([^<]+)\s+\(([^,]+),\s*([^)]+)\)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>(<span[^>]*>[^<]+</span>|[^<]+)</td></tr>'
)

def update_row(match):
    round_num, pick_num, player_name, team_abbr, position, owner, draft_pos, old_season_finish, old_points, old_value = match.groups()
    
    player_name = player_name.strip()
    normalized_name = normalize_name(player_name)
    
    # Find player_id
    player_id = None
    if normalized_name in player_id_lookup:
        player_id = player_id_lookup[normalized_name][0]
    else:
        for norm_name, (pid, orig_name) in player_id_lookup.items():
            if normalized_name in norm_name or norm_name in normalized_name:
                player_id = pid
                break
    
    # Get season data
    season_finish = "—"
    points = "—"
    value = '<span class="value-miss">✗</span>'
    
    if player_id and player_id in season_lookup:
        season_finish = season_lookup[player_id]['finish']
        points = f"{season_lookup[player_id]['points']:.1f}"
        value = calculate_value_icon(draft_pos, season_finish)
    
    return (f'<tr><td>{round_num}</td><td>{pick_num}</td><td>{player_name} ({team_abbr}, {position})</td>'
            f'<td>{owner}</td><td>{draft_pos}</td><td>{season_finish}</td><td>{points}</td><td>{value}</td></tr>')

# Update all rows
new_draft_section = re.sub(row_pattern, update_row, draft_section)

# Replace in HTML
html = html[:section_start] + new_draft_section + html[section_end:]

# Write updated HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"  ✅ Updated {len(draft_2022['picks'])} rows in HTML")

print("\n" + "="*70)
print("✅ 2022 DRAFT UPDATE COMPLETE!")
print("="*70)
print(f"\nCreated:")
print(f"  - data/seasons/2022.json")
print(f"  - Updated index.html with season data")
print(f"\nTotal players processed: {len(ppr_entries)}")

