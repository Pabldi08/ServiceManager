import subprocess

from app.config import getHost
from app.services import validateAction, validateService


def makeCommandResult(returncode, stdout="", stderr=""):
    return {
        "returncode": returncode,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
    }


def validateRemoteCommand(remoteCommand):
    if not isinstance(remoteCommand, list) or not remoteCommand:
        raise ValueError("El comando remoto debe ser una lista no vacia")

    for argument in remoteCommand:
        if not isinstance(argument, str) or not argument:
            raise ValueError("Cada argumento del comando remoto debe ser texto")


def buildSshCommand(hostData, remoteCommand):
    validateRemoteCommand(remoteCommand)

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


def executeCommand(command, timeout=30):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return makeCommandResult(
            127,
            stderr="No se encontro el comando ssh en este equipo",
        )
    except subprocess.TimeoutExpired:
        return makeCommandResult(
            124,
            stderr="Tiempo de espera agotado al conectar por SSH",
        )

    return makeCommandResult(result.returncode, result.stdout, result.stderr)


def runRemoteCommand(hostName, remoteCommand, timeout=30):
    hostData = getHost(hostName)
    command = buildSshCommand(hostData, remoteCommand)
    return executeCommand(command, timeout)


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
