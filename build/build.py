#!/usr/bin/env python3
"""Generates every page of stankiewicz.design from the texts below.

English lives at the root, Polish under /pl/. Each page gets its own title,
description, canonical and hreflang pair, and sitemap.xml lists them all.

  python3 build/build.py                 -> writes the site into the repo root
  python3 build/build.py --preview DIR   -> writes a copy whose links end in
                                            index.html (for the file-based preview)
"""
import html, json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cases import CASES, HEADINGS

SITE = "https://stankiewicz.design/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
e = html.escape

# ---------------------------------------------------------------- projects
PROJECTS = [
 {"slug":"apartment-01","n":5,
  "pl":{"name":"Apartament 01","type":"Koncepcja wnętrza","short":"Beton dla ciężaru, czarna bryła dla napięcia, sztuka jako punkt skupienia i światło jako atmosfera.","long":"Wnętrze oparte na trzech decyzjach: beton, który niesie ciężar, czarna bryła, która trzyma napięcie, i jeden kierunek światła, który robi resztę. Nic w tym mieszkaniu nie zabiega o uwagę osobno. Kompozycja działa, bo każda płaszczyzna wie, czym jest, i przy tym zostaje.","mat":["Beton","Czarna bryła","Dąb","Len","Stal"],"mood":["Powściągliwość","Ciężar","Światło kierunkowe","Cisza"]},
  "en":{"name":"Apartment 01","type":"Interior concept","short":"Concrete for weight, black volume for tension, art as a focal point and light as atmosphere.","long":"An interior built on three decisions: concrete that carries the weight, a black volume that holds the tension, and one direction of light that does the rest. Nothing in this apartment asks for attention on its own. The composition works because every surface knows what it is and stays that way.","mat":["Concrete","Black volume","Oak","Linen","Steel"],"mood":["Restraint","Weight","Directional light","Silence"]}},
 {"slug":"blue-kitchen","n":5,
  "pl":{"name":"Niebieska kuchnia","type":"Koncepcja wnętrza","short":"Ultramarynowy lakier przy szczotkowanej stali, pod sztukaterią starszą od obu.","long":"Trzy epoki spotykają się na wysokości dwudziestu centymetrów: sztukateria, płaszczyzna szczotkowanej stali i pas ultramarynowego lakieru. Kolor nie jest tu dodatkiem. Jest konstrukcją: usuń go, a pomieszczenie traci środek, nie wykończenie.","mat":["Lakier ultramarynowy","Stal szczotkowana","Mikrocement","Biała sztukateria","Czerń"],"mood":["Napięcie","Kolor jako konstrukcja","Zderzenie epok","Precyzja"]},
  "en":{"name":"Blue Kitchen","type":"Interior concept","short":"Ultramarine lacquer against brushed steel, under an ornate plaster cornice older than both.","long":"Three eras meet within twenty centimetres: the plaster cornice, a plane of brushed steel and a band of ultramarine lacquer. Colour is not an accessory here. It is structure: remove it and the room loses its centre, not its finish.","mat":["Ultramarine lacquer","Brushed steel","Microcement","White plaster","Black"],"mood":["Tension","Colour as structure","Clash of eras","Precision"]}},
 {"slug":"marble-kitchen","n":5,
  "pl":{"name":"Kuchnia marmurowa","type":"Koncepcja wnętrza","short":"Monolityczna wyspa z ciemnozielonego marmuru, matowa czarna zabudowa i jeden kierunek światła.","long":"Wyspa jest jedną bryłą. Bez widocznych łączeń, bez uchwytów, bez cokołu: masa, która czyta się jak pojedynczy blok kamienia. Wokół niej matowa czarna zabudowa znika w ścianie, a światło pada tylko z jednej strony.","mat":["Marmur zielony","Matowa czerń","Mikrocement","Stal","Szkło przydymione"],"mood":["Monolit","Głębia","Niskie światło","Masa"]},
  "en":{"name":"Marble Kitchen","type":"Interior concept","short":"A monolithic island in deep green marble, matte black joinery and a single direction of light.","long":"The island is one volume. No visible joints, no handles, no plinth: a mass that reads as a single block of stone. Around it, matte black joinery disappears into the wall, and light falls from one side only.","mat":["Green marble","Matte black","Microcement","Steel","Smoked glass"],"mood":["Monolith","Depth","Low light","Mass"]}},
 {"slug":"marble-bathroom","n":4,
  "pl":{"name":"Łazienka marmurowa","type":"Koncepcja wnętrza","short":"Ciemny marmur, orzechowa okładzina i polerowany beton, ze światłem ukrytym wzdłuż każdej krawędzi.","long":"Każde źródło światła w tej łazience jest ukryte. Taśmy biegną w szczelinach, wzdłuż krawędzi kamienia i za lustrem, dzięki czemu materiał świeci, zamiast być oświetlany. Ciemny marmur niesie masę, orzech dokłada ciepło, a okno na miasto daje jedyne zimne światło.","mat":["Ciemny marmur","Orzech","Tynk","Beton polerowany","Biała ceramika"],"mood":["Ukryte światło","Ciepło przy kamieniu","Spokój","Głębia"]},
  "en":{"name":"Marble Bathroom","type":"Interior concept","short":"Dark marble, walnut cladding and polished concrete, with light hidden along every edge.","long":"Every light source in this bathroom is hidden. Strips run in recesses, along the stone edges and behind the mirror, so the material glows instead of being lit. Dark marble carries the mass, walnut adds warmth, and the window onto the city gives the only cool light in the room.","mat":["Dark marble","Walnut","Plaster","Polished concrete","White ceramic"],"mood":["Hidden light","Warmth by stone","Calm","Depth"]}},
]

