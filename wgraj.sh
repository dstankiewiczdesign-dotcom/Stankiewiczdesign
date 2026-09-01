#!/bin/bash
# Przebudowuje stronę i wysyła na serwer. Jedno polecenie na całą aktualizację.
#   ./wgraj.sh "co się zmieniło"
set -e
OPIS="${1:-aktualizacja strony}"
cd "$(dirname "$0")"

echo "── przebudowa"
python3 ~/Damian-Assistant/STRONA/zbuduj_dist.py | tail -3

echo "── kopiowanie do repozytorium"
rm -rf dist && cp -R ~/Damian-Assistant/STRONA/dist ./dist
cp ~/Damian-Assistant/STRONA/szablon.html ~/Damian-Assistant/STRONA/zbuduj_dist.py zrodlo/

if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "── nic się nie zmieniło, nie wysyłam"; exit 0
fi

echo "── wysyłka"
git add -A
git commit -q -m "$OPIS"
git push -q origin main
echo "── gotowe. Cloudflare Pages opublikuje w ciągu minuty."
