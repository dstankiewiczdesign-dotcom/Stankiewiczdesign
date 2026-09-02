# Strona Stankiewicz Design — prototyp

Podgląd na żywo: **https://claude.ai/code/artifact/bd128224-3dd5-4e72-b81d-78b4f536da2e**
Plik: `~/Damian-Assistant/STRONA/index.html` — jeden plik, bez zależności, bez budowania.

---

## ⚠ Odstępstwo od Twojego briefu, świadome

Prosiłeś o **Next.js albo React + Vite, TypeScript i GSAP**. Na tym Macu
**nie ma zainstalowanego Node.js ani npm**, więc nie dało się nic zainstalować,
zbudować ani uruchomić. Sprawdziłem, zanim zacząłem.

Zbudowałem więc to samo bez frameworka: jeden plik HTML, wbudowany CSS i vanilla JS.
Efekt scrollowany działa tak samo — sticky sekcja, cztery kadry, płynne przejścia,
pasek postępu — tylko liczy go `requestAnimationFrame` zamiast GSAP ScrollTrigger.

**Zalety tej wersji:** działa od kliknięcia, ładuje się szybko, wgrywasz jednym plikiem
na dowolny hosting. **Wada:** przy rozbudowie do wielu podstron warto wrócić do Reacta.

**Jeśli chcesz wersję w Next.js:** zainstaluj Node — `brew install node` albo z nodejs.org —
i powiedz. Przepiszę to na komponenty z TypeScriptem i GSAP-em, struktura jest gotowa.

---

## Co gdzie podmienić

### Zdjęcia

Wszystkie są **wbudowane w plik** jako `data:image/jpeg;base64,…`, żeby strona działała
bez katalogu z obrazkami. Żeby podmienić kadr, najprościej użyć skryptu:

```bash
python3 ~/Damian-Assistant/STRONA/podmien_zdjecia.py
```

Skrypt czyta `~/Damian-Assistant/NA_STRONE_PORTFOLIO` i buduje stronę od nowa.
Zmieniasz mapę na górze skryptu — który plik trafia w które miejsce.

Obecny dobór:

| Miejsce | Plik |
|---|---|
| Hero | `apartment-01-04` |
| Tour 01 Atmosfera | `marble-kitchen-03` |
| Tour 02 Materiał | `marble-bathroom-02` |
| Tour 03 Światło | `apartment-01-05` |
| Tour 04 Kompozycja | `blue-kitchen-02` |
| Projekt Apartment 01 | `apartment-01-01` |
| Projekt Blue Kitchen | `blue-kitchen-04` |
| Projekt Marble Kitchen | `marble-kitchen-01` |
| Projekt Marble Bathroom | `marble-bathroom-04` |

### Teksty

Wszystkie siedzą w HTML-u, wyszukaj i podmień. Najważniejsze miejsca:

- **Hasło w hero** — `Before it's built,<br>it's felt.`
- **Podpis pod hasłem** — linia z klasą `sub`
- **Cztery filary** — sekcja `tour-copy`, każdy `<article class="tour-item">`
- **Cytat filozofii** — `<blockquote>`
- **Cztery usługi** — sekcja `.offer`, karty `<article class="card">`
- **Cztery kroki procesu** — sekcja `.steps`

### Kontakt

Formularz jest front-endowy. Miejsce na podpięcie jest w skrypcie na dole pliku,
oznaczone komentarzem `── PODPIĘCIE MAILA / API ──`:

```js
// fetch("/api/brief", {method:"POST", body:d})
```

Najprostsze opcje bez zaplecza: Formspree, Basin albo Web3Forms — wklejasz ich adres
w `fetch` i formularz zaczyna wysyłać na Twój e-mail. **Ustal najpierw, który adres** —
masz dwa i Meta pisze na ten bez kropek.

### Linki społecznościowe

W stopce, komplet czterech, sprawdzone 28.08:
Instagram, Facebook, TikTok, Pinterest.

---

## Decyzje, które nadal czekają

**Język.** Zbudowałem po polsku, bo tak napisałeś w briefie — „Zobacz projekty",
„Opisz projekt", „Przygotuj brief". Ale Twoja zasada marki mówi **angielski**,
obecna strona jest po angielsku, a rynek masz ogólnoświatowy. Przełączenie to
podmiana tekstów w jednym pliku. **Powiedz, którą wersję zostawiamy.**

**Nazwy projektów.** W briefie napisałeś „Warm Bathroom" i „Material Board".
Użyłem Twoich realnych nazw z kalendarza: Apartment 01, Blue Kitchen, Marble Kitchen,
Marble Bathroom. Jeśli wolisz inne — mów.

