import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "settings.json"

ALLOWED_ACTIONS = [
    "status",
    "is-active",
    "start",
    "stop",
    "restart",
]


def loadSettings(path=SETTINGS_PATH):
    try:
        with open(path, encoding="utf-8") as settingsFile:
            return json.load(settingsFile)
    except FileNotFoundError as error:
        raise ValueError(f"No se encontro el archivo de configuracion: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"El archivo de configuracion no tiene JSON valido: {path}") from error


def saveSettings(settings, path=SETTINGS_PATH):
    with open(path, "w", encoding="utf-8") as settingsFile:
        json.dump(settings, settingsFile, indent=2)
        settingsFile.write("\n")


def getHosts():
    return loadSettings().get("hosts", {})


def getHost(hostName):
    hosts = getHosts()

    if hostName not in hosts:
        raise ValueError("Host no permitido")

    hostData = hosts[hostName]
    validateHostConfig(hostName, hostData)
    return hostData


def validateHostConfig(hostName, hostData):
    if not isinstance(hostData, dict):
        raise ValueError(f"La configuracion del host '{hostName}' no es valida")

    if not hostData.get("user"):
        raise ValueError(f"El host '{hostName}' no tiene usuario SSH configurado")

    if not hostData.get("host"):
        raise ValueError(f"El host '{hostName}' no tiene direccion SSH configurada")

    port = hostData.get("port", 22)
    if not isinstance(port, int) or port <= 0:
        raise ValueError(f"El host '{hostName}' tiene un puerto SSH no valido")

    keyPath = hostData.get("key_path")
    if keyPath is not None and not keyPath:
        raise ValueError(f"El host '{hostName}' tiene una ruta de llave SSH no valida")


def getServices():
    return loadSettings().get("services", {})


def makeServiceKey(serviceName):
    key = serviceName.removesuffix(".service")
    cleanKey = []

    for character in key:
        if character.isalnum() or character in ("-", "_"):
            cleanKey.append(character)
        else:
            cleanKey.append("_")

    return "".join(cleanKey)


def addServices(serviceNames, path=SETTINGS_PATH):
    settings = loadSettings(path)
    services = settings.setdefault("services", {})
    added = []

    for serviceName in serviceNames:
        if not serviceName.endswith(".service"):
            continue

        serviceKey = makeServiceKey(serviceName)
        if serviceKey not in services:
            services[serviceKey] = serviceName
            added.append(serviceName)

    saveSettings(settings, path)
    return added


def getActions():
    return ALLOWED_ACTIONS
