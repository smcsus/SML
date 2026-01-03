# Sunday Movie League (SML)

Official website for the Sunday Movie League fantasy football league, established in 2016.

**Live Site:** https://smcsus.github.io/SML

---

## About

The Sunday Movie League is a fantasy football league that has been running since 2016. This website serves as the official record of league history, champions, standings, and member profiles.

---

## Features

### Champions Section
- Complete list of all league champions from 2016-2025
- Runner-up records for each season
- Reigning champion highlight display
- Clickable names linking to player profiles

### Season Standings (2021-2025)
- Full regular season standings with sortable data
- Statistics include: Record, Points For, Points Against, Differential, Streak, and Moves
- Playoff team highlighting
- Complete playoff brackets with all matchup scores
- Champion, Runner-up, and 3rd Place podium displays
- Season selector tabs for quick navigation between years

### League History Timeline
- Key events from 2016 to present
- Founding and commissioner history
- Scoring changes (Standard to Quarter PPR to Half PPR to Full PPR)
- Notable events including Kirchergate (2018) and league expansion (2025)

### Member Profiles
- Individual profile pages for all current members
- Profile picture placeholder
- Biography section
- League history and accolades
- Membership tenure tracking

### Current Members (12)
- Steven Masters (Commissioner, 2016-Present)
- Brandon Kircher (Founder, 2016-Present)
- Joseph Martin (2018-Present)
- Jasper Mills (2016-Present)
- David Sun (Rules Consultant, 2018-Present)
- Ethan Hatter (2017-Present)
- Camden Bendik (2017-Present)
- Lucas Matthews (2016-19, 2023-Present)
- Andrew Ortiz (2017-Present)
- Jack Johnson (2020-Present)
- Daniel Lewis (2016-19, 2025-Present)
- Ian Baker (2025-Present)

### Past Members
- David Kircher (2016-2017)
- Dino Ortiz (2018)
- Nate Webster (2016-2021) - 2016 Inaugural Champion
- Trey Melnyk (2022) - Fill-In King
- Baron Gaunt (2019) - Banned
- Logan Robinson (2016)
- Unknown Player (2016)

---

## League Champions

| Year | Champion | Runner-Up |
|------|----------|-----------|
| 2025 | Joseph Martin | Lucas Matthews |
| 2024 | David Sun | Jack Johnson |
| 2023 | Brandon Kircher | Andrew Ortiz |
| 2022 | Camden Bendik | Jasper Mills |
| 2021 | Ethan Hatter | Jasper Mills |
| 2020 | Steven Masters | Ethan Hatter |
| 2019 | Joseph Martin | Baron Gaunt |
| 2018 | Daniel Lewis | Brandon Kircher |
| 2017 | Brandon Kircher | David Kircher |
| 2016 | Nate Webster | Steven Masters |

---

## Scoring History

- **2016-2017:** Standard Scoring
- **2018-2019:** Quarter PPR (0.25 points per reception)
- **2020:** Half PPR (0.5 points per reception)
- **2021-Present:** Full PPR (1 point per reception)

---

## Technical Details

### File Structure

```
SML/
├── index.html          # Main website page
├── styles.css          # All styling
├── script.js           # Interactive functionality
├── README.md           # This file
├── LICENSE             # MIT License
└── profiles/           # Individual member profile pages
    ├── profile.css     # Shared profile styling
    ├── steven-masters.html
    ├── brandon-kircher.html
    ├── joseph-martin.html
    ├── jasper-mills.html
    ├── david-sun.html
    ├── ethan-hatter.html
    ├── camden-bendik.html
    ├── lucas-matthews.html
    ├── andrew-ortiz.html
    ├── jack-johnson.html
    ├── daniel-lewis.html
    └── ian-baker.html
```

### Technologies Used

- HTML5
- CSS3 (Custom properties, Flexbox, Grid)
- Vanilla JavaScript
- Google Fonts (Bebas Neue, Barlow)

### Design

- Dark theme with gold accents
- Responsive design for mobile and desktop
- Championship trophy aesthetic
- No external dependencies or frameworks

---

## Deployment

This site is hosted on GitHub Pages. To deploy:

1. Push all files to the `main` branch
2. Go to repository Settings > Pages
3. Set Source to "Deploy from a branch"
4. Select `main` branch and `/ (root)` folder
5. Save and wait for deployment

The site will be available at: `https://smcsus.github.io/SML`

---

## Local Development

To run locally:

1. Clone the repository
2. Open a terminal in the project directory
3. Start a local server:
   ```
   python -m http.server 8080
   ```
4. Open `http://localhost:8080` in your browser

---

## License

MIT License - Copyright (c) 2026 Steven Masters

---

## Contributing

This is a private league website. For any updates or corrections, contact the Commissioner.

