# Sunday Movie League (SML)

Official website for the Sunday Movie League fantasy football league, established in 2016.

**Live Site:** https://smcsus.github.io/SML

---

## About

A static website built to document and display the history of a fantasy football league. The site serves as the official record of league champions, season standings, historical events, draft history, and member profiles with detailed statistics and achievements.

---

## Features

- **Champions Display** - Complete list of all league champions and runner-ups with clickable profile links
- **Season Standings** - Tabbed interface showing regular season standings from 2021-2025 with full statistics
- **Playoff Brackets** - Visual bracket displays with all matchup scores for each season
- **Draft History** - Complete draft records from 2021-2025 with draft position, season finish, points, and value calculations
- **League History Timeline** - Chronological display of key events and scoring changes
- **Member Profiles** - Individual pages for each member featuring:
  - Profile statistics (championships, records, playoff history)
  - Biography
  - Draft statistics with year-by-year breakdown
  - Draft tendencies and patterns
  - Seasonal achievements
  - Complete league history timeline

---

## Tech Stack

- HTML5
- CSS3 (Custom Properties, Flexbox, Grid)
- Vanilla JavaScript
- Google Fonts (Bebas Neue, Barlow)

No external frameworks or dependencies.

---

## File Structure

```
SML/
├── index.html          # Main website page
├── styles.css          # All styling
├── script.js           # Interactive functionality
├── README.md           # This file
├── LICENSE             # MIT License
├── data/               # JSON data files
│   ├── league_database.json
│   ├── league_history.json
│   ├── drafts/         # Draft data by year
│   ├── seasons/        # Season data by year
│   └── profiles/       # Member draft statistics
├── profiles/           # Individual member profile pages
│   ├── profile.css     # Shared profile styling
│   ├── draft-stats.js  # Draft statistics and achievements
│   └── [name].html     # Individual profile pages
└── scripts/            # Python scripts for data processing
```

---

## Deployment

Hosted on GitHub Pages.

1. Push all files to the `main` branch
2. Go to repository Settings > Pages
3. Set Source to "Deploy from a branch"
4. Select `main` branch and `/ (root)` folder
5. Save and wait for deployment

---

## Local Development

```bash
# Clone the repository
git clone https://github.com/smcsus/SML.git

# Navigate to directory
cd SML

# Start local server
python -m http.server 8080

# Open in browser
http://localhost:8080
```

---

## License

MIT License
