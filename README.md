## Agenda Planner

AI-assisted meeting agenda planner with a FastAPI backend and Angular 17 frontend.

### Project Structure
- `backend/`: FastAPI app, deterministic time-slot generator, ICS export.
- `frontend/`: Angular standalone app for agenda generation/editing.
- `.github/workflows/ci.yml`: CI pipeline that blocks docker builds unless tests pass.

### Local Development
1. **Backend**
   ```bash
   cd backend
   PYTHONPATH=. python3 -m pytest
   uvicorn main:app --reload --port 8086
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run start
   ```

### Tests
- **Backend**: `PYTHONPATH=backend python3 -m pytest backend/tests`  
  Covers deterministic slot generation for short/long/multi-day events, including dinner scheduling edge cases.
- **Frontend**: `npm run test -- --watch=false`  
  Exercises agenda generation, refine/copy/download buttons, and API interactions.
- **CLI**: `PYTHONPATH=. python3 -m pytest tests/cli`  
  Validates the console helper for generate/refine/ICS workflows.

### Console Helper
A lightweight CLI is available in `cli/agenda_cli.py` and reuses the running backend API (defaults to `http://localhost:8086`).

```bash
python3 cli/agenda_cli.py generate \
  --topic "Dev <> Research Exchange" \
  --location "HQ Berlin" \
  --start "2025-01-15T09:00:00" \
  --end "2025-01-15T10:00:00" \
  --language EN \
  --email "Align priorities for Q1"

python3 cli/agenda_cli.py refine --text-file agenda.txt --language EN
python3 cli/agenda_cli.py ics --topic "Dev Sync" --location "Room A" \
  --start "2025-01-15T09:00:00" --end "2025-01-15T10:00:00" \
  --agenda-json agenda.json --output dev_sync.ics
```

Set `AGENDA_API_BASE` to target another backend host if needed.
If you omit required flags while running in an interactive terminal, the CLI will
prompt you for the missing values.

### CI/CD Guard Rails
`ci.yml` defines three jobs:
1. **Backend Tests** – installs Python deps and runs `pytest`.
2. **Frontend Tests & Build** – runs the Angular unit tests headlessly and builds the production bundle.
3. **Docker Build Verification** – executes `docker compose build` only after tests succeed, ensuring the published images are based on tested code.

Use this pipeline (or run the commands locally) before building/pushing new docker images.


