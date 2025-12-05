# Operations

## Observability
- FastAPI logs to stdout via uvicorn; capture platform logs for request traces.
- Health endpoint: `GET /health` returns status, environment, and app name.

## Configuration knobs
- `CLASSIFICATION_THRESHOLD` tunes when a message moves from clean to suspicious.
- `SPAM_KEYWORDS` and `PHISHING_DOMAINS` accept comma-separated lists to tweak detection.
- `CORS_ORIGINS` controls which frontends may call the API.

## Security hardening
- Add authentication (API keys or OAuth) before exposing beyond demo; attach `Authorization` headers.
- Terminate TLS at the load balancer or hosting provider.
- Keep dependencies patched (`pip install -r backend/requirements.txt --upgrade`).

## Maintenance
- Run `npm run lint` and `npm run test` before deployments.
- Rotate env secrets when onboarding/offboarding team members.
- Keep `.env` in sync with `.env.example` when introducing new configuration.
