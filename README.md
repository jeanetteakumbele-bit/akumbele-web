# Web de la Fundación Akumbele

Web estática generada con **Python** (sin instalar nada más), gestionada con **PowerShell** y publicada gratis en **GitHub Pages**.

## Cómo cambiar cosas

| Quiero cambiar…                    | Edito este archivo                          |
|------------------------------------|---------------------------------------------|
| Cifras, lema, menú, email          | `contenido/sitio.json`                      |
| Proyectos en marcha                | `contenido/proyectos.json`                  |
| Una historia / añadir una nueva    | `contenido/historias/*.md` (copia una existente) |
| Textos de inicio, nosotros, etc.   | `paginas/*.html`                            |
| Colores y diseño                   | `estaticos/css/estilo.css`                  |
| Cabecera y pie (todas las páginas) | `plantillas/base.html`                      |
| Noticias                           | Panel con contraseña: `/admin.html` (guarda en `estaticos/noticias.json`) |
| Contactos (CRM)                    | Mismo panel, pestaña **Contactos** (guarda en el repositorio **privado** `akumbele-crm`) |

**Imágenes:** basta con poner la parte final de la dirección de una foto de fundacionakumbele.org, p. ej. `2026/10/mutua-3.jpg`. Para fotos propias, guárdalas en `estaticos/img/` y escribe `img/nombre.jpg`.

**Historias** (`.md`): arriba van los datos entre `---`; debajo el texto. Usa `## Título` para subtítulos, `**negrita**` y `![Pie de foto](2026/10/foto.jpg)` para una imagen.

## Ver y publicar

```powershell
.\ver-en-local.ps1                 # la construye y la abre en http://localhost:8000
.\publicar.ps1 "Nueva historia"    # la sube a GitHub; en 1-2 minutos está en internet
```

GitHub construye la web automáticamente con `construir.py` (ver `.github/workflows/publicar-web.yml`).

## Estructura

```
contenido/     datos y textos (lo que más se toca)
paginas/       páginas fijas
plantillas/    cabecera, pie y plantilla de historia
estaticos/     CSS e imágenes propias
construir.py   genera la web en _site/
```
