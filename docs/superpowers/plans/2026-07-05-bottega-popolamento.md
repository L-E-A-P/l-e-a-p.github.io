# Popolamento della Bottega — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pubblicare i 7 progetti della Bottega LEAP (`/bottega/`) come lunghi post che alternano testo e gallerie per sessione di lavoro, processando ~2.7 GB di foto con la pipeline org/edit/thumb + watermark.

**Architecture:** Jekyll (github-pages, tema remoto `so-leap-theme`); collezione `bottega` con entry in `_bottega/web/*.md` (submodule) e immagini in `_bottega/img/<progetto>/<sessione>/<sigla>/{org,edit,thumb}`. Strategia incrementale: un progetto alla volta, end-to-end (pipeline → post → build → push → verifica), dal più semplice al più complesso.

**Tech Stack:** Jekyll 3.10 (gem github-pages), Python 3 + Pillow (`tools/organize/organize.py`, `tools/watermark/watermark.py`), `sips` (macOS) per HEIC, bash, git submodule.

**Spec:** `docs/superpowers/specs/2026-07-05-bottega-design.md`

## Global Constraints

- Repo principale: `/Users/alice/Documents/github/leap/web/l-e-a-p.github.io` — submodule: `_bottega` (tutti i comandi sotto assumono cwd = repo principale se non detto diversamente).
- Convenzione immagini SEMPRE: `img/<progetto>/<YYYY-MM-DD[-slug]>/<sigla>/{org,edit,thumb}/`, stessi nomi file nelle tre cartelle.
- HEIC mai dati a `organize.py` (li salta): convertire prima con `sips`; l'originale `.heic` va in `raw/` (archivio git, mai pubblicato).
- `raw/` = originali non processati o pre-conversione: committati in git, esclusi dal sito (nuova convenzione, introdotta al Task 1).
- Il match gallery su `thumb/` NON è ricorsivo → un `{% include gallery path="bottega/img/…/<sigla>/" %}` per ogni cartella-sigla.
- Titoli esatti dei post: **The Big Data Cookbook**, **FLUX**, **Umano Post Umano**, **Luccello**, **Anapnoe, Somafonico, Petalonio**, **STONED**, **Mario Bertoncini**.
- `date:` nel front matter = data dell'ultima sessione pubblicata del progetto; sessioni nel post in ordine cronologico crescente; griglia `sort_by: date` + `sort_order: reverse`.
- `org/`, `raw/`, `*.mov`, `*.heic`: sempre in git, mai nel sito pubblicato (`exclude:` in `_config.yml`).
- Ogni push ≤ ~1.5 GB (limite git ~2 GB/push); l'ordine incrementale per progetto lo garantisce già.
- Tutti i contenuti del sito in italiano.
- Commit: messaggio in italiano, footer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` + riga `Claude-Session`.
- Le foto scelte per hero/-t: proposta di Claude annotata nel messaggio di commit; Alice può sostituirle in seguito.

## Inventario di riferimento (conteggi attesi, verificati il 2026-07-05)

| Progetto / sessione | sigla → n. foto (jpg+jpeg+heic) |
|---|---|
| tbdc-citera/2023-12-01-prove-leap | ac → 2 |
| tbdc-citera/2023-12-08-prove-leap | ac → 44 |
| flux-ferracuti/2023-09-28 | ac → 6 |
| flux-ferracuti/2023-10-14 | ac → 1 |
| flux-ferracuti/2024-02-12 | ac → 21 |
| upu-ads/2024-06-08-ads-leap | ac → 33 (di cui 29 HEIC) |
| upu-ads/2024-09-14-ads-leap | ac → 21 |
| luccello/2025-05-28 | ac → 6 (tutte HEIC) |
| luccello/2025-06-19 | solo 1 .mov, NON pubblicare |
| anapnoe-somafonico-petalonio/2025-04-22 | ac → 2 |
| anapnoe-somafonico-petalonio/2025-04-24 | ac → 69 |
| anapnoe-somafonico-petalonio/2025-04-26 | ac → 21 (+4 mov) |
| anapnoe-somafonico-petalonio/2025-04-27 | ac → 5, gs → 8 (+13 mov) |
| anapnoe-somafonico-petalonio/2025-04-30 | solo 1 .mov (gs), NON pubblicare |
| stoned/2024-08-29-STONED | ac → 13 |
| stoned/2024-08-30-STONED | ac → 13 |
| stoned/2024-09-06-STONED | ac → 88 |
| stoned/2024-09-07-STONED | ac → 44 |
| stoned/2024-09-15-STONED | ac → 224 |
| stoned/2024-09-16-STONED | ac → 34 |
| mario-bertoncini/2025-06-19-prelievo | ac → 50 (di cui 17 HEIC; ha anche ac/mov/), gs → 23, mdg → 21 |
| mario-bertoncini/2025-07-31 | ac → 8, gs → 15 |
| mario-bertoncini/2025-08-08 | ac → 7 |
| mario-bertoncini/2025-08-12 | ac → 5 |
| mario-bertoncini/2025-08-13 | ac → 7 |
| mario-bertoncini/2025-08-18 | ac → 3 |
| mario-bertoncini/2025-09-04 | ac → 15 |
| mario-bertoncini/2025-09-18 | ac → 6, gs → 3 |
| mario-bertoncini/2025-09-22 | ac → 42 (+22 mov loose), gs → 3 |
| mario-bertoncini/2025-10-29-riconsegna | ac → 84 |

Sigle: `ac` Alice Cortegiani, `gs` Giuseppe Silvi, `mdg` Marco Di Gasbarro — già in `tools/watermark/photographers.yml`.

---

### Task 1: Configurazione — ordinamento griglia + exclude org/raw/mov/heic

**Files:**
- Modify: `bottega.md` (front matter)
- Modify: `_config.yml:249` (lista `exclude:`)

**Interfaces:**
- Produces: sito che pubblica solo `edit/` e `thumb/` (mai `org/`, `raw/`, `*.mov`, `*.heic`); griglia bottega ordinata per `date:` decrescente. Tutti i task successivi contano su queste regole.

- [ ] **Step 1: Baseline — build locale e misura**

```bash
cd /Users/alice/Documents/github/leap/web/l-e-a-p.github.io
bundle check || bundle install
bundle exec jekyll build 2>&1 | tail -3
du -sh _site
find _site -type d -name org | wc -l
```

Expected: build senza errori. `find` > 0 (gli `org/` oggi vengono pubblicati). Nota: la build copierà anche i ~2.7 GB di foto loose di `_bottega/img` — è atteso, lenta solo finché i progetti non sono processati (le loose spariscono task dopo task).

- [ ] **Step 2: Front matter di `bottega.md`**

Aggiungere due righe al front matter (dopo `collection: bottega`):

```yaml
sort_by: date
sort_order: reverse
```

- [ ] **Step 3: Estendere `exclude:` in `_config.yml`**

In coda alla lista `exclude:` esistente (riga 249):

```yaml
  # Sorgenti immagini/video: in git come archivio, mai nel sito pubblicato
  - "**/org"
  - "**/raw"
  - "**/*.mov"
  - "**/*.MOV"
  - "**/*.heic"
  - "**/*.HEIC"
