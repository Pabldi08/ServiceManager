from app.storage import addHostServices, loadData, makeServiceKey

ALLOWED_ACTIONS = [
    "status",
    "is-active",
    "start",
    "stop",
    "restart",
]


def getHosts():
    return loadData().get("hosts", {})


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
    return {}


def getHostServices(hostName):
    hostData = getHost(hostName)
    return hostData.get("services", {})


def addServices(hostName, serviceNames):
    return addHostServices(hostName, serviceNames)


def getActions():
    return ALLOWED_ACTIONS