# ---------------------------------------------------------------- addresses
PATHS = {
 "home":     {"en":"", "pl":"pl/"},
 "interior": {"en":"interior-design/", "pl":"pl/projektowanie-wnetrz/"},
 "viz":      {"en":"3d-visualization/", "pl":"pl/wizualizacje-3d/"},
 "projects": {"en":"projects/", "pl":"pl/projekty/"},
}
for p in PROJECTS:
    PATHS["p:"+p["slug"]] = {"en":"projects/%s/" % p["slug"], "pl":"pl/projekty/%s/" % p["slug"]}

# ---------------------------------------------------------------- shared texts
T = {
"en": dict(
  nav=[("projects","Projects"),("#studio","Studio"),("#contact","Contact")],
  svc={"interior":"Interior design","viz":"3D visualization"},
  lang_label="Language", menu="Menu", skip="Skip to content", home_crumb="Home", mat="Material palette", mood="Mood", gallery="Gallery",
  prev="Previous", next="Next", top="Back to top ↑", footer="© 2026 Stankiewicz Design · Nijmegen",
  cta_discuss="Discuss your project", cta_projects="View projects", related="Selected projects", service_of="Related service",
  # home
  hero_kicker="Stankiewicz Design · Studio",
  hero_h1="Interior design & 3D visualization",
  hero_lead="Before it’s built, it’s felt. Calm, material-led interiors and cinematic visualizations for clients across Europe and worldwide.",
  hero_alt="Apartment interior with concrete and a black volume in directional light",
  cta_contact="Get in touch",
  pf_label="Projects", pf_h2="Selected projects", all_projects="All projects",
  pf_title="Four interior concepts, each built on a single decision.",
  of_label="Services", of_h2="What I do",
  offer=[("Interior design","Layout, materials and light brought together in one concept, ready for pricing.","interior"),("3D visualizations","Realistic frames that show how a space will feel before it is built.","viz"),("Material direction","A rendered moodboard of stone, wood and metal chosen together.","interior"),("Cinematic presentations","A sequence of frames for a development or a portfolio.","viz")],
  pr_label="Process", pr_h2="Three steps",
  steps=[("Conversation & brief","We talk about the space, the way you live and the mood it should hold."),("Concept","Layout, material direction and light, agreed before anything is rendered."),("Visualization","Frames in the final light, so you see the space before it is built.")],
  ab_label="Studio", ab_h2="Damian Stankiewicz",
  ab1="I run an author-led studio for interior design and 3D visualization. My work is built on light, material and proportion, and on removing what the space does not need.",
  ab2="Based in Nijmegen, the Netherlands. Working with clients across Europe and worldwide.",
  portrait_alt="Damian Stankiewicz, interior designer",
  ct_label="Contact", ct_title="Tell me about your space.",
  ct_lead="I reply to every message personally. A few words about the space, where it is and how it should work are enough to start.",
  email="E-mail", phone="Phone", studio="Studio", city="Nijmegen, the Netherlands",
  copy="Copy", f_name="Name", f_mail="E-mail", f_type="Project type", f_msg="Message", f_send="Send message",
  view="view",
),
"pl": dict(
  nav=[("projects","Projekty"),("#studio","Studio"),("#contact","Kontakt")],
  svc={"interior":"Projektowanie wnętrz","viz":"Wizualizacje 3D"},
  lang_label="Język", menu="Menu", skip="Przejdź do treści", home_crumb="Start", mat="Paleta materiałowa", mood="Nastrój", gallery="Galeria",
  prev="Poprzedni", next="Następny", top="Na górę ↑", footer="© 2026 Stankiewicz Design · Nijmegen",
  cta_discuss="Porozmawiajmy o projekcie", cta_projects="Zobacz projekty", related="Wybrane projekty", service_of="Powiązana usługa",
  hero_kicker="Stankiewicz Design · Studio",
  hero_h1="Projektowanie wnętrz i wizualizacje 3D",
  hero_lead="Zanim powstanie, już je czujesz. Spokojne wnętrza oparte na materiale i filmowe wizualizacje dla klientów z Europy i świata.",
  hero_alt="Wnętrze apartamentu z betonem i czarną bryłą w kierunkowym świetle",
  cta_contact="Napisz do mnie",
  pf_label="Projekty", pf_h2="Wybrane projekty", all_projects="Wszystkie projekty",
  pf_title="Cztery koncepcje wnętrz, każda zbudowana na jednej decyzji.",
  of_label="Oferta", of_h2="Czym się zajmuję",
  offer=[("Projektowanie wnętrz","Układ, materiały i światło zebrane w jedną koncepcję gotową do wyceny.","interior"),("Wizualizacje 3D","Realistyczne kadry, które pokazują, jak przestrzeń będzie się czuć, zanim powstanie.","viz"),("Kierunek materiałowy","Wyrenderowany moodboard z kamieniem, drewnem i metalem dobranymi razem.","interior"),("Prezentacje filmowe","Sekwencja kadrów pod inwestycję albo portfolio.","viz")],
  pr_label="Proces", pr_h2="Trzy kroki",
  steps=[("Rozmowa i brief","Rozmawiamy o przestrzeni, Twoim stylu życia i nastroju, jaki ma mieć wnętrze."),("Koncepcja","Układ, kierunek materiałowy i światło, uzgodnione przed renderingiem."),("Wizualizacja","Kadry w docelowym świetle: widzisz przestrzeń, zanim powstanie.")],
  ab_label="Studio", ab_h2="Damian Stankiewicz",
  ab1="Prowadzę autorskie studio projektowania wnętrz i wizualizacji 3D. Moja praca opiera się na świetle, materiale i proporcji oraz na usuwaniu tego, czego przestrzeń nie potrzebuje.",
  ab2="Siedziba w Nijmegen w Holandii. Pracuję z klientami z całej Europy i świata.",
  portrait_alt="Damian Stankiewicz, projektant wnętrz",
  ct_label="Kontakt", ct_title="Opowiedz o swojej przestrzeni.",
  ct_lead="Odpowiadam osobiście na każdą wiadomość. Na start wystarczy kilka słów o przestrzeni, gdzie się znajduje i jak ma działać.",
  email="E-mail", phone="Telefon", studio="Pracownia", city="Nijmegen, Holandia",
  copy="Kopiuj", f_name="Imię", f_mail="E-mail", f_type="Typ projektu", f_msg="Wiadomość", f_send="Wyślij wiadomość",
  view="kadr",
),
}

