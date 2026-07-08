# Migration plan

## Overall approach

I would run the migration as a batch job, not as a web request. The job would
page through `Patient` resources from the FHIR API, then fetch related
`Observation` resources for each patient. Each batch would be small enough to
retry safely if the external API slows down or returns temporary errors.

The importer would use stable FHIR ids as idempotency keys. That means the
same patient or observation can be processed more than once without creating
duplicates. I would also keep a `MigrationRun` table with start time, end time,
status, counts, and any failed resource ids. This will have a clear audit trail and will
make it easier to resume after a partial failure.

For reliability, I would include:

- Pagination using FHIR bundle `next` links
- Retry with backoff for `429` and temporary `5xx` responses
- Per-patient error handling so that a single bad record does not stop the whole run
- Batch-level logging for fetched, inserted, updated, skipped, and failed counts
- A dry-run mode for checking mappings before writing data

## Data mapping

For `Patient`, I would map:

- `id` -> `fhir_id`
- preferred name from `name` -> `name`
- `gender` -> `gender`
- `birthDate` -> `birth_date`

For `Observation`, I would map:

- `id` -> `fhir_id`
- patient reference -> local patient foreign key
- `code.text` or first coding display/code -> `code_text`
- supported `value[x]` fields -> `value_text`
- `effectiveDateTime` or `effectivePeriod.start` -> `effective_date`
- `status` -> `status`

If a resource is missing its FHIR id, I would skip it and log it as it will be
needed in the future for safe upserts.

## Validation

I would validate the migration in a few layers.

First, I would compare counts:

- number of patients fetched from FHIR
- number of patients inserted or updated locally
- number of observations fetched
- number of observations inserted or updated locally
- number of skipped or failed resources

Second, I would sample records and compare important fields against the source
FHIR response. For example, I would pick a few migrated patients and verify
their name, gender, birth date, and observation values.

Third, I would add automated checks around the mapping code. The important
edge cases are nested patient names, missing optional fields, observation
`valueQuantity`, and observations with no usable value.

## Safety and PHI

For the exercise, I have used only the public HAPI FHIR sandbox and synthetic data.
In a real migration, I would treat all source data as PHI.

That means:

- Do not log full patient names, birth dates, or raw FHIR payloads
- Store secrets in environment variables or a secret manager
- Use encrypted connections to the source API and internal database
- Restrict database and log access to only the people who need it
- Keep an audit trail of migration runs and operator actions
- Avoid copying raw FHIR data into temporary files unless there is a retention
  and cleanup policy

## Rollback and recovery

The safest rollback strategy is to make writes idempotent and track each run.
If a run fails halfway through, I would mark the run as failed, keep the failed
resource ids, and restart from the last successful checkpoint.

If bad data is written, I would use the `MigrationRun` records to identify rows
created or updated by that run. Depending on the issue, I would either:

- rerun the migration after fixing the mapping, because upserts can correct the
  rows, or
- roll back rows linked to the failed run if the data should not remain visible

Before running this against production data, I would test the process in a
staging environment with production-like synthetic data and verify both the
resume path and rollback path.
