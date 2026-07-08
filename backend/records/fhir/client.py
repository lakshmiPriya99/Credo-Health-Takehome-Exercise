import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT = (5, 15)  


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


session = _build_session()


def _entries(bundle: dict) -> list:
    return [entry["resource"] for entry in bundle.get("entry", []) if "resource" in entry]


def fetch_patients(count: int) -> list:
    url = f"{settings.FHIR_BASE_URL}/Patient"
    response = session.get(url, params={"_count": count}, timeout=TIMEOUT)
    response.raise_for_status()
    return _entries(response.json())


def fetch_observations_for_patient(patient_id: str, count: int) -> list:
    url = f"{settings.FHIR_BASE_URL}/Observation"
    response = session.get(
        url, params={"patient": patient_id, "_count": count}, timeout=TIMEOUT
    )
    response.raise_for_status()
    return _entries(response.json())
