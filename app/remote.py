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


def runRemoteCommand(hostName, remoteCommand, timeout=30):
    hostData = getHost(hostName)
    command = buildSshCommand(hostData, remoteCommand)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
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


def runRemoteSystemctl(hostName, action, serviceName):
    validateAction(action)
    validateService(serviceName, hostName)

    return runRemoteCommand(
        hostName,
        [
            "sudo",
            "-n",
            "systemctl",
            action,
            serviceName,
        ],
    )
