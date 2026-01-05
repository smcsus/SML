#!/usr/bin/env python3
"""
Generate biographies for all SML members based on their profile data.
Moves Biography section to the top and generates personalized content.
"""

import json
import re
import os
from pathlib import Path

# Profile directory
PROFILES_DIR = Path("profiles")
DATA_DIR = Path("data/profiles")

# Team abbreviation to full name mapping
TEAM_NAMES = {
    "KC": "Kansas City Chiefs", "KAN": "Kansas City Chiefs",
    "SF": "San Francisco 49ers", "SFO": "San Francisco 49ers",
    "GB": "Green Bay Packers", "GNB": "Green Bay Packers",
    "NO": "New Orleans Saints", "NOR": "New Orleans Saints",
    "TB": "Tampa Bay Buccaneers", "TAM": "Tampa Bay Buccaneers",
    "WSH": "Washington Commanders", "WAS": "Washington Commanders",
    "LV": "Las Vegas Raiders", "LVR": "Las Vegas Raiders",
    "NE": "New England Patriots", "NWE": "New England Patriots",
    "BAL": "Baltimore Ravens",
    "CIN": "Cincinnati Bengals",
    "ATL": "Atlanta Falcons",
    "BUF": "Buffalo Bills",
    "IND": "Indianapolis Colts",
    "LAR": "Los Angeles Rams",
    "NYJ": "New York Jets",
    "DAL": "Dallas Cowboys",
    "MIA": "Miami Dolphins",
    "DET": "Detroit Lions",
    "PHI": "Philadelphia Eagles",
    "ARI": "Arizona Cardinals",
    "HOU": "Houston Texans",
    "JAX": "Jacksonville Jaguars",
    "MIN": "Minnesota Vikings",
    "TEN": "Tennessee Titans",
    "CAR": "Carolina Panthers",
    "CLE": "Cleveland Browns",
    "PIT": "Pittsburgh Steelers",
    "DEN": "Denver Broncos",
    "CHI": "Chicago Bears",
    "SEA": "Seattle Seahawks",
    "LAC": "Los Angeles Chargers",
    "NYG": "New York Giants"
}

def extract_profile_stats(html_content):
    """Extract league stats from HTML."""
    stats = {}
    
    # Championships
    match = re.search(r'<span class="stat-value">(\d+)</span>\s*<span class="stat-label">Championships</span>', html_content)
    if match:
        stats['championships'] = int(match.group(1))
    
    # Runner-ups
    match = re.search(r'<span class="stat-value">(\d+)</span>\s*<span class="stat-label">Runner-Up</span>', html_content)
    if match:
        stats['runner_ups'] = int(match.group(1))
    
    # Seasons
    match = re.search(r'<span class="stat-value">(\d+)</span>\s*<span class="stat-label">Seasons</span>', html_content)
    if match:
        stats['seasons'] = int(match.group(1))
    
    # Season Record
    match = re.search(r'<span class="stat-value">([\d-]+)</span>\s*<span class="stat-label">Season Record</span>', html_content)
    if match:
        stats['season_record'] = match.group(1)
    
    # Playoff Appearances
    match = re.search(r'<span class="stat-value">(\d+)</span>\s*<span class="stat-label">Playoff Appearances</span>', html_content)
    if match:
        stats['playoff_appearances'] = int(match.group(1))
    
    # Extract league history
    history_items = re.findall(r'<span class="history-year">(\d+)</span>\s*<span class="history-event[^"]*">([^<]+)</span>', html_content)
    stats['history'] = history_items
    
    return stats

def get_franchise_player_info(profile_data):
    """Get franchise player information from tendencies."""
    tendencies = profile_data.get('tendencies', {})
    franchise = tendencies.get('franchise_player')
    if franchise and franchise.get('count', 0) >= 3:
        return {
            'name': franchise['player_name'],
            'count': franchise['count'],
            'years': franchise.get('years', [])
        }
    return None

