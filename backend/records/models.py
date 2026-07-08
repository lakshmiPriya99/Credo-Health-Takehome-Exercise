from django.db import models


class Patient(models.Model):
    fhir_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255, default="Unknown")
    gender = models.CharField(max_length=20, blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.fhir_id})"


class Observation(models.Model):
    fhir_id = models.CharField(max_length=64, unique=True, db_index=True)
    patient = models.ForeignKey(Patient, related_name="observations", on_delete=models.CASCADE)
    code_text = models.CharField(max_length=255, default="Unknown")
    value_text = models.CharField(max_length=500, blank=True, default="")
    effective_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code_text}: {self.value_text}"
