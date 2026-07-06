#!/bin/bash
# Ripescaggio: riporta in galleria foto demoted con cull.sh.
# Per ogni numero: raw/<sessione>-NN.* -> org/, rigenera edit (1080, con
# watermark) e thumb (400) con gli stessi parametri di organize.py.
# Uso: tools/bottega/restore.sh <session-dir> <sigla> NN [NN ...]
# es.: tools/bottega/restore.sh _bottega/img/stoned/2024-09-15-stoned ac 07
set -euo pipefail

SESSION_DIR="${1:?uso: restore.sh <session-dir> <sigla> NN [NN ...]}"
SIGLA="${2:?uso: restore.sh <session-dir> <sigla> NN [NN ...]}"
shift 2
[ $# -gt 0 ] || { echo "ERRORE: nessun numero indicato"; exit 1; }

SRC="$SESSION_DIR/$SIGLA"
SESSIONE="$(basename "$(cd "$SESSION_DIR" && pwd)")"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# cartella temporanea a forma di .../<sigla>/edit, così watermark.py deduce il nome
TMPBASE=$(mktemp -d)
TMP="$TMPBASE/$SIGLA/edit"
mkdir -p "$TMP"
trap 'rm -rf "$TMPBASE"' EXIT

for n in "$@"; do
  NN=$(printf "%02d" "$((10#$n))")
  raw=$(ls "$SRC/raw/$SESSIONE-$NN".* 2>/dev/null | head -1)
  [ -n "$raw" ] || { echo "ERRORE: $SESSIONE-$NN non trovato in raw/ — nessuna modifica fatta"; exit 1; }
  if ls "$SRC/org/$SESSIONE-$NN".* >/dev/null 2>&1; then
    echo "ERRORE: $SESSIONE-$NN è già in org/ — nessuna modifica fatta"; exit 1
  fi
  mv "$raw" "$SRC/org/"
  python3 - "$SRC/org/$(basename "$raw")" "$TMP/$SESSIONE-$NN.jpg" "$SRC/thumb/$SESSIONE-$NN.jpg" <<'EOF'
import sys
from PIL import Image, ImageOps
src, edit_out, thumb_out = sys.argv[1], sys.argv[2], sys.argv[3]
im = ImageOps.exif_transpose(Image.open(src))
w, h = im.size
edit = im.resize((round(w * 1080 / h), 1080), Image.LANCZOS)
edit.convert("RGB").save(edit_out, quality=88, subsampling=0)
s = 400 / max(w, h)
thumb = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
thumb.convert("RGB").save(thumb_out, quality=88, subsampling=0)
EOF
  echo "restore: $SESSIONE-$NN (org e thumb pronti, edit in watermark...)"
done

python3 "$ROOT/tools/watermark/watermark.py" "$TMP" --in-place
mv "$TMP"/*.jpg "$SRC/edit/"

# invariante finale: org == edit == thumb
o=$(find "$SRC/org" -type f | wc -l | tr -d ' ')
e=$(find "$SRC/edit" -type f | wc -l | tr -d ' ')
t=$(find "$SRC/thumb" -type f | wc -l | tr -d ' ')
[ "$o" -eq "$e" ] && [ "$e" -eq "$t" ] || { echo "ATTENZIONE: conteggi disallineati org=$o edit=$e thumb=$t"; exit 1; }
echo "OK: ripescate $# foto, $SRC ora pubblica $o foto"