def get_theme_team_info(profile_data):
    """Get theme team information from tendencies."""
    tendencies = profile_data.get('tendencies', {})
    theme_team = tendencies.get('theme_team')
    if theme_team:
        team_abbr = theme_team['team']
        team_name = TEAM_NAMES.get(team_abbr, team_abbr)
        return {
            'team': team_name,
            'count': theme_team['count'],
            'year': theme_team.get('year')
        }
    return None

def generate_biography(member_name, profile_stats, profile_data):
    """Generate a personalized biography as a single 4-6 line paragraph."""
    sentences = []
    
    stats = profile_data.get('draft_stats', {})
    total_picks = stats.get('total_picks', 0)
    hit_rate = stats.get('hit_rate', 0)
    best_pick = stats.get('best_pick')
    super_hits = stats.get('super_hits', 0)
    extreme_hits = stats.get('extreme_hits', 0)
    avg_value = stats.get('avg_value', 0)
    
    seasons = profile_stats.get('seasons', 0)
    championships = profile_stats.get('championships', 0)
    runner_ups = profile_stats.get('runner_ups', 0)
    playoff_apps = profile_stats.get('playoff_appearances', 0)
    
    # Opening sentence - league tenure and accomplishments
    if seasons >= 8:
        if championships > 0:
            sentences.append(f"{member_name} is a seasoned veteran of the Sunday Movie League, having competed for {seasons} seasons and captured {championships} championship{'s' if championships > 1 else ''}.")
        elif runner_ups > 0:
            sentences.append(f"{member_name} is a league veteran with {seasons} seasons of experience, bringing consistency and dedication despite {runner_ups} runner-up finish{'es' if runner_ups > 1 else ''}.")
        else:
            sentences.append(f"{member_name} is a league veteran with {seasons} seasons of experience in the Sunday Movie League, bringing consistency and dedication to every draft.")
    elif seasons >= 5:
        sentences.append(f"With {seasons} seasons under their belt, {member_name} has established themselves as a reliable competitor in the Sunday Movie League.")
    else:
        sentences.append(f"{member_name} is a{'n emerging' if seasons <= 2 else ''} member of the Sunday Movie League, bringing{' fresh' if seasons <= 2 else ''} energy to the league.")
    
    # Championship/Runner-up highlights (if not already mentioned)
    if championships > 0 and seasons < 8:
        if runner_ups > 0:
            sentences.append(f"With {championships} championship{'s' if championships > 1 else ''} and {runner_ups} runner-up finish{'es' if runner_ups > 1 else ''}, they have proven their ability to compete at the highest level.")
        else:
            sentences.append(f"A {championships}-time champion, they know what it takes to build a winning roster and execute when it matters most.")
    elif runner_ups > 0 and seasons < 8:
        sentences.append(f"Despite {runner_ups} runner-up finish{'es' if runner_ups > 1 else ''}, they continue to chase that elusive first championship.")
    
    # Draft performance
    if hit_rate >= 25:
        sentences.append(f"Known for their sharp eye in the draft, they maintain a {hit_rate:.1f}% hit rate across {total_picks} career picks, consistently finding value in the later rounds.")
    elif hit_rate >= 15:
        sentences.append(f"With a {hit_rate:.1f}% hit rate over {total_picks} career picks, they have shown flashes of draft brilliance mixed with the occasional miss.")
    else:
        sentences.append(f"While their {hit_rate:.1f}% hit rate over {total_picks} picks may not jump off the page, they continue to refine their draft strategy season after season.")
    
    # Best pick or super hits highlight (pick one)
    if best_pick and best_pick.get('value_diff', 0) >= 20:
        player_name = best_pick.get('player_name', 'a player')
        year = best_pick.get('year')
        draft_pos = best_pick.get('draft_pos', '')
        season_finish = best_pick.get('season_finish', '')
        sentences.append(f"Their greatest draft steal came in {year} when they selected {player_name} at {draft_pos}, who finished the season as {season_finish} - a {best_pick.get('value_diff', 0)}-spot difference that exemplifies their ability to find hidden gems.")
    elif super_hits > 0:
        sentences.append(f"They have discovered {super_hits} super extreme hit{'s' if super_hits > 1 else ''} (30+ spot difference), showcasing their talent for identifying breakout players before the rest of the league catches on.")
    elif extreme_hits >= 3:
        sentences.append(f"With {extreme_hits} extreme hits to their name, they have demonstrated a knack for finding players who significantly outperform their draft position.")
    
    # Franchise player or theme team (if notable)
    franchise_info = get_franchise_player_info(profile_data)
    if franchise_info and len(sentences) < 5:
        years_str = ', '.join(map(str, franchise_info['years']))
        sentences.append(f"Known for their loyalty, they have drafted {franchise_info['name']} {franchise_info['count']} times ({years_str}), earning them the distinction of a true franchise player.")
    
    # Value hunter (if notable and space available)
    if avg_value >= 5 and len(sentences) < 5:
        sentences.append(f"With an average value of +{avg_value:.1f} spots per pick, they consistently find players who outperform their draft position, making them a true value hunter in the draft.")
    
    # Closing sentence - playoff appearances or future outlook
    if playoff_apps >= 3 and len(sentences) < 6:
        sentences.append(f"With {playoff_apps} playoff appearance{'s' if playoff_apps > 1 else ''} to their name, they have proven they can consistently build competitive rosters and make deep postseason runs.")
    elif seasons >= 5 and len(sentences) < 6:
        sentences.append(f"As they continue their journey in the Sunday Movie League, they look to build on their experience and chase championship glory.")
    elif len(sentences) < 6:
        sentences.append(f"Still early in their SML career, they have plenty of time to develop their draft strategy and make their mark on league history.")
    
    # Combine into single paragraph (4-6 sentences)
    # Take first 6 sentences max, ensure at least 4
    final_sentences = sentences[:6]
    if len(final_sentences) < 4:
        final_sentences = sentences[:4] if len(sentences) >= 4 else sentences
    
    paragraph_text = ' '.join(final_sentences)
    
    return f'<p>{paragraph_text}</p>'

