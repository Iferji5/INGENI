# INGENI

Plataforma web desarrollada con Django para presentar el portafolio, catálogo de productos y servicios personalizados de INGENI, con enfoque en manufactura aditiva y soluciones a medida.

## Características
- Landing page con narrativa comercial en español y contenido editable desde plantillas.
- Catálogo de productos y casos de estudio con fichas detalladas, imágenes y descargas.
- Formulario de contacto segmentado por tipo de proyecto, con envío de correos configurables vía SMTP.
- Configuración lista para despliegues en entornos con `gunicorn` y `Whitenoise`.

## Requisitos
- Python 3.11 o superior.
- Entorno virtual recomendado (`python -m venv .venv`).
- Dependencias listadas en `requirements.txt`.

## Puesta en marcha
```bash
python -m venv .venv
.venv\Scripts\activate      # En PowerShell usar: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La aplicación quedará disponible en `http://127.0.0.1:8000/`.

## Configuración de entorno
Crea un archivo `.env` en la raíz del proyecto (junto a `manage.py`) para definir variables sensibles. Las más relevantes son:

- `DJANGO_EMAIL_BACKEND`
- `DJANGO_EMAIL_HOST`
- `DJANGO_EMAIL_PORT`
- `DJANGO_EMAIL_USE_TLS`
- `DJANGO_EMAIL_HOST_USER`
- `DJANGO_EMAIL_HOST_PASSWORD`
- `DJANGO_DEFAULT_FROM_EMAIL`
- `DJANGO_CONTACT_EMAIL`

Si `EMAIL_HOST_USER` o `EMAIL_HOST_PASSWORD` no están definidos, Django utilizará el backend de consola para el envío de correos (útil en desarrollo).

## Comandos útiles
- `python manage.py createsuperuser` para acceder al panel de administración.
- `python manage.py collectstatic` antes de desplegar en producción.
- `python manage.py test` para ejecutar la suite de pruebas.

## Estructura relevante
- `ingeni/` configuración principal del proyecto.
- `core/` vistas, formularios y lógica de negocio pública.
- `static/` activos estáticos (imágenes y estilos).
- `TEMPLATES/` plantillas en español para las páginas públicas.
