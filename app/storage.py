import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "service_manager.json"
DEFAULT_DATA = {"hosts": {}}


def loadData(path=DATA_PATH):
    if not path.exists():
        saveData(DEFAULT_DATA.copy(), path)

    try:
        with open(path, encoding="utf-8") as dataFile:
            return json.load(dataFile)
    except json.JSONDecodeError as error:
        raise ValueError(f"El archivo de datos no tiene JSON valido: {path}") from error


def saveData(data, path=DATA_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as dataFile:
        json.dump(data, dataFile, indent=2)
        dataFile.write("\n")


def addHost(hostData, path=DATA_PATH):
    data = loadData(path)
    hosts = data.setdefault("hosts", {})
    hostName = hostData["name"]

    if hostName in hosts:
        raise ValueError("Ese host ya esta registrado")

    hosts[hostName] = {
        "user": hostData["user"],
        "host": hostData["host"],
        "port": hostData["port"],
        "services": {},
    }
    saveData(data, path)
    return hostName


def deleteHost(hostName, path=DATA_PATH):
    data = loadData(path)
    hosts = data.setdefault("hosts", {})

    if hostName not in hosts:
        raise ValueError("Host no permitido")

    del hosts[hostName]
    saveData(data, path)
    return hostName


def addHostServices(hostName, serviceNames, path=DATA_PATH):
    data = loadData(path)
    hosts = data.setdefault("hosts", {})

    if hostName not in hosts:
        raise ValueError("Host no permitido")

    services = hosts[hostName].setdefault("services", {})
    added = []

    for serviceName in serviceNames:
        if not serviceName.endswith(".service"):
            continue

        serviceKey = makeServiceKey(serviceName)
        if serviceKey not in services:
            services[serviceKey] = serviceName
            added.append(serviceName)

    saveData(data, path)
    return added


def deleteHostService(hostName, serviceKey, path=DATA_PATH):
    data = loadData(path)
    hosts = data.setdefault("hosts", {})

    if hostName not in hosts:
        raise ValueError("Host no permitido")

    services = hosts[hostName].setdefault("services", {})
    if serviceKey not in services:
        raise ValueError("Servicio no permitido")

    serviceName = services.pop(serviceKey)
    saveData(data, path)
    return serviceName


def makeServiceKey(serviceName):
    key = serviceName.removesuffix(".service")
    cleanKey = []

    for character in key:
        if character.isalnum() or character in ("-", "_"):
            cleanKey.append(character)
        else:
            cleanKey.append("_")

    return "".join(cleanKey)
