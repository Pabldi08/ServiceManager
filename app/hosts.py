def parseHostInput(hostInput):
    value = hostInput.strip()

    if "@" not in value:
        raise ValueError("El host debe tener el formato usuario@host o usuario@host:puerto")

    user, target = value.split("@", 1)
    if not user or not target:
        raise ValueError("El host debe incluir usuario y direccion")

    port = 22
    host = target

    if ":" in target:
        host, portText = target.rsplit(":", 1)
        if not portText.isdigit():
            raise ValueError("El puerto SSH debe ser un numero")
        port = int(portText)

    if not host:
        raise ValueError("El host debe incluir una direccion")

    if port <= 0:
        raise ValueError("El puerto SSH debe ser mayor que cero")

    return {
        "name": makeHostName(user, host, port),
        "user": user,
        "host": host,
        "port": port,
        "services": {},
    }


def makeHostName(user, host, port):
    base = f"{user}@{host}"
    if port != 22:
        base = f"{base}:{port}"
    return base
