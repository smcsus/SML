"""
Rebuild HTML draft sections from JSON data.
This is the core of the data-driven architecture.
"""

import json
from pathlib import Path

def normalize_team_display(team):
    """Convert normalized team to display format"""
    # Map back to common abbreviations for display
    display_map = {
        "KAN": "KC", "SFO": "SF", "GNB": "GB", "NOR": "NO", 
        "TAM": "TB", "WAS": "WSH", "LVR": "LV", "NWE": "NE"
    }
    return display_map.get(team, team)

def calculate_value_icon(draft_pos_str, season_finish_str):
    """Calculate value icon based on draft position vs season finish"""
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

def generate_draft_table_rows(year, draft_data, season_data, players_data):
    """Generate HTML table rows for a draft year"""
    rows = []
    
    # Create lookup for season rankings
    season_lookup = {}
    if season_data and 'ppr_rankings' in season_data:
        for position, rankings in season_data['ppr_rankings'].items():
            for ranking in rankings:
                player_id = ranking['player_id']
                season_lookup[player_id] = {
                    'finish': f"{position} {ranking['rank']}",
                    'points': f"{ranking['ppr']:.1f}"
                }
    
    for pick in draft_data['picks']:
        player_id = pick['player_id']
        
        # Get player info
        if player_id not in players_data['players']:
            print(f"  ⚠️  Warning: Player {player_id} not found in players database")
            continue
        
        player = players_data['players'][player_id]
        player_name = player['name']
        
        # Get team for this year
        team_normalized = player['teams_by_year'].get(str(year), '—')
        team_display = normalize_team_display(team_normalized)
        
        # Get position
        position = player['positions'][0] if player['positions'] else '—'
        
        # Get season finish and points
        season_finish = '—'
        points = '—'
        if player_id in season_lookup:
            season_finish = season_lookup[player_id]['finish']
            points = season_lookup[player_id]['points']
        
        # Calculate value
        draft_pos = pick.get('draft_pos', '—')
        value_icon = calculate_value_icon(draft_pos, season_finish)
        
        # Build row
        row = f'                            <tr><td>{pick["round"]}</td><td>{pick["pick"]}</td>'
        row += f'<td>{player_name} ({team_display}, {position})</td>'
        row += f'<td>{pick["owner"]}</td>'
        row += f'<td>{draft_pos}</td>'
        row += f'<td>{season_finish}</td>'
        row += f'<td>{points}</td>'
        row += f'<td>{value_icon}</td></tr>'
        
        rows.append(row)
    
    return '\n'.join(rows)

def rebuild_draft_section(year):
    """Rebuild a single draft section"""
    print(f"\n📅 Rebuilding {year} draft section...")
    
    # Load data
    try:
        with open(f'data/drafts/{year}.json', 'r', encoding='utf-8') as f:
            draft_data = json.load(f)
    except FileNotFoundError:
        print(f"  ⚠️  Draft file not found: data/drafts/{year}.json")
        return None
    
    try:
        with open(f'data/seasons/{year}.json', 'r', encoding='utf-8') as f:
            season_data = json.load(f)
    except FileNotFoundError:
        print(f"  ⚠️  Season file not found: data/seasons/{year}.json (using empty data)")
        season_data = None
    
    with open('data/players.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    
    # Generate table rows
    rows = generate_draft_table_rows(year, draft_data, season_data, players_data)
    
    print(f"  ✅ Generated {len(draft_data['picks'])} rows")
    return rows

def main():
    """Main function to rebuild HTML sections"""
    print("="*70)
    print("REBUILDING HTML FROM JSON DATA")
    print("="*70)
    
    # Rebuild each year
    years = ['2025', '2024', '2023']
    generated_sections = {}
    
    for year in years:
        rows = rebuild_draft_section(year)
        if rows:
            generated_sections[year] = rows
    
    print(f"\n{'='*70}")
    print("✅ HTML generation complete!")
    print(f"{'='*70}")
    print("\nGenerated sections:")
    for year, rows in generated_sections.items():
        row_count = len(rows.split('</tr>')) - 1
        print(f"  {year}: {row_count} rows")
    
    print("\n💡 Next step: Use these generated rows to replace sections in index.html")
    print("   Or create a full HTML template system")
    
    # Optionally save to file for review
    with open('data/generated_html_sections.json', 'w', encoding='utf-8') as f:
        json.dump(generated_sections, f, indent=2, ensure_ascii=False)
    print("\n💾 Generated sections saved to data/generated_html_sections.json")

if __name__ == '__main__':
    main()

