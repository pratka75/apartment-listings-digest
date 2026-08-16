# Apartment Listings Digest

> **🌐 Shareable — works anywhere.** This is the general-purpose version: set it up
> for **any city or area**. Anyone is welcome to use it — fork it, add your own
> free RentCast key and email app-password, and get your own daily alerts.
> (There's also a personal, **Newport-NJ-specific** variant with extra building
> scrapers: [apartment-listings-tracker](https://github.com/pratka75/apartment-listings-tracker) — not intended for general use.)

A **self-hosted daily email digest** of apartment listings that match your
filters, powered by the [RentCast](https://www.rentcast.io/api) listings API.
You run your own copy — your filters and secrets never leave your machine.

Each day it fetches current listings, compares them to yesterday, and emails you
a digest of **new listings, price drops/rises, removed, and back-on-market** —
each linking straight to the listing.

---

## How it works

```
Daily run → RentCast (your filters) → compare to yesterday's snapshot
          → new / price-change / removed / back-in-market → HTML email → save snapshot
```

- **One data source: RentCast.** You provide your own API key. RentCast searches
  by location (coordinates + radius, zip, or city/state) and covers most areas.
- **Pasted links are *not* scraped.** Every apartment site is structured
  differently and many block bots, so instead of unreliably scraping arbitrary
  URLs, any link you add is surfaced in a **"Check manually"** section of the
  email — a handy one-click reminder to review it yourself.
- **State** lives in `snapshot.json`, which is what makes change-detection work.
- **Delivery** is Gmail SMTP using an app password.

---

## Security posture

This app is built to be safe to run and safe to publish:

- **No secrets in git.** Your API key and email password live in `.env`
  (gitignored). Your filters live in `config.local.json` (gitignored). Only code
  and `*.example` templates are committed.
- **Injection-safe email.** All external data is HTML-escaped; links are
  restricted to `http(s)`, so a listing can't inject markup or scripts.
- **SSRF-resistant fetching.** `safefetch.py` refuses private/loopback/
  link-local/cloud-metadata addresses, validates redirect targets, and caps
  response size.
- **Header-injection-safe email.** CR/LF stripped from recipient/subject/sender.
- **Input validation.** Configs are strictly validated (email format, http-only
  links, numeric ranges, types) before use.
- **No risky dependencies.** Python standard library only — no third-party
  packages, no `eval`/`exec`/`pickle`/shell.
- **Pre-commit secret scanner** (`scripts/check_secrets.py`) blocks commits that
  contain secrets.
- **Security test suite** (`python test_security.py`) — 26 checks covering all of
  the above. Run it any time.

---

## Setup

### 1. Prerequisites
- Python 3.10+
- A free [RentCast API key](https://app.rentcast.io/app/api)
- A Gmail account with **2-Step Verification** (for the app password)

### 2. Get the code
```bash
git clone <your-repo-url>
cd apartment-listings-digest
```

### 3. Create your filters
Open **`webapp/index.html`** in a browser, fill in the form, and download your
settings file into the project folder — or copy the template manually:
```bash
cp config.example.json config.local.json
```

| Field | Meaning |
|---|---|
| `search.bedrooms` | Bedrooms (0 = studio) |
| `search.max_rent` | Budget cap (USD/month) |
| `search.location` | `{latitude, longitude, radius_miles}`, `{zipCode}`, or `{city, state}` |
| `sources.rentcast` | `true` to use RentCast |
| `watch_urls` | Optional links for the "Check manually" section |
| `email.recipient` | Where the digest is sent |

### 4. Add your secrets
```bash
cp .env.example .env
```
Fill in `RENTCAST_API_KEY`, `GMAIL_SENDER`, and `GMAIL_APP_PASSWORD`
(from https://myaccount.google.com/apppasswords). `.env` is gitignored.

### 5. Test and run
```bash
python test_security.py     # optional: confirm the security checks pass
python mailer.py            # send yourself an SMTP test
python main.py --email      # fetch, build the digest, and email it
```

The first run treats everything as new and saves the baseline; from the second
run on you get only real changes.

---

## RentCast cost note

RentCast's free tier is **50 requests/month** with **no hard spending cap**. This
app self-limits: `sources_rentcast.py` enforces a monthly request budget
(default 45) and refuses to call once reached. One daily run ≈ 30/month — free.
Email links point to a public search, so opening a listing never spends quota.

---

## Scheduling

**Windows (Task Scheduler)** or **cron** — run `python main.py --email` daily.
Your computer must be on at run time. (For a fully hands-off setup you'd host it
somewhere always-on; be aware that means your secrets live there too.)

---

## Files

| File | Purpose |
|---|---|
| `main.py` | Orchestrator |
| `config.py` / `config.local.json` | Config loader / your filters (gitignored) |
| `secrets_env.py` / `.env` | Secret loader / your secrets (gitignored) |
| `safefetch.py` | SSRF-resistant HTTP helper |
| `sources_rentcast.py` | RentCast fetcher (the data source) |
| `sources_links.py` | Routes pasted links to the "Check manually" section |
| `engine.py` | Snapshot + diff logic |
| `digest.py` | HTML email builder (escaped) |
| `mailer.py` | Gmail SMTP sender |
| `scripts/check_secrets.py` | Pre-commit secret scanner |
| `test_security.py` | Security regression suite |
| `webapp/index.html` | Static settings builder |