**Podstrony projektów.** Dziś kafle prowadzą do formularza. Docelowo każdy projekt
powinien mieć własną stronę ze wszystkimi kadrami. To druga tura.

**Portret i tekst o sobie.** Nadal brakuje. Bez tego nie ma sekcji „o mnie",
a przy usłudze projektowej to najdroższa dziura na całej stronie.

---

# Wersja 2 — dwujęzyczna (28.08.2026)

Podgląd: **https://claude.ai/code/artifact/bd128224-3dd5-4e72-b81d-78b4f536da2e**

## Języki

Domyślny **angielski**, przełącznik **EN / PL** w prawym górnym rogu.
Wybór zapisuje się w przeglądarce, więc przy kolejnej wizycie wraca ten sam język.
Przełączają się wszystkie teksty **razem z opisami alt zdjęć** — to ważne dla wyszukiwarek.

Hasło `Before it's built, it's felt.` zostaje po angielsku w obu wersjach.
To tagline marki, nie zdanie do tłumaczenia.

**Gdzie edytować teksty:** obiekt `I18N` w skrypcie na dole pliku. Dwa bloki, `en` i `pl`,
te same klucze. Dodajesz zdanie w jednym — dodaj też w drugim, inaczej zostanie puste.

## Nawigacja

Przezroczysta nad hero, po przewinięciu 40 px dostaje ciemne tło z rozmyciem.
Zawiera: Portfolio, Proces, O mnie, Kontakt, ikony social i przełącznik języka.
Poniżej 900 px linki chowają się pod hamburger, który otwiera pełnoekranowe menu.

## Ikony social

W tablicy `SOCIAL` na górze skryptu. Każdy wpis to nazwa, adres i ścieżka SVG.
Instagram, TikTok i Pinterest są podpięte prawdziwymi adresami.
**Behance jest zakomentowany** — odkomentuj blok i wpisz adres, ikona pojawi się sama
w nawigacji i w stopce.

## Kontakt

Trzy przyciski akcji plus formularz.

| Przycisk | Działanie |
|---|---|
| Napisz e-mail | `mailto:` na adres ze zmiennej `MAIL` |
| Wyślij wiadomość | przewija do formularza |
| Zadzwoń | `tel:` ze zmiennej `PHONE` |

**Numeru telefonu celowo nie wpisałem.** Zmienna `PHONE` jest pusta, więc zamiast
działającego przycisku widać wyszarzony napis „Numer do uzupełnienia". Wpisz numer
w formacie `+31612345678`, a przycisk zacznie działać sam. Nie chciałem wstawiać
zmyślonego numeru na stronę, która może pójść na produkcję.

**Adres e-mail** ustawiony na `d.stankiewicz.design@gmail.com`. Masz dwa adresy —
jeśli kontakt ma iść na ten drugi, zmień `MAIL`.

## Portfolio

Siedem pozycji w tablicy `PROJEKTY`. Każda ma zdjęcie, a osobno wersję `en` i `pl`
z nazwą, typem projektu i opisem. Kafle prowadzą dziś do formularza —
docelowo każdy dostanie własną podstronę.

| Pozycja | Zdjęcie | Typ |
|---|---|---|
| Apartment 01 | apartment-01-01 | Interior concept |
| Blue Kitchen | blue-kitchen-04 | Interior concept |
| Marble Kitchen | marble-kitchen-01 | Interior concept |
| Marble Bathroom | marble-bathroom-04 | Interior concept |
| Material Direction | moodboard łazienki | Material direction |
| Bathroom Visualizations | marble-bathroom-03 | 3D visualization |
| Interior Details | marble-kitchen-04 | 3D visualization |

⚠ **Do przemyślenia:** „Bathroom Visualizations" i „Marble Bathroom" to ta sama łazienka,
tylko raz jako koncepcja, raz jako zestaw kadrów. Na siatce mogą czytać się jak dwa
projekty, których nie ma. Rozważ połączenie albo zmianę nazwy drugiej pozycji.

## O mnie

Sekcja gotowa, z Twoim tekstem w obu językach.
**Portret to elegancki placeholder** — ramka z ikoną i podpisem.

Podmiana: znajdź w pliku komentarz `══ PORTRET` i zamień całą zawartość
`<div class="portrait">…</div>` na:

```html
<div class="portrait"><img src="portret.jpg" alt="Damian Stankiewicz"></div>
```

Kadr pionowy 4:5, najlepiej ciemny, żeby trzymał klimat reszty.

## Co dalej

