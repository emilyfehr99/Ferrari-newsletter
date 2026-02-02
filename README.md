# Ferrari F1 Newsletter

A premium weekly newsletter for Ferrari F1 fans (Tifosi) featuring news, technical analysis, and race insights.

## Quick Start

### Generate Newsletter
```bash
cd src
python3 main.py --preview --days 7
```

### View Newsletter
Open `templates/generated_preview.html` in your browser.

## Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Your newsletter will be available at `your-project.vercel.app`

## Features

- 📰 **News Scraping** - 5 RSS sources (F1, Motorsport.com, The Race, Autosport, MotorsportWeek)
- 🔍 **Smart Filtering** - Ferrari-specific content with deduplication
- 🎨 **Premium Design** - Italian flag accents, Ferrari branding
- 🌍 **Multi-language** - English, French, Italian support
- 📊 **Live Standings** - Ergast F1 API integration
- 📧 **Email Ready** - SMTP support for automated sending

## File Structure

```
ferrari-newsletter/
├── src/
│   ├── main.py              # CLI orchestrator
│   ├── news_scraper.py      # RSS/web scraping
│   ├── content_filter.py    # Article filtering
│   ├── template_renderer.py # HTML generation
│   ├── email_sender.py      # SMTP sending
│   └── subscriber_manager.py # Subscriber storage
├── templates/
│   ├── generated_preview.html # Latest newsletter
│   └── signup.html          # Subscription page
└── vercel.json              # Deployment config
```
