import re
import json
from pathlib import Path

# Load corrected stats
with open('data/profile_stats_corrected.json', 'r') as f:
    stats_data = json.load(f)

profiles_dir = Path("profiles")
profile_files = list(profiles_dir.glob("*.html"))

for profile_file in profile_files:
    if profile_file.name in ["profile.css", "DRAFT_STATS_IMPLEMENTATION_GUIDE.md"]:
        continue
    
    profile_key = profile_file.stem.lower()
    stats = stats_data.get(profile_key, {})
    
    if not stats:
        print(f"No stats found for {profile_key}, skipping")
        continue
    
    print(f"Updating {profile_file.name}...")
    
    with open(profile_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update championships
    championships = stats.get('championships', 0)
    content = re.sub(
        r'<span class="stat-value">\d+</span>\s*<span class="stat-label">Championships</span>',
        f'<span class="stat-value">{championships}</span>\n                        <span class="stat-label">Championships</span>',
        content
    )
    
    # Update runner-ups
    runner_ups = stats.get('runner_ups', 0)
    content = re.sub(
        r'<span class="stat-value">\d+</span>\s*<span class="stat-label">Runner-Up</span>',
        f'<span class="stat-value">{runner_ups}</span>\n                        <span class="stat-label">Runner-Up</span>',
        content
    )
    
    # Update playoff record
    playoff_record = stats.get('playoff_record', '—')
    content = re.sub(
        r'<span class="stat-value">[^<]*</span>\s*<span class="stat-label">Playoff Record</span>',
        f'<span class="stat-value">{playoff_record}</span>\n                        <span class="stat-label">Playoff Record</span>',
        content
    )
    
    # Update playoff appearances
    playoff_appearances = stats.get('playoff_appearances', 0)
    content = re.sub(
        r'<span class="stat-value">\d+</span>\s*<span class="stat-label">Playoff Appearances</span>',
        f'<span class="stat-value">{playoff_appearances}</span>\n                        <span class="stat-label">Playoff Appearances</span>',
        content
    )
    
    with open(profile_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated {profile_file.name}: {championships} championships, {runner_ups} runner-ups, {playoff_record} playoff record, {playoff_appearances} appearances")

print("\nDone!")

