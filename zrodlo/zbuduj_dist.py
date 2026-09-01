#!/usr/bin/env python3
"""Buduje wersję produkcyjną do dist/.

Różnice wobec podglądu:
  • zdjęcia jako prawdziwe pliki w dist/images/, nie base64 — przeglądarka je cachuje
  • osobna strona HTML pod każdym adresem /portfolio/<slug>/
  • treść projektu wpisana w HTML już na etapie budowania, więc Google widzi ją bez JS
  • pełny <head>: opis, canonical, Open Graph, dane strukturalne, favicon
  • robots.txt, sitemap.xml, .htaccess

    python3 ~/Damian-Assistant/STRONA/zbuduj_dist.py
"""
import io, os, re, json, base64, shutil, glob, sys
from PIL import Image

TU = os.path.dirname(os.path.abspath(__file__))
DOM = os.path.expanduser("~")
DIST = f"{TU}/dist"
PORT = f"{DOM}/Damian-Assistant/NA_STRONE_PORTFOLIO"
GOT = f"{DOM}/Desktop/GOTOWE WIZUALIZACJE "
SYG = f"{DOM}/Damian-Assistant/brand/sygnet.png"

# ══ USTAW PRZED WGRANIEM ══
DOMENA = "https://stankiewicz.design"
MAIL = "d.stankiewicz.design@gmail.com"
OPIS = ("Author-led interior design and 3D visualization studio. Atmospheric, mood-led spaces "
        "built on light, material, proportion and cinematic composition. Nijmegen, working internationally.")
SOCIAL = ["https://www.instagram.com/stankiewiczdesign",
          "https://www.facebook.com/profile.php?id=61581186960442",
          "https://www.tiktok.com/@stankiewiczdesign",
          "https://www.pinterest.com/StankiewiczDesign/"]

MOOD_ZRODLA = {
    "apartment-01":    f"{GOT}/Apartament 01/SOCIALE/mood board 1.png",
    "blue-kitchen":    f"{GOT}/Niebieska kuchnia/SOCIALE/mood board - niebieska kuchnia bez kratek.png",
    "marble-kitchen":  f"{GOT}/kuchnia marmurowa/SOCIALE/mood board .png",
    "marble-bathroom": f"{DOM}/Damian-Assistant/PAKIET_LAZIENKA_MARMUR/00_moodboard_IG_1080x1350.jpg",
}
HERO_EXTRA = f"{PORT}/apartment-01/stankiewicz-design-apartment-01-04.jpg"

szablon = io.open(f"{TU}/szablon.html", encoding="utf8").read()
PROJEKTY = json.loads(re.search(r"var PROJEKTY = (\[.*?\]);", szablon, re.S).group(1))

# ── zapis prawdziwych plików obrazów ──────────────────────────────
shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(f"{DIST}/images/projects", exist_ok=True)
SCIEZKI = {}

def zapisz(src, rel, w, q=80):
    cel = f"{DIST}/{rel}"
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(cel, "JPEG", quality=q, optimize=True, progressive=True)
    return "/" + rel

for p in PROJEKTY:
    s = p["slug"]
    for i, f in enumerate(sorted(glob.glob(f"{PORT}/{s}/*.jpg")), 1):
        SCIEZKI[f"{s}-{i:02d}"] = zapisz(f, f"images/projects/{s}/visual-{i:02d}.jpg",
                                         1600 if i == 1 else 1200)
    SCIEZKI[f"{s}-mood"] = zapisz(MOOD_ZRODLA[s], f"images/projects/{s}/moodboard.jpg", 1200)
SCIEZKI["apart04"] = zapisz(HERO_EXTRA, "images/hero-01.jpg", 1800, 78)

# ── favicon i obrazek podglądu ────────────────────────────────────
fav = ""
if os.path.exists(SYG):
    im = Image.open(SYG).convert("RGBA").resize((64, 64), Image.LANCZOS)
    tlo = Image.new("RGBA", (64, 64), (10, 10, 11, 255)); tlo.alpha_composite(im)
    b = io.BytesIO(); tlo.convert("RGB").save(b, "PNG", optimize=True)
    fav = '\n  <link rel="icon" type="image/png" href="data:image/png;base64,' \
          + base64.b64encode(b.getvalue()).decode() + '">'

