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
WYMIARY = {}

def zapisz(src, rel, w, q=80):
    cel = f"{DIST}/{rel}"
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(cel, "JPEG", quality=q, optimize=True, progressive=True)
    WYMIARY["/" + rel] = im.size
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

def hreflang(url_en):
    """Para adresów EN/PL plus x-default. Google potrzebuje obu, wskazujących na siebie."""
    pl = "/pl" + url_en
    return (f'\n  <link rel="alternate" hreflang="en" href="{DOMENA}{url_en}">'
            f'\n  <link rel="alternate" hreflang="pl" href="{DOMENA}{pl}">'
            f'\n  <link rel="alternate" hreflang="x-default" href="{DOMENA}{url_en}">')

def head(tytul, opis, url, obraz, jezyk="en", url_en=None):
    ld = json.dumps({"@context":"https://schema.org","@type":"ProfessionalService",
        "name":"Stankiewicz Design","description":OPIS,"url":DOMENA,"email":MAIL,
        "image":DOMENA+OG[""],"areaServed":"Worldwide",
        "address":{"@type":"PostalAddress","addressLocality":"Nijmegen","addressCountry":"NL"},
        "knowsLanguage":["en","pl","nl"],"sameAs":SOCIAL}, ensure_ascii=False)
    alt = hreflang(url_en if url_en is not None else url)
    return f"""<!DOCTYPE html>
<html lang="{jezyk}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(tytul)}</title>
  <meta name="description" content="{esc(opis)}">
  <meta name="theme-color" content="#0A0A0B">
  <link rel="canonical" href="{DOMENA}{url}">{alt}{fav}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Stankiewicz Design">
  <meta property="og:title" content="{esc(tytul)}">
  <meta property="og:description" content="{esc(opis)}">
  <meta property="og:url" content="{DOMENA}{url}">
  <meta property="og:image" content="{DOMENA}{obraz}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{"pl_PL" if jezyk=="pl" else "en_GB"}">
  <meta property="og:locale:alternate" content="{"en_GB" if jezyk=="pl" else "pl_PL"}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{ld}</script>
{STYLE}</head>
<body>
"""

# ── treść projektu wpisana w HTML, żeby istniała bez JavaScriptu ──
def wym(sciezka):
    w, h = WYMIARY.get(sciezka, (0, 0))
    return f' width="{w}" height="{h}"' if w else ""

ETY = {"en":{"paleta":"Material palette","mood":"Mood","galeria":"Visualizations",
             "moodboard":"Moodboard","back":"Back to portfolio","start":"Start a project"},
       "pl":{"paleta":"Paleta materiałowa","mood":"Nastrój","galeria":"Wizualizacje",
             "moodboard":"Moodboard","back":"Wróć do portfolio","start":"Zacznij projekt"}}

def projekt_html(p, jezyk="en"):
    t = p[jezyk]
    PREF = "/pl" if jezyk == "pl" else ""
    kadry = [f"{p['slug']}-{i:02d}" for i in range(2, p["kadry"] + 1)]
    sw = "".join('<span class="sw"><i style="background:%s"></i>%s</span>' % (s["c"], esc(s[jezyk]))
                 for s in p["paleta"])
    md = "".join("<span>%s</span>" % esc(m) for m in t["mood"])
    gal = "".join('<figure%s><img src="%s"%s alt="%s — %d" loading="lazy"></figure>'
                  % (' class="wide"' if len(kadry) % 2 and i == len(kadry) - 1 else "",
                     SCIEZKI[k], wym(SCIEZKI[k]), esc(t["n"]), i + 2) for i, k in enumerate(kadry))
    _h = SCIEZKI[p["slug"] + "-01"]
    _m = SCIEZKI[p["slug"] + "-mood"]
    return (f'<div class="phero"><img src="{_h}"{wym(_h)} alt="{esc(t["n"])}">'
            f'<div class="phead"><span class="kind">{esc(t["k"])}</span><h1>{esc(t["n"])}</h1>'
            f'<p>{esc(t["krotki"])}</p></div></div>'
            f'<section class="dark"><div class="wrap pgrid"><p class="lead">{esc(t["dlugi"])}</p>'
            f'<div class="side"><div><h3>{ETY[jezyk]["paleta"]}</h3><div class="swatches">{sw}</div></div>'
            f'<div><h3>{ETY[jezyk]["mood"]}</h3><div class="moods">{md}</div></div></div></div></section>'
            f'<section class="dark" style="padding-top:0"><div class="wrap" style="padding-top:0">'
            f'<p class="eyebrow" style="margin-bottom:24px">{ETY[jezyk]["galeria"]}</p>'
            f'<div class="gal">{gal}</div></div></section>'
            f'<section class="dark" style="padding-top:0"><div class="wrap" style="padding-top:0">'
            f'<p class="eyebrow" style="margin-bottom:24px">{ETY[jezyk]["moodboard"]}</p>'
            f'<div class="mood-shot"><img src="{_m}"{wym(_m)} '
            f'alt="{esc(t["n"])} — moodboard" loading="lazy"></div>'
            f'<div class="pnav" style="margin-top:36px">'
            f'<a class="btn" href="{PREF}/#portfolio" data-back="1">&larr; {ETY[jezyk]["back"]}</a>'
            f'<a class="btn solid" href="{PREF}/#contact" data-back="1">{ETY[jezyk]["start"]}</a>'
            f'</div></div></section>')

