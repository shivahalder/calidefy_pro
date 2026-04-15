# Calidefy — Your Smart Calendar PLEASE DO THIS THIS IS A URL FOR MY PRIVATE SERVER :http://217.216.40.184:2004/#/ the username and password is Horsey  password is Moose939 please go to files on the side click on document the full folder is there Please do this 


A beautiful, AI-powered calendar built with Next.js, featuring drag & drop events, live weather, and an AI assistant.

---

## Getting Started

> Make sure you `cd` into the project folder first:

```bash
cd calendar-app
```

### 1. Add your OpenRouter API key

Create or edit `.env.local` in the `calendar-app` folder:

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

Get a free key at [openrouter.ai](https://openrouter.ai).

### 2. Install dependencies (first time only)

```bash
cd calendar-app
npm install
```

### 3. Run the dev server

```bash
cd calendar-app
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Features

| Feature | Details |
|---|---|
| Drag & Drop | Drag any event to a different day |
| Live Weather | Auto-detects your location via Open-Meteo (no key needed) |
| AI Assistant | Chat with Claude via OpenRouter to create/edit/delete events |
| Settings | Theme, time format, week start, export/import/clear data |
| Mobile | Responsive layout with bottom nav bar |
| Dark Mode | Toggle in Settings |

---

## Project Structure

```
calendar-app/
├── app/
│   ├── api/ai/route.ts        # OpenRouter AI endpoint
│   ├── components/
│   │   ├── CalendarApp.tsx    # Main app shell
│   │   ├── CalendarGrid.tsx   # Month grid with drag & drop
│   │   ├── EventModal.tsx     # Create / edit event modal
│   │   ├── EventPill.tsx      # Draggable event pill
│   │   ├── Sidebar.tsx        # Dark sidebar + mini calendar
│   │   ├── AIAssistant.tsx    # AI chat panel
│   │   ├── Settings.tsx       # Settings modal
│   │   ├── useEvents.ts       # Event state + localStorage
│   │   ├── useWeather.ts      # Open-Meteo weather hook
│   │   └── useSettings.ts     # Settings state + localStorage
│   ├── page.tsx
│   └── layout.tsx
├── .env.local                 # Your API keys (not committed)
└── package.json
```

---

## Common Commands

```bash
# Always cd first!
cd calendar-app

npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Run production build
npm run lint     # Lint the code
```
