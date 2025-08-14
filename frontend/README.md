
# Sift Mail — Frontend (Static)

This is the production-ready static frontend for Sift Mail.

## Structure
- `index.html` — Landing page with CTA (“Connect Gmail”) and waitlist form.
- `styles.css` — Dark, brand-consistent styles.
- `app.js` — JS with `API_BASE` for your backend (`/auth/start` route).
- `data-policy.html`, `privacy.html`, `terms.html` — Legal pages.
- `assets/logo.svg` — Simple wordmark.

## Configure
In `app.js`, set the API base for your environment:
```js
// For local dev:
localStorage.setItem('API_BASE','http://localhost:8080');
// For production (example):
// localStorage.setItem('API_BASE','https://api.siftmail.app');
```

## Deploy (Netlify)
1. Push this folder to GitHub (public or private).
2. In Netlify, “Deploy with GitHub” → select the repo → **No build command** (static).
3. Publish directory: the repository root.
4. Connect your domain and go live.

## Notes
- Replace the Formspree endpoint in `app.js` with your real waitlist endpoint.
- The “Connect Gmail” button calls `${API_BASE}/auth/start`.
