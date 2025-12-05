# SiftMail frontend

Next.js application that exposes the SiftMail console and live classifier demo.

## Scripts
- `npm run dev` – start dev server at http://localhost:3000
- `npm run build` – production build in `.next`
- `npm run start` – serve the production build
- `npm run lint` – `next lint` using the default Next.js ESLint config

## Configuration
The frontend reads the backend URL from `NEXT_PUBLIC_API_BASE_URL` (see `.env.example`). During local development it defaults to `http://localhost:8000`.

## Pages
- `/` – marketing splash with live classifier + batch tester
- `/app` – operations console/health
- `/app/batch` – batch JSON classifier
- `/app/messages` – example verdict log
- `/auth`, `/privacy`, `/data-policy`, `/terms` – supporting documentation

Deployment guidance lives in `docs/deployment.md`.
