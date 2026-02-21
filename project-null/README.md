# KisaanSeva — Farmer Scheme Portal

A platform that helps Indian farmers discover government schemes, crop insurance, and subsidies they're eligible for.

## Architecture

```
project-null/
├── farmer-app/        # React SPA — farmer-facing app (port 3000)
├── service-portal/    # React SPA — agent/Jan Suvidha Kendra portal (port 3001)
├── backend/           # FastAPI backend (port 8000) — to be built
├── docker-compose.yml # Full-stack orchestration
├── Dockerfile         # Multi-stage build for both frontends
├── nginx.conf         # Reverse proxy config
└── .env.example       # Environment variables template
```

## Quick Start

### Development (frontend only)

```bash
# Farmer App
cd farmer-app
npm install
npm run dev          # → http://localhost:3000

# Service Portal (separate terminal)
cd service-portal
npm install
npm run dev          # → http://localhost:3001
```

### Full Stack (with Docker)

```bash
cp .env.example .env  # Edit with real values
docker compose up --build
```

- Farmer App: http://localhost:3000
- Service Portal: http://localhost:3001
- Backend API: http://localhost:8000/docs

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Farmer App | React 19 + Vite + Tailwind CSS (green theme) |
| Service Portal | React 19 + Vite + Tailwind CSS (blue theme) |
| Backend | FastAPI + PostgreSQL + Redis + Celery |
| Auth | OTP-only for farmers, username/password for agents |
| Farmer ID | `KS` + 9 alphanumeric chars (e.g. `KSXR7BM2QAL`) |

## Farmer App Pages

| Route | Page |
|-------|------|
| `/` | Landing page with hero, features, trust badges |
| `/signup` | 3-step signup: form → OTP → welcome with Farmer ID + QR |
| `/login` | Phone/ID → OTP → dashboard |
| `/home` | Dashboard with stats, quick actions, deadlines |
| `/schemes` | Filterable scheme list with eligibility badges |
| `/schemes/:id` | Scheme detail + eligibility check + form download |
| `/insurance` | PMFBY premium calculator + plan comparison |
| `/subsidies` | Subsidy list + calendar view with reminders |
| `/profile` | Farmer ID card, personal/farm edit, crops, documents, access log |

## Service Portal Pages

| Route | Page |
|-------|------|
| `/login` | Agent username/password login |
| `/dashboard` | Stats, quick actions, recent sessions |
| `/lookup` | Search farmer by ID/phone/name |
| `/farmer/:id` | Farmer detail with session-gated data access |
| `/activity` | Paginated session log with search |

## Key Features

- **Eligibility engine**: Auto-matches farmer profile to schemes
- **Pre-filled forms**: Download application forms with farmer data
- **Deadline tracking**: Calendar view with SMS reminders
- **Farmer ID + QR**: Unique ID for service center visits
- **Access transparency**: Farmers see who accessed their data
- **Multi-language**: English + Hindi (i18n ready)
- **Mobile-first**: Bottom tab navigation, responsive layout
