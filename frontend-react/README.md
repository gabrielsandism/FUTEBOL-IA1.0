# Football Scanner AI — Frontend (React/Next.js)

Modern, responsive web interface for the Football Scanner AI system.

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm build

# Start production server
npm start
```

Access: http://localhost:3000

## Stack

- **Next.js 14** — React framework with SSR/SSG
- **Tailwind CSS** — Utility-first styling
- **Zustand** — Lightweight state management
- **Recharts** — Data visualization
- **Lucide React** — Icon library
- **TypeScript** — Type safety

## Architecture

```
src/
├── pages/          # Next.js pages (routes)
├── components/     # Reusable React components
├── store/          # Zustand global state
├── styles/         # Tailwind CSS
└── utils/          # Helper functions
```

## Features

- 📊 **Dashboard** — Live match overview, active alerts
- 🏟️ **Matches** — Detailed match information
- 📋 **Rules** — Enable/disable detection rules
- 🔔 **Alerts** — Real-time notifications
- 📈 **Stats** — System metrics and performance

## API Integration

The frontend connects to the backend FastAPI server at `http://127.0.0.1:8000`.

Key endpoints:
- `GET /api/matches/live` — Live matches
- `GET /api/alerts/` — Active alerts
- `GET /api/rules/` — Detection rules
- `GET /api/stats` — System stats
- `POST /api/alerts/{id}/dismiss` — Dismiss alert
- `PATCH /api/rules/{code}` — Toggle rule

## Styling

Dark theme optimized for real-time monitoring dashboards.

Colors:
- Primary: `#3fb950` (success/green)
- Warning: `#d29922` (yellow)
- Danger: `#f85149` (red)
- Info: `#58a6ff` (blue)
- Background: `#0d1117` (dark)
