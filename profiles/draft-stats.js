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
    'Baker': 'baker'
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
            displayDraftAchievements(data, playersData);
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

function displayDraftAchievements(profileData, playersData) {
    const container = document.getElementById('draft-achievements-content');
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
        
        const achievements = calculateAchievements(allPicks, stats, playersData, profileData.picks_by_year);
        
        if (achievements.length === 0) {
            container.innerHTML = '<p class="no-achievements">No achievements earned yet</p>';
            return;
        }
        
        let html = '<div class="achievements-grid">';
        achievements.forEach(achievement => {
            html += `
                <div class="achievement-badge" data-tooltip="${achievement.description.replace(/"/g, '&quot;')}">
                    <span class="achievement-icon">${achievement.icon}</span>
                    <span class="achievement-name">${achievement.name}</span>
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

function calculateAchievements(allPicks, stats, playersData, picksByYear) {
    const achievements = [];
    
    // Sharpshooter - 20%+ hit rate (lowered from 30%)
    if (stats.hit_rate >= 20) {
        achievements.push({
            name: 'Sharpshooter',
            icon: '🎯',
            description: `Achieved ${stats.hit_rate.toFixed(1)}% hit rate across all seasons`
        });
    }
    
    // Diamond Miner - 1+ super extreme hits (lowered from 3)
    if (stats.super_hits >= 1) {
        achievements.push({
            name: 'Diamond Miner',
            icon: '💎',
            description: `Drafted ${stats.super_hits} super extreme hit${stats.super_hits > 1 ? 's' : ''} (30+ spot difference)`
        });
    }
    
    // Gold Digger - 3+ extreme hits (lowered from 5)
    if (stats.extreme_hits >= 3) {
        achievements.push({
            name: 'Gold Digger',
            icon: '⭐',
            description: `Drafted ${stats.extreme_hits} extreme hits (15+ spot difference)`
        });
    }
    
    // Franchise Tag - Same player 3+ times
    const franchisePlayers = findFranchisePlayers(allPicks);
    if (franchisePlayers.length > 0 && franchisePlayers[0].count >= 3) {
        achievements.push({
            name: 'Franchise Tag',
            icon: '🏷️',
            description: `Drafted ${franchisePlayers[0].player_name} ${franchisePlayers[0].count} times`
        });
    }
    
    // Prophet - Drafted a player who finished #1 at their position
    const numberOnePicks = findNumberOnePicks(allPicks);
    if (numberOnePicks.length > 0) {
        achievements.push({
            name: 'Prophet',
            icon: '🔮',
            description: `Drafted ${numberOnePicks[0].player_name} who finished #1 at ${numberOnePicks[0].position}`
        });
    }
    
    // Value Hunter - Average value of +5 or better (lowered from +10)
    if (stats.avg_value >= 5) {
        achievements.push({
            name: 'Value Hunter',
            icon: '💰',
            description: `Average value of +${stats.avg_value.toFixed(1)} spots across all picks`
        });
    }
    
    // Perfect Round - 100% hit rate in a single round
    const perfectRound = findPerfectRound(allPicks);
    if (perfectRound) {
        achievements.push({
            name: 'Perfect Round',
            icon: '✨',
            description: `100% hit rate in Round ${perfectRound.round} (${perfectRound.year})`
        });
    }
    
    // Homer - 4+ players from same NFL team in one year (lowered from 5)
    const homerYear = findHomerYear(allPicks, playersData);
    if (homerYear) {
        achievements.push({
            name: 'Homer',
            icon: '🏠',
            description: `Drafted ${homerYear.count} players from ${homerYear.team} in ${homerYear.year}`
        });
    }
    
    // Late Round Legend - 40%+ hit rate in rounds 10+ (lowered from 50%)
    const lateRoundStats = calculateLateRoundStats(allPicks);
    if (lateRoundStats.hitRate >= 40 && lateRoundStats.total >= 3) {
        achievements.push({
            name: 'Late Round Legend',
            icon: '🌙',
            description: `${lateRoundStats.hitRate.toFixed(0)}% hit rate in rounds 10+ (${lateRoundStats.hits}/${lateRoundStats.total})`
        });
    }
    
    // Rising Star - 3+ consecutive years of improving hit rate
    if (picksByYear) {
        const risingStar = checkRisingStar(picksByYear);
        if (risingStar) {
            achievements.push({
                name: 'Rising Star',
                icon: '📈',
                description: `3+ consecutive years of improving hit rate`
            });
        }
    }
    
    // Steal Artist - Best value pick (if significant)
    if (stats.best_pick && stats.best_pick.value_diff >= 20) {
        achievements.push({
            name: 'Steal Artist',
            icon: '🎁',
            description: `Drafted ${stats.best_pick.player_name} ${stats.best_pick.draft_pos} → ${stats.best_pick.season_finish} (+${stats.best_pick.value_diff} spots)`
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

function checkRisingStar(picksByYear) {
    const years = Object.keys(picksByYear).sort((a, b) => parseInt(a) - parseInt(b));
    if (years.length < 3) return false;
    
    let consecutiveImprovements = 0;
    let lastHitRate = null;
    
    for (let i = 0; i < years.length; i++) {
        const picks = picksByYear[years[i]];
        const stats = calculateYearStats(picks);
        
        if (lastHitRate !== null && stats.hitRate > lastHitRate) {
            consecutiveImprovements++;
            if (consecutiveImprovements >= 2) return true; // 3 consecutive years = 2 improvements
        } else {
            consecutiveImprovements = 0;
        }
        
        lastHitRate = stats.hitRate;
    }
    
    return false;
}

// Tab functionality
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const targetContent = document.getElementById(`${targetTab}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// Load stats when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadDraftStats();
        initTabs();
    });
} else {
    loadDraftStats();
    initTabs();
}

