from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

from app.config import getHosts
from app.remote import runRemoteSystemctl
from app.services import getAllowedActions, getAllowedServices, getServiceUnit


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "static"


def buildOptions(items, selectedValue=None):
    options = []

    for value, label in items:
        selected = " selected" if value == selectedValue else ""
        options.append(
            f'<option value="{escape(value)}"{selected}>{escape(label)}</option>'
        )

    return "\n".join(options)


def renderResult(result):
    if result is None:
        return ""

    statusClass = "result-ok" if result["returncode"] == 0 else "result-error"
    stdout = escape(result["stdout"]) or "(sin salida)"
    stderr = escape(result["stderr"]) or "(sin error)"

    return f"""
    <section class="result {statusClass}">
      <div class="result-header">
        <h2>Resultado</h2>
        <span>codigo {result["returncode"]}</span>
      </div>
      <label>Salida</label>
      <pre>{stdout}</pre>
      <label>Error</label>
      <pre>{stderr}</pre>
    </section>
    """


def renderIndex(selected=None, result=None):
    selected = selected or {}
    hosts = [(hostName, hostName) for hostName in getHosts()]
    services = [
        (serviceKey, f"{serviceKey} ({serviceName})")
        for serviceKey, serviceName in getAllowedServices().items()
    ]
    actions = [(action, action) for action in getAllowedActions()]

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = html.replace("{{ host_options }}", buildOptions(hosts, selected.get("host")))
    html = html.replace(
        "{{ service_options }}",
        buildOptions(services, selected.get("service")),
    )
    html = html.replace(
        "{{ action_options }}",
        buildOptions(actions, selected.get("action")),
    )
    html = html.replace("{{ result }}", renderResult(result))
    return html


class ServiceManagerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            self.sendHtml(renderIndex())
            return

        if path == "/static/styles.css":
            self.sendStaticCss()
            return

        self.send_error(404, "Pagina no encontrada")

    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/run":
            self.send_error(404, "Pagina no encontrada")
            return

        form = self.readForm()
        selected = {
            "host": form.get("host", [""])[0],
            "service": form.get("service", [""])[0],
            "action": form.get("action", [""])[0],
        }

        try:
            serviceName = getServiceUnit(selected["service"])
            result = runRemoteSystemctl(
                hostName=selected["host"],
                action=selected["action"],
                serviceName=serviceName,
            )
        except ValueError as error:
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": str(error),
            }

        self.sendHtml(renderIndex(selected, result))

    def readForm(self):
        contentLength = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(contentLength).decode("utf-8")
        return parse_qs(body)

    def sendHtml(self, html):
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def sendStaticCss(self):
        css = (STATIC_DIR / "styles.css").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(css)))
        self.end_headers()
        self.wfile.write(css)


def runServer(host="127.0.0.1", port=5500):
    server = ThreadingHTTPServer((host, port), ServiceManagerHandler)
    if sys.stdout is not None:
        try:
            print(f"ServiceManager disponible en http://{host}:{port}")
        except OSError:
            pass
    server.serve_forever()
