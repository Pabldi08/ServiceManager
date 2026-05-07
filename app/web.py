from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

from app.config import addServices, deleteService, getHosts
from app.discovery import listAvailableServices
from app.hosts import parseHostInput
from app.remote import runRemoteSystemctl
from app.services import getServiceUnit
from app.status import getServiceStatuses
from app.storage import addHost, deleteHost
from app.views import renderIndex


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


def getSelectedHost(hostName=""):
    if hostName:
        return hostName

    hosts = getHosts()
    return next(iter(hosts), "")


def getSafeServiceStatuses(hostName):
    if not hostName:
        return None

    try:
        return getServiceStatuses(hostName)
    except ValueError:
        return None


class ServiceManagerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsedUrl = urlparse(self.path)
        path = parsedUrl.path

        if path in ("/", "/index.html"):
            query = parse_qs(parsedUrl.query)
            selected = {"host": getSelectedHost(query.get("host", [""])[0])}
            statuses = getSafeServiceStatuses(selected["host"])
            
            self.sendHtml(renderIndex(selected, statuses=statuses))
            return

        if path == "/static/styles.css":
            self.sendStaticCss()
            return

        if path == "/static/theme.js":
            self.sendStaticJs("theme.js")
            return

        self.send_error(404, "Pagina no encontrada")

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/run":
            self.handleRun()
            return

        if path == "/hosts":
            self.handleAddHost()
            return

        if path == "/delete-host":
            self.handleDeleteHost()
            return

        if path == "/discover":
            self.handleDiscover()
            return

        if path == "/register-services":
            self.handleRegisterServices()
            return

        if path == "/delete-service":
            self.handleDeleteService()
            return

        if path == "/status":
            self.handleStatus()
            return

        self.send_error(404, "Pagina no encontrada")

    def handleAddHost(self):
        form = self.readForm()
        hostInput = form.get("host_input", [""])[0]

        try:
            hostName = addHost(parseHostInput(hostInput))
            selected = {"host": hostName}
            result = {
                "returncode": 0,
                "stdout": f"Host registrado: {hostName}",
                "stderr": "",
            }
        except ValueError as error:
            selected = {}
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": str(error),
            }

        self.sendHtml(renderIndex(selected, result))

    def handleDeleteHost(self):
        form = self.readForm()
        hostName = form.get("host", [""])[0]

        try:
            deletedHost = deleteHost(hostName)
            selected = {"host": getSelectedHost()}
            result = {
                "returncode": 0,
                "stdout": f"Host eliminado: {deletedHost}",
                "stderr": "",
            }
        except ValueError as error:
            selected = {"host": getSelectedHost(hostName)}
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": str(error),
            }

        statuses = getSafeServiceStatuses(selected["host"])
        self.sendHtml(renderIndex(selected, result, statuses=statuses))

    def handleRun(self):
        form = self.readForm()
        selected = {
            "host": form.get("host", [""])[0],
            "service": form.get("service", [""])[0],
            "action": form.get("action", [""])[0],
        }

        try:
            serviceName = getServiceUnit(selected["service"], selected["host"])
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

        statuses = getSafeServiceStatuses(selected["host"])

        self.sendHtml(renderIndex(selected, result, statuses=statuses))

    def handleStatus(self):
        form = self.readForm()
        selected = {"host": form.get("host", [""])[0]}

        try:
            statuses = getServiceStatuses(selected["host"])
            result = {
                "returncode": 0,
                "stdout": f"Service states checked: {len(statuses)} services",
                "stderr": "",
            }
        except ValueError as error:
            statuses = []
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": str(error),
            }

        self.sendHtml(renderIndex(selected, result, statuses=statuses))

    def handleDiscover(self):
        form = self.readForm()
        selected = {"host": form.get("host", [""])[0]}

        try:
            discovery = listAvailableServices(selected["host"])
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
            self.sendHtml(renderIndex(selected, result, discoveredServices=[]))
            return

        result = {
            "returncode": 0,
            "stdout": f"Available services found: {len(discovery['services'])}",
            "stderr": "",
        }
        self.sendHtml(
            renderIndex(
                selected,
                result,
                discoveredServices=discovery["services"],
                statuses=getSafeServiceStatuses(selected["host"]),
            )
        )

    def handleRegisterServices(self):
        form = self.readForm()
        selected = {"host": form.get("host", [""])[0]}
        serviceNames = form.get("services", [])
        discoveredServices = form.get("discovered_services")

        if not serviceNames:
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": "No services selected to register",
            }
            self.sendHtml(renderIndex(selected, result, discoveredServices=discoveredServices))
            return

        addedServices = addServices(selected["host"], serviceNames)
        result = {
            "returncode": 0,
            "stdout": f"New services registered: {len(addedServices)}",
            "stderr": "",
        }
        self.sendHtml(
            renderIndex(
                selected,
                result,
                discoveredServices=discoveredServices,
                statuses=getSafeServiceStatuses(selected["host"]),
            )
        )

    def handleDeleteService(self):
        form = self.readForm()
        selected = {"host": form.get("host", [""])[0]}
        serviceKey = form.get("service", [""])[0]
        discoveredServices = form.get("discovered_services")

        try:
            serviceName = deleteService(selected["host"], serviceKey)
            result = {
                "returncode": 0,
                "stdout": f"Service removed: {serviceName}",
                "stderr": "",
            }
        except ValueError as error:
            result = {
                "returncode": 1,
                "stdout": "",
                "stderr": str(error),
            }

        self.sendHtml(
            renderIndex(
                selected,
                result,
                discoveredServices=discoveredServices,
                statuses=getSafeServiceStatuses(selected["host"]),
            )
        )

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

    def sendStaticJs(self, fileName):
        script = (STATIC_DIR / fileName).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript; charset=utf-8")
        self.send_header("Content-Length", str(len(script)))
        self.end_headers()
        self.wfile.write(script)


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
