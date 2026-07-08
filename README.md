# Credo Health FHIR Migration Exercise

This is an implementation of Credo Health's take-home exercise. It reads
synthetic Patient and Observation data from the public HAPI FHIR R4 sandbox,
stores a simplified version in SQLite, and shows the migrated patients in a
React UI.

The public sandbox is here: https://hapi.fhir.org/baseR4

[`Plan.md`](./Plan.md), is included, which describes the overall flow of this exercise.

## Tech stack

- Backend: Django, Django REST Framework, SQLite
- Frontend: React, Vite, React Router
- Tests: Django test runner

## How to run it

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py migrate_fhir_data --count 20 --obs-count 20
python manage.py runserver 127.0.0.1:8000
```

The API runs at `http://127.0.0.1:8000/api/`.

Available endpoints:

- `GET /api/patients/`
- `GET /api/patients/<id>/`

The migration command can be run more than once. It uses the FHIR resource id
as the local upsert key, so repeated runs update existing rows instead of
creating duplicates.

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tests

```bash
cd backend
source venv/bin/activate
python manage.py test
```

The current tests cover the main things for this exercise:

- Patient mapping from nested FHIR JSON
- Observation `valueQuantity` mapping
- Patient detail API response with nested observations
- Retry behavior when the upstream FHIR server returns temporary `5xx` errors

## Notes on the implementation

The migration command fetches a bounded number of patients and observations
using `--count` and `--obs-count` for this exercise.

For a real 50,000-patient migration, I would add pagination over FHIR bundles,
checkpointing, run history, better structured logging, and reconciliation
checks after each batch.

Here the local schema is smaller than FHIR. I have stored the fields needed
for this UI and API:

- Patient: FHIR id, name, gender, birth date
- Observation: FHIR id, patient, code text, value text, effective date, status

FHIR observations can represent values in a few different ways. In this app I've
flattened the supported value types into one display field called `value_text`.
This keeps the internal model easier to query and avoids copying too much of
FHIR's full structure into the app.

If a Patient or Observation is missing its FHIR id, the command skips it and
logs a warning. This is because the id makes the upsert safe. 

## AI use

I used Claude for the initial project scaffolding, the initial Django
migrations, the FHIR client retry test and the README. The remaining code was
written by myself (Lakshmi Priya), including the FHIR field mapping, API behavior,
migrations, React screens, other tests and revision of the README.

## If I had more time

- Follow FHIR pagination links instead of only fetching one bounded page.
- Add a `MigrationRun` table for checkpoints, counts, and failed-resource ids.
- Add a simple patient search box.
- Add a reconciliation command that compares expected and migrated counts.
