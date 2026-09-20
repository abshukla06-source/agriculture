# Smart Agriculture AI — Streamlit

A single-app version of your Smart Agriculture project: sensor input, the
crop decision engine, live weather, and Gemini-powered advice, all running
inside one Streamlit app (no separate FastAPI backend or React frontend
needed).

## What changed from your original setup

- **No FastAPI server and no separate React frontend.** `app.py` calls
  `decision_engine.py`, `crop_data.py`, `weather.py`, and `ai_service.py`
  directly in-process — Streamlit Community Cloud only runs one process,
  so this is what makes a single deploy possible.
- **No standalone sensor simulator.** Use the sidebar's "Generate new
  reading" button (same random ranges as `sensor_simulator.py`) or enter
  values manually. If you have real hardware later, point it at a small
  API or write straight into `smartagri.db` — ask and I can wire that up.
- `weather.py` — `get_weather()` now takes `latitude`/`longitude`
  arguments (sidebar inputs), defaulting to your original Jaipur
  coordinates.
- `ai_service.py` — the Gemini client is created lazily and reads the API
  key from Streamlit secrets (or an env var) instead of crashing on
  import if the key is missing. **Double-check the model name**
  (`gemini-3.6-flash`, kept from your original code) is still valid for
  your API key — override it by setting a `GEMINI_MODEL` secret/env var
  if not.
- `crop_data.py`, `decision_engine.py`, `database.py`, `models.py` are
  unchanged.

## Run locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml and paste your real Gemini key
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repo (public or private).
2. Go to https://share.streamlit.io → **New app**.
3. Pick the repo, branch, and set **Main file path** to `app.py`.
4. Open **Advanced settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-real-key"
   ```
5. Click **Deploy**.

## Note on data persistence

`smartagri.db` (SQLite) is created on the app's local disk. On Streamlit
Community Cloud that disk is **ephemeral** — it resets whenever the app
reboots or redeploys, so sensor history won't survive long-term. That's
fine for a demo/hackathon; if you need persistent history, swap
`database.py`'s `DATABASE_URL` for a hosted Postgres URL (e.g. from
Supabase or Neon) — the rest of the code doesn't need to change since
it's already using SQLAlchemy.
