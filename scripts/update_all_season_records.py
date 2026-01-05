import re
import json
from pathlib import Path

# Load extracted records
with open('data/member_season_records.json', 'r') as f:
    records_data = json.load(f)

profiles_dir = Path("profiles")
profile_files = list(profiles_dir.glob("*.html"))

for profile_file in profile_files:
    if profile_file.name in ["profile.css", "DRAFT_STATS_IMPLEMENTATION_GUIDE.md"]:
        continue
    
    profile_key = profile_file.stem.lower()
    records = records_data.get(profile_key, {})
    
    if not records:
        print(f"No records found for {profile_key}, skipping")
        continue
    
    print(f"Updating {profile_file.name}...")
    
    with open(profile_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update season record
    season_record = records.get('season_record', '—')
    # Replace the em dash or any existing value
    content = re.sub(
        r'<span class="stat-value">[^<]*</span>\s*<span class="stat-label">Season Record</span>',
        f'<span class="stat-value">{season_record}</span>\n                                <span class="stat-label">Season Record</span>',
        content
    )
    
    # Update playoff record
    playoff_record = records.get('playoff_record', '—')
    # Replace the em dash or any existing value
    content = re.sub(
        r'<span class="stat-value">[^<]*</span>\s*<span class="stat-label">Playoff Record</span>',
        f'<span class="stat-value">{playoff_record}</span>\n                                <span class="stat-label">Playoff Record</span>',
        content
    )
    
    with open(profile_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated {profile_file.name} with {season_record} / {playoff_record}")

print("\nDone!")

