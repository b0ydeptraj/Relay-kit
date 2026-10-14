import json
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

from tools.api_interceptor.codegen import generate_curl_command, generate_python_script
from tools.api_interceptor.mobile_helper import (
    FRIDA_UNIVERSAL_SSL_BYPASS,
    compute_openssl_subject_hash,
    prepare_system_ca_cert,
)
from tools.api_interceptor.models import CapturedRequest, extract_security_tokens
from tools.api_interceptor.sniffer_hub import SnifferHub, run_sniffer_hub


class TestApiInterceptorModels(unittest.TestCase):
    def test_token_extraction_from_headers_and_query(self):
        url = "https://www.tiktok.com/api/item/list/?msToken=fake_mstoken_123&X-Bogus=bogus_abc"
        headers = {
            "Cookie": "sessionid=test_session_999; passport_csrf_token=csrf_tok_888",
            "X-Gorgon": "040440040001",
            "X-Khronos": "1700000000",
            "Authorization": "Bearer eyJhbGciOi...",
        }
        body = json.dumps({"device_id": "7123456789012345678"})

        tokens = extract_security_tokens(url, headers, body)
        self.assertEqual(tokens.get("msToken"), "fake_mstoken_123")
        self.assertEqual(tokens.get("X-Bogus"), "bogus_abc")
        self.assertEqual(tokens.get("cookie_sessionid"), "test_session_999")
        self.assertEqual(tokens.get("x-gorgon"), "040440040001")
        self.assertEqual(tokens.get("authorization"), "Bearer eyJhbGciOi...")
        self.assertEqual(tokens.get("body_device_id"), "7123456789012345678")

    def test_captured_request_serialization(self):
        req = CapturedRequest(
            url="https://api.tiktok.com/v1/video/upload",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"title": "Test Video"}),
            source="mobile",
        )
        d = req.to_dict()
        self.assertEqual(d["method"], "POST")
        self.assertEqual(d["source"], "mobile")
        self.assertEqual(d["host"], "api.tiktok.com")
        self.assertEqual(d["path"], "/v1/video/upload")

        # Reconstruct
        restored = CapturedRequest.from_dict(d)
        self.assertEqual(restored.id, req.id)
        self.assertEqual(restored.url, req.url)
        self.assertEqual(restored.source, "mobile")

    def test_action_correlation_and_user_data_spotlight(self):
        # Simulating request triggered by clicking 'Xem hồ sơ' returning JSON with username
        req = CapturedRequest(
            url="https://example.com/api/v1/profile/detail?uid=1052",
            method="GET",
            response_body=json.dumps({"username": "NguyenVanA", "id": 1052, "email": "a@example.com"}),
            trigger_action="Xem hồ sơ",
        )
        d = req.to_dict()
        self.assertTrue(d["is_important"])
        self.assertIn("IMPORTANT", d["tags"])
        self.assertIn("USER", d["tags"])
        self.assertIn("IDOR", d["tags"])
        self.assertEqual(d["trigger_action"], "Xem hồ sơ")
        self.assertIn("NguyenVanA", d["preview_summary"])
        self.assertIn('Kích hoạt bởi: "Xem hồ sơ"', d["highlight_reason"])

    def test_form_submission_and_vietnamese_auth_tags(self):
        # Simulating form submission from university portal with Vietnamese credentials and ASP.NET ViewState
        req = CapturedRequest(
            url="http://118.70.155.201/Login.aspx",
            method="POST",
            headers={"Cookie": "ASP.NET_SessionId=sess123; .ASPXAUTH=AUTH_TICKET_999"},
            body="__VIEWSTATE=wEPDwUKMT&__EVENTVALIDATION=wEdAAUC&txtusername=SV2026001&txtpassword=Secret123&btnDangNhap=%C4%90%C4%83ng+nh%E1%BA%ADp",
            trigger_action="Đăng nhập",
        )
        d = req.to_dict()
        self.assertTrue(d["is_important"])
        self.assertIn("AUTH", d["tags"])
        self.assertIn("ACTION", d["tags"])
        self.assertEqual(d["trigger_action"], "Đăng nhập")
        self.assertFalse(d["is_noise"])
        self.assertIn("txtusername", d["extracted_tokens"])
        self.assertIn("txtpassword", d["extracted_tokens"])
        self.assertIn("__VIEWSTATE", d["extracted_tokens"])
        self.assertIn(".ASPXAUTH", d["extracted_tokens"])
        self.assertEqual(d["extracted_tokens"][".ASPXAUTH"], "AUTH_TICKET_999")
        self.assertEqual(d["extracted_tokens"]["txtusername"], "SV2026001")
        self.assertEqual(d["extracted_tokens"]["txtpassword"], "Secret123")