- **Portret** — jedyny brakujący element treści
- **Numer telefonu** — jedna zmienna
- **Podpięcie formularza** — Formspree, Basin albo Web3Forms, miejsce oznaczone w kodzie
- **Podstrony projektów** — druga tura
- **Behance** — jeśli założysz, odkomentuj wpis

---

# Wersja 3 — slider hero i wersja produkcyjna (28.08.2026)

## Slider w hero

Pięć kadrów: Apartament 01 → Blue Kitchen → Marble Kitchen → Marble Bathroom → Material Direction.
Zmiana **co 5 sekund**, przenikanie 1,8 s, powolny najazd trwający 9 s — dłużej niż postój kadru,
więc ruch nigdy się nie zatrzymuje i nie „szarpie" przy zmianie.

**Kropki** w prawym dolnym rogu, na telefonie przenoszą się w lewo na dół i układają poziomo.
Klik przełącza kadr i restartuje odliczanie.

Kadr w tle nie liczy się, gdy karta przeglądarki jest nieaktywna — nie zjada baterii.
Przy `prefers-reduced-motion` rotacja jest wyłączona, zostaje pierwszy kadr i działające kropki.

**Gdzie zmienić:** tablica `SLIDES` na górze skryptu. Każdy wpis to klucz obrazu z rejestru `IMG`,
punkt startu najazdu `ox`/`oy` oraz opis alt po angielsku i polsku.
Odstęp zmienia zmienna `SLIDE_MS`.

**Rejestr obrazów.** Wszystkie zdjęcia siedzą teraz raz w obiekcie `IMG` i są stamtąd pobierane
przez hero, tour i portfolio. Dzięki temu kadry używane w kilku miejscach nie powielają się
w pliku — strona ma 1,88 MB zamiast 2,4 MB.

## dist/ — to wgrywasz na serwer

`index.html` w głównym katalogu **jest fragmentem**, bez `<head>`. Zbudowałem go pod podgląd.
Wersję na serwer robi:

```bash
python3 ~/Damian-Assistant/STRONA/zbuduj_dist.py
```

Powstaje katalog `dist/` z pięcioma plikami:

| Plik | Do czego |
|---|---|
| `index.html` | pełny dokument HTML z metadanymi |
| `og.jpg` | podgląd 1200×630 przy udostępnianiu linku |
| `robots.txt` | zgoda na indeksowanie i wskazanie mapy strony |
| `sitemap.xml` | mapa strony dla Google |
| `.htaccess` | kompresja, cache obrazów, `index.html` jako strona główna |

Co zawiera `<head>`: tytuł, opis pod wyniki wyszukiwania, canonical, favicon z Twojego sygnetu,
komplet Open Graph i Twitter Card, oraz dane strukturalne JSON-LD typu ProfessionalService —
nazwa, opis, adres e-mail, miasto, kraj, języki i cztery profile social.
**W danych strukturalnych nie ma niczego wymyślonego** — brak telefonu, ulicy i cen, bo ich nie mam.

## ⚠ Dwujęzyczność a Google — realny problem

Przełącznik EN/PL działa w JavaScripcie na **jednym adresie**. Dla użytkownika to wygodne,
ale **Google zaindeksuje tylko wersję domyślną, czyli angielską**. Polska nie istnieje
dla wyszukiwarki, bo nie ma własnego adresu.

Jeśli chcesz być znajdowany po polsku, potrzebne są dwa adresy:

```
stankiewicz.design/en/
stankiewicz.design/pl/
```

plus znaczniki `hreflang` wskazujące na siebie nawzajem. To około godziny pracy —
powiedz, a przebuduję. **Dopóki celujesz w rynek międzynarodowy, sama angielska wersja
jest wystarczająca** i nie ma pośpiechu.

---

# Wersja 4 — portfolio z podstronami (31.08.2026)

## Portfolio

Zostały **cztery prawdziwe projekty**. Interior Details, Bathroom Visualizations
i Material Direction zniknęły jako osobne kafle — moodboard i paleta materiałowa
są teraz **wewnątrz każdego projektu**, tak jak prosiłeś.

## Podstrony

| Adres | Projekt |
|---|---|
| `/portfolio/apartment-01/` | Apartament 01 |
| `/portfolio/blue-kitchen/` | Niebieska kuchnia |
| `/portfolio/marble-kitchen/` | Kuchnia marmurowa |
| `/portfolio/marble-bathroom/` | Łazienka marmurowa |

Każda zawiera: pełnoekranowy kadr otwierający, tytuł, typ projektu, krótki i długi opis
w obu językach, **paletę materiałową z próbnikami koloru**, **słowa-klucze nastroju**,
galerię pozostałych wizualizacji, **moodboard** oraz dwa przyciski — powrót do portfolio
i rozpoczęcie projektu.

