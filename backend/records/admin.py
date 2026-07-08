from django.contrib import admin

from .models import Observation, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "fhir_id", "gender", "birth_date")
    search_fields = ("name", "fhir_id")


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("code_text", "value_text", "patient", "effective_date", "status")
    list_filter = ("status",)