# ---------------------------------------------------------------- service pages
SERVICES = {
"interior": {
 "img":"images/projects/marble-kitchen/visual-01.jpg", "projects":["apartment-01","marble-kitchen","marble-bathroom"],
 "en": dict(
  title="Interior Design Services | Stankiewicz Design",
  desc="Interior design concepts built on light, material and proportion: layout, material palette, lighting and visualizations, for clients across Europe and worldwide.",
  label="Services", h1="Interior Design Services",
  lead="A complete interior concept built on light, material and proportion. You see how the space will feel before a single wall is touched, and you get a concept that is ready for contractor pricing.",
  alt="Marble kitchen concept: a green marble island and matte black joinery",
  sections=[
   ("Who it is for", "<p>Private clients planning a new apartment, a house or a renovation, who want one clear direction instead of a collection of separate decisions. The same approach works for a single room, such as a kitchen or a bathroom, and for a whole home.</p>"),
   ("What the concept includes", None),
   ("How we work together", None),
   ("Working across Europe and worldwide", "<p>The studio is based in Nijmegen, in the Netherlands, and works with clients in other countries. The brief, presentations and feedback happen online. You share floor plans, measurements and photos of the space; I share the direction, the visualizations and the final concept as digital files.</p>"),
   ("What affects price and timing", "<p>The size of the space, the number of rooms, how many views you want visualized and the level of detail. Every project gets an individual quote after the first conversation, so tell me as much as you can about the space when you get in touch.</p>"),
  ],
  includes=[("Layout and proportion","How the space is divided and how you move through it."),("Material palette","Stone, wood, metal and textiles chosen together, shown as a rendered moodboard."),("Lighting concept","Where the light comes from, at what hour, and what it does to the materials."),("Visualizations of key views","Realistic frames of the most important parts of the space in the final light."),("A concept ready for pricing","A complete set of materials you can take to a contractor, plus help in choosing contractors and material sources.")],
  how=[("Brief","We talk about the space, the way you live and what is meant to stay in your head. Without this, the rest is guesswork."),("Direction","Moodboard and material direction. You see the atmosphere before the first plan exists."),("Visualize","Visualizations in the final light. We check proportion and materials on frames, not on samples."),("Present","A complete set of materials and documentation. I also help choose contractors and material sources.")],
 ),
 "pl": dict(
  title="Projektowanie wnętrz | Stankiewicz Design",
  desc="Koncepcje wnętrz oparte na świetle, materiale i proporcji: układ, paleta materiałów, światło i wizualizacje. Dla klientów z Polski, Europy i świata.",
  label="Usługi", h1="Projektowanie wnętrz",
  lead="Kompletna koncepcja wnętrza zbudowana na świetle, materiale i proporcji. Widzisz, jak przestrzeń będzie się czuć, zanim ktokolwiek ruszy ścianę, i dostajesz koncepcję gotową do wyceny wykonawczej.",
  alt="Koncepcja kuchni marmurowej: wyspa z zielonego marmuru i matowa czarna zabudowa",
  sections=[
   ("Dla kogo", "<p>Dla osób, które planują nowe mieszkanie, dom albo remont i chcą jednego, spójnego kierunku zamiast zbioru osobnych decyzji. To samo podejście sprawdza się przy jednym pomieszczeniu, na przykład kuchni lub łazience, i przy całym domu.</p>"),
   ("Co obejmuje koncepcja", None),
   ("Jak wygląda współpraca", None),
   ("Współpraca w Europie i na świecie", "<p>Studio ma siedzibę w Nijmegen w Holandii i pracuje z klientami z innych krajów. Brief, prezentacje i uwagi odbywają się online. Ty przesyłasz rzuty, wymiary i zdjęcia przestrzeni, ja kierunek, wizualizacje i gotową koncepcję w plikach.</p>"),
   ("Od czego zależy cena i termin", "<p>Od wielkości przestrzeni, liczby pomieszczeń, liczby kadrów do wizualizacji i poziomu szczegółu. Każdy projekt wyceniam indywidualnie po pierwszej rozmowie, więc w wiadomości opisz przestrzeń jak najdokładniej.</p>"),
  ],
  includes=[("Układ i proporcje","Jak przestrzeń jest podzielona i jak się po niej poruszasz."),("Paleta materiałów","Kamień, drewno, metal i tkaniny dobrane razem, pokazane jako wyrenderowany moodboard."),("Koncepcja światła","Skąd pada światło, o jakiej porze i co robi z materiałami."),("Wizualizacje kluczowych widoków","Realistyczne kadry najważniejszych miejsc w docelowym świetle."),("Koncepcja gotowa do wyceny","Komplet materiałów dla wykonawcy oraz pomoc w doborze wykonawców i źródeł materiałów.")],
  how=[("Brief","Rozmawiamy o przestrzeni, stylu życia i o tym, co ma zostać w głowie. Bez tego reszta jest zgadywaniem."),("Kierunek","Moodboard i kierunek materiałowy. Widzisz atmosferę, zanim powstanie pierwszy rzut."),("Wizualizacja","Wizualizacje w docelowym świetle. Sprawdzamy proporcje i materiały na kadrach, nie na próbkach."),("Prezentacja","Komplet materiałów i dokumentacji. Pomagam też dobrać wykonawcę i źródła materiałów.")],
 )},
"viz": {
 "img":"images/projects/blue-kitchen/visual-01.jpg", "projects":["blue-kitchen","apartment-01","marble-bathroom"],
 "en": dict(
  title="3D Interior Visualization | Stankiewicz Design",
  desc="Atmospheric 3D interior visualizations with cinematic light: still images, material moodboards and presentation sequences, for clients across Europe and worldwide.",
  label="Services", h1="3D Interior Visualization",
  lead="Realistic frames with cinematic light. Not a furniture presentation, but the atmosphere of a space: how it will feel at a given hour of the day, before it is built.",
  alt="Blue kitchen concept: ultramarine lacquer, brushed steel and a plaster cornice",
  sections=[
   ("Who it is for", "<p>Private clients who want to see their interior before deciding, and anyone who needs to present a space that does not exist yet: a renovation, a new apartment or a development.</p>"),
   ("What you receive", None),
   ("How it works", None),
   ("What I need to start", "<p>Floor plans with dimensions and ceiling heights, the position of windows and doors, photos of the space if it exists, and any material or furniture references you already have. Most of all, a few words about the mood you are after.</p>"),
   ("What affects price and timing", "<p>The number of views, the size and complexity of the space and how much of it has to be designed from scratch. Every project gets an individual quote after the brief. The work is done remotely, so it does not matter where in the world the space is.</p>"),
  ],
  includes=[("Still images","High-resolution frames of the space in its final light, composed like photographs, not like a catalogue."),("Moodboard scene","A rendered scene with material samples, so the direction is visible before the project begins."),("Cinematic presentation","A sequence of frames for a development or a portfolio: material that sells the space, not the floor plan.")],
  how=[("Brief","We talk about the space and the mood it should have."),("Direction","A moodboard and material direction to agree on before rendering."),("Visualize","Frames in the final light; we check proportion and materials on the images."),("Deliver","The final images, prepared for print, screen or presentation.")],
 ),
 "pl": dict(
  title="Wizualizacje 3D wnętrz | Stankiewicz Design",
  desc="Klimatyczne wizualizacje 3D wnętrz w filmowym świetle: kadry, moodboardy materiałowe i sekwencje prezentacyjne. Dla klientów z Polski, Europy i świata.",
  label="Usługi", h1="Wizualizacje 3D wnętrz",
  lead="Realistyczne kadry o filmowym świetle. Nie prezentacja mebli, tylko atmosfera przestrzeni: jak będzie się czuć o określonej porze dnia, zanim powstanie.",
  alt="Koncepcja niebieskiej kuchni: ultramarynowy lakier, szczotkowana stal i sztukateria",
  sections=[
   ("Dla kogo", "<p>Dla osób, które chcą zobaczyć swoje wnętrze przed podjęciem decyzji, i dla wszystkich, którzy muszą pokazać przestrzeń, której jeszcze nie ma: remont, nowe mieszkanie albo inwestycję.</p>"),
   ("Co otrzymujesz", None),
   ("Jak to działa", None),
   ("Czego potrzebuję na start", "<p>Rzutów z wymiarami i wysokością pomieszczeń, położenia okien i drzwi, zdjęć przestrzeni, jeśli już istnieje, oraz inspiracji materiałowych lub meblowych, jeśli je masz. A przede wszystkim kilku słów o nastroju, jaki ma mieć wnętrze.</p>"),
   ("Od czego zależy cena i termin", "<p>Od liczby kadrów, wielkości i złożoności przestrzeni oraz tego, ile trzeba zaprojektować od zera. Każdy projekt wyceniam indywidualnie po briefie. Pracuję zdalnie, więc nie ma znaczenia, w którym miejscu świata jest przestrzeń.</p>"),
  ],
  includes=[("Kadry","Wizualizacje w wysokiej rozdzielczości, w docelowym świetle, komponowane jak fotografie, nie jak katalog."),("Scena moodboardu","Wyrenderowana scena z próbkami materiałów, dzięki której kierunek widać, zanim zacznie się projekt."),("Prezentacja filmowa","Sekwencja kadrów pod inwestycję albo portfolio: materiał, który sprzedaje przestrzeń, nie rzut.")],
  how=[("Brief","Rozmawiamy o przestrzeni i nastroju, jaki ma mieć."),("Kierunek","Moodboard i kierunek materiałowy do akceptacji przed renderingiem."),("Wizualizacja","Kadry w docelowym świetle; proporcje i materiały sprawdzamy na obrazach."),("Przekazanie","Gotowe wizualizacje przygotowane do druku, ekranu lub prezentacji.")],
 )},
}

