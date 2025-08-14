
# Sift Mail — Frontend Secure (Next.js)

This UI talks to your FastAPI backend **via server-side API routes** that inject `X-API-Key` from env,
so the key is never exposed to the browser.

## Configure
Create `.env.local`:
```
BACKEND_URL=http://localhost:8080
SIFT_API_KEY=the-same-key-you-configured-on-the-backend
```
You may also set `NEXT_PUBLIC_BACKEND_URL` if you want the landing page button to hit `/auth/start` directly.

## Run
```bash
npm install
npm run dev
# open http://localhost:3000
```

## Deploy
- Netlify or Vercel: set env vars `BACKEND_URL` and `SIFT_API_KEY` in project settings.
- Build: `npm run build`, Start: `npm start`

## Pages
- `/` — Connect Gmail + entry to dashboard
- `/app/dashboard` — Shadow toggle, rules, batch classify, digest, audit
