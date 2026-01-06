"""
Calculate draft statistics for each member profile.
Generates comprehensive draft analytics from draft and season data.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

def normalize_player_id(name):
    """Normalize player name to player_id format."""
    # Remove suffixes
    for suffix in [' Jr.', ' Sr.', ' II', ' III', ' IV']:
        name = name.replace(suffix, '')
    # Remove punctuation and spaces, lowercase
    return ''.join(c.lower() for c in name if c.isalnum())

def calculate_value(draft_pos_num, season_finish_num):
    """Calculate value based on draft position and season finish."""
    if season_finish_num is None:
        return None, "miss"
    
    diff = draft_pos_num - season_finish_num
    
    if diff >= 30:
        return diff, "super_hit"
    elif diff >= 15:
        return diff, "extreme_hit"
    elif diff >= 6:
        return diff, "hit"
    elif abs(diff) <= 5:
        return diff, "push"
    else:
        return diff, "miss"

def parse_draft_pos(draft_pos_str):
    """Parse draft position string (e.g., 'RB 5') to number."""
    if not draft_pos_str or draft_pos_str == "—":
        return None
    try:
        parts = draft_pos_str.split()
        if len(parts) >= 2:
            return int(parts[1])
    except:
        pass
    return None

def parse_season_finish(season_finish_str):
    """Parse season finish string (e.g., 'RB 3') to number."""
    if not season_finish_str or season_finish_str == "—":
        return None
    try:
        parts = season_finish_str.split()
        if len(parts) >= 2:
            return int(parts[1])
    except:
        pass
    return None

def load_all_drafts():
    """Load all draft JSON files."""
    drafts = {}
    drafts_dir = Path("data/drafts")
    for year_file in sorted(drafts_dir.glob("*.json")):
        year = int(year_file.stem)
        with open(year_file, 'r') as f:
            drafts[year] = json.load(f)
    return drafts

def load_all_seasons():
    """Load all season JSON files."""
    seasons = {}
    seasons_dir = Path("data/seasons")
    for year_file in sorted(seasons_dir.glob("*.json")):
        year = int(year_file.stem)
        with open(year_file, 'r') as f:
            seasons[year] = json.load(f)
    return seasons

def get_season_finish(player_id, position, year, seasons_data):
    """Get season finish for a player in a given year."""
    if year not in seasons_data:
        return None, None
    
    season = seasons_data[year]
    position_key = position.upper()
    
    if position_key not in season.get("ppr_rankings", {}):
        return None, None
    
    rankings = season["ppr_rankings"][position_key]
    for entry in rankings:
        if entry["player_id"] == player_id:
            return entry["rank"], entry["ppr"]
    
    return None, None

def calculate_member_stats():
    """Calculate draft statistics for all members."""
    drafts = load_all_drafts()
    seasons = load_all_seasons()
    
    # Load players to get positions
    with open("data/players.json", 'r') as f:
        players_data = json.load(f)
    
    # Initialize member stats
    member_stats = defaultdict(lambda: {
        "total_picks": 0,
        "hits": 0,
        "misses": 0,
        "pushes": 0,
        "extreme_hits": 0,
        "super_hits": 0,
        "picks_by_year": defaultdict(list),
        "picks_by_position": defaultdict(list),
        "best_picks": [],
        "worst_picks": [],
        "round_stats": defaultdict(lambda: {"hits": 0, "misses": 0, "pushes": 0, "total": 0})
    })
    
    # Process each draft year
    for year, draft_data in drafts.items():
        for pick in draft_data.get("picks", []):
            owner = pick.get("owner")
            if not owner:
                continue
            
            player_id = pick.get("player_id")
            draft_pos_str = pick.get("draft_pos", "")
            round_num = pick.get("round", 0)
            
            # Get player info
            player_info = players_data.get("players", {}).get(player_id, {})
            player_name = player_info.get("name", "Unknown")
            positions = player_info.get("positions", [])
            position = positions[0] if positions else "UNK"
            
            # Parse draft position
            draft_pos_num = parse_draft_pos(draft_pos_str)
            
            # Get season finish
            season_finish_num, ppr_points = get_season_finish(player_id, position, year, seasons)
            
            # Calculate value
            value_diff, value_type = calculate_value(draft_pos_num, season_finish_num)
            
            # Create pick record
            pick_record = {
                "year": year,
                "round": round_num,
                "pick": pick.get("pick", 0),
                "player_id": player_id,
                "player_name": player_name,
                "position": position,
                "draft_pos": draft_pos_str,
                "draft_pos_num": draft_pos_num,
                "season_finish": f"{position} {season_finish_num}" if season_finish_num else "—",
                "season_finish_num": season_finish_num,
                "ppr_points": ppr_points,
                "value_diff": value_diff,
                "value_type": value_type
            }
            
            # Update member stats
            stats = member_stats[owner]
            stats["total_picks"] += 1
            stats["picks_by_year"][year].append(pick_record)
            stats["picks_by_position"][position].append(pick_record)
            stats["round_stats"][round_num]["total"] += 1
            
            if value_type == "hit":
                stats["hits"] += 1
                stats["round_stats"][round_num]["hits"] += 1
            elif value_type == "extreme_hit":
                stats["hits"] += 1
                stats["extreme_hits"] += 1
                stats["round_stats"][round_num]["hits"] += 1
            elif value_type == "super_hit":
                stats["hits"] += 1
                stats["super_hits"] += 1
                stats["round_stats"][round_num]["hits"] += 1
            elif value_type == "miss":
                stats["misses"] += 1
                stats["round_stats"][round_num]["misses"] += 1
            elif value_type == "push":
                stats["pushes"] += 1
                stats["round_stats"][round_num]["pushes"] += 1
            
            # Track best/worst picks
            if value_diff is not None:
                if value_diff > 0:  # Positive value (hit)
                    stats["best_picks"].append(pick_record)
                elif value_diff < -5:  # Miss
                    stats["worst_picks"].append(pick_record)
    
    # Sort and limit best/worst picks
    for owner, stats in member_stats.items():
        stats["best_picks"].sort(key=lambda x: x.get("value_diff", 0) or 0, reverse=True)
        stats["best_picks"] = stats["best_picks"][:10]
        
        stats["worst_picks"].sort(key=lambda x: x.get("value_diff", 0) or 0)
        stats["worst_picks"] = stats["worst_picks"][:10]
        
        # Calculate hit rate
        total_with_result = stats["hits"] + stats["misses"] + stats["pushes"]
        stats["hit_rate"] = (stats["hits"] / total_with_result * 100) if total_with_result > 0 else 0
        
        # Calculate average value
        all_values = [p.get("value_diff", 0) or 0 for picks in stats["picks_by_year"].values() for p in picks if p.get("value_diff") is not None]
        stats["avg_value"] = sum(all_values) / len(all_values) if all_values else 0
    
    return dict(member_stats)

def generate_profile_json(member_name, stats):
    """Generate JSON file for a member profile."""
    # Normalize member name to filename
    filename = member_name.lower().replace(" ", "-")
    
    output_dir = Path("data/profiles")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{filename}.json"
    
    # Convert defaultdicts to regular dicts for JSON serialization
    output_data = {
        "member": member_name,
        "draft_stats": {
            "total_picks": stats["total_picks"],
            "total_hits": stats["hits"],
            "total_misses": stats["misses"],
            "total_pushes": stats["pushes"],
            "extreme_hits": stats["extreme_hits"],
            "super_hits": stats["super_hits"],
            "hit_rate": round(stats["hit_rate"], 1),
            "avg_value": round(stats["avg_value"], 1),
            "best_pick": stats["best_picks"][0] if stats["best_picks"] else None,
            "worst_pick": stats["worst_picks"][0] if stats["worst_picks"] else None
        },
        "picks_by_year": {str(k): v for k, v in stats["picks_by_year"].items()},
        "picks_by_position": {k: v for k, v in stats["picks_by_position"].items()},
        "round_stats": {str(k): v for k, v in stats["round_stats"].items()},
        "top_10_best_picks": stats["best_picks"][:10],
        "top_10_worst_picks": stats["worst_picks"][:10]
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    return output_file

def main():
    """Main execution."""
    print("=" * 70)
    print("CALCULATING PROFILE DRAFT STATISTICS")
    print("=" * 70)
    print()
    
    print("Loading draft and season data...")
    member_stats = calculate_member_stats()
    
    print(f"✅ Calculated stats for {len(member_stats)} members")
    print()
    
    print("Generating profile JSON files...")
    for member_name, stats in member_stats.items():
        output_file = generate_profile_json(member_name, stats)
        print(f"  ✅ {member_name}: {output_file}")
    
    print()
    print("=" * 70)
    print("✅ PROFILE STATS GENERATION COMPLETE!")
    print("=" * 70)
    print()
    
    # Print summary
    print("\n📊 Summary Statistics:")
    for member_name, stats in sorted(member_stats.items()):
        print(f"\n{member_name}:")
        print(f"  Total Picks: {stats['total_picks']}")
        print(f"  Hit Rate: {stats['hit_rate']:.1f}%")
        print(f"  Hits: {stats['hits']} | Misses: {stats['misses']} | Pushes: {stats['pushes']}")
        print(f"  Extreme Hits: {stats['extreme_hits']} | Super Hits: {stats['super_hits']}")
        if stats['best_picks']:
            best = stats['best_picks'][0]
            print(f"  Best Pick: {best['player_name']} ({best['year']}) - {best['draft_pos']} → {best['season_finish']} (diff: +{best['value_diff']})")
        if stats['worst_picks']:
            worst = stats['worst_picks'][0]
            print(f"  Worst Pick: {worst['player_name']} ({worst['year']}) - {worst['draft_pos']} → {worst['season_finish']} (diff: {worst['value_diff']})")

if __name__ == "__main__":
    main()

