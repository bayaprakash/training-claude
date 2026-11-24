# TODO — Demo Infrastructure Monitoring Application

Small, AI-friendly increments. Check items off as you complete them.  
Reference: [requirements.md](./requirements.md)

---

## 1. Project initialization & basic UI

- [x] Scaffold Flask app layout (`app/`, `routes/`, `templates/`, `static/`, `config.py`, `run.py`)
- [x] Add `requirements.txt` (Flask, python-dotenv) and `.gitignore` (`.env`, `__pycache__`, `.venv`, SQLite)
- [x] Add `.env.example` with `SECRET_KEY` placeholder — document in README that secrets never go in git
- [x] **Security:** Load config via `python-dotenv`; no hardcoded secrets
- [x] Create base layout template + home/landing page (attractive, minimal CSS)
- [x] Wire a health/home route that renders the basic UI
- [x] **Docs:** Root `README.md` — how to create venv, install deps, run locally

---

## 2. Sign-in & unit tests

- [x] Add session-based login routes (`/login`, `/logout`)
- [x] Seed default user `admin` with **hashed** password for `admin123` (Werkzeug)
- [x] Protect monitoring routes — redirect unauthenticated users to login
- [x] **Security:** Use `SECRET_KEY` from env for sessions; never store plaintext passwords; CSRF-friendly form patterns for demo
- [x] Add pytest + Flask test client setup (`tests/`)
- [x] Unit tests: login success, login failure, logout, protected route requires auth
- [x] **Docs:** Document default credentials in README (demo-only warning) and how to run tests

---

## 3. Server registry (add / list / remove)

- [x] Choose demo storage (SQLite or JSON file) for registered servers
- [x] Service layer: create / list / delete servers (thin routes)
- [x] Form/API to add server: hostname/IP, SSH port (default 22), SSH username, auth (password or key path), display name, collection mode (`ssh` | `mock`)
- [x] List + remove UI (admin-only, still behind login)
- [x] **Security:** Do not log SSH passwords/keys; store credentials only as needed for demo; validate/sanitize hostname and port input
- [x] Unit tests: add server, list servers, delete server, reject invalid input
- [x] **Docs:** Document server fields and collection modes in README or `docs/`

---

## 4. Mock metrics collector

- [x] Implement mock collector returning CPU, memory, network, listening ports
- [x] JSON API endpoint for one server’s metrics (read-only)
- [x] Dashboard cards/table showing mock metrics for registered mock servers
- [x] **Security:** Metrics endpoints require auth; read-only — no remote command UI
- [x] Unit tests: mock payload shape and auth on metrics API
- [x] **Docs:** Note that mock mode needs no real hosts

---

## 5. SSH metrics collector

- [x] Add Paramiko (or equivalent) to `requirements.txt` (pinned)
- [x] SSH collector: CPU %, memory used/free, network RX/TX, listening ports
- [x] Map collection mode `ssh` → live collector; handle timeout/unreachable without crashing
- [x] UI status: online / unreachable / mock
- [x] **Security:** Prefer key-based demo notes; never echo credentials in templates/logs; connection timeouts; no shell escape injection in remote commands (fixed command strings only)
- [x] Unit tests: mock SSH failure → unreachable; successful parse of sample command output (mocked client)
- [x] **Docs:** Minimal SSH prerequisites (user, port, key/password) for local demo

---

## 6. Dashboard UX — 30s refresh & polish

- [x] Auto-refresh dashboard every 30 seconds (meta refresh or light JS fetch)
- [x] Optional manual refresh control
- [x] Read-only metrics detail view per server
- [x] **Security:** Confirm no write/exec actions exposed in UI
- [x] Smoke/UI tests or route tests for dashboard + refresh endpoint
- [x] **Docs:** Screenshot or short “using the dashboard” section in README

---

## 7. CI/CD (GitHub Actions)

- [x] Add `.github/workflows/ci.yml`
- [x] Job: checkout → set up Python 3.11+ → install deps → run pytest
- [x] Optional lint step (e.g. ruff/flake8) if lightweight
- [x] **Security:** No secrets in workflow logs; use env examples only; do not commit `.env`
- [x] **Docs:** Document CI status badge / how CI runs in README

---

## 8. Final demo checklist

- [x] End-to-end local run: login → add mock server → see metrics → add SSH server (if available) → logout
- [x] Verify acceptance criteria from PRD §10
- [x] **Security:** Final pass — hashed admin password, auth gates, `.gitignore` covers secrets/DB
- [x] **Docs:** Finalize README (setup, run, test, CI, demo credentials warning)

---

## Suggested order

`1 → 2 → 3 → 4 → 5 → 6 → 7 → 8`

Complete each checkbox group before moving on so increments stay reviewable and testable.
