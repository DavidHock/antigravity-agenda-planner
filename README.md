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

### CI/CD Guard Rails
`ci.yml` defines three jobs:
1. **Backend Tests** – installs Python deps and runs `pytest`.
2. **Frontend Tests & Build** – runs the Angular unit tests headlessly and builds the production bundle.
3. **Docker Build Verification** – executes `docker compose build` only after tests succeed, ensuring the published images are based on tested code.

Use this pipeline (or run the commands locally) before building/pushing new docker images.


