# stankiewicz.design

Strona studia Stankiewicz Design. Jeden statyczny serwis, bez systemu zarządzania treścią.

## Co gdzie leży

| Katalog | Zawartość |
|---|---|
| `dist/` | **strona, która idzie na serwer** — to hostuje Cloudflare Pages |
| `zrodlo/` | szablon i skrypt budujący, do odtworzenia `dist/` |

## Jak zaktualizować

Zdjęcia projektów siedzą w `~/Damian-Assistant/NA_STRONE_PORTFOLIO`.
Po zmianach:

```bash
python3 ~/Damian-Assistant/STRONA/zbuduj_dist.py
cp -R ~/Damian-Assistant/STRONA/dist ~/stankiewicz-www/
cd ~/stankiewicz-www && git add -A && git commit -m "opis zmiany" && git push
```

Cloudflare Pages publikuje nową wersję sam, w ciągu minuty.

## Ustawienia w Cloudflare Pages

| Pole | Wartość |
|---|---|
| Framework preset | None |
| Build command | *(zostaw puste)* |
| Build output directory | `dist` |

## Strony

```
/                            strona główna
/portfolio/apartment-01/
/portfolio/blue-kitchen/
/portfolio/marble-kitchen/
/portfolio/marble-bathroom/
```

Mapa strony: `/sitemap.xml`