def og_obraz(src, rel):
    im = Image.open(src).convert("RGB")
    k = max(1200 / im.width, 630 / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    l = (im.width - 1200) // 2; t = (im.height - 630) // 2
    cel = f"{DIST}/{rel}"; os.makedirs(os.path.dirname(cel), exist_ok=True)
    im.crop((l, t, l + 1200, t + 630)).save(cel, "JPEG", quality=84, optimize=True)
    return "/" + rel

OG = {"": og_obraz(HERO_EXTRA, "images/og.jpg")}
for p in PROJEKTY:
    OG[p["slug"]] = og_obraz(sorted(glob.glob(f"{PORT}/{p['slug']}/*.jpg"))[0],
                             f"images/projects/{p['slug']}/og.jpg")

# ── rejestr base64 → ścieżki ──────────────────────────────────────
szablon = szablon.replace('var TRYB = "hash";', 'var TRYB = "pages";')

# Szablon powstał jako fragment do podglądu: zaczyna się własnym <title> i ma <style>
# w treści. W pełnym dokumencie tytuł musi być jeden, a style w <head>.
_t = re.search(r"<title>.*?</title>\s*", szablon, re.S)
if _t:
    szablon = szablon[:_t.start()] + szablon[_t.end():]
_s = re.search(r"<style>.*?</style>\s*", szablon, re.S)
STYLE = ""
if _s:
    STYLE = "  " + _s.group(0).strip() + "\n"
    szablon = szablon[:_s.start()] + szablon[_s.end():]
tresc = re.sub(r"var IMG = \{.*?\n\};",
               "var IMG = " + json.dumps(SCIEZKI, ensure_ascii=False, indent=1) + ";",
               szablon, flags=re.S)

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def head(tytul, opis, url, obraz):
    ld = json.dumps({"@context":"https://schema.org","@type":"ProfessionalService",
        "name":"Stankiewicz Design","description":OPIS,"url":DOMENA,"email":MAIL,
        "image":DOMENA+OG[""],"areaServed":"Worldwide",
        "address":{"@type":"PostalAddress","addressLocality":"Nijmegen","addressCountry":"NL"},
        "knowsLanguage":["en","pl","nl"],"sameAs":SOCIAL}, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(tytul)}</title>
  <meta name="description" content="{esc(opis)}">
  <meta name="theme-color" content="#0A0A0B">
  <link rel="canonical" href="{DOMENA}{url}">{fav}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Stankiewicz Design">
  <meta property="og:title" content="{esc(tytul)}">
  <meta property="og:description" content="{esc(opis)}">
  <meta property="og:url" content="{DOMENA}{url}">
  <meta property="og:image" content="{DOMENA}{obraz}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="en_GB">
  <meta property="og:locale:alternate" content="pl_PL">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{ld}</script>
{STYLE}</head>
<body>
"""

# ── treść projektu wpisana w HTML, żeby istniała bez JavaScriptu ──
def projekt_html(p):
    t = p["en"]
    kadry = [f"{p['slug']}-{i:02d}" for i in range(2, p["kadry"] + 1)]
    sw = "".join('<span class="sw"><i style="background:%s"></i>%s</span>' % (s["c"], esc(s["en"]))
                 for s in p["paleta"])
    md = "".join("<span>%s</span>" % esc(m) for m in t["mood"])
    gal = "".join('<figure%s><img src="%s" alt="%s — %d" loading="lazy"></figure>'
                  % (' class="wide"' if len(kadry) % 2 and i == len(kadry) - 1 else "",
                     SCIEZKI[k], esc(t["n"]), i + 2) for i, k in enumerate(kadry))
    return (f'<div class="phero"><img src="{SCIEZKI[p["slug"]+"-01"]}" alt="{esc(t["n"])}">'
            f'<div class="phead"><span class="kind">{esc(t["k"])}</span><h1>{esc(t["n"])}</h1>'
            f'<p>{esc(t["krotki"])}</p></div></div>'
            f'<section class="dark"><div class="wrap pgrid"><p class="lead">{esc(t["dlugi"])}</p>'
            f'<div class="side"><div><h3>Material palette</h3><div class="swatches">{sw}</div></div>'
            f'<div><h3>Mood</h3><div class="moods">{md}</div></div></div></div></section>'
            f'<section class="dark" style="padding-top:0"><div class="wrap" style="padding-top:0">'
            f'<p class="eyebrow" style="margin-bottom:24px">Visualizations</p>'
            f'<div class="gal">{gal}</div></div></section>'
            f'<section class="dark" style="padding-top:0"><div class="wrap" style="padding-top:0">'
            f'<p class="eyebrow" style="margin-bottom:24px">Moodboard</p>'
            f'<div class="mood-shot"><img src="{SCIEZKI[p["slug"]+"-mood"]}" '
            f'alt="{esc(t["n"])} — moodboard" loading="lazy"></div>'
            f'<div class="pnav" style="margin-top:36px">'
            f'<a class="btn" href="/#portfolio" data-back="1">&larr; Back to portfolio</a>'
            f'<a class="btn solid" href="/#contact" data-back="1">Start a project</a>'
            f'</div></div></section>')

# ── strona główna ─────────────────────────────────────────────────
io.open(f"{DIST}/index.html", "w", encoding="utf8").write(
    head("Stankiewicz Design — Interior design & 3D visualization", OPIS, "/", OG[""])
    + tresc + "\n</body>\n</html>\n")

# ── podstrony projektów ───────────────────────────────────────────
for p in PROJEKTY:
    s = p["slug"]; t = p["en"]
    # Blok strony głównej znika z podstrony w całości — inaczej zostaje w kodzie
    # drugi <h1> z hasłem marki i Google widzi go przed nazwą projektu.
    _i = tresc.index('<div id="home">')
    _j = tresc.index('<div id="project" hidden></div>')
    ciało = tresc[:_i] + tresc[_j:]
    ciało = ciało.replace('<div id="project" hidden></div>',
                          '<div id="project">' + projekt_html(p) + "</div>", 1)
    os.makedirs(f"{DIST}/portfolio/{s}", exist_ok=True)
    io.open(f"{DIST}/portfolio/{s}/index.html", "w", encoding="utf8").write(
        head(f"{t['n']} — {t['k']} | Stankiewicz Design", t["krotki"],
             f"/portfolio/{s}/", OG[s]) + ciało + "\n</body>\n</html>\n")

# ── pliki pomocnicze ──────────────────────────────────────────────
io.open(f"{DIST}/robots.txt", "w", encoding="utf8").write(
    f"User-agent: *\nAllow: /\n\nSitemap: {DOMENA}/sitemap.xml\n")

url_xml = "".join(
    f"  <url>\n    <loc>{DOMENA}{u}</loc>\n    <changefreq>monthly</changefreq>\n"
    f"    <priority>{pr}</priority>\n  </url>\n"
    for u, pr in [("/", "1.0")] + [(f"/portfolio/{p['slug']}/", "0.8") for p in PROJEKTY])
io.open(f"{DIST}/sitemap.xml", "w", encoding="utf8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + url_xml + "</urlset>\n")

io.open(f"{DIST}/.htaccess", "w", encoding="utf8").write("""DirectoryIndex index.html
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml
</IfModule>
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png  "access plus 1 year"
  ExpiresByType text/html  "access plus 0 seconds"
</IfModule>
""")

waga = sum(os.path.getsize(os.path.join(r, f))
           for r, _, fs in os.walk(DIST) for f in fs)
print(f"{DIST}")
print(f"stron HTML: {1 + len(PROJEKTY)}   obrazów: {len(SCIEZKI) + len(OG)}   "
      f"razem: {round(waga/1024/1024, 2)} MB")
print(f"strona główna: {round(os.path.getsize(f'{DIST}/index.html')/1024)} KB")
print("\nWgraj całą zawartość dist/ do katalogu głównego hostingu.")