# ── obrazy wprost w HTML ──────────────────────────────────────────
# Bez tego strona główna nie ma ani jednego zdjęcia w kodzie: wszystko buduje
# JavaScript. Google zobaczyłby stronę studia wizualizacji bez wizualizacji,
# a pierwsze wczytanie czekałoby na skrypt.
def obrazy_w_html(html, jezyk):
    T = I18N.get(jezyk, {})
    # 1. kadry sekcji przewijanej — dopisz src
    def tour(m):
        k = m.group(1)
        sc = SCIEZKI.get(k, "")
        return f'<img src="{sc}"{wym(sc)} data-img="{k}"'
    html = re.sub(r'<img data-img="([a-z0-9-]+)"', tour, html)

    # 2. slajdy hero
    def _slajd(idx, sl):
        sc = SCIEZKI[sl["k"]]
        aktywny = " on" if idx == 0 else ""
        leniwy = "" if idx == 0 else ' loading="lazy"'
        return ('<div class="slide' + aktywny + '" style="--ox:' + sl["ox"]
                + ';--oy:' + sl["oy"] + '">'
                '<img src="' + sc + '"' + wym(sc) + ' alt="' + esc(sl[jezyk]) + '"'
                + leniwy + '></div>')
    slajdy = "".join(_slajd(k, sl) for k, sl in enumerate(SLAJDY))
    kropki = "".join(f'<button type="button" role="tab" data-s="{i}" '
                     f'aria-current="{"true" if i == 0 else "false"}"></button>'
                     for i in range(len(SLAJDY)))
    html = html.replace('<div class="slides" id="slides" aria-hidden="true"></div>',
                        f'<div class="slides" id="slides" aria-hidden="true">{slajdy}</div>', 1)
    html = html.replace('<div class="dots" id="dots" role="tablist" aria-label="Hero"></div>',
                        f'<div class="dots" id="dots" role="tablist" aria-label="Hero">{kropki}</div>', 1)

    # 3. karty portfolio
    pref = "/pl" if jezyk == "pl" else ""
    karty = "".join(
        f'<a class="proj" href="{pref}/portfolio/{p["slug"]}/">'
        f'<span class="shot"><img src="{SCIEZKI[p["slug"]+"-01"]}"'
        f'{wym(SCIEZKI[p["slug"]+"-01"])} alt="{esc(p[jezyk]["n"])} — {esc(p[jezyk]["k"])}" loading="lazy"></span>'
        f'<span class="body"><span class="top"><b>{esc(p[jezyk]["n"])}</b>'
        f'<span class="kind">{esc(p[jezyk]["k"])}</span></span>'
        f'<span class="desc">{esc(p[jezyk]["krotki"])}</span>'
        f'<span class="more">{esc(T.get("proj.more", ""))} &rarr;</span></span></a>'
        for p in PROJEKTY)
    html = html.replace('<div class="grid" id="projGrid"></div>',
                        f'<div class="grid" id="projGrid">{karty}</div>', 1)
    return html

_sl = re.search(r"var SLIDES = (\[.*?\n\];)", tresc, re.S)
SLAJDY = json.loads(re.sub(r"(\{|,)\s*([a-z0-9]+)\s*:", lambda m: f'{m.group(1)}"{m.group(2)}":',
                           _sl.group(1)[:-1])) if _sl else []

# ── tłumaczenie treści wprost w HTML ──────────────────────────────
# JS podmienia teksty dopiero po wczytaniu strony. Google czyta surowy HTML,
# więc polska wersja musi mieć polskie zdania już w pliku.
_i18n = re.search(r"var I18N = (\{.*?\n\};)", tresc, re.S)
_raw = _i18n.group(1)[:-1] if _i18n else "{}"
# klucze en: i pl: są w JS bez cudzysłowów — JSON ich nie przyjmie
_raw = re.sub(r"(\{|,)\s*(en|pl)\s*:", lambda m: f'{m.group(1)}"{m.group(2)}":', _raw)
I18N = json.loads(_raw)

