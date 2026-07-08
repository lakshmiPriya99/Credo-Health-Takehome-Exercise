from django.test import SimpleTestCase

from records.fhir.transform import observation_fields_from_fhir, patient_fields_from_fhir


class PatientTransformTests(SimpleTestCase):
    def test_prefers_official_name_over_other_uses(self):
        resource = {
            "resourceType": "Patient",
            "id": "2",
            "name": [
                {"use": "usual", "given": ["Bob"], "family": "Nickname"},
                {"use": "official", "given": ["Robert"], "family": "Smith"},
            ],
        }
        fields = patient_fields_from_fhir(resource)
        self.assertEqual(fields["name"], "Robert Smith")


class ObservationTransformTests(SimpleTestCase):
    def test_value_quantity_formats_value_and_unit(self):
        resource = {
            "resourceType": "Observation",
            "id": "10",
            "code": {"text": "Glucose"},
            "valueQuantity": {"value": 268, "unit": "mg"},
        }
        fields = observation_fields_from_fhir(resource)
        self.assertEqual(fields["value_text"], "268 mg")
