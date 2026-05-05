from app.remote import runRemoteCommand
from app.services import getAllowedServices, validateService


KNOWN_STATES = ["active", "inactive", "failed", "activating", "deactivating"]


def parseServiceState(output):
    state = output.strip().splitlines()[0] if output.strip() else ""

    if state in KNOWN_STATES:
        return state

    return "unknown"


def getServiceStatus(hostName, serviceName):
    validateService(serviceName, hostName)

    result = runRemoteCommand(
        hostName,
        ["systemctl", "is-active", serviceName],
        timeout=20,
    )

    return {
        "service": serviceName,
        "state": parseServiceState(result["stdout"]),
        "returncode": result["returncode"],
        "stderr": result["stderr"],
    }


def getServiceStatuses(hostName):
    statuses = []

    for serviceKey, serviceName in getAllowedServices(hostName).items():
        status = getServiceStatus(hostName, serviceName)
        status["key"] = serviceKey
        statuses.append(status)

    return statuses