def przetlumacz(html, jezyk):
    if jezyk == "en":
        return html
    T = I18N.get("pl", {})
    def tekst(m):
        klucz = m.group(2)
        return m.group(1) + esc(T[klucz]) if klucz in T else m.group(0)
    html = re.sub(r'(data-t="([^"]+)"[^>]*>)[^<]*', tekst, html)
    def opis(m):
        klucz = m.group(1)
        return f'alt="{esc(T[klucz])}" data-t-alt="{klucz}"' if klucz in T else m.group(0)
    html = re.sub(r'alt="" data-t-alt="([^"]+)"', opis, html)
    return html

# ── obie wersje językowe: EN w katalogu głównym, PL w /pl/ ────────
OPIS_PL = ("Autorskie studio projektowania wnętrz i wizualizacji 3D. Atmosferyczne przestrzenie "
           "oparte na świetle, materiale, proporcji i filmowej kompozycji. Nijmegen, rynek międzynarodowy.")
TYT = {"en": "Stankiewicz Design — Interior design & 3D visualization",
       "pl": "Stankiewicz Design — Projektowanie wnętrz i wizualizacje 3D"}
OP = {"en": OPIS, "pl": OPIS_PL}

for jezyk in ("en", "pl"):
    pref = "/pl" if jezyk == "pl" else ""
    kat = f"{DIST}/pl" if jezyk == "pl" else DIST
    os.makedirs(kat, exist_ok=True)

    io.open(f"{kat}/index.html", "w", encoding="utf8").write(
        head(TYT[jezyk], OP[jezyk], f"{pref}/", OG[""], jezyk, "/")
        + obrazy_w_html(przetlumacz(tresc, jezyk), jezyk) + "\n</body>\n</html>\n")

    for p in PROJEKTY:
        sl = p["slug"]; t = p[jezyk]
        _i = tresc.index('<div id="home">')
        _j = tresc.index('<div id="project" hidden></div>')
        ciało = przetlumacz(tresc[:_i] + tresc[_j:], jezyk)
        ciało = ciało.replace('<div id="project" hidden></div>',
                              '<div id="project">' + projekt_html(p, jezyk) + "</div>", 1)
        os.makedirs(f"{kat}/portfolio/{sl}", exist_ok=True)
        io.open(f"{kat}/portfolio/{sl}/index.html", "w", encoding="utf8").write(
            head(f"{t['n']} — {t['k']} | Stankiewicz Design", t["krotki"],
                 f"{pref}/portfolio/{sl}/", OG[sl], jezyk, f"/portfolio/{sl}/")
            + ciało + "\n</body>\n</html>\n")

# ── strona 404 ────────────────────────────────────────────────────
io.open(f"{DIST}/404.html", "w", encoding="utf8").write(
    head("404 — Stankiewicz Design", "Page not found.", "/404.html", OG[""], "en", "/404.html")
    + '<section class="dark" style="min-height:100svh;display:grid;place-items:center">'
      '<div class="wrap" style="text-align:center;display:grid;gap:22px;justify-items:center">'
      '<p class="eyebrow">404</p>'
      '<h1 style="font-size:clamp(30px,5vw,58px);max-width:16ch">This page does not exist.</h1>'
      '<p style="color:var(--concrete);max-width:34ch">Ta strona nie istnieje. '
      'Wróć na stronę główną albo do portfolio.</p>'
      '<div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center">'
      '<a class="btn solid" href="/">Home</a>'
      '<a class="btn" href="/#portfolio">Portfolio</a></div>'
      '</div></section>\n</body>\n</html>\n')

# ── pliki pomocnicze ──────────────────────────────────────────────
io.open(f"{DIST}/robots.txt", "w", encoding="utf8").write(
    f"User-agent: *\nAllow: /\n\nSitemap: {DOMENA}/sitemap.xml\n")

_adresy = [("/", "1.0")] + [(f"/portfolio/{p['slug']}/", "0.8") for p in PROJEKTY]
def _alt(u):
    return ("".join(f'    <xhtml:link rel="alternate" hreflang="{h}" href="{DOMENA}{a}"/>\n'
            for h, a in (("en", u), ("pl", "/pl" + u), ("x-default", u))))
url_xml = "".join(
    f"  <url>\n    <loc>{DOMENA}{pre}{u}</loc>\n{_alt(u)}"
    f"    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
    for pre in ("", "/pl") for u, pr in _adresy)
io.open(f"{DIST}/sitemap.xml", "w", encoding="utf8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + url_xml + "</urlset>\n")

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
print(f"stron HTML: {2 * (1 + len(PROJEKTY)) + 1}   obrazów: {len(SCIEZKI) + len(OG)}   "
      f"razem: {round(waga/1024/1024, 2)} MB")
print(f"strona główna: {round(os.path.getsize(f'{DIST}/index.html')/1024)} KB")
print("\nWgraj całą zawartość dist/ do katalogu głównego hostingu.")
