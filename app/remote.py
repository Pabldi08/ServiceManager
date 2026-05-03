import subprocess

from app.services import validateAction, validateService
from app.config import HOSTS

def runRemoteSystemctl(hostName, action, serviceName):
    if hostName not in HOSTS:
        raise ValueError("Host no permitido")
    
    validateAction(action)
    validateService(serviceName)

    hostData = HOSTS[hostName]

    user = hostData["user"]
    host = hostData["host"]

    remote_target = f"{user}@{host}"

    command = [
        "ssh",
        remote_target,
        "sudo",
        "systemctl",
        action,
        serviceName
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip()
    }