class TestApiInterceptorCodegen(unittest.TestCase):
    def test_generate_python_script(self):
        req = CapturedRequest(
            url="https://www.tiktok.com/api/post",
            method="POST",
            headers={"X-Test": "123", "Content-Type": "application/json"},
            body=json.dumps({"title": "Reup Video"}),
        )
        py_code = generate_python_script(req)
        self.assertIn("import requests", py_code)
        self.assertIn("https://www.tiktok.com/api/post", py_code)
        self.assertIn('"X-Test": "123"', py_code)
        self.assertIn("requests.post", py_code)
        self.assertIn("json=payload", py_code)

    def test_generate_curl_command(self):
        req = CapturedRequest(
            url="https://www.tiktok.com/api/feed",
            method="GET",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        curl_cmd = generate_curl_command(req)
        self.assertTrue(curl_cmd.startswith("curl -X GET"))
        self.assertIn('"https://www.tiktok.com/api/feed"', curl_cmd)
        self.assertIn('-H "User-Agent: Mozilla/5.0"', curl_cmd)


class TestMobileHelper(unittest.TestCase):
    def test_frida_script_content(self):
        self.assertIn("libsscronet.so", FRIDA_UNIVERSAL_SSL_BYPASS)
        self.assertIn("TrustManagerImpl", FRIDA_UNIVERSAL_SSL_BYPASS)
        self.assertIn("SSL_CTX_set_custom_verify", FRIDA_UNIVERSAL_SSL_BYPASS)

    def test_prepare_system_ca_cert(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cert_file = tmp_path / "test_ca.pem"
            cert_file.write_bytes(b"-----BEGIN CERTIFICATE-----\nFAKE_CERT_DATA\n-----END CERTIFICATE-----")

            res = prepare_system_ca_cert(cert_file, output_dir=tmp_path)
            self.assertTrue(res["system_hash"].endswith(".0"))
            self.assertTrue(Path(res["output_file"]).is_file())
            self.assertIn("adb push", res["adb_instructions"])


class TestSnifferHubServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8998  # Use 8998 for isolated unit test
        cls.server = run_sniffer_hub(port=cls.port, host="127.0.0.1")
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_hub_lifecycle_and_http_endpoints(self):
        base_url = f"http://127.0.0.1:{self.port}"

        # 1. Check status
        with urllib.request.urlopen(f"{base_url}/api/status") as resp:
            data = json.loads(resp.read().decode())
            self.assertTrue(data["ok"])
            self.assertEqual(data["total_captured"], 0)

        # 2. Ingest desktop request
        sample_req = {
            "url": "https://www.tiktok.com/api/item/create/?msToken=tok_test",
            "method": "POST",
            "headers": {"X-Bogus": "bogus_123"},
            "body": json.dumps({"caption": "Hello world"}),
            "source": "desktop",
        }
        post_data = json.dumps(sample_req).encode()
        req = urllib.request.Request(
            f"{base_url}/api/ingest",
            data=post_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            ingest_res = json.loads(resp.read().decode())
            self.assertTrue(ingest_res["ok"])
            req_id = ingest_res["request"]["id"]

        # 3. Check feed
        with urllib.request.urlopen(f"{base_url}/api/feed?filter=tiktok") as resp:
            feed_data = json.loads(resp.read().decode())
            self.assertTrue(feed_data["ok"])
            self.assertEqual(len(feed_data["requests"]), 1)
            self.assertEqual(feed_data["requests"][0]["id"], req_id)

        # 4. Codegen endpoint
        with urllib.request.urlopen(f"{base_url}/api/codegen/{req_id}") as resp:
            code_res = json.loads(resp.read().decode())
            self.assertTrue(code_res["ok"])
            self.assertIn("requests.post", code_res["python"])
            self.assertIn("curl -X POST", code_res["curl"])

        # 5. Tokens endpoint
        with urllib.request.urlopen(f"{base_url}/api/tokens") as resp:
            tokens_res = json.loads(resp.read().decode())
            self.assertTrue(tokens_res["ok"])
            self.assertIn("www.tiktok.com", tokens_res["tokens"])

        # 6. Test ingesting self-capture URL does not throw 500 error
        ignored_req = {
            "url": "http://127.0.0.1:8999/api/feed",
            "method": "GET",
        }
        req_ignored = urllib.request.Request(
            f"{base_url}/api/ingest",
            data=json.dumps(ignored_req).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_ignored) as resp:
            ignored_res = json.loads(resp.read().decode())
            self.assertTrue(ignored_res["ok"])
            self.assertIsNone(ignored_res["request"])


if __name__ == "__main__":
    unittest.main()
