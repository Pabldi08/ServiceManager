# ServiceManager

Gestor de servicios Linux, pensado inicialmente para Raspberry Pi OS.

La aplicación permite conectarse por SSH a una máquina remota y gestionar servicios del sistema usando `systemctl`.

---

## Ejecutar

Para iniciar la aplicación:

```bash
python3 run.py
```

Después abre en el navegador:

```text
http://127.0.0.1:5500
```

Si el puerto `5500` ya está ocupado, puedes usar otro puerto:

```bash
PORT=5501 python3 run.py
```

En PowerShell:

```powershell
$env:PORT=5501
python3 run.py
```

---

## Ejecutar con Bun

También se puede lanzar con Bun:

```bash
bun run start
```

Bun se usa aquí como lanzador del proyecto. La aplicación sigue siendo una app Python y `run.py` sigue siendo el punto de entrada principal.

Para ejecutar los tests con Bun:

```bash
bun run test
```

---

## Estructura del proyecto

- `data/service_manager.json`: datos persistentes creados por la app con hosts y servicios seleccionados.
- `app/services.py`: valida que solo se usen servicios y acciones permitidas.
- `app/remote.py`: construye y ejecuta comandos SSH con `systemctl`.
- `app/web.py`: crea una interfaz web mínima usando solo la librería estándar.
- `app/storage.py`: guarda y carga la configuración editable desde la interfaz.
- `app/hosts.py`: valida entradas SSH como `usuario@host` o `usuario@host:puerto`.
- `templates/index.html`: estructura visual de la página.
- `static/styles.css`: estilos de la página.
- `static/theme.js`: guarda el tema elegido en `localStorage`.
- `package.json`: comandos para lanzar y probar el proyecto usando Bun.

---

## Configuración desde la interfaz

La configuración principal ya no se edita manualmente en `settings.json`.

Ahora se gestiona desde la web:

1. Abre la aplicación.
2. Añade un host SSH con formato `usuario@host` o `usuario@host:puerto`.
3. Selecciona el host.
4. Pulsa `Listar servicios` para consultar servicios disponibles con SSH.
5. Marca manualmente los servicios que quieres gestionar.
6. Guarda los servicios seleccionados.

Los datos se guardan en:

```text
data/service_manager.json
```

No se solicitan ni se guardan passwords. La conexión debe funcionar con claves SSH ya configuradas para el usuario local.

---

## Conexión SSH sin introducir contraseña

La forma recomendada de conectarse por SSH sin escribir la contraseña cada vez es usar una clave SSH pública/privada.

No se recomienda guardar contraseñas en texto plano.

---

### 1. Crear una clave SSH

En tu máquina local, ejecuta:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_rpi -C "clave-ssh-raspberry"
```

Cuando pregunte por una contraseña para la clave, puedes pulsar `Enter` si quieres conectarte sin escribir contraseña cada vez.

Esto genera dos archivos:

```text
~/.ssh/id_ed25519_rpi
~/.ssh/id_ed25519_rpi.pub
```

El archivo privado:

```text
~/.ssh/id_ed25519_rpi
```

no debe compartirse nunca.

El archivo público:

```text
~/.ssh/id_ed25519_rpi.pub
```

es el que se copiará al servidor.

---

### 2. Copiar la clave pública al servidor

Ejecuta:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_rpi.pub pablo@100.92.192.38
```

La primera vez pedirá la contraseña normal del usuario remoto.

Después de esto, la clave pública quedará registrada en la Raspberry Pi y ya no debería pedir contraseña al conectarse.

---

### 3. Probar la conexión

```bash
ssh -i ~/.ssh/id_ed25519_rpi pablo@100.92.192.38
```

Si todo está bien configurado, deberías entrar sin introducir la contraseña del usuario `pablo`.

---

### 4. Configurar un alias SSH opcional

Para no tener que escribir siempre la IP, el usuario y la ruta de la clave, puedes crear un alias SSH.

Edita el archivo:

```bash
nano ~/.ssh/config
```

Añade:

```sshconfig
Host raspberry
    HostName 100.92.192.38
    User pablo
    Port 22
    IdentityFile ~/.ssh/id_ed25519_rpi
    IdentitiesOnly yes
```

Guarda el archivo y ajusta permisos:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519_rpi
chmod 644 ~/.ssh/id_ed25519_rpi.pub
chmod 600 ~/.ssh/config
```

Ahora puedes conectarte simplemente con:

```bash
ssh raspberry
```

---

## Seleccionar servicios manualmente

La página tiene una sección llamada `Seleccionar servicios`.

Funcionamiento:

1. Selecciona un host configurado.
2. Pulsa `Listar servicios`.
3. La app ejecuta por SSH:

```bash
systemctl list-units --type=service --no-pager --no-legend
```

4. Se muestra una lista con los servicios encontrados.
5. Selecciona manualmente los servicios que quieres gestionar.
6. Pulsa `Guardar seleccionados`.

La app no registra automáticamente todos los servicios encontrados.

---

## Tema accesible

La interfaz incluye un selector de tema:

- `Light Mode`
- `Dark Mode`
- `System Mode`

`System Mode` usa la preferencia del sistema mediante `prefers-color-scheme`.

La preferencia se guarda en `localStorage`, por lo que se mantiene al recargar la página.

---

## Seguridad

La aplicación valida que solo se puedan ejecutar servicios y acciones permitidas.

No se deben guardar contraseñas en archivos de configuración.

La autenticación SSH debe hacerse mediante claves SSH.

El archivo persistente de la app solo guarda hosts y servicios seleccionados, nunca passwords.

---

## Resumen rápido

Crear clave SSH:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_rpi -C "clave-ssh-raspberry"
```

Copiar clave al servidor:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_rpi.pub pablo@100.92.192.38
```

Probar conexión:

```bash
ssh -i ~/.ssh/id_ed25519_rpi pablo@100.92.192.38
```

Ejecutar la app:

```bash
python3 run.py
```
