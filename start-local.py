"""Local portfolio server and dashboard editor API."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import uuid
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DASHBOARD = ROOT / "dashboard"
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "portfolio.json"
FRONTEND_DATA_FILE = DIST / "data" / "portfolio.json"
SYNC_SOURCE = ROOT / "scripts" / "portfolio-sync.js"
SYNC_TARGET = DIST / "portfolio-sync.js"
UPLOAD_DIR = DIST / "wp-content" / "uploads" / "portfolio"
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def atomic_write_json(path: Path, value: object) -> None:
    """Write through a temporary file so a failed write cannot corrupt JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        json.dump(value, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        temporary_path = Path(tmp.name)
    os.replace(temporary_path, path)


def ensure_project_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        atomic_write_json(DATA_FILE, {"profile": {}, "projects": [], "experience": [], "testimonials": []})
    sync_frontend(json.loads(DATA_FILE.read_text(encoding="utf-8")))


def sync_frontend(value: object) -> None:
    """Copy dashboard data and the content-only sync script into the deployable site."""
    atomic_write_json(FRONTEND_DATA_FILE, value)
    if SYNC_SOURCE.exists():
        SYNC_TARGET.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SYNC_SOURCE, SYNC_TARGET)
    homepage = DIST / "index.html"
    html = homepage.read_text(encoding="utf-8")
    tag = '<script src="/portfolio-sync.js"></script>'
    if tag not in html:
        homepage.write_text(html.replace("</body>", f"{tag}</body>"), encoding="utf-8")


def safe_filename(filename: str) -> str:
    original = Path(filename).name
    extension = Path(original).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Format harus JPG, JPEG, PNG, WEBP, GIF, atau SVG.")
    stem = re.sub(r"[^a-z0-9]+", "-", Path(original).stem.lower()).strip("-") or "image"
    return f"{stem}-{uuid.uuid4().hex[:8]}{extension}"


class PortfolioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def _send_json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = HTTPStatus.BAD_REQUEST) -> None:
        self._send_json({"ok": False, "error": message}, status)

    def _read_body(self, limit: int) -> bytes | None:
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            self._send_error_json("Content-Length tidak valid.", HTTPStatus.LENGTH_REQUIRED)
            return None
        if length < 0 or length > limit:
            self._send_error_json("Ukuran request terlalu besar.", HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return None
        return self.rfile.read(length)

    def do_GET(self) -> None:  # noqa: N802 - required by http.server
        path = urlparse(self.path).path
        if path in {"/dashboard", "/dashboard/"}:
            dashboard_file = DASHBOARD / "index.html"
            if not dashboard_file.exists():
                self.send_error(HTTPStatus.NOT_FOUND, "Dashboard belum tersedia")
                return
            body = dashboard_file.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/data":
            try:
                self._send_json(json.loads(DATA_FILE.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError) as exc:
                self._send_error_json(f"Gagal membaca data: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - required by http.server
        path = urlparse(self.path).path
        if path == "/api/data":
            body = self._read_body(MAX_JSON_BYTES)
            if body is None:
                return
            try:
                value = json.loads(body.decode("utf-8"))
                if not isinstance(value, dict):
                    raise ValueError("Data utama harus berupa object JSON.")
                atomic_write_json(DATA_FILE, value)
                sync_frontend(value)
                self._send_json({"ok": True, "message": "Data tersimpan dan website utama diperbarui."})
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                self._send_error_json(f"JSON tidak valid: {exc}")
            except OSError as exc:
                self._send_error_json(f"Gagal menyimpan data: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if path == "/api/upload-image":
            self._upload_image()
            return
        self._send_error_json("Endpoint tidak ditemukan.", HTTPStatus.NOT_FOUND)

    def _upload_image(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            self._send_error_json("Content-Length tidak valid.", HTTPStatus.LENGTH_REQUIRED)
            return
        if length < 0 or length > MAX_IMAGE_BYTES:
            self._send_error_json("Ukuran gambar maksimal 10 MB.", HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        if not self.headers.get("Content-Type", "").startswith("multipart/form-data"):
            self._send_error_json("Upload harus menggunakan multipart/form-data.")
            return

        import cgi
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST"})
        upload = form["image"] if "image" in form else None
        if upload is None or not getattr(upload, "filename", None):
            self._send_error_json("Pilih file gambar terlebih dahulu.")
            return
        try:
            filename = safe_filename(upload.filename)
            destination = UPLOAD_DIR / filename
            with destination.open("wb") as output:
                shutil.copyfileobj(upload.file, output)
            self._send_json({"ok": True, "filename": filename, "url": f"/wp-content/uploads/portfolio/{filename}"})
        except ValueError as exc:
            self._send_error_json(str(exc))
        except OSError as exc:
            self._send_error_json(f"Gagal menyimpan gambar: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    ensure_project_dirs()
    port = int(os.environ.get("PORT", "8080"))
    with ThreadingHTTPServer(("127.0.0.1", port), PortfolioHandler) as server:
        print(f"Website lokal: http://localhost:{port}")
        print(f"Dashboard lokal: http://localhost:{port}/dashboard/")
        print("Tekan Ctrl+C untuk berhenti.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
