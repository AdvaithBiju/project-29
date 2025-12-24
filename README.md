# Blood Report Analyzer (MVP)

A monorepo delivering a FastAPI backend and Flutter mobile app for educational blood report review. The MVP lets users create profiles, upload lab reports, parse biomarkers, view insights/trends, and export a physician-friendly SBAR summary.

## Repository layout
- `backend/`: FastAPI service with parsing, insights, and PDF generation.
- `app/`: Flutter client (Android-first but cross-platform ready).
- `shared/`: placeholder for shared schemas (OpenAPI/notes).

## Prerequisites
- Python 3.11+
- Flutter 3.x with Android toolchain
- Docker (for Postgres)
- Tesseract OCR installed locally for image parsing (MVP uses `pytesseract`).

## Setup

### Database via Docker
```bash
docker-compose up -d db
```
Postgres will listen on `localhost:5432` with default credentials `postgres/postgres` and database `blood_reports`.

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# env vars (override as needed)
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/blood_reports"
export SECRET_KEY="change-me"
uvicorn app.main:app --reload
```

Key endpoints (JWT protected except register/login):
- `POST /auth/register` `{email, password}`
- `POST /auth/login`
- Profiles CRUD: `/profiles`
- Reports upload + confirm: `/profiles/{id}/reports`
- Insights: `/profiles/{id}/reports/{report_id}/insights`
- SBAR PDF: `/profiles/{id}/reports/{report_id}/sbar.pdf`

### Backend tests
```bash
cd backend
pytest
```
Fixtures live in `backend/tests/fixtures`. Parser tests cover PDF text and OCR-like text. Smoke test exercises auth, profile, upload, and insights.

### Flutter app
```bash
cd app
flutter pub get
flutter run
```

The app uses:
- `http` for API calls
- `file_picker` and `image_picker` for uploads
- `flutter_local_notifications` for local reminders
- Simple token storage via `shared_preferences`

### Shared models/openapi
`shared/README.md` documents how to regenerate OpenAPI and share contracts. The backend serves OpenAPI at `/docs` and `/openapi.json` when running.

## Security & disclaimers
- JWT auth required for all protected routes.
- Basic file type/size validation on uploads.
- Educational decision-support only; not a diagnostic tool.
- Avoid logging raw health data.

## Roadmap (post-MVP)
- Cloud storage (S3) adapter
- Smarter parsing/ML heuristics
- End-to-end integration tests with real PDFs/images
