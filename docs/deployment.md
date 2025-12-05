# Deployment

## Backend (FastAPI)
- **Container build:**
  ```bash
  docker build -t siftmail-backend -f backend/Dockerfile .
  docker run -p 8000:8000 --env-file .env siftmail-backend
  ```
- **Procfile:** `web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` works on Heroku/Railway style platforms.
- **Environment:** ensure the variables from `.env.example` are set (`APP_ENV`, `BACKEND_PORT`, `CORS_ORIGINS`, `CLASSIFICATION_THRESHOLD`, keyword/domain lists).

## Frontend (Next.js)
- **Production build:**
  ```bash
  cd frontend
  npm install
  npm run build
  npm start  # serves the production build
  ```
- **Netlify/Vercel:** the repository includes `frontend/netlify.toml`; build command `npm run build` and publish `.next`. Set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend URL.

## CI expectations
GitHub Actions (`.github/workflows/mono-ci.yml`) runs on every push/PR:
- Backend: install deps → ruff lint → pytest → byte-compile
- Frontend: npm install → `next lint` → `next build`

## Manual deployment flow
1. Provision a container app (Railway/Render/Heroku) for the backend using `backend/Dockerfile` or `Procfile`.
2. Set environment variables from `.env.example` in the platform dashboard.
3. Deploy the frontend to Netlify/Vercel or any Node host using the build commands above.
4. Point `NEXT_PUBLIC_API_BASE_URL` to the public backend URL; redeploy frontend when it changes.
