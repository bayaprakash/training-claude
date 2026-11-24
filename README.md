# InfraWatch — Demo Linux Monitoring

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Local Flask demo for L1–L3 teams to view Linux **CPU**, **memory**, **network**, and **listening ports** without day-to-day SSH logins.

Specs: [docs/requirements.md](docs/requirements.md) · Tasks: [docs/TODO.md](docs/TODO.md)

> Replace `OWNER/REPO` in the badge URL after you push to GitHub.

## Status

**Done:** TODO §1–§8 (scaffold → sign-in → registry → mock/SSH → 30s refresh → CI → final docs)

## Quick start

```bash
cd Monitoring_Application
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # never commit .env
python run.py
```

Open http://127.0.0.1:5095  
(Uses port **5095** by default so it does not collide with other demos on `:5000`. Override with `PORT=5000 python run.py` if free.)

### Demo credentials (local only — change for anything beyond this demo)

| Field | Value |
|-------|--------|
| Username | `admin` |
| Password | `admin123` |

Password is stored as a **Werkzeug hash** in `.env` (`ADMIN_PASSWORD_HASH`), never plaintext in code.

## Using the dashboard

1. Sign in with the demo credentials.
2. Open **Servers** → add a host.
   - **mock** — fake metrics, no real SSH needed
   - **ssh** — needs hostname/IP, port (default 22), username, and password or private key path
3. Open **Dashboard** — cards show CPU, memory, RX/TX, and port count.
4. Status badges: **online** / **unreachable** / **mock**.
5. Metrics **auto-refresh every 30 seconds**; use **Refresh now** anytime.
6. Open a server for the listening-ports detail view (read-only — no remote shell).

## Tests

```bash
pytest -q
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) on push/PR:

1. Checkout
2. Python 3.11
3. `pip install -r requirements.txt`
4. `ruff check app tests`
5. `pytest -q` (uses workflow env placeholders only — no real `.env` secrets)

## Security notes (demo)

- Secrets via `python-dotenv` / `.env` (gitignored)
- Session cookie: HttpOnly + SameSite=Lax
- Auth required for home, servers, dashboard, and `/api/*`
- `/health` is public for local liveness checks
- SSH credentials encrypted at rest (Fernet derived from `SECRET_KEY`); never rendered in templates
- Remote SSH commands are fixed strings (no user input interpolation)