```

- [ ] **Step 4: Rebuild e verifica esclusioni**

```bash
bundle exec jekyll build 2>&1 | tail -3
find _site -type d \( -name org -o -name raw \) | wc -l        # atteso: 0
find _site -type f \( -iname "*.mov" -o -iname "*.heic" \) | wc -l  # atteso: 0
grep -c "thumb/" _site/lazzaro/2025-04-29-ansc/index.html      # atteso: > 0 (gallerie intatte)
du -sh _site                                                    # atteso: sensibilmente < baseline
```

Se i pattern `**/org` non filtrano i file statici delle collezioni (conteggio ≠ 0): provare le varianti esplicite per base (`_bottega/img/**/org`, `_lazzaro/img/**/org`, `_archi-di-pietra/img/**/org`, `_domeniche/img/**/org`, `images/posts/**/org`, e le equivalenti senza prefisso `img/`), una famiglia per volta, ribuildando. Se NESSUN pattern funziona sulle collezioni: fermarsi e riportare ad Alice (contingenza: workflow GitHub Actions per Pages che pota `_site` — decisione sua).

- [ ] **Step 5: Verifica che la griglia bottega ordini per data**

```bash
grep -A2 "sort_by" bottega.md
```

Expected: le due righe presenti. (La verifica visiva d'ordinamento avviene al Task 2, quando ci saranno ≥ 2 entry.)

- [ ] **Step 6: Commit (repo principale)**

```bash
git add bottega.md _config.yml
git commit -m "$(cat <<'EOF'
Bottega: griglia per data (reverse) + exclude org/raw/mov/heic dal sito

