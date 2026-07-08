from django.core.management.base import BaseCommand

from records.fhir.client import fetch_observations_for_patient, fetch_patients
from records.fhir.transform import observation_fields_from_fhir, patient_fields_from_fhir
from records.models import Observation, Patient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Number of patients to fetch")
        parser.add_argument(
            "--obs-count", type=int, default=20, help="Max observations to fetch per patient"
        )

    def handle(self, *args, **options):
        count = options["count"]
        obs_count = options["obs_count"]

        try:
            patient_resources = fetch_patients(count)
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Failed to fetch patients: {exc}"))
            return

        patients_created = 0
        patients_updated = 0
        observations_migrated = 0
        skipped_observations = 0
        errors = []

        for index, resource in enumerate(patient_resources, start=1):
            fhir_id = resource.get("id")

            if not fhir_id:
                errors.append((f"bundle entry {index}", "missing Patient.id"))
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping Patient bundle entry {index}: missing id"
                    )
                )
                continue

            try:
                fields = patient_fields_from_fhir(resource)
                patient, created = Patient.objects.update_or_create(
                    fhir_id=fhir_id, defaults=fields
                )
                patients_created += created
                patients_updated += not created

                obs_resources = fetch_observations_for_patient(fhir_id, obs_count)
                for obs_index, obs_resource in enumerate(obs_resources, start=1):
                    obs_fhir_id = obs_resource.get("id")
                    if not obs_fhir_id:
                        skipped_observations += 1
                        self.stderr.write(
                            self.style.WARNING(
                                "Skipping Observation entry "
                                f"{obs_index} for patient {fhir_id}: missing id"
                            )
                        )
                        continue

                    obs_fields = observation_fields_from_fhir(obs_resource)
                    Observation.objects.update_or_create(
                        fhir_id=obs_fhir_id,
                        defaults={**obs_fields, "patient": patient},
                    )
                    observations_migrated += 1
            except Exception as exc:
                errors.append((fhir_id, str(exc)))
                self.stderr.write(self.style.WARNING(f"Error processing patient {fhir_id}: {exc}"))
                continue

        self.stdout.write(self.style.SUCCESS("\nMigration complete."))
        self.stdout.write(
            f"Patients processed: {len(patient_resources) - len(errors)}/{len(patient_resources)} "
            f"({len(errors)} errors)"
        )
        self.stdout.write(f"  created: {patients_created}, updated: {patients_updated}")
        self.stdout.write(f"Observations migrated: {observations_migrated}")
        if skipped_observations:
            self.stdout.write(f"Observations skipped: {skipped_observations}")
        if errors:
            self.stdout.write("Errors:")
            for fhir_id, message in errors:
                self.stdout.write(f"  - Patient {fhir_id}: {message}")
