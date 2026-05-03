
ALLOWED_SERVICES = {
    "ssh": "ssh.service",
    "nginx": "nginx.service",
    "cloudflared": "cloudflared.service",
    "gallinerito": "gallinerito.service"
}

ALLOWED_ACTIONS = [
    "status",
    "is-active",
    "start",
    "stop",
    "restart"
]

def getAllowedServices():
    return ALLOWED_SERVICES

def getAllowedActions():
    return ALLOWED_ACTIONS

def validateService(serviceName):
    if serviceName not in ALLOWED_SERVICES.values():
        raise ValueError("Servicio no permitido")


def validateAction(action):
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Acción no permitida")


