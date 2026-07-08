import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from django.test import SimpleTestCase, override_settings

from records.fhir.client import fetch_patients

PATIENT_BUNDLE = (
    b'{"resourceType": "Bundle", "entry": '
    b'[{"resource": {"resourceType": "Patient", "id": "1"}}]}'
)


class _FlakyHandler(BaseHTTPRequestHandler):

    fail_count = 0
    calls = 0

    def do_GET(self):
        type(self).calls += 1
        if type(self).calls <= type(self).fail_count:
            self.send_response(500)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/fhir+json")
        self.end_headers()
        self.wfile.write(PATIENT_BUNDLE)

    def log_message(self, format, *args):
        pass  # keep test output quiet


class RetryBehaviorTests(SimpleTestCase):

    def _start_server(self, fail_count):
        _FlakyHandler.calls = 0
        _FlakyHandler.fail_count = fail_count
        server = HTTPServer(("127.0.0.1", 0), _FlakyHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        return f"http://127.0.0.1:{port}"

    def test_recovers_after_transient_5xx_errors(self):
        base_url = self._start_server(fail_count=2)
        with override_settings(FHIR_BASE_URL=base_url):
            resources = fetch_patients(count=1)
        self.assertEqual(resources[0]["id"], "1")
        self.assertEqual(_FlakyHandler.calls, 3)  # 2 failures + 1 eventual success
