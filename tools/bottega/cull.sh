#!/bin/bash
# Sfinimento di una galleria pubblicata: "demote, non delete".
# Per ogni numero: org/<sessione>-NN.* -> raw/, rimozione di edit/ e thumb/.
# I numeri NON si riassegnano mai: i buchi sono ok, gli URL restano stabili.
# Uso: tools/bottega/cull.sh <session-dir> <sigla> NN [NN ...]
# es.: tools/bottega/cull.sh _bottega/img/stoned/2024-09-15-stoned ac 03 07 12
set -euo pipefail

SESSION_DIR="${1:?uso: cull.sh <session-dir> <sigla> NN [NN ...]}"
SIGLA="${2:?uso: cull.sh <session-dir> <sigla> NN [NN ...]}"
shift 2
[ $# -gt 0 ] || { echo "ERRORE: nessun numero indicato"; exit 1; }

SRC="$SESSION_DIR/$SIGLA"
SESSIONE="$(basename "$(cd "$SESSION_DIR" && pwd)")"
[ -d "$SRC/org" ] || { echo "ERRORE: $SRC/org non esiste (galleria non processata?)"; exit 1; }

# valida TUTTI i numeri prima di toccare qualsiasi cosa (niente stati a metà)
ORGS=(); EDITS=(); THUMBS=()
for n in "$@"; do
  NN=$(printf "%02d" "$((10#$n))")
  org=$(ls "$SRC/org/$SESSIONE-$NN".* 2>/dev/null | head -1)
  [ -n "$org" ] || { echo "ERRORE: $SESSIONE-$NN non trovato in org/ — nessuna modifica fatta"; exit 1; }
  [ -f "$SRC/edit/$SESSIONE-$NN.jpg" ] || { echo "ERRORE: manca edit/$SESSIONE-$NN.jpg — nessuna modifica fatta"; exit 1; }
  [ -f "$SRC/thumb/$SESSIONE-$NN.jpg" ] || { echo "ERRORE: manca thumb/$SESSIONE-$NN.jpg — nessuna modifica fatta"; exit 1; }
  ORGS+=("$org"); EDITS+=("$SRC/edit/$SESSIONE-$NN.jpg"); THUMBS+=("$SRC/thumb/$SESSIONE-$NN.jpg")
done

mkdir -p "$SRC/raw"
for i in "${!ORGS[@]}"; do
  mv "${ORGS[$i]}" "$SRC/raw/"
  rm "${EDITS[$i]}" "${THUMBS[$i]}"
  echo "demote: $(basename "${ORGS[$i]}") -> raw/ (edit e thumb rimossi)"
done

# invariante finale: org == edit == thumb
o=$(find "$SRC/org" -type f | wc -l | tr -d ' ')
e=$(find "$SRC/edit" -type f | wc -l | tr -d ' ')
t=$(find "$SRC/thumb" -type f | wc -l | tr -d ' ')
[ "$o" -eq "$e" ] && [ "$e" -eq "$t" ] || { echo "ATTENZIONE: conteggi disallineati org=$o edit=$e thumb=$t"; exit 1; }
echo "OK: $SRC ora pubblica $o foto ($# spostate in raw/)"
