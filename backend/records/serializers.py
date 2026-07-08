from rest_framework import serializers

from .models import Observation, Patient


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ["id", "fhir_id", "code_text", "value_text", "effective_date", "status"]


class PatientListSerializer(serializers.ModelSerializer):
    observation_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = ["id", "fhir_id", "name", "gender", "birth_date", "observation_count"]


class PatientDetailSerializer(serializers.ModelSerializer):
    observations = ObservationSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = ["id", "fhir_id", "name", "gender", "birth_date", "observations"]
