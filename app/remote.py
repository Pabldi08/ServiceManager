import subprocess

from app.config import getHost
from app.services import validateAction, validateService


def buildSshCommand(hostData, remoteCommand):
    user = hostData["user"]
    host = hostData["host"]
    port = str(hostData.get("port", 22))
    remoteTarget = f"{user}@{host}"

    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        "-p",
        port,
    ]

    keyPath = hostData.get("key_path")
    if keyPath:
        command.extend(["-i", keyPath])

    command.extend([
        remoteTarget,
        *remoteCommand,
    ])

    return command


def runRemoteSystemctl(hostName, action, serviceName):
    hostData = getHost(hostName)

    validateAction(action)
    validateService(serviceName)

    command = buildSshCommand(
        hostData,
        [
            "sudo",
            "-n",
            "systemctl",
            action,
            serviceName,
        ],
    )

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
