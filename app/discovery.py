from app.remote import runRemoteCommand


DISCOVER_SERVICES_COMMAND = [
    "systemctl",
    "list-unit-files",
    "--type=service",
    "--no-pager",
    "--no-legend",
]


def parseServiceUnits(output):
    services = []

    for line in output.splitlines():
        parts = line.split()

        if not parts:
            continue

        serviceName = parts[0]
        if serviceName.endswith(".service") and serviceName not in services:
            services.append(serviceName)

    return services


def discoverServices(hostName):
    result = runRemoteCommand(hostName, DISCOVER_SERVICES_COMMAND, timeout=45)

    if result["returncode"] != 0:
        return {
            "returncode": result["returncode"],
            "services": [],
            "stderr": result["stderr"],
        }

    return {
        "returncode": 0,
        "services": parseServiceUnits(result["stdout"]),
        "stderr": "",
    }
