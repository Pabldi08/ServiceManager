from app.config import getActions, getHostServices


def getAllowedServices(hostName):
    return getHostServices(hostName)


def getAllowedActions():
    return getActions()


def getServiceUnit(serviceKey, hostName):
    services = getAllowedServices(hostName)

    if serviceKey not in services:
        raise ValueError("Servicio no permitido")

    return services[serviceKey]


def validateService(serviceName, hostName):
    if serviceName not in getAllowedServices(hostName).values():
        raise ValueError("Servicio no permitido")


def validateAction(action):
    if action not in getAllowedActions():
        raise ValueError("Accion no permitida")
