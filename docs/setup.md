# Local setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd siftmail-monorepo
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Adjust `NEXT_PUBLIC_API_BASE_URL` or classifier thresholds as needed.

3. **Python environment (backend)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   python -m pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```

4. **Node environment (frontend)**
   ```bash
   # Ensure Node 18+ and npm are installed
   npm install --workspaces
   ```

5. **Run the stack**
   - Start everything from the repo root:
     ```bash
     npm run dev
     ```
   - Or run individually:
     ```bash
     npm run dev:backend  # FastAPI on http://localhost:8000 (loads backend/app/main.py)
     npm run dev:frontend # Next.js on http://localhost:3000
     ```

6. **Lint and tests**
   ```bash
   npm run lint   # ruff + next lint
   npm run test   # pytest + frontend lint
   ```

7. **Build**
   ```bash
   npm run build  # Next.js production build
   ```

8. **API smoke test**
   ```bash
   curl -X POST http://localhost:8000/api/sift/classify \
     -H "Content-Type: application/json" \
     -d '{"subject":"hello","body":"test","sender":"a@b.com","recipient":"c@d.com"}'
   ```