Gli originali restano in git come archivio; il sito pubblica solo
edit/ (watermarked) e thumb/. Vale per tutte le collezioni.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)"
```

Non pushare ancora: si pusha col Task 2 (primo progetto completo).

---

### Task 2: Script di pipeline + progetto pilota The Big Data Cookbook (`tbdc-citera`)

**Files:**
- Create: `tools/bottega/process-session.sh`
- Create: `tools/bottega/make-hero.py`
- Create: `_bottega/web/tbdc-citera.md`
- Create (generati): `_bottega/img/tbdc-citera/{tbdc-citera-hero.jpg,tbdc-citera-t.jpg}` + `org/edit/thumb` nelle 2 sessioni

**Interfaces:**
- Consumes: exclude e sort del Task 1.
- Produces: `process-session.sh <session-dir> <sigla>` (converte HEIC→jpg con originali in `raw/`, organizza in `org/edit/thumb`, verifica conteggi, elimina i loose, watermarka `edit/`); `make-hero.py <foto-edit> <cartella-progetto>` (genera `<slug>-hero.jpg` 1600×800 e `<slug>-t.jpg` 800×800). Tutti i task 3–8 li usano identici.

- [ ] **Step 1: Scrivere `tools/bottega/process-session.sh`**

```bash
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
```

```bash
chmod +x tools/bottega/process-session.sh
```

- [ ] **Step 2: Scrivere `tools/bottega/make-hero.py`**

```python
#!/usr/bin/env python3
"""Genera <slug>-hero.jpg (1600x800) e <slug>-t.jpg (800x800) per un progetto
bottega, dalla foto indicata (convenzione dimensioni: hero/-t di lazzaro).
Uso: make-hero.py <foto-sorgente> <cartella-progetto>
Es.: make-hero.py _bottega/img/tbdc-citera/2023-12-08-prove-leap/ac/edit/2023-12-08-prove-leap-07.jpg _bottega/img/tbdc-citera
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

src, proj = Path(sys.argv[1]), Path(sys.argv[2])
slug = proj.resolve().name
img = ImageOps.exif_transpose(Image.open(src))
ImageOps.fit(img, (1600, 800), Image.LANCZOS).save(proj / f"{slug}-hero.jpg", quality=88, subsampling=0)
ImageOps.fit(img, (800, 800), Image.LANCZOS).save(proj / f"{slug}-t.jpg", quality=88, subsampling=0)
print(f"OK: {slug}-hero.jpg (1600x800), {slug}-t.jpg (800x800)")
```

```bash
chmod +x tools/bottega/make-hero.py
```

- [ ] **Step 3: Test dello script sulla sessione più piccola (2 foto) — prima dry-run di organize**

```bash
python3 tools/organize/organize.py _bottega/img/tbdc-citera/2023-12-01-prove-leap/ac \
        _bottega/img/tbdc-citera/2023-12-01-prove-leap ac --dry-run
```

Expected: elenca 2 rinominazioni `-> 2023-12-01-prove-leap-01/02.jpg`, "niente scritto".

```bash
tools/bottega/process-session.sh _bottega/img/tbdc-citera/2023-12-01-prove-leap ac
find _bottega/img/tbdc-citera/2023-12-01-prove-leap/ac -type f | sort
```

Expected: `OK: … -> 2 foto`; nelle tre cartelle `org/edit/thumb` gli stessi 2 nomi (`2023-12-01-prove-leap-01.jpg`, `-02.jpg`); nessun file loose; watermark presente sugli edit (verifica visiva: aprire `edit/2023-12-01-prove-leap-01.jpg` con Read e controllare monogramma LEAP + "Alice Cortegiani" in basso a sinistra).

- [ ] **Step 4: Processare la seconda sessione**

```bash
tools/bottega/process-session.sh _bottega/img/tbdc-citera/2023-12-08-prove-leap ac
```

Expected: `OK: … -> 44 foto`.

- [ ] **Step 5: Hero e thumbnail**

Guardare le thumb (`Read` su alcune di `_bottega/img/tbdc-citera/2023-12-08-prove-leap/ac/thumb/`), scegliere una foto orizzontale rappresentativa (nitida, soggetto leggibile). Se la scelta è verticale, usare come sorgente il file corrispondente in `org/` (piena risoluzione) invece che in `edit/`.

```bash
python3 tools/bottega/make-hero.py \
  _bottega/img/tbdc-citera/2023-12-08-prove-leap/ac/edit/<FOTO-SCELTA>.jpg \
  _bottega/img/tbdc-citera
sips -g pixelWidth -g pixelHeight _bottega/img/tbdc-citera/tbdc-citera-hero.jpg _bottega/img/tbdc-citera/tbdc-citera-t.jpg
```

Expected: 1600×800 e 800×800.

- [ ] **Step 6: Scrivere `_bottega/web/tbdc-citera.md`**

```markdown
---
title: "The Big Data Cookbook"
date: 2023-12-08
image:
  path: bottega/img/tbdc-citera/tbdc-citera-hero.jpg
  thumbnail: bottega/img/tbdc-citera/tbdc-citera-t.jpg
  caption: ""
---

Le sessioni di prova al LEAP di *The Big Data Cookbook* di Pasquale Citera,
dicembre 2023.

<!--more-->

## 1 dicembre 2023

{% include gallery path="bottega/img/tbdc-citera/2023-12-01-prove-leap/ac/" %}

## 8 dicembre 2023

{% include gallery path="bottega/img/tbdc-citera/2023-12-08-prove-leap/ac/" %}
```

- [ ] **Step 7: Build locale e verifica rendering**

```bash
bundle exec jekyll build 2>&1 | tail -3
ls _site/bottega/tbdc-citera/index.html
grep -c "tbdc-citera/2023-12-08-prove-leap/ac/thumb" _site/bottega/tbdc-citera/index.html   # atteso: 44
grep -c "tbdc-citera/2023-12-01-prove-leap/ac/thumb" _site/bottega/tbdc-citera/index.html   # atteso: 2
find _site -type d \( -name org -o -name raw \) | wc -l                                     # atteso: 0
grep -o "bottega/tbdc-citera\|bottega/mb" _site/bottega/index.html | sort -u               # atteso: entrambe le entry in griglia
```

- [ ] **Step 8: Pulizia .DS_Store e commit submodule `_bottega`**

```bash
find _bottega/img -name ".DS_Store" -delete
cd _bottega
git add img/tbdc-citera web/tbdc-citera.md
git status --short   # controllare che entrino SOLO i file del progetto
git commit -m "$(cat <<'EOF'
bottega web: The Big Data Cookbook (tbdc-citera), 2 sessioni dic 2023

46 foto ac in org/edit/thumb, edit watermarked. Hero: <FOTO-SCELTA>.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)"
git push
cd ..
```

Nota: gli script `tools/bottega/*` vivono nel repo PRINCIPALE, non nel submodule; si committano allo Step 9.

- [ ] **Step 9: Bump submodule + script nel repo principale, push**

```bash
git add _bottega tools/bottega
git commit -m "$(cat <<'EOF'
bump _bottega: The Big Data Cookbook + script pipeline bottega

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)"
git push
```

(Questo push include anche il commit di config del Task 1.)

- [ ] **Step 10: Verifica online (build Pages ~1–5 min)**

```bash
sleep 120
curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/tbdc-citera/
curl -s https://l-e-a-p.github.io/bottega/tbdc-citera/ | grep -c "thumb"
curl -s -o /dev/null -w "%{http_code}\n" "https://l-e-a-p.github.io/bottega/img/tbdc-citera/2023-12-08-prove-leap/ac/org/2023-12-08-prove-leap-01.jpg"
```

Expected: `200`; conteggio thumb > 0; l'URL `org/` risponde **404** (exclude efficace anche su Pages). Se dopo 3 tentativi distanziati la pagina non appare o l'org è servito: STOP, riportare ad Alice prima di procedere coi progetti grossi.

---

### Task 3: FLUX (`flux-ferracuti`)

**Files:**
- Create: `_bottega/web/flux-ferracuti.md`
- Create (generati): hero/-t + org/edit/thumb nelle 3 sessioni

**Interfaces:**
- Consumes: `tools/bottega/process-session.sh`, `tools/bottega/make-hero.py` (Task 2).

- [ ] **Step 1: Processare le 3 sessioni**

```bash
tools/bottega/process-session.sh _bottega/img/flux-ferracuti/2023-09-28 ac   # atteso: OK 6 foto
tools/bottega/process-session.sh _bottega/img/flux-ferracuti/2023-10-14 ac   # atteso: OK 1 foto
tools/bottega/process-session.sh _bottega/img/flux-ferracuti/2024-02-12 ac   # atteso: OK 21 foto
```

- [ ] **Step 2: Hero e thumbnail** — guardare le thumb, scegliere foto orizzontale rappresentativa (idealmente lo strumento FLUX):

```bash
python3 tools/bottega/make-hero.py _bottega/img/flux-ferracuti/<SESSIONE>/ac/edit/<FOTO-SCELTA>.jpg _bottega/img/flux-ferracuti
```

- [ ] **Step 3: Scrivere `_bottega/web/flux-ferracuti.md`**

```markdown
---
title: "FLUX"
date: 2024-02-12
image:
  path: bottega/img/flux-ferracuti/flux-ferracuti-hero.jpg
  thumbnail: bottega/img/flux-ferracuti/flux-ferracuti-t.jpg
  caption: ""
---

FLUX è lo strumento-progetto di Francesco Ferracuti, sviluppato come progetto
di laurea del triennio. In bottega, le sessioni di lavoro al LEAP.

<!--more-->

## 28 settembre 2023

{% include gallery path="bottega/img/flux-ferracuti/2023-09-28/ac/" %}

## 14 ottobre 2023

{% include gallery path="bottega/img/flux-ferracuti/2023-10-14/ac/" %}

## 12 febbraio 2024

{% include gallery path="bottega/img/flux-ferracuti/2024-02-12/ac/" %}
```

- [ ] **Step 4: Build locale e verifica**

```bash
bundle exec jekyll build 2>&1 | tail -3
grep -c "flux-ferracuti/2024-02-12/ac/thumb" _site/bottega/flux-ferracuti/index.html   # atteso: 21
grep -c "flux-ferracuti/2023-09-28/ac/thumb" _site/bottega/flux-ferracuti/index.html   # atteso: 6
```

- [ ] **Step 5: Commit `_bottega`, push, bump, verifica online**

```bash
find _bottega/img/flux-ferracuti -name ".DS_Store" -delete
cd _bottega && git add img/flux-ferracuti web/flux-ferracuti.md && git commit -m "$(cat <<'EOF'
bottega web: FLUX (flux-ferracuti), 3 sessioni 2023-2024

28 foto ac in org/edit/thumb, edit watermarked. Hero: <FOTO-SCELTA>.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega && git commit -m "$(cat <<'EOF'
bump _bottega: FLUX

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
sleep 120 && curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/flux-ferracuti/   # atteso: 200
```

---

### Task 4: Umano Post Umano (`upu-ads`) — primo caso HEIC

**Files:**
- Create: `_bottega/web/upu-ads.md`
- Create (generati): hero/-t + org/edit/thumb nelle 2 sessioni; `2024-06-08-ads-leap/ac/raw/` con i 29 `.heic`

**Interfaces:**
- Consumes: script del Task 2 (la conversione HEIC è dentro `process-session.sh`).

- [ ] **Step 1: Processare le 2 sessioni**

```bash
tools/bottega/process-session.sh _bottega/img/upu-ads/2024-06-08-ads-leap ac   # atteso: 29 righe "HEIC: …", poi OK 33 foto
tools/bottega/process-session.sh _bottega/img/upu-ads/2024-09-14-ads-leap ac   # atteso: OK 21 foto
ls _bottega/img/upu-ads/2024-06-08-ads-leap/ac/raw | wc -l                     # atteso: 29
```

- [ ] **Step 2: Hero e thumbnail** (foto orizzontale rappresentativa):

```bash
python3 tools/bottega/make-hero.py _bottega/img/upu-ads/<SESSIONE>/ac/edit/<FOTO-SCELTA>.jpg _bottega/img/upu-ads
```

- [ ] **Step 3: Scrivere `_bottega/web/upu-ads.md`**

```markdown
---
title: "Umano Post Umano"
date: 2024-09-14
image:
  path: bottega/img/upu-ads/upu-ads-hero.jpg
  thumbnail: bottega/img/upu-ads/upu-ads-t.jpg
  caption: ""
---

*Umano Post Umano* — performance distribuita, per un teatro sonoro
corpo/macchina/spazio — di Agostino Di Scipio, eseguita in prima assoluta il
19 dicembre 2024 nell'ambito di Nuova Consonanza. In bottega, stralci del
lavoro di ricerca condotto al LEAP insieme ad Agostino.

<!--more-->

## 8 giugno 2024

{% include gallery path="bottega/img/upu-ads/2024-06-08-ads-leap/ac/" %}

## 14 settembre 2024

{% include gallery path="bottega/img/upu-ads/2024-09-14-ads-leap/ac/" %}
```

- [ ] **Step 4: Build locale e verifica (incluso: raw/ non pubblicato)**

```bash
bundle exec jekyll build 2>&1 | tail -3
grep -c "upu-ads/2024-06-08-ads-leap/ac/thumb" _site/bottega/upu-ads/index.html   # atteso: 33
find _site -type d -name raw | wc -l                                              # atteso: 0
```

- [ ] **Step 5: Commit `_bottega`, push, bump, verifica online**

```bash
find _bottega/img/upu-ads -name ".DS_Store" -delete
cd _bottega && git add img/upu-ads web/upu-ads.md && git commit -m "$(cat <<'EOF'
bottega web: Umano Post Umano (upu-ads), 2 sessioni 2024

54 foto ac in org/edit/thumb (29 HEIC convertite, originali in raw/),
edit watermarked. Hero: <FOTO-SCELTA>.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega && git commit -m "$(cat <<'EOF'
bump _bottega: Umano Post Umano

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
sleep 120 && curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/upu-ads/   # atteso: 200
curl -s -o /dev/null -w "%{http_code}\n" "https://l-e-a-p.github.io/bottega/img/upu-ads/2024-06-08-ads-leap/ac/raw/$(ls _bottega/img/upu-ads/2024-06-08-ads-leap/ac/raw | head -1 | sed 's/ /%20/g')"   # atteso: 404
```

---

### Task 5: Luccello (`luccello`)

**Files:**
- Create: `_bottega/web/luccello.md`
- Create (generati): hero/-t + org/edit/thumb in 2025-05-28; `ac/raw/` con i 6 `.heic`

**Interfaces:**
- Consumes: script del Task 2.

- [ ] **Step 1: Processare la sessione con foto** (i nomi contengono spazi, es. `IMG_5284 2.HEIC` — lo script li gestisce):

```bash
tools/bottega/process-session.sh _bottega/img/luccello/2025-05-28 ac   # atteso: 6 "HEIC:", OK 6 foto
```

La sessione `2025-06-19` (solo un .mov) NON si processa e NON va nel post: resta in git, esclusa dal sito, in attesa del canale video.

- [ ] **Step 2: Hero e thumbnail** (6 foto: scegliere la migliore orizzontale; se tutte verticali usare la corrispondente in `org/`):

```bash
python3 tools/bottega/make-hero.py _bottega/img/luccello/2025-05-28/ac/edit/<FOTO-SCELTA>.jpg _bottega/img/luccello
```

- [ ] **Step 3: Scrivere `_bottega/web/luccello.md`**

```markdown
---
title: "Luccello"
date: 2025-05-28
image:
  path: bottega/img/luccello/luccello-hero.jpg
  thumbnail: bottega/img/luccello/luccello-t.jpg
  caption: ""
---

Luccello è un organismo del ciclo *Canto alla durata* di Giuseppe Silvi: al
violoncello, produce un meccanismo di feedback acustico mediante induzione
elettromagnetica.

<!--more-->

## 28 maggio 2025

{% include gallery path="bottega/img/luccello/2025-05-28/ac/" %}
```

- [ ] **Step 4: Build locale e verifica**

```bash
bundle exec jekyll build 2>&1 | tail -3
grep -c "luccello/2025-05-28/ac/thumb" _site/bottega/luccello/index.html   # atteso: 6
```

- [ ] **Step 5: Commit `_bottega`, push, bump, verifica online**

```bash
find _bottega/img/luccello -name ".DS_Store" -delete
cd _bottega && git add img/luccello web/luccello.md && git commit -m "$(cat <<'EOF'
bottega web: Luccello, sessione mag 2025

6 foto ac (HEIC convertite, originali in raw/), edit watermarked.
Hero: <FOTO-SCELTA>. La sessione 2025-06-19 (solo video) resta in archivio.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega && git commit -m "$(cat <<'EOF'
bump _bottega: Luccello

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
sleep 120 && curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/luccello/   # atteso: 200
```

---

### Task 6: Anapnoe, Somafonico, Petalonio (`anapnoe-somafonico-petalonio`) — multi-fotografo

**Files:**
- Create: `_bottega/web/anapnoe-somafonico-petalonio.md`
- Create (generati): hero/-t + org/edit/thumb in 5 cartelle-sigla (4 sessioni con foto)

**Interfaces:**
- Consumes: script del Task 2.

- [ ] **Step 1: Processare le 5 cartelle-sigla** (i .mov loose restano dove sono: ignorati da organize, esclusi dal sito):

```bash
tools/bottega/process-session.sh _bottega/img/anapnoe-somafonico-petalonio/2025-04-22 ac   # atteso: OK 2
tools/bottega/process-session.sh _bottega/img/anapnoe-somafonico-petalonio/2025-04-24 ac   # atteso: OK 69
tools/bottega/process-session.sh _bottega/img/anapnoe-somafonico-petalonio/2025-04-26 ac   # atteso: OK 21
tools/bottega/process-session.sh _bottega/img/anapnoe-somafonico-petalonio/2025-04-27 ac   # atteso: OK 5
tools/bottega/process-session.sh _bottega/img/anapnoe-somafonico-petalonio/2025-04-27 gs   # atteso: OK 8
```

La sessione `2025-04-30` (solo un .mov gs) NON si processa e NON va nel post.

- [ ] **Step 2: Hero e thumbnail** (scegliere una foto che mostri uno dei tre organismi):

```bash
python3 tools/bottega/make-hero.py _bottega/img/anapnoe-somafonico-petalonio/<SESSIONE>/<SIGLA>/edit/<FOTO-SCELTA>.jpg _bottega/img/anapnoe-somafonico-petalonio
```

- [ ] **Step 3: Scrivere `_bottega/web/anapnoe-somafonico-petalonio.md`**

```markdown
---
title: "Anapnoe, Somafonico, Petalonio"
date: 2025-04-27
image:
  path: bottega/img/anapnoe-somafonico-petalonio/anapnoe-somafonico-petalonio-hero.jpg
  thumbnail: bottega/img/anapnoe-somafonico-petalonio/anapnoe-somafonico-petalonio-t.jpg
  caption: ""
---

Tre organismi elettroacustici per *Canto alla durata* di Giuseppe Silvi:
anapnoe, sordina elettroacustica; somafonico, corpetto elettroacustico;
petalonio, il trombino per clarinetto contrabbasso che alloggia l'anapnoe.

<!--more-->

## 22 aprile 2025

{% include gallery path="bottega/img/anapnoe-somafonico-petalonio/2025-04-22/ac/" %}

## 24 aprile 2025

{% include gallery path="bottega/img/anapnoe-somafonico-petalonio/2025-04-24/ac/" %}

## 26 aprile 2025

{% include gallery path="bottega/img/anapnoe-somafonico-petalonio/2025-04-26/ac/" %}

## 27 aprile 2025

{% include gallery path="bottega/img/anapnoe-somafonico-petalonio/2025-04-27/ac/" %}

{% include gallery path="bottega/img/anapnoe-somafonico-petalonio/2025-04-27/gs/" %}
```

- [ ] **Step 4: Build locale e verifica** (due gallerie distinte per il 27 aprile):

```bash
bundle exec jekyll build 2>&1 | tail -3
grep -c "2025-04-27/ac/thumb" _site/bottega/anapnoe-somafonico-petalonio/index.html   # atteso: 5
grep -c "2025-04-27/gs/thumb" _site/bottega/anapnoe-somafonico-petalonio/index.html   # atteso: 8
```

Verificare col Read di un edit gs che il watermark riporti "Giuseppe Silvi".

- [ ] **Step 5: Commit `_bottega`, push, bump, verifica online**

```bash
find _bottega/img/anapnoe-somafonico-petalonio -name ".DS_Store" -delete
cd _bottega && git add img/anapnoe-somafonico-petalonio web/anapnoe-somafonico-petalonio.md && git commit -m "$(cat <<'EOF'
bottega web: Anapnoe, Somafonico, Petalonio, 4 sessioni apr 2025

105 foto (ac+gs) in org/edit/thumb, edit watermarked. Hero: <FOTO-SCELTA>.
La sessione 2025-04-30 (solo video) resta in archivio.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega && git commit -m "$(cat <<'EOF'
bump _bottega: Anapnoe, Somafonico, Petalonio

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
sleep 120 && curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/anapnoe-somafonico-petalonio/   # atteso: 200
```

---

### Task 7: STONED (`stoned`) — selezione provvisoria

**Files:**
- Create: `_bottega/web/stoned.md`
- Rename: le 6 cartelle sessione `*-STONED` → `*-stoned` (minuscolo)
- Create (generati): hero/-t; per sessione: `ac/raw/` con TUTTI gli originali + org/edit/thumb della selezione (~6–8)

**Interfaces:**
- Consumes: script del Task 2.

- [ ] **Step 1: Normalizzare i nomi sessione in minuscolo**

```bash
cd _bottega/img/stoned
for d in *-STONED; do mv "$d" "${d%-STONED}-stoned"; done
ls   # atteso: 2024-08-29-stoned … 2024-09-16-stoned
cd ../../..
```

- [ ] **Step 2: Archiviare tutti gli originali in raw/** (una sessione alla volta):

```bash
for s in _bottega/img/stoned/*/; do
  mkdir -p "${s}ac/raw"
  find "${s}ac" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) -exec mv {} "${s}ac/raw/" \;
done
find _bottega/img/stoned -path "*/raw/*" -type f | wc -l   # atteso: 416
```

- [ ] **Step 3: Selezione provvisoria (~6–8 per sessione)**

Per ogni sessione: guardare le foto in `ac/raw/` (Read, a campione ragionato — per la sessione da 224 scorrere per gruppi di orario), scegliere 6–8 foto nitide, esposte correttamente, rappresentative e varie (dettagli costruttivi + totali + persone al lavoro, no doppioni), e ricopiarle loose in `ac/`:

```bash
cp "_bottega/img/stoned/<SESSIONE>/ac/raw/<FOTO>.jpeg" "_bottega/img/stoned/<SESSIONE>/ac/"
```

- [ ] **Step 4: Processare le 6 sessioni**

```bash
for s in _bottega/img/stoned/*/; do tools/bottega/process-session.sh "$s" ac; done
```

Expected: 6 × `OK … 6-8 foto`. (Le raw restano al loro posto: lo script tocca solo i file loose.)

- [ ] **Step 5: Hero e thumbnail** (foto orizzontale dell'altoparlante):

```bash
python3 tools/bottega/make-hero.py _bottega/img/stoned/<SESSIONE>/ac/edit/<FOTO-SCELTA>.jpg _bottega/img/stoned
```

- [ ] **Step 6: Scrivere `_bottega/web/stoned.md`**

```markdown
---
title: "STONED"
date: 2024-09-16
image:
  path: bottega/img/stoned/stoned-hero.jpg
  thumbnail: bottega/img/stoned/stoned-t.jpg
  caption: ""
---

STONED è un altoparlante con sistema di diffusione sferica/tetraedrica di
Giuseppe Silvi, concepito per un'installazione nell'ambito del Festival
ArteScienza 2024. Dalle sessioni di costruzione, una prima selezione.

<!--more-->

## 29 agosto 2024

{% include gallery path="bottega/img/stoned/2024-08-29-stoned/ac/" %}

## 30 agosto 2024

{% include gallery path="bottega/img/stoned/2024-08-30-stoned/ac/" %}

## 6 settembre 2024

{% include gallery path="bottega/img/stoned/2024-09-06-stoned/ac/" %}

## 7 settembre 2024

{% include gallery path="bottega/img/stoned/2024-09-07-stoned/ac/" %}

## 15 settembre 2024

{% include gallery path="bottega/img/stoned/2024-09-15-stoned/ac/" %}

## 16 settembre 2024

{% include gallery path="bottega/img/stoned/2024-09-16-stoned/ac/" %}
```

- [ ] **Step 7: Build locale e verifica**

```bash
bundle exec jekyll build 2>&1 | tail -3
for s in 2024-08-29 2024-08-30 2024-09-06 2024-09-07 2024-09-15 2024-09-16; do
  grep -c "stoned/$s-stoned/ac/thumb" _site/bottega/stoned/index.html
done   # atteso: 6-8 per riga
find _site -type d -name raw | wc -l   # atteso: 0
```

- [ ] **Step 8: Commit `_bottega`, push, bump, verifica online**

Il commit pesa ~800 MB — è il push singolo più grosso: se `git push` fallisse
per dimensione, spezzare committando 3 sessioni alla volta.

```bash
find _bottega/img/stoned -name ".DS_Store" -delete
cd _bottega && git add img/stoned web/stoned.md && git commit -m "$(cat <<'EOF'
bottega web: STONED, 6 sessioni ago-set 2024 (selezione provvisoria)

416 originali in ac/raw/ (archivio), ~40 selezionate in org/edit/thumb,
edit watermarked. Selezione fine di Alice a seguire. Hero: <FOTO-SCELTA>.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega && git commit -m "$(cat <<'EOF'
bump _bottega: STONED

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
sleep 120 && curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/stoned/   # atteso: 200
```

---

### Task 8: Mario Bertoncini (`mario-bertoncini`) — 11 sessioni, 3 fotografi, fascicoli PDF

**Files:**
- Create: `_bottega/web/mario-bertoncini.md` (sostituisce `web/mb.md`)
- Delete: `_bottega/web/mb.md`, `_bottega/img/mb.jpg`
- Create (generati): hero/-t + org/edit/thumb in 15 cartelle-sigla

**Interfaces:**
- Consumes: script del Task 2.
- ⚠ Cambia URL pubblico: `/bottega/mb/` → `/bottega/mario-bertoncini/` (deciso in spec).

- [ ] **Step 1: Processare le 15 cartelle-sigla**

```bash
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-06-19-prelievo ac    # atteso: 17 "HEIC:", OK 50
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-06-19-prelievo gs    # atteso: OK 23
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-06-19-prelievo mdg   # atteso: OK 21
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-07-31 ac             # atteso: OK 8
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-07-31 gs             # atteso: OK 15
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-08-08 ac             # atteso: OK 7
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-08-12 ac             # atteso: OK 5
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-08-13 ac             # atteso: OK 7
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-08-18 ac             # atteso: OK 3
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-09-04 ac             # atteso: OK 15
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-09-18 ac             # atteso: OK 6
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-09-18 gs             # atteso: OK 3
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-09-22 ac             # atteso: OK 42
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-09-22 gs             # atteso: OK 3
tools/bottega/process-session.sh _bottega/img/mario-bertoncini/2025-10-29-riconsegna ac  # atteso: OK 84
```

Note: `2025-06-19-prelievo/ac/mov/` e i 22 `.mov` loose in `2025-09-22/ac` restano dove sono (archivio, esclusi dal sito). Verificare col Read di un edit mdg che il watermark riporti "Marco Di Gasbarro".

- [ ] **Step 2: Hero e thumbnail** (foto orizzontale d'insieme degli strumenti):

```bash
python3 tools/bottega/make-hero.py _bottega/img/mario-bertoncini/<SESSIONE>/<SIGLA>/edit/<FOTO-SCELTA>.jpg _bottega/img/mario-bertoncini
```

- [ ] **Step 3: Scrivere `_bottega/web/mario-bertoncini.md` e rimuovere il placeholder**

```markdown
---
title: "Mario Bertoncini"
date: 2025-10-29
image:
  path: bottega/img/mario-bertoncini/mario-bertoncini-hero.jpg
  thumbnail: bottega/img/mario-bertoncini/mario-bertoncini-t.jpg
  caption: ""
---

La conservazione e il restauro degli strumenti della collezione Mario
Bertoncini, dal prelievo alla riconsegna. Ogni intervento è documentato da un
fascicolo: i PDF in coda al diario.

<!--more-->

## 19 giugno 2025 — prelievo

{% include gallery path="bottega/img/mario-bertoncini/2025-06-19-prelievo/ac/" %}

{% include gallery path="bottega/img/mario-bertoncini/2025-06-19-prelievo/gs/" %}

{% include gallery path="bottega/img/mario-bertoncini/2025-06-19-prelievo/mdg/" %}

## 31 luglio 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-07-31/ac/" %}

{% include gallery path="bottega/img/mario-bertoncini/2025-07-31/gs/" %}

## 8 agosto 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-08-08/ac/" %}

## 12 agosto 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-08-12/ac/" %}

## 13 agosto 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-08-13/ac/" %}

## 18 agosto 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-08-18/ac/" %}

## 4 settembre 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-09-04/ac/" %}

## 18 settembre 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-09-18/ac/" %}

{% include gallery path="bottega/img/mario-bertoncini/2025-09-18/gs/" %}

## 22 settembre 2025

{% include gallery path="bottega/img/mario-bertoncini/2025-09-22/ac/" %}

{% include gallery path="bottega/img/mario-bertoncini/2025-09-22/gs/" %}

## 29 ottobre 2025 — riconsegna

{% include gallery path="bottega/img/mario-bertoncini/2025-10-29-riconsegna/ac/" %}

## Fascicoli d'intervento

### [MB-1980-01 · Grande Spirale]({{ 'bottega/src/interventi/mb/mb-1980-01-grande-spirale/fascicolo/mb-1980-01-grande-spirale.pdf' | absolute_url }}){: target="_blank" }

### [MB-1980-02 · Kathedrale]({{ 'bottega/src/interventi/mb/mb-1980-02-kathedrale/fascicolo/mb-1980-02-kathedrale.pdf' | absolute_url }}){: target="_blank" }

### [MB-1980-03 · Arpa circolare]({{ 'bottega/src/interventi/mb/mb-1980-03-arpa-circolare/fascicolo/mb-1980-03-arpa-circolare.pdf' | absolute_url }}){: target="_blank" }

### [MB-1990-01 · Violino I]({{ 'bottega/src/interventi/mb/mb-1990-01-violino-I/fascicolo/mb-1990-01-violino-I.pdf' | absolute_url }}){: target="_blank" }

### [MB-1990-02 · Violino II]({{ 'bottega/src/interventi/mb/mb-1990-02-violino-II/fascicolo/mb-1990-02-violino-II.pdf' | absolute_url }}){: target="_blank" }

### [MB-1990-03 · Viola]({{ 'bottega/src/interventi/mb/mb-1990-03-viola/fascicolo/mb-1990-03-viola.pdf' | absolute_url }}){: target="_blank" }

### [MB-1990-04 · Violoncello]({{ 'bottega/src/interventi/mb/mb-1990-04-violoncello/fascicolo/mb-1990-04-violoncello.pdf' | absolute_url }}){: target="_blank" }
```

```bash
cd _bottega && git rm web/mb.md img/mb.jpg && cd ..
```

- [ ] **Step 4: Build locale e verifica (gallerie + PDF serviti + vecchio URL sparito)**

```bash
bundle exec jekyll build 2>&1 | tail -3
grep -c "2025-06-19-prelievo/mdg/thumb" _site/bottega/mario-bertoncini/index.html            # atteso: 21
grep -c "2025-10-29-riconsegna/ac/thumb" _site/bottega/mario-bertoncini/index.html           # atteso: 84
ls "_site/bottega/src/interventi/mb/mb-1980-01-grande-spirale/fascicolo/mb-1980-01-grande-spirale.pdf"  # atteso: esiste
ls _site/bottega/mb 2>&1                                                                      # atteso: No such file
```

- [ ] **Step 5: Commit `_bottega`, push, bump, verifica online**

Commit ~1 GB: se il push fallisse per dimensione, spezzare per gruppi di
sessioni. Il `git rm` dello Step 3 ha già staged le rimozioni di `mb.md` e
`img/mb.jpg`.

```bash
find _bottega/img/mario-bertoncini -name ".DS_Store" -delete
cd _bottega && git add img/mario-bertoncini web/mario-bertoncini.md && git commit -m "$(cat <<'EOF'
bottega web: Mario Bertoncini, 11 sessioni giu-ott 2025 (prelievo->riconsegna)

292 foto (ac+gs+mdg, 17 HEIC convertite con originali in raw/) in
org/edit/thumb, edit watermarked. Link ai 7 fascicoli PDF.
Sostituisce il placeholder mb.md (URL: /bottega/mario-bertoncini/).
Hero: <FOTO-SCELTA>.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega && git commit -m "$(cat <<'EOF'
bump _bottega: Mario Bertoncini

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
sleep 120 && curl -s -o /dev/null -w "%{http_code}\n" https://l-e-a-p.github.io/bottega/mario-bertoncini/   # atteso: 200
curl -s -o /dev/null -w "%{http_code}\n" "https://l-e-a-p.github.io/bottega/src/interventi/mb/mb-1980-02-kathedrale/fascicolo/mb-1980-02-kathedrale.pdf"   # atteso: 200
```

---

### Task 9: Chiusura — documentazione e misura finale

**Files:**
- Modify: `_bottega/CLAUDE.md` (nuova sezione web)
- Modify: `CLAUDE.md` (repo principale: sigle datate)

**Interfaces:**
- Consumes: tutto quanto sopra pubblicato.

- [ ] **Step 1: Aggiungere a `_bottega/CLAUDE.md` la sezione web** (in coda al file):

```markdown
## Web (bottega sul sito)

Le pagine del sito vivono in `web/` (collezione Jekyll `bottega` del repo
principale, layout `project`, griglia in `/bottega/` ordinata per `date:`
decrescente). Un post per progetto, stesso slug della cartella immagini.

Immagini in `img/<progetto>/<YYYY-MM-DD[-slug]>/<sigla>/{org,edit,thumb}/`
(convenzione LEAP, stessi nomi file nelle tre cartelle) più:

- `img/<progetto>/<progetto>-hero.jpg` (1600×800) e `<progetto>-t.jpg`
  (800×800): hero e thumbnail del post (`tools/bottega/make-hero.py`).
- `raw/` dentro una cartella-sigla: originali non processati (HEIC
  pre-conversione, foto in attesa di selezione). In git, MAI pubblicati.
- `org/`, `raw/`, `*.mov`, `*.heic` sono esclusi dal sito via `exclude:`
  nel `_config.yml` del repo principale.

Pipeline per sessione (dal repo principale):

    tools/bottega/process-session.sh _bottega/img/<progetto>/<sessione> <sigla>

(converte HEIC con originali in raw/, organizza org/edit/thumb, elimina i
loose, watermarka edit/). `date:` del post = ultima sessione pubblicata.
Sessioni nel post in ordine cronologico; un include gallery per
cartella-sigla (il match thumb/ non è ricorsivo).
```

- [ ] **Step 2: Correggere la sezione sigle nel `CLAUDE.md` principale**

Sostituire le righe della sezione "## Sigle fotografo":

```markdown
## Sigle fotografo
La fonte di verità è `tools/watermark/photographers.yml` (ac, dt, gs, lz,
mdg, grdm, ff, pc, ml, sla, sl, …). Mai duplicare o invertire sigle
esistenti; le nuove ricorrenti si aggiungono lì.
```

- [ ] **Step 3: Misura finale del sito**

```bash
bundle exec jekyll build 2>&1 | tail -3
du -sh _site        # atteso: < 1 GB
find _site -type d \( -name org -o -name raw \) | wc -l   # atteso: 0
for p in tbdc-citera flux-ferracuti upu-ads luccello anapnoe-somafonico-petalonio stoned mario-bertoncini; do
  curl -s -o /dev/null -w "%{http_code} $p\n" "https://l-e-a-p.github.io/bottega/$p/"
done   # atteso: 200 per tutti e 7
```

- [ ] **Step 4: Commit finale**

```bash
cd _bottega && git add CLAUDE.md && git commit -m "$(cat <<'EOF'
CLAUDE.md: documentate le convenzioni web della bottega

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push && cd ..
git add _bottega CLAUDE.md && git commit -m "$(cat <<'EOF'
CLAUDE.md: sigle fotografo -> photographers.yml; bump _bottega (doc)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SxDAP4S5YhE8RSUeCYRWue
EOF
)" && git push
```

---

## Fuori scope (dal design, non in questo piano)

Video su YouTube + embed · `interfantasia-ferracuti` (attende materiali) · selezione fine di STONED (Alice) · testi curati dei post (Alice, man mano).
