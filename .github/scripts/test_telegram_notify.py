import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
import unittest
from unittest.mock import Mock

from telegram_notify import NotificationError, format_message, send_message


JOBS = ("sanity_check", "run_tests", "mirror_repo", "build_docker_image")
RUN = "https://github.com/test/project/actions/runs/42"
GAME = "https://example.invalid/game/"
TOKEN = "123:mock_token"
CHAT = -10012345
AUTHOR = 'Злата "QA" \\ Build'
SHA = "deadbeef001122334455"


def outcomes(**changes):
    return {job: {"result": changes.get(job, "success")} for job in JOBS}


class TelegramNotificationTests(unittest.TestCase):
    def exchange(self, message, status=200, body=b'{"ok":true}'):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                return

            def do_POST(self):
                request = self.rfile.read(int(self.headers["Content-Length"]))
                requests.append((self.path, self.headers["Content-Type"], request))
                self.send_response(status)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        with HTTPServer(("127.0.0.1", 0), Handler) as server:
            server.timeout = 5
            worker = Thread(target=server.handle_request)
            worker.start()
            try:
                send_message(http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=4),
                             TOKEN, CHAT, message)
            finally:
                worker.join(timeout=6)
        self.assertEqual(len(requests), 1)
        path, content_type, payload = requests[0]
        self.assertEqual(path, f"/bot{TOKEN}/sendMessage")
        self.assertIn("application/json", content_type)
        return json.loads(payload)

    def test_success_payload_round_trips_unicode_quotes_and_newlines(self):
        message = format_message(outcomes(), AUTHOR, SHA, RUN, GAME)
        self.assertEqual(self.exchange(message), {"chat_id": CHAT, "text": message})
        self.assertIn(GAME, message)
        self.assertIn(AUTHOR, message)
        self.assertIn(RUN, message)

    def test_unity_activation_failure_notifies_even_when_docker_is_skipped(self):
        message = format_message(
            outcomes(run_tests="failure", mirror_repo="skipped", build_docker_image="skipped"),
            AUTHOR, SHA, RUN, GAME,
        )
        self.assertIn("Ошибки задач: run_tests.", message)
        self.assertIn("Пропущены: mirror_repo, build_docker_image.", message)
        self.assertIn(RUN, message)
        self.assertNotIn(GAME, message)
        self.assertEqual(self.exchange(message)["text"], message)

    def test_skipped_and_cancelled_jobs_are_not_success(self):
        for status in ("skipped", "cancelled"):
            with self.subTest(status=status):
                message = format_message(outcomes(run_tests=status), AUTHOR, SHA, RUN, GAME)
                self.assertNotIn("завершились успешно", message)
                self.assertNotIn(GAME, message)

    def test_check_message_identifies_simulation(self):
        message = format_message(outcomes(), AUTHOR, SHA, RUN, check=True)
        self.assertIn("Unity не запускалась", message)
        self.assertNotIn("Игра:", message)

    def test_incomplete_status_is_rejected(self):
        with self.assertRaises(NotificationError):
            format_message({}, AUTHOR, SHA, RUN)

    def test_http_errors_do_not_expose_request_credentials(self):
        for status in (400, 401, 403, 429, 500):
            with self.subTest(status=status):
                with self.assertRaisesRegex(NotificationError, f"HTTP {status}") as error:
                    self.exchange("test", status, f'{{"description":"{TOKEN} {CHAT}"}}'.encode())
                self.assertNotIn(TOKEN, str(error.exception))
                self.assertNotIn(str(CHAT), str(error.exception))

    def test_api_error_and_malformed_json_are_failures(self):
        for body, diagnostic in ((b'{"ok":false}', "ok != true"), (b'not-json', "некорректный JSON")):
            with self.subTest(body=body):
                with self.assertRaisesRegex(NotificationError, diagnostic):
                    self.exchange("test", body=body)

    def test_transport_exception_is_redacted(self):
        connection = Mock()
        connection.request.side_effect = OSError(f"Failure with {TOKEN}")
        with self.assertRaises(NotificationError) as error:
            send_message(connection, TOKEN, CHAT, "test")
        self.assertNotIn(TOKEN, str(error.exception))
        connection.close.assert_called_once()
