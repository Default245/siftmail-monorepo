# SiftMail overview

SiftMail is an AI-backed email defense layer built as a FastAPI backend and a Next.js frontend console. Traffic flows from users in the browser to the frontend (Next.js), which calls the FastAPI backend. The backend scores mail content for spam and phishing indicators and returns explainable verdicts. Batch requests allow processing multiple messages at once. The backend is stateless and reads configuration from environment variables.

**Architecture (textual):**
1. User opens the Next.js app and interacts with the classification or batch forms.
2. The frontend issues HTTPS requests to the FastAPI backend using `NEXT_PUBLIC_API_BASE_URL`.
3. FastAPI applies keyword and domain heuristics, produces a risk score, and returns verdicts and reasons.
4. Results are rendered in the UI; operators can iterate quickly without touching data stores.

**Tech stack**
- Backend: Python 3.11, FastAPI, uvicorn, pytest, ruff
- Frontend: Next.js 14 (React 18), ESLint via `next lint`
- CI: GitHub Actions (`.github/workflows/mono-ci.yml`)
- Deployment targets: any container-compatible platform for the backend, and Netlify/Vercel/Node host for the Next.js build

**Key directories**
- `backend/`: FastAPI app, classification logic, tests, Dockerfile, Procfile
- `frontend/`: Next.js app with live classifier UI and policy pages
- `docs/`: project documentation
