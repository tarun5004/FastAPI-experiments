# FastAPI-experiments

A collection of FastAPI experiments, examples, and **25 in-depth Hinglish guides** covering backend topics from basics to production (FastAPI, SQLAlchemy, Alembic, Celery, WebSockets, Redis, Docker, CI/CD, monitoring, frontend integration, and more).

---

## Quick links
- Docs: `docs/` (25 comprehensive guides — read in Hinglish with diagrams and code)
- Main app: `main.py`

## What you can find here
- Learning examples for FastAPI and common backend problems
- Opinionated guides (Hinglish) that explain "kyun" (why) and "kaise" (how) with analogies and diagrams
- Ready-to-run snippets and Docker examples

---

## Quick start (Windows - PowerShell)

1. Create and activate virtual environment

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if present)

```powershell
pip install -r requirements.txt
```

3. Run the FastAPI app

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Visit interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Documentation highlights (examples)
- `22_frontend_basics.md` — HTML, CSS, JS, Fetch API
- `23_frontend_frameworks.md` — React, Vue, API integration
- `24_system_design_dsa.md` — System design and DSA notes for interviews
- `25_performance_scaling.md` — Profiling, caching, scaling patterns

See the full list inside `docs/`.

---

## Contributing
1. Fork → Create a branch → Commit → Open PR
2. Add tests where applicable
3. Keep docs clear and add examples

If you want I can add GitHub Actions to run linting and deploy docs to GitHub Pages.

---

## License
MIT

---

If you want, I can now commit these changes and push them to GitHub (and add a basic GitHub Actions workflow). Would you like me to push now?