**Placeholdery nie były potrzebne.** Każdy z czterech projektów ma komplet renderów
i własny moodboard, wszystko z Twoich folderów.

## Dwa tryby tras

Zmienna `TRYB` na górze skryptu, przełącza ją automatycznie `zbuduj_dist.py`:

- **`hash`** — podgląd w jednym pliku. Adresy typu `#/portfolio/blue-kitchen`.
- **`pages`** — wersja z `dist/`, gdzie każdy adres to osobny plik HTML.

Nie zmieniaj tego ręcznie.

## dist/ — co się zmieniło

Zdjęcia są teraz **prawdziwymi plikami**, nie base64:

```
dist/images/hero-01.jpg
dist/images/og.jpg
dist/images/projects/blue-kitchen/visual-01.jpg
dist/images/projects/blue-kitchen/visual-02.jpg
dist/images/projects/blue-kitchen/moodboard.jpg
dist/images/projects/blue-kitchen/og.jpg
```

Efekt: **strona główna waży 63 KB zamiast 3,5 MB**. Zdjęcia ładują się osobno,
przeglądarka je cachuje, a przy przejściu na podstronę nie pobiera ich drugi raz.

**Treść każdej podstrony jest wpisana w HTML** już podczas budowania — tytuł, opis,
paleta, galeria i moodboard istnieją w kodzie bez uruchamiania JavaScriptu.
To ma znaczenie dla Google.

Każda podstrona ma własny tytuł, opis, canonical i własny obrazek podglądu przy
udostępnianiu. Mapa strony wymienia wszystkie pięć adresów.

## Jak wgrać

```bash
python3 ~/Damian-Assistant/STRONA/zbuduj_dist.py
open ~/Damian-Assistant/STRONA/dist
```

Zawartość `dist/` wgrywasz do katalogu głównego hostingu — **całą, z podkatalogami**.
Struktura katalogów musi zostać zachowana, bo adresy `/portfolio/<slug>/` opierają się
na prawdziwych folderach.

⚠ **Zanim wgrasz:** obecna strona to WordPress. Wgranie `index.html` do tego samego
katalogu nie usunie WordPressa, tylko doda drugą stronę główną. Zrób najpierw kopię,
a najlepiej wgraj to na subdomenę testową i zobacz na żywo, zanim podmienisz produkcję.

---

# Wersja 5 — dwa języki dla Google (02.09.2026)

Domknąłem to, co sam wcześniej zgłosiłem jako brak: **polska wersja nie istniała
dla wyszukiwarki.** Przełącznik podmieniał teksty w JavaScripcie na jednym adresie,
więc Google indeksował wyłącznie angielski.

## Struktura adresów

```
/                              EN — wersja domyślna
/pl/                           PL
/portfolio/blue-kitchen/       EN
/pl/portfolio/blue-kitchen/    PL
404.html
```

**Jedenaście stron HTML.** Każda para ma znaczniki `hreflang` wskazujące na siebie
nawzajem plus `x-default` na angielską. Mapa strony wymienia dziesięć adresów
z trzydziestoma wpisami alternatywnych wersji.

Przełącznik EN/PL nie podmienia już tekstów w miejscu — **przenosi na bliźniaczy adres**.
Dzięki temu adres w pasku zawsze zgadza się z językiem na ekranie, a link da się wysłać
komuś w konkretnej wersji.

## Trzy błędy, które przy okazji wyszły

**Polska strona miała w kodzie angielskie zdania.** JavaScript podmieniał je dopiero
po wczytaniu, a Google czyta surowy HTML. Teraz builder tłumaczy treść na etapie
budowania — polskie zdania są w pliku.

**Strona główna nie miała ani jednego obrazu w HTML.** Slider, kadry sekcji przewijanej
i karty portfolio budował wyłącznie JavaScript. Dla studia wizualizacji to strona bez
wizualizacji. Teraz jest tam **trzynaście zdjęć wpisanych wprost w kod**.

**Brakowało wymiarów obrazów.** Bez `width` i `height` przeglądarka nie wie, ile miejsca
zarezerwować, i układ skacze przy wczytywaniu. Wszystkie 29 obrazów ma teraz wymiary.

## Co zostało

| | |
|---|---|
| Portret do sekcji O mnie | brak pliku |
| Wysłanie na GitHub | konto i token po Twojej stronie |
| Podpięcie Cloudflare Pages | pięć kliknięć po wysłaniu |
| Podpięcie formularza | Formspree albo podobne, miejsce oznaczone w kodzie |