PAGE_META = {
 "home": {"en":("Interior Design & 3D Visualization | Stankiewicz Design","Before it’s built, it’s felt. Interior design & 3D visualization studio. Light, material, proportion, silence."),
          "pl":("Projektowanie wnętrz i wizualizacje 3D | Stankiewicz Design","Zanim powstanie, już je czujesz. Studio projektowania wnętrz i wizualizacji 3D. Światło, materiał, proporcja, cisza.")},
 "projects": {"en":("Projects | Stankiewicz Design","Four interior concepts by Stankiewicz Design, each built on a single decision: concrete, colour, stone and hidden light."),
              "pl":("Projekty | Stankiewicz Design","Cztery koncepcje wnętrz Stankiewicz Design, każda zbudowana na jednej decyzji: beton, kolor, kamień i ukryte światło.")},
}

# ---------------------------------------------------------------- helpers
def img_size(path):
    """Pixel size of a JPEG, read from its SOF marker (no image library needed)."""
    import struct
    with open(os.path.join(ROOT, path), "rb") as f:
        f.read(2)
        while True:
            m, ln = struct.unpack(">2sH", f.read(4))
            if m[1] in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">xHH", f.read(5))
                return w, h
            f.seek(ln - 2, 1)

PREVIEW = False

def rel(target, here):
    """Relative link from page `here` to page `target` (both are paths like 'pl/projekty/')."""
    t = "../" * here.count("/") + target
    if PREVIEW:
        return t + "index.html"
    return t or "./"

