"""
Generador de la web de la Fundación Akumbele.

Lee los textos de  contenido/  y  paginas/ , los mete en  plantillas/base.html
y deja la web lista en la carpeta  _site/ .  Solo usa Python estándar (3.10+).

    python construir.py
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).parent
CONTENIDO = RAIZ / "contenido"
PAGINAS = RAIZ / "paginas"
PLANTILLAS = RAIZ / "plantillas"
ESTATICOS = RAIZ / "estaticos"
SALIDA = RAIZ / "_site"

sitio = json.loads((CONTENIDO / "sitio.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- utilidades
def img(ruta: str) -> str:
    """Rutas cortas (2026/10/foto.jpg) apuntan a las imágenes de la web de la fundación."""
    if not ruta or ruta.startswith(("http://", "https://", "/", "img/")):
        return ruta
    return sitio["imagenes"] + ruta


def e(texto) -> str:
    return html.escape(str(texto or ""), quote=True)


def leer_frontmatter(texto: str) -> tuple[dict, str]:
    """Separa la cabecera '--- clave: valor ---' del cuerpo."""
    datos: dict = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", texto, re.S)
    if not m:
        return datos, texto
    for linea in m.group(1).splitlines():
        if ":" in linea:
            k, v = linea.split(":", 1)
            datos[k.strip()] = v.strip()
    return datos, texto[m.end():]


def markdown(texto: str) -> str:
    """Markdown sencillo: ## títulos, párrafos, **negrita**, *cursiva*, [enlaces](url) e ![imágenes](ruta)."""
    def en_linea(s: str) -> str:
        s = e(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", s)
        s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
        return s

    salida = []
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        b = bloque.strip()
        if not b:
            continue
        if m := re.fullmatch(r"!\[(.*?)\]\((.+?)\)", b):
            salida.append(f'<figure><img src="{e(img(m.group(2)))}" alt="{e(m.group(1))}" loading="lazy">'
                          f'<figcaption>{e(m.group(1))}</figcaption></figure>')
        elif b.startswith("### "):
            salida.append(f"<h3>{en_linea(b[4:])}</h3>")
        elif b.startswith("## "):
            salida.append(f"<h2>{en_linea(b[3:])}</h2>")
        elif all(l.lstrip().startswith("- ") for l in b.splitlines()):
            items = "".join(f"<li>{en_linea(l.lstrip()[2:])}</li>" for l in b.splitlines())
            salida.append(f"<ul>{items}</ul>")
        else:
            salida.append(f"<p>{en_linea(' '.join(b.splitlines()))}</p>")
    return "\n".join(salida)


# ------------------------------------------------------------ bloques comunes
def bloque_cifras() -> str:
    return "".join(
        f'<div class="cifra"><span class="cifra-valor">{e(c["valor"])}</span>'
        f'<span class="cifra-texto">{e(c["texto"])}</span></div>'
        for c in sitio["cifras"]
    )


def bloque_proyectos() -> str:
    proyectos = json.loads((CONTENIDO / "proyectos.json").read_text(encoding="utf-8"))
    tarjetas = []
    for p in proyectos:
        coste = f'<p class="coste">Coste: {e(p["coste"])}</p>' if p.get("coste") else ""
        tarjetas.append(f"""
        <article class="tarjeta">
          <div class="tarjeta-img" style="background-image:url('{e(img(p['imagen']))}')">
            <span class="estado">{e(p['estado'])}</span></div>
          <div class="tarjeta-cuerpo">
            <p class="meta">{e(p['area'])} · {e(p['lugar'])}</p>
            <h3>{e(p['titulo'])}</h3>
            <p>{e(p['texto'])}</p>{coste}
          </div>
        </article>""")
    return "".join(tarjetas)


def cargar_historias() -> list[dict]:
    historias = []
    for f in sorted((CONTENIDO / "historias").glob("*.md")):
        datos, cuerpo = leer_frontmatter(f.read_text(encoding="utf-8"))
        datos["slug"] = f.stem
        datos["cuerpo"] = cuerpo
        historias.append(datos)
    return sorted(historias, key=lambda h: int(h.get("orden", 99)))


def bloque_historias(historias: list[dict]) -> str:
    return "".join(f"""
        <a class="historia" href="historias/{e(h['slug'])}.html">
          <div class="historia-img" style="background-image:url('{e(img(h.get('portada')))}')"></div>
          <div class="historia-texto">
            <p class="meta">{e(h.get('lugar'))} · {e(h.get('fecha'))}</p>
            <h3>{e(h['titulo'])}</h3>
            <p>{e(h.get('resumen'))}</p>
            <span class="leer">Leer la historia →</span>
          </div>
        </a>""" for h in historias)


# ----------------------------------------------------------------- montaje
BASE = (PLANTILLAS / "base.html").read_text(encoding="utf-8")


def menu(actual: str, prefijo: str) -> str:
    enlaces = []
    for m in sitio["menu"]:
        clases = []
        if m.get("boton"):
            clases.append("boton")
        if m["url"] == actual:
            clases.append("activo")
        cls = f' class="{" ".join(clases)}"' if clases else ""
        enlaces.append(f'<a href="{prefijo}{m["url"]}"{cls}>{e(m["titulo"])}</a>')
    return "".join(enlaces)


def contacto() -> str:
    c = sitio["contacto"]
    partes = []
    if c.get("email"):
        partes.append(f'<a href="mailto:{e(c["email"])}">{e(c["email"])}</a>')
    if c.get("instagram"):
        partes.append(f'<a href="{e(c["instagram"])}">Instagram</a>')
    if not partes and c.get("web_actual"):
        partes.append(f'<a href="{e(c["web_actual"])}">Escríbenos</a>')
    return " · ".join(partes)


def montar(contenido: str, *, titulo: str, descripcion: str, archivo: str, prefijo: str = "",
           imagen_social: str = "") -> str:
    reemplazos = {
        "{{contenido}}": contenido,
        "{{titulo}}": e(f"{titulo} · {sitio['nombre']}" if titulo != sitio["nombre"] else titulo),
        "{{descripcion}}": e(descripcion or sitio["descripcion"]),
        "{{imagen_social}}": e(img(imagen_social or "2026/09/home-1-e1790806343577.jpg")),
        "{{menu}}": menu(archivo, prefijo),
        "{{contacto}}": contacto(),
        "{{lema}}": e(sitio["lema"]),
        "{{nombre}}": e(sitio["nombre"]),
        "{{prefijo}}": prefijo,
        "{{anio}}": str(date.today().year),
    }
    salida = BASE
    for k, v in reemplazos.items():
        salida = salida.replace(k, v)
    return salida


def rellenar(fragmento: str, historias: list[dict]) -> str:
    fragmento = fragmento.replace("{{cifras}}", bloque_cifras())
    fragmento = fragmento.replace("{{proyectos}}", bloque_proyectos())
    fragmento = fragmento.replace("{{historias}}", bloque_historias(historias))
    fragmento = fragmento.replace("{{lema}}", e(sitio["lema"]))
    # {{img:2026/10/foto.jpg}} -> dirección completa de la imagen
    return re.sub(r"\{\{img:(.+?)\}\}", lambda m: e(img(m.group(1).strip())), fragmento)


def construir() -> None:
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    shutil.copytree(ESTATICOS, SALIDA)
    (SALIDA / "historias").mkdir()
    historias = cargar_historias()
    generadas = []

    # Páginas fijas: paginas/*.html (con cabecera --- titulo / descripcion ---)
    for f in sorted(PAGINAS.glob("*.html")):
        datos, cuerpo = leer_frontmatter(f.read_text(encoding="utf-8"))
        pagina = montar(rellenar(cuerpo, historias), titulo=datos.get("titulo", sitio["nombre"]),
                        descripcion=datos.get("descripcion", ""), archivo=f.name,
                        imagen_social=datos.get("imagen", ""))
        (SALIDA / f.name).write_text(pagina, encoding="utf-8")
        generadas.append(f.name)

    # Una página por historia
    plantilla = (PLANTILLAS / "historia.html").read_text(encoding="utf-8")
    for i, h in enumerate(historias):
        sig = historias[(i + 1) % len(historias)]
        cuerpo = (plantilla
                  .replace("{{portada}}", e(img(h.get("portada"))))
                  .replace("{{titulo}}", e(h["titulo"]))
                  .replace("{{subtitulo}}", e(h.get("subtitulo")))
                  .replace("{{meta}}", e(f"{h.get('lugar', '')} · {h.get('fecha', '')}"))
                  .replace("{{cuerpo}}", markdown(h["cuerpo"]))
                  .replace("{{sig_slug}}", e(sig["slug"]))
                  .replace("{{sig_titulo}}", e(sig["titulo"])))
        pagina = montar(cuerpo, titulo=h["titulo"], descripcion=h.get("resumen", ""),
                        archivo="historias.html", prefijo="../", imagen_social=h.get("portada", ""))
        (SALIDA / "historias" / f"{h['slug']}.html").write_text(pagina, encoding="utf-8")
        generadas.append(f"historias/{h['slug']}.html")

    (SALIDA / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Web construida en {SALIDA} ({len(generadas)} páginas):")
    for g in generadas:
        print("  ·", g)


if __name__ == "__main__":
    construir()
