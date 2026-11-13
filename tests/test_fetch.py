import contextlib
import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from scripts import build_site, fetch_availability

DATA = json.loads((build_site.ROOT / "data" / "availability.json").read_text())


class Stub(BaseHTTPRequestHandler):
    status, body = 200, b""

    def do_GET(self):
        self.send_response(self.status)
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


class FetchTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.target = Path(self.dir.name) / "availability.json"
        self.original = json.dumps(DATA, indent=2).encode()
        self.target.write_bytes(self.original)
        self.server = HTTPServer(("127.0.0.1", 0), type("H", (Stub,), {}))
        self.handler = self.server.RequestHandlerClass
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_port}/"

    def serve(self, body, status=200):
        self.handler.status = status
        self.handler.body = body if isinstance(body, bytes) else json.dumps(body).encode()

    def refresh(self):
        with contextlib.redirect_stderr(io.StringIO()):
            return fetch_availability.main(self.url, self.target)

    def assert_untouched(self):
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertEqual(list(Path(self.dir.name).iterdir()), [self.target])

    def test_empty_response_keeps_data(self):
        self.serve(b"")
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_malformed_json_keeps_data(self):
        self.serve(b"{not json")
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_empty_store_list_keeps_data(self):
        self.serve({**DATA, "updated_at": "2026-11-14T02:00:00Z", "stores": []})
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_missing_store_keeps_data(self):
        self.serve({**DATA, "updated_at": "2026-11-14T02:00:00Z", "stores": DATA["stores"][1:]})
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_missing_order_url_keeps_data(self):
        stores = [dict(s) for s in DATA["stores"]]
        del stores[0]["order_url"]
        self.serve({**DATA, "updated_at": "2026-11-14T02:00:00Z", "stores": stores})
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_stale_timestamp_keeps_data(self):
        self.serve({**DATA, "updated_at": "2020-01-01T00:00:00Z"})
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_http_error_keeps_data(self):
        self.serve(json.dumps({**DATA, "updated_at": "2026-11-14T02:00:00Z"}), status=503)
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_unreachable_keeps_data(self):
        self.server.shutdown()
        self.server.server_close()
        self.assertNotEqual(self.refresh(), 0)
        self.assert_untouched()

    def test_valid_response_replaces_data(self):
        fresh = {**DATA, "updated_at": "2026-11-14T02:00:00Z"}
        fresh["stores"] = [dict(s, status="in_stock") for s in DATA["stores"]]
        self.serve(fresh)
        self.assertEqual(self.refresh(), 0)
        self.assertEqual(json.loads(self.target.read_text()), fresh)
        self.assertEqual(list(Path(self.dir.name).iterdir()), [self.target])


if __name__ == "__main__":
    unittest.main()
