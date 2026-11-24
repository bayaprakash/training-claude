# PRD — Demo Infrastructure Monitoring Application

## 1. Overview

Local demo web app for internal L1/L2/L3 and app teams to view Linux server health (CPU, memory, network, ports) without SSH-ing into hosts for day-to-day checks.

**Scope:** Single-machine Flask demo. Not production HA, multi-tenant, or alerting.

## 2. Problem

Operators currently log into each Linux server to inspect real-time memory, CPU, network usage, and listening ports. That is slow, error-prone, and hard to share across teams.

## 3. Users

| Role | Need |
|------|------|
| L1 / L2 / L3 ops | Read-only view of server metrics |
| App / infra engineers | Same read-only dashboard; no config changes via UI beyond admin add-server |

UI is **read-only** for metrics. Only authenticated admin can add/remove servers.

## 4. Goals (Demo)

- Sign in with a default admin account
- Register Linux servers (hostname + SSH)
- Show CPU, memory, network I/O, and listening ports
- Support **live SSH collection** and **mock metrics** (for offline demo)
- Auto-refresh every **30 seconds**
- Attractive Flask + HTML/CSS UI, runnable locally where Cursor runs

## 5. Non-Goals

- Alerting, paging, or ticket integration
- Multi-user RBAC beyond single admin
- Windows / non-Linux targets
- Historical time-series DB / long retention
- Production hardening (SSO, audit, TLS termination)

## 6. Features

### 6.1 Authentication

- Sign-in page required before any monitoring view
- Default username: `admin`
- Default password: `admin123` (store **hashed** at rest; never plaintext in code or DB)
- Session-based login for the demo
- Logout available from the UI

### 6.2 Read-only UI

- Dashboard and detail views show metrics only — no remote shell, no config edits on targets
- Clear visual status (online / unreachable / mock mode)

### 6.3 Add Linux servers

When adding a server, capture at least:

| Field | Required | Notes |
|-------|----------|--------|
| Hostname or IP | Yes | Target identity |
| SSH port | Yes | Default `22` |
| SSH username | Yes | Used for remote commands |
| SSH auth | Yes | Password or private key path (demo: one method is enough) |
| Display name | No | Friendly label |
| Collection mode | Yes | `ssh` (live) or `mock` |

Admin can list and remove registered servers.

### 6.4 Metrics (all four)

| Metric | What to show |
|--------|----------------|
| CPU | Overall utilization % |
| Memory | Used / free (and % used) |
| Network | RX/TX throughput or byte counters (simple demo view) |
| Ports | Listening ports (and optionally process if easy via SSH) |

### 6.5 Collection modes

1. **SSH (live):** Connect to the host and gather metrics with standard Linux commands (e.g. CPU/mem from `/proc` or `top`/`free`, network from `/proc/net/dev` or `ip`, ports from `ss`/`netstat`).
2. **Mock:** Return plausible fake metrics so the UI can be demoed without reachable servers.

If SSH fails, show unreachable state; do not crash the app.

### 6.6 Refresh

- Dashboard auto-refreshes every **30 seconds**
- Manual refresh control is nice-to-have

## 7. Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| Framework | Flask |
| UI | Flask templates + CSS (attractive, simple) |
| Auth password hashing | Standard library / Werkzeug (e.g. `generate_password_hash`) |
| SSH client | Paramiko or equivalent (pin in `requirements.txt`) |
| Config | `python-dotenv`; no hardcoded secrets |
| Storage (demo) | SQLite or local JSON/file for servers + hashed admin password |

## 8. High-Level Architecture

```
Browser (read-only UI, 30s refresh)
    → Flask app (auth, CRUD servers, metric APIs)
        → Store (registered servers + hashed credentials)
        → Collector
            → SSH mode → Linux hosts
            → Mock mode → generated metrics
```

Keep route handlers thin; put collection and storage logic in services.

## 9. Minimal Local Setup

1. Create venv and `pip install -r requirements.txt`
2. Copy `.env.example` → `.env` (secret key, optional default admin hash seed)
3. Run Flask app locally (e.g. `python run.py` or `flask run`)
4. Open browser → sign in as `admin` / `admin123`
5. Add a server (mock or SSH) → view metrics

## 10. Acceptance Criteria

- [ ] Login works with `admin` / `admin123`; password stored hashed
- [ ] Unauthenticated users cannot see monitoring pages
- [ ] Admin can add a Linux server with hostname + SSH fields
- [ ] Admin can choose SSH or mock collection
- [ ] Dashboard shows CPU, memory, network, and listening ports
- [ ] UI auto-refreshes every 30s
- [ ] Metrics UI is read-only
- [ ] App runs locally with Flask for the demo

## 11. Out of Scope for v1 Demo

Multi-admin users, TLS, SSO, agents on hosts, historical graphs beyond current snapshot, mobile-native apps.
