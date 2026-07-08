from django.db.models import Count
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Patient
from .serializers import PatientDetailSerializer, PatientListSerializer


class PatientViewSet(ReadOnlyModelViewSet):
    queryset = Patient.objects.annotate(observation_count=Count("observations")).order_by("name")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PatientDetailSerializer
        return PatientListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("observations")
        return queryset
