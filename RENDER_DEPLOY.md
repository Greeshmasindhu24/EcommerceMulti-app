# Render deploy — read this if you see the OLD site

Your repo had two frontend folders:

| Folder | Content |
|--------|---------|
| `frontend/` | **NEW** Style app (use this) |
| `frontend/frontend/` | **OLD** duplicate (removed) |

## Frontend static site on Render (`ecommercemulti-app2`)

| Setting | Value |
|---------|--------|
| Root Directory | `frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `build` |
| Environment | `REACT_APP_API_URL=https://ecommercemulti-app1.onrender.com` |

**Do NOT use** Root Directory `frontend/frontend` — that was the old UI.

After fixing settings: **Manual Deploy → Clear build cache & deploy**

## Backend

| Setting | Value |
|---------|--------|
| Root Directory | `backend` |
| Start Command | `gunicorn app:app` |
| URL | https://ecommercemulti-app1.onrender.com |

## How to tell the new site loaded

- Title: **Style | Online Shopping** (not "React App")
- Banner: **Premium Collection 2026**
- Category cards: **Explore Collection →**