def asset(path, here):
    return "../" * here.count("/") + path

def link(key, lang, here, anchor=""):
    return rel(PATHS[key][lang], here) + anchor

def head(lang, key, title, desc, here, img="images/og.jpg"):
    alt_lang = "pl" if lang == "en" else "en"
    url = SITE + PATHS[key][lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0C0D0D">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{SITE + PATHS[key]['en']}">
<link rel="alternate" hreflang="pl" href="{SITE + PATHS[key]['pl']}">
<link rel="alternate" hreflang="x-default" href="{SITE + PATHS[key]['en']}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE + img}">
<meta property="og:locale" content="{'en_GB' if lang == 'en' else 'pl_PL'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito+Sans:opsz,wght@6..12,300;6..12,400&display=swap">
<link rel="stylesheet" href="{asset('assets/site.css', here)}">
"""

ORG = {"@context":"https://schema.org","@type":"Organization","name":"Stankiewicz Design","url":SITE,"logo":SITE+"icon-192.png","email":"studio@stankiewicz.design","telephone":"+31639283666","address":{"@type":"PostalAddress","addressLocality":"Nijmegen","addressCountry":"NL"},"founder":{"@type":"Person","name":"Damian Stankiewicz"},"areaServed":"Worldwide","sameAs":["https://www.instagram.com/stankiewiczdesign","https://www.pinterest.com/StankiewiczDesign/","https://www.tiktok.com/@stankiewiczdesign"]}

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>\n"

def crumbs_ld(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(items)]}

INTRO = """<div class="intro" id="intro" aria-hidden="true">
  <div class="morph"><span id="m1"></span><span id="m2"></span></div>
  <svg><defs><filter id="threshold"><feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 255 -140"/></filter></defs></svg>
</div>
<script>
/* liquid text intro, adapted from the MorphingText component to plain JS */
(function(){
  const el=document.getElementById("intro");
  if(matchMedia("(prefers-reduced-motion: reduce)").matches){el.remove();return}
  /* Safari and every iPhone browser (WebKit) wipe out the text with the SVG threshold filter, so there we use a soft blur crossfade */
  const ua=navigator.userAgent,soft=/AppleWebKit/.test(ua)&&!/(Chrome|Chromium|Android)\\//.test(ua);
  if(soft)el.classList.add("soft");
  document.documentElement.style.overflow="hidden";
  const a=document.getElementById("m1"),b=document.getElementById("m2");
  const words=["Stankiewicz","Design"],MORPH=1.0,HOLD=0.9;
  let t0=null,raf;
  const cap=soft?12:100,pw=soft?1:.4;
  function style(f){
    b.style.filter=`blur(${Math.min(8/f-8,cap)}px)`;b.style.opacity=`${Math.pow(f,pw)*100}%`;
    const g=1-f;a.style.filter=`blur(${Math.min(8/g-8,cap)}px)`;a.style.opacity=`${Math.pow(g,pw)*100}%`;
  }
  function frame(now){
    if(t0===null)t0=now;
    const t=(now-t0)/1000;
    // stage 0: "" -> words[0]; stage 1: words[0] -> words[1]
    const stage=Math.min(Math.floor(t/(MORPH+HOLD)),words.length-1),local=t-stage*(MORPH+HOLD);
    a.textContent=stage===0?"":words[stage-1];b.textContent=words[stage];
    if(local<MORPH)style(Math.max(local/MORPH,.001));else{b.style.filter="none";b.style.opacity="100%";a.style.opacity="0%"}
    if(t<words.length*(MORPH+HOLD))raf=requestAnimationFrame(frame);else done();
  }
  function done(){cancelAnimationFrame(raf);el.classList.add("out");document.documentElement.style.overflow="";setTimeout(()=>el.remove(),700)}
  el.addEventListener("click",done);
  /* start only once the page is painted and the font is ready, so phones see the first word */
  let go=false;const start=()=>{if(go)return;go=true;raf=requestAnimationFrame(()=>requestAnimationFrame(frame))};
  if(document.fonts&&document.fonts.load)document.fonts.load('300 64px "Nunito Sans"',"Stankiewicz Design").then(start,start);else start();
  setTimeout(start,1500);
})();
</script>
"""

SOCIAL = [("Instagram","https://www.instagram.com/stankiewiczdesign"),("Facebook","https://www.facebook.com/profile.php?id=61581186960442"),("TikTok","https://www.tiktok.com/@stankiewiczdesign"),("Pinterest","https://www.pinterest.com/StankiewiczDesign/")]

def brand(lang, key, here):
    href = "#top" if key == "home" else link("home", lang, here)
    return f'<a class="brand" href="{href}"><img src="{asset("images/logo-mark.png", here)}" width="30" height="30" alt="">Stankiewicz Design</a>'

def nav(lang, key, here):
    t = T[lang]
    items = []
    for k, label in t["nav"]:
        if k == "#contact":
            href = "#contact"              # every page ends with the contact section
        elif k.startswith("#"):
            href = k if key == "home" else link("home", lang, here, k)
        else:
            href = link(k, lang, here)
        cur = ' aria-current="page"' if (k == key or (k == "projects" and key.startswith("p:"))) else ""
        items.append(f'<a href="{href}"{cur}>{e(label)}</a>')
    cur_attr = lambda l: ' aria-current="true"' if l == lang else ""
    sw = "".join(f'<a href="{link(key, l, here)}" hreflang="{l}" lang="{l}"{cur_attr(l)}>{l.upper()}</a>' for l in ("en", "pl"))
    return f"""<a class="skip" href="#top">{e(t['skip'])}</a>
<nav>
  <div class="wrap">
    {brand(lang, key, here)}
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">{t['menu']}</button>
    <div class="links" id="menu">{''.join(items)}</div>
    <div class="lang" role="group" aria-label="{t['lang_label']}">{sw}</div>
  </div>
</nav>
"""

def footer(lang, key, here):
    t = T[lang]
    social = "".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in SOCIAL)
    links = f'<a href="{link("projects", lang, here)}">{e(dict(t["nav"])["projects"])}</a>' + "".join(f'<a href="{link(k, lang, here)}">{e(v)}</a>' for k, v in t["svc"].items())
    return f"""<footer><div class="wrap">
  <div class="foot-top">{brand(lang, key, here)}<div class="social">{social}</div><a class="text-link" href="#top">{e(t['top'])}</a></div>
  <div class="foot-bottom"><p class="small">{e(t['footer'])}</p><div class="foot-links">{links}</div></div>
</div></footer>
<div class="done" id="done" role="status" aria-live="polite"></div>
"""

def page_end(here):
    return f'<script src="{asset("assets/site.js", here)}" defer></script>\n</body>\n</html>\n'

def card(p, lang, here, short=False):
    t = p[lang]
    text = f'<p>{e(t["short"])}</p>' if short else ""
    return (f'<a class="proj" href="{link("p:"+p["slug"], lang, here)}"><div class="frame">'
            f'<img src="{asset("images/projects/%s/visual-01.jpg" % p["slug"], here)}" width="1402" height="1122" alt="{e(t["name"])}: {e(t["short"])}" loading="lazy"></div>'
            f'<div class="proj-name"><h3>{e(t["name"])}</h3><span class="label">{e(t["type"])}</span></div>{text}</a>')

def rows(items):
    return '<div class="rows">' + "".join(f'<div class="row"><span class="label">{i+1:02d}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(items)) + "</div>"

def contact_section(lang, here, selected=0):
    t = T[lang]
    opts = "".join(f"<option{' selected' if i == selected else ''}>{e(o[0])}</option>" for i, o in enumerate(t["offer"]))
    return f"""<section id="contact">
  <div class="wrap contact">
    <div>
      <p class="label">{t['ct_label']}</p>
      <h2>{e(t['ct_title'])}</h2>
      <p class="lead">{e(t['ct_lead'])}</p>
      <div class="details">
        <div><span class="label">{t['email']}</span><div class="mail"><a id="mail" href="mailto:studio@stankiewicz.design">studio@stankiewicz.design</a><button type="button" id="copy">{t['copy']}</button></div></div>
        <div><span class="label">{t['phone']}</span><a href="tel:+31639283666">+31 6 39 28 36 66</a></div>
        <div><span class="label">{t['studio']}</span><span>{e(t['city'])}</span></div>
      </div>
    </div>
    <form id="form" action="{asset('kontakt.php', here)}" method="POST">
      <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="pair">
        <div class="field"><label for="f-name">{t['f_name']}</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="f-mail">{t['f_mail']}</label><input id="f-mail" name="email" type="email" autocomplete="email" required></div>
      </div>
      <div class="field"><label for="f-type">{t['f_type']}</label><select id="f-type" name="type">{opts}</select></div>
      <div class="field"><label for="f-msg">{t['f_msg']}</label><textarea id="f-msg" name="message" required></textarea></div>
      <div class="send"><button class="btn solid" type="submit" id="send">{t['f_send']}</button><p class="note" id="form-note" role="status" aria-live="polite"></p></div>
    </form>
  </div>
</section>
"""

# ---------------------------------------------------------------- pages
def home(lang):
    here, t = PATHS["home"][lang], T[lang]
    title, desc = PAGE_META["home"][lang]
    grid = "".join(card(p, lang, here) for p in PROJECTS)
    offer = "".join(f'<a href="{link(k, lang, here)}"><h3>{e(a)}<span aria-hidden="true">→</span></h3><p>{e(b)}</p></a>' for a, b, k in t["offer"])
    steps = "".join(f'<li><span class="num">{i+1:02d}</span><h3>{e(a)}</h3><p>{e(b)}</p></li>' for i, (a, b) in enumerate(t["steps"]))
    org = dict(ORG, url=SITE + here)
    return (head(lang, "home", title, desc, here) + jsonld(org) + "</head>\n<body data-root=\"%s\">\n" % asset("", here) + INTRO + nav(lang, "home", here) + f"""
<header class="hero" id="top">
  <div class="wrap">
    <div class="hero-text">
      <p class="label">{e(t['hero_kicker'])}</p>
      <h1>{e(t['hero_h1'])}</h1>
      <p class="lead">{e(t['hero_lead'])}</p>
      <div class="cta"><a class="btn solid" href="#projects">{e(t['cta_projects'])}</a><a class="text-link" href="#contact">{e(t['cta_contact'])}</a></div>
    </div>
    <div class="hero-img"><img src="{asset('images/hero-01.jpg', here)}" width="1402" height="1122" fetchpriority="high" alt="{e(t['hero_alt'])}"></div>
  </div>
</header>

<section id="projects">
  <div class="wrap">
    <div class="head"><p class="label">{t['pf_label']}</p><h2>{e(t['pf_h2'])}</h2></div>
    <div class="grid">{grid}</div>
    <p class="all"><a class="text-link" href="{link('projects', lang, here)}">{e(t['all_projects'])} →</a></p>
  </div>
</section>

<section id="services">
  <div class="wrap">
    <div class="head"><p class="label">{t['of_label']}</p><h2>{e(t['of_h2'])}</h2></div>
    <div class="offer">{offer}</div>
  </div>
</section>

<section id="process">
  <div class="wrap">
    <div class="head"><p class="label">{t['pr_label']}</p><h2>{e(t['pr_h2'])}</h2></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>

<section id="studio">
  <div class="wrap about">
    <div>
      <p class="label">{t['ab_label']}</p>
      <h2>{e(t['ab_h2'])}</h2>
      <p>{e(t['ab1'])}</p>
      <p>{e(t['ab2'])}</p>
    </div>
    <img src="{asset('images/portrait.jpg', here)}" width="1000" height="1250" alt="{e(t['portrait_alt'])}" loading="lazy">
  </div>
</section>

""" + contact_section(lang, here) + footer(lang, "home", here) + page_end(here))


def crumb_html(lang, here, trail):
    parts = [f'<a href="{link("home", lang, here)}">{e(T[lang]["home_crumb"])}</a>']
    for key, name in trail[:-1]:
        parts.append(f'<a href="{link(key, lang, here)}">{e(name)}</a>')
    parts.append(f'<span aria-current="page">{e(trail[-1][1])}</span>')
    return '<p class="crumbs">' + " / ".join(parts) + "</p>"

def crumb_ld(lang, trail):
    items = [(T[lang]["home_crumb"], PATHS["home"][lang])] + [(n, PATHS[k][lang]) for k, n in trail]
    return jsonld(crumbs_ld(items))

def projects_page(lang):
    key, here, t = "projects", PATHS["projects"][lang], T[lang]
    title, desc = PAGE_META["projects"][lang]
    name = dict(t["nav"])["projects"]
    trail = [(key, name)]
    grid = "".join(card(p, lang, here, short=True) for p in PROJECTS)
    return (head(lang, key, title, desc, here) + crumb_ld(lang, trail) + f'</head>\n<body data-root="{asset("", here)}">\n' + nav(lang, key, here) + f"""
<header class="page-hero" id="top"><div class="wrap">
  {crumb_html(lang, here, trail)}
  <h1>{e(name)}</h1>
  <p class="lead">{e(t['pf_title'])}</p>
</div></header>
<section style="border-top:0;padding-top:0"><div class="wrap"><div class="grid">{grid}</div></div></section>
""" + contact_section(lang, here) + footer(lang, key, here) + page_end(here))

def project_page(lang, i):
    p = PROJECTS[i]; t = p[lang]; u = T[lang]
    key = "p:" + p["slug"]; here = PATHS[key][lang]
    title = f"{t['name']} — {t['type']} | Stankiewicz Design"
    desc = t["short"]
    trail = [("projects", dict(u["nav"])["projects"]), (key, t["name"])]
    img = lambda k: asset(f"images/projects/{p['slug']}/visual-0{k}.jpg", here)
    gallery = "".join(f'<img src="{img(k)}" alt="{e(t["name"])}, {u["view"]} {k}" loading="lazy" width="1402" height="1122">' for k in range(2, p["n"] + 1))
    mw, mh = img_size(f"images/projects/{p['slug']}/moodboard.jpg")
    gallery += f'<img class="wide" src="{asset("images/projects/%s/moodboard.jpg" % p["slug"], here)}" alt="Moodboard: {e(t["name"])}" loading="lazy" width="{mw}" height="{mh}">'
    chips = lambda xs: e(" · ".join(xs))
    case_html = '<section class="case"><div class="wrap">' + "".join(f'<div class="head"><h2 class="label">{e(h)}</h2><div class="prose"><p>{e(x)}</p></div></div>' for h, x in zip(HEADINGS[lang], CASES[p["slug"]][lang])) + "</div></section>\n"
    prev, nxt = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    svc = "interior" if i != 1 else "viz"
    svc_name = u["svc"][svc]
    ld = {"@context":"https://schema.org","@type":"CreativeWork","name":t["name"],"genre":t["type"],"description":t["long"],"image":SITE+f"images/projects/{p['slug']}/visual-01.jpg","inLanguage":lang,"creator":{"@type":"Organization","name":"Stankiewicz Design","url":SITE}}
    return (head(lang, key, title, desc, here, img=f"images/projects/{p['slug']}/visual-01.jpg") + jsonld(ld) + crumb_ld(lang, trail) + f'</head>\n<body data-root="{asset("", here)}">\n' + nav(lang, key, here) + f"""
<header class="page-hero" id="top"><div class="wrap">
  {crumb_html(lang, here, trail)}
  <p class="label">{e(t['type'])}</p>
  <h1>{e(t['name'])}</h1>
  <p class="lead">{e(t['short'])}</p>
</div></header>
<div class="wrap cover-wrap"><img class="cover" src="{img(1)}" width="1402" height="1122" fetchpriority="high" alt="{e(t['name'])}: {e(t['short'])}"></div>
<section><div class="wrap two">
  <div class="prose"><p>{e(t['long'])}</p></div>
  <div class="meta">
    <div><span class="label">{u['mat']}</span><p>{chips(t['mat'])}</p></div>
    <div><span class="label">{u['mood']}</span><p>{chips(t['mood'])}</p></div>
    <div><span class="label">{u['service_of']}</span><p><a href="{link(svc, lang, here)}">{e(svc_name)} →</a></p></div>
  </div>
</div></section>
{case_html}<section><div class="wrap">
  <div class="head"><p class="label">{u['gallery']}</p><h2>{e(t['name'])}</h2></div>
  <div class="gallery">{gallery}</div>
</div></section>
<section><div class="wrap pnav">
  <a href="{link('p:'+prev['slug'], lang, here)}"><span class="label">← {u['prev']}</span><h3>{e(prev[lang]['name'])}</h3></a>
  <a class="next" href="{link('p:'+nxt['slug'], lang, here)}"><span class="label">{u['next']} →</span><h3>{e(nxt[lang]['name'])}</h3></a>
</div></section>
""" + contact_section(lang, here) + footer(lang, key, here) + page_end(here))

def service_page(lang, key):
    s = SERVICES[key]; c = s[lang]; u = T[lang]; here = PATHS[key][lang]
    trail = [(key, c["h1"])]
    blocks = []
    for heading, body in c["sections"]:
        if body is None:
            if "includes" in c and heading == c["sections"][1][0]:
                inner = '<ul class="list">' + "".join(f"<li><strong>{e(a)}</strong><span>{e(b)}</span></li>" for a, b in c["includes"]) + "</ul>"
            else:
                inner = rows(c.get("how") or u["steps"])
            blocks.append(f'<section><div class="wrap"><div class="head"><h2 class="label">{e(heading)}</h2><div></div></div>{inner}</div></section>')
        else:
            blocks.append(f'<section><div class="wrap head" style="margin-bottom:0"><h2 class="label">{e(heading)}</h2><div class="prose">{body}</div></div></section>')
    grid = "".join(card(p, lang, here) for p in PROJECTS if p["slug"] in s["projects"][:2])
    ld = {"@context":"https://schema.org","@type":"Service","name":c["h1"],"serviceType":c["h1"],"description":c["desc"],"areaServed":"Worldwide","inLanguage":lang,"provider":{"@type":"Organization","name":"Stankiewicz Design","url":SITE},"url":SITE+here}
    return (head(lang, key, c["title"], c["desc"], here, img=s["img"]) + jsonld(ld) + crumb_ld(lang, trail) + f'</head>\n<body data-root="{asset("", here)}">\n' + nav(lang, key, here) + f"""
<header class="page-hero" id="top"><div class="wrap">
  {crumb_html(lang, here, trail)}
  <p class="label">{e(c['label'])}</p>
  <h1>{e(c['h1'])}</h1>
  <p class="lead">{e(c['lead'])}</p>
  <div class="cta"><a class="btn solid" href="#contact">{e(u['cta_discuss'])}</a><a class="text-link" href="{link('projects', lang, here)}">{e(u['cta_projects'])}</a></div>
</div></header>
<div class="wrap cover-wrap"><img class="cover" src="{asset(s['img'], here)}" width="1402" height="1122" fetchpriority="high" alt="{e(c['alt'])}"></div>
""" + "\n".join(blocks) + f"""
<section><div class="wrap">
  <div class="head"><h2 class="label">{e(u['related'])}</h2><div></div></div>
  <div class="grid">{grid}</div>
</div></section>
""" + contact_section(lang, here, 1 if key == "viz" else 0) + footer(lang, key, here) + page_end(here))

# ---------------------------------------------------------------- write
def build(out):
    pages = {}
    for lang in ("en", "pl"):
        pages[PATHS["home"][lang]] = home(lang)
        pages[PATHS["projects"][lang]] = projects_page(lang)
        for i in range(len(PROJECTS)):
            pages[PATHS["p:" + PROJECTS[i]["slug"]][lang]] = project_page(lang, i)
        for key in ("interior", "viz"):
            pages[PATHS[key][lang]] = service_page(lang, key)
    for path, content in pages.items():
        d = os.path.join(out, path)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(content)
    urls = []
    for key, pl in PATHS.items():
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE + pl[l]}"/>' for l in ("en", "pl")) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE + pl["en"]}"/>'
        for l in ("en", "pl"):
            urls.append(f"<url><loc>{SITE + pl[l]}</loc><lastmod>{TODAY}</lastmod>{alts}</url>")
    with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
    return sorted(pages)

if __name__ == "__main__":
    out = ROOT
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        PREVIEW, out = True, sys.argv[2]
    for p in build(out):
        print("/" + p)
