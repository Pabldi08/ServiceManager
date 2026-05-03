import subprocess

from app.config import getHosts
from app.services import validateAction, validateService


def runRemoteSystemctl(hostName, action, serviceName):
    hosts = getHosts()

    if hostName not in hosts:
        raise ValueError("Host no permitido")

    validateAction(action)
    validateService(serviceName)

    hostData = hosts[hostName]

    user = hostData["user"]
    host = hostData["host"]
    remoteTarget = f"{user}@{host}"

    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        remoteTarget,
        "sudo",
        "-n",
        "systemctl",
        action,
        serviceName,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": "No se encontro el comando ssh en este equipo",
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": 124,
            "stdout": "",
            "stderr": "Tiempo de espera agotado al conectar por SSH",
        }

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
