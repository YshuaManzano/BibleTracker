# VerseTrack - Bible Reading App PRD

## Overview
A comprehensive Bible reading tracker app with reading plans, progress visualization, AI-powered summaries, mood-based reading, and gamification features.

## Tech Stack
- **Frontend**: Expo React Native (SDK 54), expo-router
- **Backend**: FastAPI (Python), MongoDB
- **AI**: OpenAI GPT-5.2 via Emergent LLM Key
- **Bible Data**: wldeh/bible-api CDN (KJV, ASV, WEB translations)

## Core Features (MVP)
1. **Authentication**: JWT-based email/password (register, login, logout)
2. **Reading Plans**: 5 preset plans (Whole Bible 1yr, NT 90 Days, Wisdom Books, Life of David, Gospels 30 Days)
3. **Progress Dashboard**: Daily verse, streak tracker, heat map (13 weeks), stats
4. **Grace Day System**: 1 grace day per month to keep streaks alive
5. **Smart Catch-Up**: Recalculate plan to spread missed chapters
6. **Bible Reader**: Full chapter text (KJV) with verse numbers, serif font
7. **AI TL;DR Summaries**: GPT-5.2 chapter summaries with caching
8. **Interactive Bible Map**: Grid of all 66 books with completion status
9. **Mood-Based Reading**: 6 moods (Anxious, Joyful, Grieving, Grateful, Seeking, Lonely) with curated passages
10. **Note-Taking**: CRUD notes attached to chapters
11. **Badges/Milestones**: 13 unlockable badges (Pentateuch, Wisdom, Pauline Epistles, etc.)
12. **Dark Mode**: Warm amber tones, auto-switch + manual toggle (Auto/Light/Dark)
13. **Profile**: User stats, badge showcase, theme settings

## Screens
- Login / Register
- Home Dashboard (Daily Verse, Streak, Heat Map, Quick Actions)
- Plans (Browse / Active with progress bars)
- Bible Map (66-book grid, OT/NT filter)
- Reader (Chapter text, AI summary, notes, mark as read)
- Mood Reading (6 emotion cards with suggested passages)
- Profile (Stats, Appearance, Badges, Sign Out)

## API Endpoints
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Bible: `/api/bible/books`, `/api/bible/chapter/{version}/{book}/{ch}`, `/api/bible/daily-verse`
- Plans: `/api/plans`, `/api/plans/activate/{id}`, `/api/plans/active`, `/api/plans/recalculate`
- Progress: `/api/progress/mark-read`, `/api/progress/heatmap`, `/api/progress/streak`, `/api/progress/books-status`
- Notes: `/api/notes` (GET, POST), `/api/notes/{id}` (PUT, DELETE)
- AI: `/api/ai/summary/{book}/{ch}`, `/api/ai/mood-suggestions`
- Badges: `/api/badges`
- Dashboard: `/api/dashboard`
- Settings: `/api/settings`, `/api/settings/theme`

## Future Features (Post-MVP)
- Audio Bible integration
- Reading Circles (social groups)
- Prayer Requests
- Shared Highlights feed
- Daily Verse widget
- Additional translations
- Time Capsule for notes (see what you wrote a year ago)
