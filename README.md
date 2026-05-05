# ServiceManager
Gestor de servicios linux inicialmente para raspberryOS.

## Ejecutar

```powershell
python3 run.py
```

Despues abre `http://127.0.0.1:5500`.

Tambien se puede lanzar con Bun:

```powershell
bun run start
```

Bun se usa aqui como lanzador del proyecto. La aplicacion sigue siendo una app Python y `run.py` sigue siendo el punto de entrada principal.

Para ejecutar los tests con Bun:

```powershell
bun run test
```

## Como esta conectado

- `settings.json`: hosts y servicios configurables sin tocar codigo Python.
- `app/services.py`: valida que solo se usen servicios y acciones permitidas.
- `app/remote.py`: construye y ejecuta el comando SSH con `systemctl`.
- `app/web.py`: crea una interfaz web minima usando solo la libreria estandar.
- `templates/index.html`: estructura visual de la pagina.
- `static/styles.css`: estilos de la pagina.
- `package.json`: comandos para lanzar y probar el proyecto usando Bun.

## Configuracion de hosts

Cada host debe tener `user` y `host`. Tambien puede tener `port` y `key_path`:

```json
{
  "hosts": {
    "raspberry": {
      "user": "pablo",
      "host": "100.92.192.38",
      "port": 22,
      "key_path": "~/.ssh/id_rsa"
    }
  }
}
```

`key_path` es opcional. No guardes passwords dentro de este archivo.
