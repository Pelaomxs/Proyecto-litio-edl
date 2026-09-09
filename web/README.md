# Portafolio EDL — version web (Django)

Sitio web para el Portafolio de Extraccion Directa de Litio (EDL): muestra las diapositivas de contexto
del proyecto y luego las dos calculadoras interactivas ya validadas
([Calculadora_EDL.html](../Calculadora_EDL.html) y
[Simulador_Sorbente_EDL.html](../Simulador_Sorbente_EDL.html)), portadas a un layout comun. No tiene
base de datos, login ni formularios — es un sitio de solo lectura pensado para compartir con un link.

## Correr en local

```bash
cd web
pip install -r requirements.txt
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## Paginas

- `/` — contexto del proyecto y galeria de las diapositivas del PPT (`Presentacion_EDL_Completa_Ricardo.pptx`,
  exportadas como PNG en `portafolio/static/portafolio/slides/`).
- `/calculo/edl-vs-evaporacion/` — comparacion economica y ambiental EDL vs evaporacion.
- `/calculo/sorbente/` — costo real oculto por degradacion del sorbente.

## Regenerar las imagenes de las diapositivas

Si el PPT cambia, hay que re-exportar las diapositivas (requiere Windows + PowerPoint instalado, via
automatizacion COM con `pywin32`):

```python
import win32com.client
powerpoint = win32com.client.Dispatch("PowerPoint.Application")
presentation = powerpoint.Presentations.Open(r"ruta\al\Presentacion.pptx", WithWindow=False)
for i in range(1, presentation.Slides.Count + 1):
    presentation.Slides(i).Export(f"portafolio/static/portafolio/slides/slide-{i:02d}.png", "PNG", 1600, 900)
presentation.Close()
powerpoint.Quit()
```

## Desplegado en Railway

Proyecto **portafolio-edl** (servicio `web`), desplegado con `railway up` directo desde esta carpeta.

- **URL**: https://web-production-9660d.up.railway.app
- Publico, sin login — pensado para compartir el link directamente.

Variables configuradas en Railway: `SECRET_KEY`, `DEBUG=False` (ver `.env.example`). No hace falta
`DJANGO_SUPERUSER_*` ni base de datos — este sitio no los usa.

### Como volver a desplegar despues de un cambio

```bash
cd web
railway up --service web --detach
```

Logs: `railway logs --service web` (agrega `--build` para el build). Variables:
`railway variables --service web`.
