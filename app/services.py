from app.config import getActions, getServices


def getAllowedServices():
    return getServices()


def getAllowedActions():
    return getActions()


def getServiceUnit(serviceKey):
    services = getAllowedServices()

    if serviceKey not in services:
        raise ValueError("Servicio no permitido")

    return services[serviceKey]


def validateService(serviceName):
    if serviceName not in getAllowedServices().values():
        raise ValueError("Servicio no permitido")


def validateAction(action):
    if action not in getAllowedActions():
        raise ValueError("Accion no permitida")
