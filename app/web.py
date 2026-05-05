from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

from app.config import addServices, getHosts
from app.discovery import discoverServices
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


def renderDiscoveredServices(selectedHost=None, discoveredServices=None):
    if not discoveredServices:
        return ""

    serviceInputs = []
    registeredServices = set(getAllowedServices().values())

    for serviceName in discoveredServices:
        checked = "" if serviceName in registeredServices else " checked"
        disabled = " disabled" if serviceName in registeredServices else ""
        badge = " <span>registrado</span>" if serviceName in registeredServices else ""
        escapedService = escape(serviceName)

        serviceInputs.append(f"""
          <label class="check-row">
            <input type="checkbox" name="services" value="{escapedService}"{checked}{disabled}>
            <span>{escapedService}{badge}</span>
          </label>
        """)

    return f"""
    <section class="panel discovery-results">
      <h2>Servicios descubiertos</h2>
      <p>Selecciona los servicios que quieres registrar como permitidos.</p>
      <form method="post" action="/register-services" class="discovery-list">
        <input type="hidden" name="host" value="{escape(selectedHost or '')}">
        {''.join(serviceInputs)}
        <button type="submit">Registrar seleccionados</button>
      </form>
    </section>
    """


def renderIndex(selected=None, result=None, discoveredServices=None):
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
    html = html.replace(
        "{{ discovery_host_options }}",
        buildOptions(hosts, selected.get("host")),
    )
    html = html.replace(
        "{{ discovered_services }}",
        renderDiscoveredServices(selected.get("host"), discoveredServices),
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

        if path == "/run":
            self.handleRun()
            return

        if path == "/discover":
            self.handleDiscover()
            return

        if path == "/register-services":
            self.handleRegisterServices()
            return

        self.send_error(404, "Pagina no encontrada")

    def handleRun(self):
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

    def handleDiscover(self):
        form = self.readForm()
        selected = {"host": form.get("host", [""])[0]}

        try:
            discovery = discoverServices(selected["host"])
        except ValueError as error:
            discovery = {
                "returncode": 1,
                "services": [],
                "stderr": str(error),
            }

        if discovery["returncode"] != 0:
            result = {
                "returncode": discovery["returncode"],
                "stdout": "",
                "stderr": discovery["stderr"],
            }
            self.sendHtml(renderIndex(selected, result))
            return

        result = {
            "returncode": 0,
            "stdout": f"Se encontraron {len(discovery['services'])} servicios",
            "stderr": "",
        }
        self.sendHtml(renderIndex(selected, result, discovery["services"]))

    def handleRegisterServices(self):
        form = self.readForm()
        selected = {"host": form.get("host", [""])[0]}
        serviceNames = form.get("services", [])

        if not serviceNames:
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": "No se seleccionaron servicios para registrar",
            }
            self.sendHtml(renderIndex(selected, result))
            return

        addedServices = addServices(serviceNames)
        result = {
            "returncode": 0,
            "stdout": f"Servicios nuevos registrados: {len(addedServices)}",
            "stderr": "",
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


def getServerPort(defaultPort=5500):
    portValue = os.environ.get("PORT")

    if portValue is None:
        return defaultPort

    try:
        return int(portValue)
    except ValueError as error:
        raise ValueError("La variable PORT debe ser un numero") from error


def runServer(host="127.0.0.1", port=None):
    port = port or getServerPort()

    try:
        server = ThreadingHTTPServer((host, port), ServiceManagerHandler)
    except OSError as error:
        if error.errno == 98:
            print(
                f"No se pudo iniciar ServiceManager: el puerto {port} ya esta en uso."
            )
            print("Cierra el servidor anterior o usa otro puerto con PORT=5501 python3 run.py")
            return

        raise

    if sys.stdout is not None:
        try:
            print(f"ServiceManager disponible en http://{host}:{port}")
        except OSError:
            pass
    server.serve_forever()
