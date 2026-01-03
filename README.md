# Sunday Movie League (SML)

Official website for the Sunday Movie League fantasy football league, established in 2016.

**Live Site:** https://smcsus.github.io/SML

---

## About

A static website built to document and display the history of a fantasy football league. The site serves as the official record of league champions, season standings, historical events, and member profiles.

---

## Features

- **Champions Display** - Complete list of all league champions and runner-ups with clickable profile links
- **Season Standings** - Tabbed interface showing regular season standings from 2021-2025 with full statistics (Record, Points For, Points Against, Differential, Streak, Moves)
- **Playoff Brackets** - Visual bracket displays with all matchup scores for each season
- **League History Timeline** - Chronological display of key events and scoring changes
- **Member Profiles** - Individual pages for each member with profile picture placeholder, biography section, and league history
- **Responsive Design** - Works on desktop and mobile devices

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
└── profiles/           # Individual member profile pages
    ├── profile.css     # Shared profile styling
    └── [name].html     # Individual profile pages
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
