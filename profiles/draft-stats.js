/**
 * Load and display draft statistics for member profiles
 */

// Map member aliases to their JSON filename
const memberFileMap = {
    'Lucas': 'lucas',
    'Jasper': 'jasper',
    'Masters': 'masters',
    'Kircher': 'kircher',
    'Cam': 'cam',
    'Hatter': 'hatter',
    'Sunny': 'sunny',
    'JMar': 'jmar',
    'JJ': 'jj',
    'Drew': 'drew',
    'Nuts': 'nuts',
    'PPWW': 'ppww',
    'D-Lew': 'd-lew',
    'Baker': 'baker',
    'Nate': 'nate',
    'Trey': 'trey'
};

function getValueIcon(valueType, valueDiff) {
    if (valueType === 'super_hit') {
        return '<span class="value-icon super-hit">💎</span>';
    } else if (valueType === 'extreme_hit') {
        return '<span class="value-icon extreme-hit">✓</span>';
    } else if (valueType === 'hit') {
        return '<span class="value-icon hit">✓</span>';
    } else if (valueType === 'push') {
        return '<span class="value-icon push">≈</span>';
    } else {
        return '<span class="value-icon miss">✗</span>';
    }
}

function formatValueDiff(diff) {
    if (diff === null || diff === undefined) return 'N/A';
    return diff > 0 ? `+${diff}` : `${diff}`;
}

async function loadDraftStats() {
    const profileNameElement = document.querySelector('.profile-name');
    if (!profileNameElement) {
        console.warn('Profile name not found');
        return;
    }

    const memberName = profileNameElement.textContent.trim();
    const filename = memberFileMap[memberName] || memberName.toLowerCase().replace(/\s+/g, '-');
    
    try {
        const response = await fetch(`../data/profiles/${filename}.json`);
        if (!response.ok) {
            console.warn(`Draft stats not found for ${memberName}`);
            return;
        }
        
        const data = await response.json();
        displayDraftStats(data);
        
        // Load players data for tendencies and achievements
        const playersResponse = await fetch('../data/players.json');
        if (playersResponse.ok) {
            const playersData = await playersResponse.json();
            displayDraftTendencies(data, playersData);
            await displayDraftAchievements(data, playersData);
        }
    } catch (error) {
        console.error('Error loading draft stats:', error);
    }
}

function displayDraftStats(data) {
    const stats = data.draft_stats;
    
    // Display draft stats table
    displayDraftStatsTable(data.picks_by_year || {}, stats);
}


