# ServiceManager
Gestor de servicios linux inicialmente para raspberryOS.

## Ejecutar

```powershell
python run.py
```

Despues abre `http://127.0.0.1:8000`.

## Como esta conectado

- `settings.json`: hosts y servicios configurables sin tocar codigo Python.
- `app/services.py`: valida que solo se usen servicios y acciones permitidas.
- `app/remote.py`: construye y ejecuta el comando SSH con `systemctl`.
- `app/web.py`: crea una interfaz web minima usando solo la libreria estandar.
- `templates/index.html`: estructura visual de la pagina.
- `static/styles.css`: estilos de la pagina.
