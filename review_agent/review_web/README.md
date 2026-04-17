# Review Web (Survey/Tutorial) — runnable UI + API

This is a small, self-contained web app for the `review_agent/` artifact-driven workflow.

## Quick start (Windows PowerShell)

1. Start backend (serves the built frontend too):

```powershell
cd E:\aixiaowo\review
.\review_agent\review_web\backend\run.ps1
```

2. Open:

- http://127.0.0.1:8731

You should see the pre-scaffolded demo project: `demo_survey_web`.

## What you can do in the UI

- Workbench flow: import papers -> abstract decisions -> Phase 1 -> upload PDFs -> Phase 2 -> Phase 3 -> Phase 4
- PDF convention for Phase 2: `review_agent/review_projects/<slug>/05_evidence/pdfs/<paper_id>.pdf`

## Dev mode (optional)

Backend (reload):

```powershell
cd E:\aixiaowo\review\review_agent\review_web\backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8731 --reload
```

Frontend (Vite dev server with `/api` proxy):

```powershell
cd E:\aixiaowo\review\review_agent\review_web\frontend
npm install
npm run dev
```

Then open:

- http://127.0.0.1:5173