function displayDraftStatsTable(picksByYear, overallStats) {
    const tbody = document.getElementById('draft-stats-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const years = Object.keys(picksByYear).sort((a, b) => parseInt(b) - parseInt(a));
    
    // Add year rows
    years.forEach(year => {
        const picks = picksByYear[year];
        const stats = calculateYearStats(picks);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="col-year">${year}</td>
            <td>${picks.length}</td>
            <td>${stats.hits}</td>
            <td>${stats.misses}</td>
            <td>${stats.pushes}</td>
            <td>${stats.hitRate.toFixed(1)}%</td>
            <td class="best-pick-cell">
                ${stats.bestPick ? `
                    <span class="pick-name">${stats.bestPick.player_name}</span>
                    <span class="pick-detail">${stats.bestPick.draft_pos} → ${stats.bestPick.season_finish}</span>
                ` : '<span class="pick-detail">—</span>'}
            </td>
            <td class="value-cell">
                ${stats.bestPick ? getValueIcon(stats.bestPick.value_type, stats.bestPick.value_diff) : '—'}
            </td>
            <td></td>
            <td class="worst-pick-cell">
                ${stats.worstPick ? `
                    <span class="pick-name">${stats.worstPick.player_name}</span>
                    <span class="pick-detail">${stats.worstPick.draft_pos} → ${stats.worstPick.season_finish}</span>
                ` : '<span class="pick-detail">—</span>'}
            </td>
            <td class="value-cell">
                ${stats.worstPick ? getValueIcon(stats.worstPick.value_type, stats.worstPick.value_diff) : '—'}
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // Add career totals row
    const careerRow = document.createElement('tr');
    careerRow.className = 'career-row';
    careerRow.innerHTML = `
        <td class="col-year"><strong>Career</strong></td>
        <td><strong>${overallStats.total_picks}</strong></td>
        <td><strong>${overallStats.total_hits}</strong></td>
        <td><strong>${overallStats.total_misses}</strong></td>
        <td><strong>${overallStats.total_pushes}</strong></td>
        <td><strong>${overallStats.hit_rate.toFixed(1)}%</strong></td>
        <td class="best-pick-cell">
            ${overallStats.best_pick ? `
                <span class="pick-name"><strong>${overallStats.best_pick.player_name}</strong></span>
                <span class="pick-detail">${overallStats.best_pick.draft_pos} → ${overallStats.best_pick.season_finish}</span>
            ` : '<span class="pick-detail">—</span>'}
        </td>
        <td class="value-cell">
            ${overallStats.best_pick ? getValueIcon(overallStats.best_pick.value_type, overallStats.best_pick.value_diff) : '—'}
        </td>
        <td></td>
        <td class="worst-pick-cell">
            ${overallStats.worst_pick ? `
                <span class="pick-name"><strong>${overallStats.worst_pick.player_name}</strong></span>
                <span class="pick-detail">${overallStats.worst_pick.draft_pos} → ${overallStats.worst_pick.season_finish}</span>
            ` : '<span class="pick-detail">—</span>'}
        </td>
        <td class="value-cell">
            ${overallStats.worst_pick ? getValueIcon(overallStats.worst_pick.value_type, overallStats.worst_pick.value_diff) : '—'}
        </td>
    `;
    tbody.appendChild(careerRow);
}

function calculateYearStats(picks) {
    let hits = 0, misses = 0, pushes = 0;
    let bestPick = null, worstPick = null;
    
    picks.forEach(pick => {
        if (pick.value_type === 'hit' || pick.value_type === 'extreme_hit' || pick.value_type === 'super_hit') {
            hits++;
            if (!bestPick || (pick.value_diff && pick.value_diff > (bestPick.value_diff || 0))) {
                bestPick = pick;
            }
        } else if (pick.value_type === 'miss') {
            misses++;
            if (!worstPick || (pick.value_diff && pick.value_diff < (worstPick.value_diff || 0))) {
                worstPick = pick;
            }
        } else if (pick.value_type === 'push') {
            pushes++;
        }
    });
    
    const total = hits + misses + pushes;
    const hitRate = total > 0 ? (hits / total) * 100 : 0;
    
    return { hits, misses, pushes, hitRate, bestPick, worstPick };
}

function displayDraftTendencies(profileData, playersData) {
    const container = document.getElementById('draft-tendencies-content');
    if (!container) return;
    
    const allPicks = [];
    Object.values(profileData.picks_by_year || {}).forEach(yearPicks => {
        allPicks.push(...yearPicks);
    });
    
    if (allPicks.length === 0) {
        container.innerHTML = '<p class="no-tendencies">No draft data available</p>';
        return;
    }
    
    // Calculate tendencies
    const franchisePlayers = findFranchisePlayers(allPicks);
    const themeTeams = findThemeTeams(allPicks, playersData);
    const positionPreferences = findPositionPreferences(allPicks);
    
    const insights = [];
    
    // Only add most significant franchise player
    if (franchisePlayers.length > 0 && franchisePlayers[0].count >= 3) {
        insights.push({
            label: 'Franchise Player',
            value: `${franchisePlayers[0].player_name} (${franchisePlayers[0].count}x)`,
            years: franchisePlayers[0].years
        });
    }
    
    // Only add most significant theme team
    if (themeTeams.length > 0) {
        insights.push({
            label: 'Theme Team',
            value: `${themeTeams[0].team} (${themeTeams[0].percentage}%)`
        });
    }
    
    // Early Round Strategy - what position they prioritize in rounds 1-3
    const earlyRoundStrategy = findEarlyRoundStrategy(allPicks);
    if (earlyRoundStrategy) {
        insights.push({
            label: 'Early Round Strategy',
            value: earlyRoundStrategy
        });
    }
    
    if (insights.length === 0) {
        container.innerHTML = '<p class="no-tendencies">No significant tendencies found</p>';
        return;
    }
    
    let html = '<div class="tendency-section">';
    insights.forEach(insight => {
        if (insight.years) {
            html += `<div class="tendency-item"><span class="tendency-label">${insight.label}:</span><span class="tendency-value">${insight.value}</span><span class="tendency-years">${insight.years.join(', ')}</span></div>`;
        } else {
            html += `<div class="tendency-item"><span class="tendency-label">${insight.label}:</span><span class="tendency-value">${insight.value}</span></div>`;
        }
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function findFranchisePlayers(allPicks) {
    const playerCounts = {};
    
    allPicks.forEach(pick => {
        const playerId = pick.player_id;
        if (!playerCounts[playerId]) {
            playerCounts[playerId] = {
                player_name: pick.player_name,
                count: 0,
                years: []
            };
        }
        playerCounts[playerId].count++;
        playerCounts[playerId].years.push(pick.year);
    });
    
    // Only show players drafted 3+ times
    return Object.values(playerCounts)
        .filter(p => p.count >= 3)
        .sort((a, b) => b.count - a.count)
        .slice(0, 3);
}

function findThemeTeams(allPicks, playersData) {
    const teamCounts = {};
    
    allPicks.forEach(pick => {
        const playerId = pick.player_id;
        const player = playersData.players[playerId];
        if (player && player.teams_by_year) {
            const year = pick.year.toString();
            const team = player.teams_by_year[year];
            if (team) {
                if (!teamCounts[team]) {
                    teamCounts[team] = 0;
                }
                teamCounts[team]++;
            }
        }
    });
    
    const totalPicks = allPicks.length;
    // Only show teams with 5+ players OR 15%+ of total picks
    return Object.entries(teamCounts)
        .map(([team, count]) => ({ 
            team, 
            count,
            percentage: ((count / totalPicks) * 100).toFixed(1)
        }))
        .filter(tt => tt.count >= 5 || parseFloat(tt.percentage) >= 15)
        .sort((a, b) => b.count - a.count)
        .slice(0, 3);
}

function findPositionPreferences(allPicks) {
    const positionCounts = {};
    
    allPicks.forEach(pick => {
        const pos = pick.position;
        if (!positionCounts[pos]) {
            positionCounts[pos] = 0;
        }
        positionCounts[pos]++;
    });
    
    return Object.entries(positionCounts)
        .map(([position, count]) => ({ position, count }))
        .sort((a, b) => b.count - a.count);
}

function findEarlyRoundStrategy(allPicks) {
    // Analyze rounds 1-3
    const earlyRoundPicks = allPicks.filter(pick => pick.round >= 1 && pick.round <= 3);
    if (earlyRoundPicks.length < 6) return null; // Need at least 6 picks to be meaningful
    
    const positionCounts = {};
    earlyRoundPicks.forEach(pick => {
        const pos = pick.position;
        if (!positionCounts[pos]) {
            positionCounts[pos] = 0;
        }
        positionCounts[pos]++;
    });
    
    const sorted = Object.entries(positionCounts)
        .map(([position, count]) => ({ position, count }))
        .sort((a, b) => b.count - a.count);
    
    if (sorted.length === 0) return null;
    
    const topPosition = sorted[0];
    const percentage = ((topPosition.count / earlyRoundPicks.length) * 100).toFixed(0);
    
    // Only show if one position is 40%+ of early round picks
    if (parseFloat(percentage) >= 40) {
        return `${topPosition.position} (${percentage}% of rounds 1-3)`;
    }
    
    return null;
}

async function displayDraftAchievements(profileData, playersData) {
    const container = document.getElementById('achievements-content');
    if (!container) {
        console.warn('Achievements container not found');
        return;
    }
    
    try {
        const allPicks = [];
        Object.values(profileData.picks_by_year || {}).forEach(yearPicks => {
            allPicks.push(...yearPicks);
        });
        
        if (allPicks.length === 0) {
            container.innerHTML = '<p class="no-achievements">No achievements available</p>';
            return;
        }
        
        const stats = profileData.draft_stats;
        if (!stats) {
            container.innerHTML = '<p class="no-achievements">No stats available</p>';
            return;
        }
        
        // Load league database for season-based achievements
        let leagueData = null;
        try {
            const leagueResponse = await fetch('../data/league_database.json');
            if (leagueResponse.ok) {
                leagueData = await leagueResponse.json();
            }
        } catch (error) {
            console.warn('Could not load league database:', error);
        }
        
        const achievements = await calculateAchievements(allPicks, stats, playersData, profileData.picks_by_year, leagueData);
        
        if (achievements.length === 0) {
            container.innerHTML = '<p class="no-achievements">No achievements earned yet</p>';
            return;
        }
        
        // Group achievements by name to show multiple years
        const achievementsByType = {};
        achievements.forEach(achievement => {
            const key = achievement.name;
            if (!achievementsByType[key]) {
                achievementsByType[key] = {
                    name: achievement.name,
                    icon: achievement.icon,
                    years: []
                };
            }
            achievementsByType[key].years.push({
                year: achievement.year,
                description: achievement.description
            });
        });
        
        // Sort years within each achievement type
        Object.values(achievementsByType).forEach(achievement => {
            achievement.years.sort((a, b) => parseInt(b.year) - parseInt(a.year));
        });
        
        let html = '<div class="achievements-grid">';
        Object.values(achievementsByType).forEach(achievement => {
            const yearsList = achievement.years.map(y => y.year).join(', ');
            
            // Build full tooltip with all years' details
            let fullDescription = '';
            if (achievement.years.length === 1) {
                fullDescription = achievement.years[0].description;
            } else {
                // Show full details for each year
                fullDescription = achievement.years.map(y => `${y.year}: ${y.description}`).join(' | ');
            }
            
            html += `
                <div class="achievement-badge" data-tooltip="${fullDescription.replace(/"/g, '&quot;')}">
                    <span class="achievement-icon">${achievement.icon}</span>
                    <span class="achievement-name">${achievement.name}</span>
                    <span class="achievement-year">${yearsList}</span>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error displaying achievements:', error);
        container.innerHTML = '<p class="no-achievements">Error loading achievements</p>';
    }
}

async function calculateAchievements(allPicks, stats, playersData, picksByYear, leagueData) {
    const achievements = [];
    
    // Sharpshooter - 30%+ hit rate in a single season (season-based award)
    if (picksByYear) {
        Object.keys(picksByYear).forEach(year => {
            const yearPicks = picksByYear[year];
            const yearStats = calculateYearStats(yearPicks);
            if (yearStats.hitRate >= 30) {
                achievements.push({
                    name: 'Sharpshooter',
                    icon: '🎯',
                    year: year,
                    description: `Achieved ${yearStats.hitRate.toFixed(1)}% hit rate in ${year}`
                });
            }
        });
    }
    
    // Diamond Miner - Super extreme hits by year
    if (picksByYear) {
        Object.keys(picksByYear).forEach(year => {
            const yearPicks = picksByYear[year];
            const superHits = yearPicks.filter(p => p.value_type === 'super_hit').length;
            if (superHits >= 1) {
                achievements.push({
                    name: 'Gem Hunter',
                    icon: '💎',
                    year: year,
                    description: `Drafted ${superHits} super extreme hit${superHits > 1 ? 's' : ''} in ${year} (30+ spot difference)`
                });
            }
        });
    }
    
    // Gold Digger - Extreme hits by year
    if (picksByYear) {
        Object.keys(picksByYear).forEach(year => {
            const yearPicks = picksByYear[year];
            const extremeHits = yearPicks.filter(p => p.value_type === 'extreme_hit').length;
            if (extremeHits >= 3) {
                achievements.push({
                    name: 'Gold Digger',
                    icon: '⭐',
                    year: year,
                    description: `Drafted ${extremeHits} extreme hits in ${year} (15+ spot difference)`
                });
            }
        });
    }
    
    // Franchise Tag - Same player 3+ times (career achievement, show first year they hit 3)
    const franchisePlayers = findFranchisePlayers(allPicks);
    if (franchisePlayers.length > 0 && franchisePlayers[0].count >= 3) {
        // Find the year they drafted the player for the 3rd time
        const playerPicks = allPicks.filter(p => p.player_id === franchisePlayers[0].player_id)
            .sort((a, b) => parseInt(a.year) - parseInt(b.year));
        if (playerPicks.length >= 3) {
            const thirdYear = playerPicks[2].year;
            achievements.push({
                name: 'Franchise Tag',
                icon: '🏷️',
                year: thirdYear,
                description: `Drafted ${franchisePlayers[0].player_name} for the 3rd time in ${thirdYear} (${franchisePlayers[0].count} total)`
            });
        }
    }
    
    // Prophet - Drafted a player who finished #1 at their position (by year)
    if (picksByYear) {
        Object.keys(picksByYear).forEach(year => {
            const yearPicks = picksByYear[year];
            const numberOnePicks = yearPicks.filter(p => p.season_finish_num === 1);
            if (numberOnePicks.length > 0) {
                // Show all #1 picks if multiple
                if (numberOnePicks.length === 1) {
                    achievements.push({
                        name: 'Prophet',
                        icon: '🔮',
                        year: year,
                        description: `Drafted ${numberOnePicks[0].player_name} who finished #1 at ${numberOnePicks[0].position} in ${year}`
                    });
                } else {
                    const playersList = numberOnePicks.map(p => `${p.player_name} (#1 ${p.position})`).join(', ');
                    achievements.push({
                        name: 'Prophet',
                        icon: '🔮',
                        year: year,
                        description: `Drafted ${numberOnePicks.length} players who finished #1 at their position in ${year}: ${playersList}`
                    });
                }
            }
        });
    }
    
    // Value Hunter - Average value of +5 or better by year
    if (picksByYear) {
        Object.keys(picksByYear).forEach(year => {
            const yearPicks = picksByYear[year];
            const yearValues = yearPicks.filter(p => p.value_diff !== null && p.value_diff !== undefined)
                .map(p => p.value_diff);
            if (yearValues.length > 0) {
                const avgValue = yearValues.reduce((a, b) => a + b, 0) / yearValues.length;
                if (avgValue >= 5) {
                    achievements.push({
                        name: 'Value Hunter',
                        icon: '💰',
                        year: year,
                        description: `Average value of +${avgValue.toFixed(1)} spots in ${year}`
                    });
                }
            }
        });
    }
    
    // Perfect Round - 100% hit rate in a single round (already has year)
    const perfectRounds = findAllPerfectRounds(allPicks);
    perfectRounds.forEach(round => {
        achievements.push({
            name: 'Perfect Round',
            icon: '✨',
            year: round.year,
            description: `100% hit rate in Round ${round.round} (${round.year})`
        });
    });
    
    // Homer - 4+ players from same NFL team in one year (already has year)
    const homerYears = findAllHomerYears(allPicks, playersData);
    homerYears.forEach(homer => {
        achievements.push({
            name: 'Homer',
            icon: '🏠',
            year: homer.year,
            description: `Drafted ${homer.count} players from ${homer.team} in ${homer.year}`
        });
    });
    
    // Late Round Legend - 40%+ hit rate in rounds 10+ by year
    if (picksByYear) {
        Object.keys(picksByYear).forEach(year => {
            const yearPicks = picksByYear[year];
            const lateRoundStats = calculateLateRoundStatsForYear(yearPicks);
            if (lateRoundStats.hitRate >= 40 && lateRoundStats.total >= 3) {
                achievements.push({
                    name: 'Late Legend',
                    icon: '🌙',
                    year: year,
                    description: `${lateRoundStats.hitRate.toFixed(0)}% hit rate in rounds 10+ in ${year} (${lateRoundStats.hits}/${lateRoundStats.total})`
                });
            }
        });
    }
    
    // Rising Star - 3+ consecutive years of improving hit rate (show first year of streak)
    if (picksByYear) {
        const risingStar = checkRisingStar(picksByYear);
        if (risingStar) {
            achievements.push({
                name: 'Rising Star',
                icon: '📈',
                year: risingStar.startYear,
                description: `3+ consecutive years of improving hit rate starting in ${risingStar.startYear}`
            });
        }
    }
    
    // Season-based achievements (require league data)
    if (leagueData && leagueData.seasons) {
        const profileNameElement = document.querySelector('.profile-name');
        const memberName = profileNameElement ? profileNameElement.textContent.trim() : '';
        const memberAlias = memberFileMap[memberName] || memberName.toLowerCase().replace(/\s+/g, '-');
        
        // Cookie - Led league in points_for in a season (all years)
        const pointsForLeaders = findPointsForLeaders(leagueData, memberAlias);
        pointsForLeaders.forEach(leader => {
            achievements.push({
                name: 'Want Cookie?',
                icon: '🍪',
                year: leader.year,
                description: `Led league in scoring in ${leader.year} with ${leader.points_for.toFixed(1)} points`
            });
        });
        
        // Cakewalk - Least points_against in a season (all years)
        const pointsAgainstLeaders = findPointsAgainstLeaders(leagueData, memberAlias);
        pointsAgainstLeaders.forEach(leader => {
            achievements.push({
                name: 'Cakewalk',
                icon: '🎂',
                year: leader.year,
                description: `Easiest schedule in ${leader.year} with only ${leader.points_against.toFixed(1)} points against`
            });
        });
        
        // Iron Will - Made playoffs despite bottom half scoring (all years)
        const ironWillYears = findAllIronWill(leagueData, memberAlias);
        ironWillYears.forEach(ironWill => {
            achievements.push({
                name: 'Iron Will',
                icon: '💪',
                year: ironWill.year,
                description: `Made playoffs in ${ironWill.year} despite ranking ${ironWill.points_rank}/${ironWill.total_teams} in scoring`
            });
        });
    }
    
    return achievements;
}

function findNumberOnePicks(allPicks) {
    return allPicks.filter(pick => {
        if (!pick.season_finish_num) return false;
        return pick.season_finish_num === 1;
    });
}

function findPerfectRound(allPicks) {
    const roundStats = {};
    
    allPicks.forEach(pick => {
        const key = `${pick.year}-${pick.round}`;
        if (!roundStats[key]) {
            roundStats[key] = {
                year: pick.year,
                round: pick.round,
                total: 0,
                hits: 0
            };
        }
        roundStats[key].total++;
        if (pick.value_type === 'hit' || pick.value_type === 'extreme_hit' || pick.value_type === 'super_hit') {
            roundStats[key].hits++;
        }
    });
    
    for (const key in roundStats) {
        const stats = roundStats[key];
        if (stats.total >= 3 && stats.hits === stats.total) {
            return stats;
        }
    }
    
    return null;
}

function findAllPerfectRounds(allPicks) {
    const roundStats = {};
    const perfectRounds = [];
    
    allPicks.forEach(pick => {
        const key = `${pick.year}-${pick.round}`;
        if (!roundStats[key]) {
            roundStats[key] = {
                year: pick.year,
                round: pick.round,
                total: 0,
                hits: 0
            };
        }
        roundStats[key].total++;
        if (pick.value_type === 'hit' || pick.value_type === 'extreme_hit' || pick.value_type === 'super_hit') {
            roundStats[key].hits++;
        }
    });
    
    for (const key in roundStats) {
        const stats = roundStats[key];
        if (stats.total >= 3 && stats.hits === stats.total) {
            perfectRounds.push(stats);
        }
    }
    
    return perfectRounds;
}

function findHomerYear(allPicks, playersData) {
    const yearTeamCounts = {};
    
    allPicks.forEach(pick => {
        const player = playersData.players[pick.player_id];
        if (player && player.teams_by_year) {
            const year = pick.year.toString();
            const team = player.teams_by_year[year];
            if (team) {
                const key = `${pick.year}-${team}`;
                if (!yearTeamCounts[key]) {
                    yearTeamCounts[key] = {
                        year: pick.year,
                        team: team,
                        count: 0
                    };
                }
                yearTeamCounts[key].count++;
            }
        }
    });
    
    for (const key in yearTeamCounts) {
        const data = yearTeamCounts[key];
        if (data.count >= 4) {
            return data;
        }
    }
    
    return null;
}

function findAllHomerYears(allPicks, playersData) {
    const yearTeamCounts = {};
    const homerYears = [];
    
    allPicks.forEach(pick => {
        const player = playersData.players[pick.player_id];
        if (player && player.teams_by_year) {
            const year = pick.year.toString();
            const team = player.teams_by_year[year];
            if (team) {
                const key = `${pick.year}-${team}`;
                if (!yearTeamCounts[key]) {
                    yearTeamCounts[key] = {
                        year: pick.year,
                        team: team,
                        count: 0
                    };
                }
                yearTeamCounts[key].count++;
            }
        }
    });
    
    for (const key in yearTeamCounts) {
        const data = yearTeamCounts[key];
        if (data.count >= 4) {
            homerYears.push(data);
        }
    }
    
    return homerYears;
}

function calculateLateRoundStats(allPicks) {
    const latePicks = allPicks.filter(pick => pick.round >= 10);
    let hits = 0;
    
    latePicks.forEach(pick => {
        if (pick.value_type === 'hit' || pick.value_type === 'extreme_hit' || pick.value_type === 'super_hit') {
            hits++;
        }
    });
    
    const total = latePicks.length;
    const hitRate = total > 0 ? (hits / total) * 100 : 0;
    
    return { hits, total, hitRate };
}

function calculateLateRoundStatsForYear(yearPicks) {
    const latePicks = yearPicks.filter(pick => pick.round >= 10);
    let hits = 0;
    
    latePicks.forEach(pick => {
        if (pick.value_type === 'hit' || pick.value_type === 'extreme_hit' || pick.value_type === 'super_hit') {
            hits++;
        }
    });
    
    const total = latePicks.length;
    const hitRate = total > 0 ? (hits / total) * 100 : 0;
    
    return { hits, total, hitRate };
}

function checkRisingStar(picksByYear) {
    const years = Object.keys(picksByYear).sort((a, b) => parseInt(a) - parseInt(b));
    if (years.length < 3) return false;
    
    let consecutiveImprovements = 0;
    let lastHitRate = null;
    let startYear = null;
    
    for (let i = 0; i < years.length; i++) {
        const picks = picksByYear[years[i]];
        const stats = calculateYearStats(picks);
        
        if (lastHitRate !== null && stats.hitRate > lastHitRate) {
            consecutiveImprovements++;
            if (startYear === null) {
                startYear = years[i - 1]; // Start year is the year before the first improvement
            }
            if (consecutiveImprovements >= 2) {
                return { startYear: startYear || years[0] }; // 3 consecutive years = 2 improvements
            }
        } else {
            consecutiveImprovements = 0;
            startYear = null;
        }
        
        lastHitRate = stats.hitRate;
    }
    
    return false;
}

// Helper functions for season-based achievements
function findPointsForLeaders(leagueData, memberAlias) {
    const leaders = [];
    
    Object.keys(leagueData.seasons).forEach(year => {
        const season = leagueData.seasons[year];
        if (!season.standings) return;
        
        // Find member's team
        const memberTeam = season.standings.find(team => team.owner_alias === memberAlias);
        if (!memberTeam) return;
        
        // Find max points_for in this season
        const maxPoints = Math.max(...season.standings.map(t => t.points_for || 0));
        
        // Check if member led the league
        if (memberTeam.points_for === maxPoints) {
            leaders.push({
                year: year,
                points_for: memberTeam.points_for
            });
        }
    });
    
    return leaders.sort((a, b) => parseInt(b.year) - parseInt(a.year));
}

function findPointsAgainstLeaders(leagueData, memberAlias) {
    const leaders = [];
    
    Object.keys(leagueData.seasons).forEach(year => {
        const season = leagueData.seasons[year];
        if (!season.standings) return;
        
        // Find member's team
        const memberTeam = season.standings.find(team => team.owner_alias === memberAlias);
        if (!memberTeam) return;
        
        // Find min points_against in this season
        const minPoints = Math.min(...season.standings.map(t => t.points_against || Infinity));
        
        // Check if member had the easiest schedule
        if (memberTeam.points_against === minPoints) {
            leaders.push({
                year: year,
                points_against: memberTeam.points_against
            });
        }
    });
    
    return leaders.sort((a, b) => parseInt(b.year) - parseInt(a.year));
}

function findIronWill(leagueData, memberAlias) {
    let ironWill = null;
    
    Object.keys(leagueData.seasons).forEach(year => {
        const season = leagueData.seasons[year];
        if (!season.standings) return;
        
        // Find member's team
        const memberTeam = season.standings.find(team => team.owner_alias === memberAlias);
        if (!memberTeam || !memberTeam.playoff_team) return;
        
        const totalTeams = season.standings.length;
        const halfPoint = Math.ceil(totalTeams / 2);
        
        // Sort by points_for to find rank
        const sortedByPoints = [...season.standings].sort((a, b) => (b.points_for || 0) - (a.points_for || 0));
        const pointsRank = sortedByPoints.findIndex(t => t.owner_alias === memberAlias) + 1;
        
        // Check if they made playoffs despite being in bottom half of scoring
        if (pointsRank > halfPoint) {
            ironWill = {
                year: year,
                points_rank: pointsRank,
                total_teams: totalTeams
            };
        }
    });
    
    return ironWill;
}

function findAllIronWill(leagueData, memberAlias) {
    const ironWillYears = [];
    
    // Get playoff appearances from members data
    const memberData = leagueData.members?.[memberAlias];
    const playoffYears = memberData?.playoff_appearances || [];
    
    Object.keys(leagueData.seasons).forEach(year => {
        // Only check years where they made playoffs
        if (!playoffYears.includes(year)) return;
        
        const season = leagueData.seasons[year];
        if (!season.standings) return;
        
        // Find member's team
        const memberTeam = season.standings.find(team => team.owner_alias === memberAlias);
        if (!memberTeam) return;
        
        const totalTeams = season.standings.length;
        const halfPoint = Math.ceil(totalTeams / 2);
        
        // Sort by points_for to find rank
        const sortedByPoints = [...season.standings].sort((a, b) => (b.points_for || 0) - (a.points_for || 0));
        const pointsRank = sortedByPoints.findIndex(t => t.owner_alias === memberAlias) + 1;
        
        // Check if they made playoffs despite being in bottom half of scoring
        if (pointsRank > halfPoint) {
            ironWillYears.push({
                year: year,
                points_rank: pointsRank,
                total_teams: totalTeams
            });
        }
    });
    
    return ironWillYears.sort((a, b) => parseInt(b.year) - parseInt(a.year));
}

// Load stats when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDraftStats);
} else {
    loadDraftStats();
}

