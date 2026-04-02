import mimetypes
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = Path(os.getenv("APP_DATA_DIR", "storage"))
if not DATA_DIR.is_absolute():
    DATA_DIR = BASE_DIR / DATA_DIR
DATA_FILE = DATA_DIR / "data.json"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_messages() -> dict:
    if not DATA_FILE.exists():
        print(f"{DATA_FILE} does not exist. Returning empty messages.")
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            print(f"Loading messages from {DATA_FILE}...")
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def save_messages(messages: dict) -> None:
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._send_html_file(f"{TEMPLATES_DIR}/index.html")
        elif self.path == "/message":
            self._send_html_file(f"{TEMPLATES_DIR}/message.html")
        elif self.path == "/read":
            # Load messages from data.json
            messages = load_messages()

            # Render the template with messages
            template = env.get_template("read.html")
            rendered_html = template.render(messages=messages)

            self._set_successful_response()
            self.wfile.write(rendered_html.encode())
        else:
            # Serve static files
            requested_path = (BASE_DIR / self.path.lstrip("/")).resolve()

            if not str(requested_path).startswith(str(BASE_DIR)):
                self.send_error(403)
                return

            if requested_path.exists() and requested_path.is_file():
                self._send_static(requested_path)
            else:
                self._send_html_file(f"{TEMPLATES_DIR}/error.html", status=404)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode())

            # Extract username and message
            username = data.get("username", [""])[0]
            message = data.get("message", [""])[0]

            # Create a dictionary to store the message
            message_data = {"username": username, "message": message}

            # Save the message to data.json
            existing_data = load_messages()

            timestamp = datetime.now().isoformat()
            existing_data[timestamp] = message_data
            save_messages(existing_data)

            # Redirect back to the message page
            self.send_response(303)
            self.send_header("Location", "/message")
            self.end_headers()

    def _send_html_file(self, filename, status=200):
        if not Path(filename).exists():
            self.send_error(404, "File not found")
            return
        self._set_successful_response(status, "text/html")
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def _send_static(self, filename, status=200):
        if filename.is_file():
            mime_type, _ = mimetypes.guess_type(filename)
            self._set_successful_response(
                status, mime_type or "application/octet-stream"
            )
            with open(filename, "rb") as file:
                self.wfile.write(file.read())

    def _set_successful_response(self, status=200, content_type="text/html"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()


def run(server_class=HTTPServer, handler_class=MyRequestHandler, port=3000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server.")
        pass
    httpd.server_close()


if __name__ == "__main__":
    run()