def move_biography_to_top(html_content):
    """Move Biography section to appear right after profile stats and before Draft Statistics."""
    # Find the Biography section (more flexible pattern)
    bio_match = re.search(
        r'(<section class="profile-section">\s*<h2 class="section-heading">Biography</h2>.*?</section>)',
        html_content,
        re.DOTALL
    )
    
    if not bio_match:
        return html_content
    
    bio_section = bio_match.group(1)
    
    # Remove the original Biography section
    html_content = html_content.replace(bio_section, '', 1)
    
    # Find where to insert it - look for closing divs after profile-stats
    # Try multiple patterns
    patterns = [
        r'(</div>\s*</div>\s*\n\s*<!-- Draft Statistics Section -->)',  # Exact match
        r'(</div>\s*</div>\s*(?:\n\s*)?<!-- Draft Statistics Section -->)',  # Flexible whitespace
        r'(</div>\s*</div>\s*(?:\n\s*)?<!-- Draft)',  # Partial match
        r'(<!-- Draft Statistics Section -->)',  # Just the comment
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            # Insert Biography section before Draft Statistics
            insert_point = match.start()
            before = html_content[:insert_point]
            after = html_content[insert_point:]
            
            # Clean up any existing Biography Section comment
            before = re.sub(r'\s*<!-- Biography Section -->\s*', '', before)
            
            # Insert the biography
            html_content = before + '\n\n        <!-- Biography Section -->\n        ' + bio_section + '\n\n        ' + after
            break
    
    return html_content

def process_profile(html_file):
    """Process a single profile HTML file."""
    print(f"Processing {html_file.name}...")
    
    # Read HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract member name from HTML - try multiple patterns
    name_match = re.search(r'<h1 class="profile-name">([^<]+)</h1>', html_content)
    if not name_match:
        # Try alternative pattern with more whitespace
        name_match = re.search(r'<h1[^>]*class="profile-name"[^>]*>([^<]+)</h1>', html_content)
    if not name_match:
        # Try to get from filename as fallback
        member_name = html_file.stem.capitalize()
        print(f"  Using filename as member name: {member_name}")
    else:
        member_name = name_match.group(1).strip()
    
    # Extract profile stats from HTML
    profile_stats = extract_profile_stats(html_content)
    
    # Load profile JSON data
    json_file = DATA_DIR / f"{html_file.stem}.json"
    if not json_file.exists():
        print(f"  No JSON data found for {member_name}, using basic biography")
        profile_data = {}
    else:
        with open(json_file, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
    
    # Generate biography
    biography_html = generate_biography(member_name, profile_stats, profile_data)
    
    # Check if Biography section exists
    bio_section_pattern = r'(<section class="profile-section">\s*<h2 class="section-heading">Biography</h2>\s*<div class="bio-content">).*?(</div>\s*</section>)'
    bio_match = re.search(bio_section_pattern, html_content, re.DOTALL)
    
    if bio_match:
        # Replace existing biography content - match the paragraph inside
        html_content = re.sub(
            r'(<div class="bio-content">)\s*<p>.*?</p>(\s*</div>)',
            r'\1\n                ' + biography_html + '\n            \2',
            html_content,
            flags=re.DOTALL
        )
    else:
        # Create new Biography section
        bio_section = f"""        <section class="profile-section">
            <h2 class="section-heading">Biography</h2>
            <div class="bio-content">
                {biography_html.replace(chr(10), chr(10) + '                ')}
            </div>
        </section>"""
        
        # Insert after profile-stats (before Draft Statistics)
        # Try multiple patterns
        patterns = [
            r'(</div>\s*</div>\s*\n\s*<!-- Draft Statistics Section -->)',
            r'(</div>\s*</div>\s*(?:\n\s*)?<!-- Draft Statistics Section -->)',
            r'(<!-- Draft Statistics Section -->)',
        ]
        
        inserted = False
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                if '<!-- Draft Statistics Section -->' in pattern:
                    # Insert before Draft Statistics
                    html_content = html_content.replace(
                        match.group(0),
                        f'        <!-- Biography Section -->\n        {bio_section}\n\n        <!-- Draft Statistics Section -->'
                    )
                else:
                    # Insert after closing divs
                    html_content = html_content.replace(
                        match.group(0),
                        f'</div>\n        </div>\n\n        <!-- Biography Section -->\n        {bio_section}\n\n        <!-- Draft Statistics Section -->'
                    )
                inserted = True
                break
        
        if not inserted:
            # Last resort: find the comment and insert before it
            html_content = html_content.replace(
                '<!-- Draft Statistics Section -->',
                f'        <!-- Biography Section -->\n        {bio_section}\n\n        <!-- Draft Statistics Section -->',
                1
            )
    
    # Move Biography section to top (if not already there)
    html_content = move_biography_to_top(html_content)
    
    # Write updated HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  ✓ Updated biography for {member_name}")

def main():
    """Process all profile HTML files."""
    if not PROFILES_DIR.exists():
        print(f"Error: {PROFILES_DIR} directory not found")
        return
    
    profile_files = list(PROFILES_DIR.glob("*.html"))
    
    if not profile_files:
        print("No profile HTML files found")
        return
    
    print(f"Found {len(profile_files)} profile files\n")
    
    for html_file in sorted(profile_files):
        try:
            process_profile(html_file)
        except Exception as e:
            print(f"  ✗ Error processing {html_file.name}: {e}")
    
    print(f"\n✓ Completed processing {len(profile_files)} profiles")

if __name__ == "__main__":
    main()

