from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from records.models import Observation, Patient


class PatientApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = Patient.objects.create(
            fhir_id="abc123", name="Jane Doe", gender="female", birth_date="1990-01-01"
        )
        Observation.objects.create(
            fhir_id="obs1", patient=self.patient, code_text="Glucose", value_text="90 mg"
        )
        Observation.objects.create(
            fhir_id="obs2", patient=self.patient, code_text="Blood pressure", value_text="120/80"
        )

    def test_detail_returns_nested_observations(self):
        response = self.client.get(reverse("patient-detail", args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["observations"]), 2)
        codes = {obs["code_text"] for obs in response.data["observations"]}
        self.assertEqual(codes, {"Glucose", "Blood pressure"})
