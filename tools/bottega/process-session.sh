#!/bin/bash
# Pipeline bottega per una cartella-sigla di sessione:
#   HEIC -> jpg (sips; originali .heic in raw/), organize.py (org/edit/thumb),
#   verifica conteggi, rimozione sorgenti loose, watermark su edit/.
# Uso: tools/bottega/process-session.sh _bottega/img/<progetto>/<sessione> <sigla>
set -euo pipefail

SESSION_DIR="${1:?uso: process-session.sh <session-dir> <sigla>}"
SIGLA="${2:?uso: process-session.sh <session-dir> <sigla>}"
SRC="$SESSION_DIR/$SIGLA"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -d "$SRC" ] || { echo "ERRORE: $SRC non esiste"; exit 1; }
if [ -e "$SRC/org" ]; then echo "ERRORE: $SRC/org esiste già (sessione processata?)"; exit 1; fi

# 1) HEIC -> jpg; l'originale .heic va in raw/ (archivio, mai pubblicato)
find "$SRC" -maxdepth 1 -type f -iname '*.heic' -print0 | while IFS= read -r -d '' f; do
  out="${f%.*}.jpg"
  # doppio export iPhone: se esiste già un jpg omonimo, non sovrascriverlo
  [ -e "$out" ] && out="${f%.*}-heic.jpg"
  sips -s format jpeg -s formatOptions best "$f" --out "$out" >/dev/null
  mkdir -p "$SRC/raw"
  mv "$f" "$SRC/raw/"
  echo "HEIC: $(basename "$f") -> $(basename "$out") (originale in raw/)"
done

# 2) conteggio sorgenti
N_SRC=$(find "$SRC" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \) | wc -l | tr -d ' ')
[ "$N_SRC" -gt 0 ] || { echo "ERRORE: nessuna immagine in $SRC"; exit 1; }

# 3) org/edit/thumb con rinomina <sessione>-NN
python3 "$ROOT/tools/organize/organize.py" "$SRC" "$SESSION_DIR" "$SIGLA"

# 4) verifica: org == edit == thumb == sorgenti
for d in org edit thumb; do
  n=$(find "$SRC/$d" -type f | wc -l | tr -d ' ')
  [ "$n" -eq "$N_SRC" ] || { echo "ERRORE: $d/ ha $n file, attesi $N_SRC"; exit 1; }
done

# 5) rimozione sorgenti loose (copie byte-identiche già in org/)
find "$SRC" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \) -delete

# 6) watermark (nome dedotto dalla sigla nel percorso)
python3 "$ROOT/tools/watermark/watermark.py" "$SRC/edit" --in-place

echo "OK: $SRC -> $N_SRC foto in org/edit/thumb (edit watermarked)"
