# Repo `_dapdi` (domeniche come submodule) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estrarre la collezione `domeniche` dal repo principale in un repo dedicato `_dapdi` (git submodule) con la tassonomia asset di `_archi-di-pietra`, preservando gli URL `/domeniche/`, e versarci la prima galleria (DAPDI-III).

**Architecture:** Nuovo repo `L-E-A-P/_dapdi` agganciato come submodule a `l-e-a-p.github.io`. Pagine markdown alla radice del submodule (URL invariati); asset in `img/<evento>/<sigla>/{org,edit,thumb}`, `src/`, `doc/`. La collezione Jekyll viene rinominata `domeniche`→`dapdi` (vincolo cartella=`_<chiave>`) con `permalink: /domeniche/:path/` per tenere gli URL pubblici. Il motore gallerie del tema è già source-agnostic e non si tocca.

**Tech Stack:** Jekyll / github-pages (remote_theme `L-E-A-P/so-leap-theme`), git submodule, `gh` CLI, `sips` (resize immagini su macOS), bash.

**Riferimenti:** spec `docs/superpowers/specs/2026-06-04-dapdi-repo-design.md`. Tutti i path sono relativi a `~/Documents/github/leap/` salvo diversa indicazione.

**Verifica:** la build autorevole è GitHub Pages + `curl` degli URL live. In locale `jekyll serve` NON riflette (tema remoto, submodule non inizializzati). Comando di monitoraggio build:
```bash
gh api repos/L-E-A-P/l-e-a-p.github.io/pages/builds/latest --jq '{status,error:.error.message,commit}'
```

---

### Task 1: Creare il repo remoto `L-E-A-P/_dapdi` (azione esterna, conferma utente)

**Files:** nessuno (operazione remota).

- [ ] **Step 1: Confermare con l'utente** la creazione del repo GitHub `L-E-A-P/_dapdi` (azione outward irreversibile). Procedere solo con ok esplicito.

- [ ] **Step 2: Creare il repo vuoto privato/pubblico coerente con gli altri**

Run:
```bash
gh repo create L-E-A-P/_dapdi --private --description "Domeniche Alla Periferia Dell'Impero — contenuti e gallerie (submodule di l-e-a-p.github.io)"
```
Expected: `✓ Created repository L-E-A-P/_dapdi on GitHub`. (Usare `--public` se gli altri content-repo sono pubblici: verificare prima con `gh repo view L-E-A-P/_archi-di-pietra --json visibility -q .visibility` e allineare.)

- [ ] **Step 3: Verificare visibilità coerente con `_archi-di-pietra`**

Run: `gh repo view L-E-A-P/_archi-di-pietra --json visibility -q .visibility && gh repo view L-E-A-P/_dapdi --json visibility -q .visibility`
Expected: le due visibilità coincidono. Se no, `gh repo edit L-E-A-P/_dapdi --visibility <match>`.

---

### Task 2: Scaffolding del repo `_dapdi` in locale

**Files:**
- Create: `_dapdi/.git` (init)
- Create: `_dapdi/README.md`, `_dapdi/LICENSE`, `_dapdi/.gitignore`, `_dapdi/CLAUDE.md`
- Create dirs: `_dapdi/img/`, `_dapdi/src/`, `_dapdi/doc/`, `_dapdi/bin/`

- [ ] **Step 1: Inizializzare il repo e le cartelle**

Run:
```bash
cd ~/Documents/github/leap
mkdir -p _dapdi/{img,src,doc,bin}
cd _dapdi && git init -b main
```
Expected: `Initialized empty Git repository in .../_dapdi/.git/`.

- [ ] **Step 2: Copiare `.gitignore` e `LICENSE` da `_archi-di-pietra` (stessa convenzione)**

Run:
```bash
cd ~/Documents/github/leap
cp _archi-di-pietra/.gitignore _dapdi/.gitignore
cp _archi-di-pietra/LICENSE _dapdi/LICENSE
```
Expected: nessun output (file copiati).

- [ ] **Step 3: Scrivere `_dapdi/README.md`**

```markdown
# _dapdi

Contenuti e gallerie fotografiche di **Domeniche Alla Periferia Dell'Impero** (DAPDI),
collezione del sito [leaphz.net](https://www.leaphz.net/domeniche/).

Agganciato come git submodule a `L-E-A-P/l-e-a-p.github.io` (collezione Jekyll `dapdi`,
URL pubblici `/domeniche/...`). Struttura asset ereditata da `_archi-di-pietra`.

Vedi `CLAUDE.md` per la convenzione delle immagini e `bin/import-domenica.sh` per importare una galleria.
```

- [ ] **Step 4: Scrivere `_dapdi/CLAUDE.md`** (adattato da `_archi-di-pietra/CLAUDE.md`)

```markdown
# Convenzione immagini gallerie (repo `_dapdi`)

Le immagini delle gallerie sono organizzate **sempre** con questa struttura, una cartella per **fotografo** identificato dalla sua sigla:

```
img/EVENTO/<sigla-fotografo>/org/    foto originali scattate (full-res) — NON pubblicate, sorgente
img/EVENTO/<sigla-fotografo>/edit/   resize alleggerite, CON logo + nome del fotografo — aperte nel lightbox
img/EVENTO/<sigla-fotografo>/thumb/  miniature mostrate nella griglia
```

`org/`, `edit/`, `thumb/` contengono gli **stessi nomi file**. Questa struttura deve valere SEMPRE.
Convenzione `EVENTO`: `AAAA-MM-GG-dapdi-<n-romano>` (es. `2024-03-24-dapdi-iii`).

## Sigle fotografo
- `ac` = Alice Cortegiani
- `dt` = Davide Tedesco
- altre sigle in uso nei repo LEAP: `gmd`, `lz`, `gs`
- nome esteso da normalizzare a sigla: `marco-iacobucci`

## Import di una galleria
Usare lo script (resize via `sips`):

```bash
bin/import-domenica.sh <cartella-originali> <evento> <sigla>
# es: bin/import-domenica.sh ~/Downloads/3a-domenica 2024-03-24-dapdi-iii ac
```
Genera `img/<evento>/<sigla>/{org,edit,thumb}` e stampa la riga `{% include gallery %}` da incollare nella pagina.

## Pagine e URL
Le pagine markdown stanno alla **radice** del repo (`001-prima-domenica.md`, ...): URL `/domeniche/<slug>/`.
Il motore del tema (`so-leap-theme/_includes/gallery`) prende le miniature da `thumb/` e le immagini complete del lightbox da `edit/`. Le immagini di questo repo vivono nella **collezione** (`site.collections[].files`); path include `dapdi/img/...`.

## TODO futuro
Watermark automatico (logo + nome fotografo) sulle immagini in `edit/`, rigenerandole da `org/`.
```

- [ ] **Step 5: Commit dello scaffold**

Run:
```bash
cd ~/Documents/github/leap/_dapdi
git add -A && git commit -m "scaffold: struttura repo _dapdi (asset archi + CLAUDE.md)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: commit creato con README, LICENSE, .gitignore, CLAUDE.md.

---

### Task 3: Script `bin/import-domenica.sh`

**Files:**
- Create: `_dapdi/bin/import-domenica.sh`

- [ ] **Step 1: Scrivere lo script**

```bash
#!/usr/bin/env bash
# Importa una galleria domenica nella convenzione org/edit/thumb.
# Uso: import-domenica.sh <cartella-originali> <evento> <sigla>
#   es: import-domenica.sh ~/Downloads/3a-domenica 2024-03-24-dapdi-iii ac
# Genera img/<evento>/<sigla>/{org,edit,thumb} con stessi nomi file
#   org   = originali rinominati <evento>-NN.<ext>
#   edit  = resize altezza 1080 (watermark in un passo successivo)
#   thumb = 400x300 (cover-crop, assume sorgenti landscape)
set -euo pipefail

SRC="${1:?serve la cartella degli originali}"
EVENTO="${2:?serve lo slug evento, es 2024-03-24-dapdi-iii}"
SIGLA="${3:?serve la sigla fotografo, es ac}"

# La radice del repo = cartella padre di bin/
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/img/$EVENTO/$SIGLA"
mkdir -p "$DEST/org" "$DEST/edit" "$DEST/thumb"

# Raccoglie gli originali (jpg/jpeg/png), ordinati, e li rinomina <evento>-NN.<ext>
i=0
find "$SRC" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) \
  | sort | while IFS= read -r f; do
    i=$((i+1))
    n=$(printf '%02d' "$i")
    ext="$(echo "${f##*.}" | tr '[:upper:]' '[:lower:]')"
    name="$EVENTO-$n.$ext"
    cp "$f" "$DEST/org/$name"
    # edit: altezza 1080
    sips --resampleHeight 1080 "$DEST/org/$name" --out "$DEST/edit/$name" >/dev/null
    # thumb: 400x300 cover-crop (resample a h=300 -> w>=400 per landscape, poi crop centrato)
    sips --resampleHeight 300 "$DEST/edit/$name" --out "$DEST/thumb/$name" >/dev/null
    sips -c 300 400 "$DEST/thumb/$name" --out "$DEST/thumb/$name" >/dev/null
    echo "  $name"
done

echo
echo "Fatto. Incolla nella pagina:"
echo "{% include gallery path=\"dapdi/img/$EVENTO/$SIGLA/\" %}"
```

- [ ] **Step 2: Renderlo eseguibile**

Run: `chmod +x ~/Documents/github/leap/_dapdi/bin/import-domenica.sh`
Expected: nessun output.

- [ ] **Step 3: Verifica sintassi (no esecuzione)**

Run: `bash -n ~/Documents/github/leap/_dapdi/bin/import-domenica.sh && echo OK`
Expected: `OK`.

- [ ] **Step 4: Commit**

Run:
```bash
cd ~/Documents/github/leap/_dapdi
git add bin/import-domenica.sh && git commit -m "feat: script import-domenica (org/edit/thumb via sips)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Migrare le 5 pagine `_domeniche` → `_dapdi` (radice)

**Files:**
- Create: `_dapdi/00N-*.md` (5 file)
- (rimozione di `l-e-a-p.github.io/_domeniche/` avviene in Task 7)

- [ ] **Step 1: Copiare i 5 markdown nella radice del submodule**

Run:
```bash
cd ~/Documents/github/leap
cp l-e-a-p.github.io/_domeniche/00*.md _dapdi/
ls _dapdi/*.md
```
Expected: elenca `001-prima-domenica.md … 005-quinta-domenica.md`.

- [ ] **Step 2: Verificare che il front-matter NON contenga path dipendenti dalla vecchia posizione**

Run: `grep -nE 'image:|path:|src/' ~/Documents/github/leap/_dapdi/*.md`
Expected: i riferimenti immagine sono del tipo `images/...` (risolti dal repo principale via `absolute_url`) — vanno lasciati invariati. Se compaiono path relativi a `_domeniche/`, segnalarli (non previsti).

- [ ] **Step 3: Commit**

Run:
```bash
cd ~/Documents/github/leap/_dapdi
git add 00*.md && git commit -m "content: migra le 5 pagine domeniche dal repo principale

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Importare la galleria DAPDI-III (caso parziale: org+edit già esistono)

**Files:**
- Create: `_dapdi/img/2024-03-24-dapdi-iii/ac/{org,edit,thumb}/`
- Modify: `_dapdi/003-terza-domenica.md` (aggiunta include gallery)

Sorgente: `l-e-a-p.github.io/images/posts/2024-03-24-DAPDI-III/` ha già `org/` ed `edit/` (26 foto `2024-03-24-dapdi3-NN.jpg`), manca `thumb/`.

- [ ] **Step 1: Spostare org/ ed edit/ nella struttura `_dapdi` sotto `ac/`**

Run:
```bash
cd ~/Documents/github/leap
SRC=l-e-a-p.github.io/images/posts/2024-03-24-DAPDI-III
DEST=_dapdi/img/2024-03-24-dapdi-iii/ac
mkdir -p "$DEST"
# git mv nel repo PRINCIPALE non serve: i file passano a un altro repo. Copia + rimozione dal main in Task 7.
cp -R "$SRC/org" "$DEST/org"
cp -R "$SRC/edit" "$DEST/edit"
mkdir -p "$DEST/thumb"
ls "$DEST/edit" | wc -l
```
Expected: `26`.

- [ ] **Step 2: Generare le thumb 400x300 dalle edit esistenti**

Run:
```bash
cd ~/Documents/github/leap/_dapdi/img/2024-03-24-dapdi-iii/ac
for f in edit/*.jpg; do
  b="$(basename "$f")"
  sips --resampleHeight 300 "$f" --out "thumb/$b" >/dev/null
  sips -c 300 400 "thumb/$b" --out "thumb/$b" >/dev/null
done
ls thumb | wc -l
```
Expected: `26`.

- [ ] **Step 3: Verificare le dimensioni generate (thumb 400x300, edit altezza 1080)**

Run:
```bash
cd ~/Documents/github/leap/_dapdi/img/2024-03-24-dapdi-iii/ac
sips -g pixelWidth -g pixelHeight thumb/2024-03-24-dapdi3-01.jpg | awk '/pixel/{print $2}'
sips -g pixelHeight edit/2024-03-24-dapdi3-01.jpg | awk '/pixel/{print $2}'
```
Expected: thumb `400` poi `300`; edit altezza `1080` (se le edit esistenti fossero a un'altezza diversa, annotarlo — restano comunque valide per il lightbox).

- [ ] **Step 4: Aggiungere l'include alla pagina terza domenica**

Aggiungere in fondo a `~/Documents/github/leap/_dapdi/003-terza-domenica.md`:
```liquid

{% include gallery path="dapdi/img/2024-03-24-dapdi-iii/ac/" %}
```

- [ ] **Step 5: Commit**

Run:
```bash
cd ~/Documents/github/leap/_dapdi
git add img/2024-03-24-dapdi-iii 003-terza-domenica.md
git commit -m "gallery: DAPDI-III (terza domenica) — org/edit/thumb sotto ac/

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Push del repo `_dapdi` e collegamento del remote

**Files:** nessuno locale.

- [ ] **Step 1: Collegare il remote e pushare**

Run:
```bash
cd ~/Documents/github/leap/_dapdi
git remote add origin git@github.com:L-E-A-P/_dapdi.git
git push -u origin main
```
Expected: branch `main` pushato su `origin`.

- [ ] **Step 2: Verificare lo SHA remoto (servirà per il bump submodule)**

Run: `cd ~/Documents/github/leap/_dapdi && git rev-parse HEAD`
Expected: stampa lo SHA del commit di testa (annotarlo come `<DAPDI_SHA>`).

---

### Task 7: Cablare il submodule e la collezione nel repo principale

**Files:**
- Modify: `l-e-a-p.github.io/.gitmodules`
- Modify: `l-e-a-p.github.io/_config.yml` (blocco collezione + defaults)
- Modify: `l-e-a-p.github.io/domeniche.md` (`collection: dapdi`)
- Delete: `l-e-a-p.github.io/_domeniche/` (5 .md migrati)
- Create (gitlink): `l-e-a-p.github.io/_dapdi`

- [ ] **Step 1: Aggiungere il submodule**

Run:
```bash
cd ~/Documents/github/leap/l-e-a-p.github.io
git submodule add git@github.com:L-E-A-P/_dapdi.git _dapdi
```
Expected: clona `_dapdi` e aggiorna `.gitmodules`. (Se il path `_dapdi` esiste già perché il repo locale è lì, usare invece: `git submodule add git@github.com:L-E-A-P/_dapdi.git _dapdi` dopo aver spostato il repo locale, oppure aggiungere a mano la voce in `.gitmodules` e `git submodule absorbgitdirs`. Verificare lo stato con `git submodule status`.)

- [ ] **Step 2: Rinominare la collezione `domeniche`→`dapdi` con permalink esplicito**

In `l-e-a-p.github.io/_config.yml`, sostituire il blocco:
```yaml
  domeniche:
    output: true
    permalink: /:collection/:path/
```
con:
```yaml
  dapdi:
    output: true
    permalink: /domeniche/:path/
```

- [ ] **Step 3: Aggiornare i `defaults` della collezione**

In `l-e-a-p.github.io/_config.yml`, sostituire:
```yaml
  # Domeniche collection
  - scope:
      path: "_domeniche"
      type: domeniche
    values:
      layout: project
      comments: true
      share: true
      author: LEAP
```
con:
```yaml
  # Domeniche (collezione dapdi, submodule _dapdi)
  - scope:
      path: "_dapdi"
      type: dapdi
    values:
      layout: project
      comments: true
      share: true
      author: LEAP
```

- [ ] **Step 4: Aggiornare la landing `domeniche.md`**

In `l-e-a-p.github.io/domeniche.md`, cambiare la sola riga front-matter:
```yaml
collection: dapdi
```
(era `collection: domeniche`; `permalink: /domeniche/` resta invariato.)

- [ ] **Step 5: Rimuovere la vecchia cartella in-repo**

Run:
```bash
cd ~/Documents/github/leap/l-e-a-p.github.io
git rm -r _domeniche
```
Expected: rimuove i 5 .md (ora vivono nel submodule).

- [ ] **Step 6: Sanity-check locale del config (YAML valido + niente residui `domeniche` come collezione)**

Run:
```bash
cd ~/Documents/github/leap/l-e-a-p.github.io
ruby -ryaml -e 'YAML.load_file("_config.yml"); puts "YAML OK"'
grep -nE '^\s*domeniche:|path: "_domeniche"|type: domeniche|collection: domeniche' _config.yml domeniche.md || echo "nessun residuo"
```
Expected: `YAML OK` e `nessun residuo`.

- [ ] **Step 7: Commit (bump submodule + config + rimozione)**

Run:
```bash
cd ~/Documents/github/leap/l-e-a-p.github.io
git add .gitmodules _dapdi _config.yml domeniche.md
git commit -m "domeniche: collezione in submodule _dapdi (URL /domeniche/ invariati)

- _domeniche (in-repo) -> submodule _dapdi
- collezione 'domeniche' rinominata 'dapdi' con permalink /domeniche/:path/
- defaults e landing aggiornati; vecchia cartella rimossa
- prima galleria: DAPDI-III su terza domenica

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 8: Deploy, build e verifica live

**Files:** nessuno.

- [ ] **Step 1: Push del repo principale (triggera il rebuild Pages)**

Run: `cd ~/Documents/github/leap/l-e-a-p.github.io && git push`
Expected: push su `main`.

- [ ] **Step 2: Monitorare la build fino a `built` sul commit appena pushato**

Run (loop, ~max 6 min):
```bash
cd ~/Documents/github/leap/l-e-a-p.github.io
target=$(git rev-parse HEAD)
for i in $(seq 1 24); do
  out=$(gh api repos/L-E-A-P/l-e-a-p.github.io/pages/builds/latest --jq '{status,error:.error.message,commit}')
  echo "$out"
  c=$(echo "$out" | grep -o '[0-9a-f]\{40\}'); st=$(echo "$out" | grep -o '"status":"[a-z]*"' | grep -o '[a-z]*"$' | tr -d '"')
  [ "$c" = "$target" ] && { [ "$st" = "built" ] || [ "$st" = "errored" ]; } && break
  sleep 15
done
```
Expected: `status` `built`, `error` `null`, `commit` = target.

- [ ] **Step 3: Verificare gli URL pubblici (invarianza + galleria)**

Run:
```bash
for u in / /domeniche/ /domeniche/001-prima-domenica/ /domeniche/003-terza-domenica/ ; do
  printf '%s -> ' "$u"; curl -s -o /dev/null -w '%{http_code}\n' "https://www.leaphz.net$u"
done
curl -s https://www.leaphz.net/domeniche/003-terza-domenica/ | grep -c 'class="gallery'
curl -s https://www.leaphz.net/domeniche/003-terza-domenica/ | grep -o '/dapdi/img/2024-03-24-dapdi-iii/ac/thumb/[^"]*' | head -3
```
Expected: tutti `200`; `grep -c 'class="gallery'` ≥ `1`; elenca alcune URL `/dapdi/img/.../thumb/...`.

- [ ] **Step 4: Verifica visiva manuale (utente)**

Aprire `https://www.leaphz.net/domeniche/003-terza-domenica/` con hard refresh: griglia a 4 colonne, lightbox singola (GLightbox). Controllare che `/domeniche/` (landing) e le altre `/domeniche/00N-*/` rendano come prima.

---

## Self-Review (eseguito)

- **Copertura spec:** sez.1 struttura → Task 2/3; sez.2 cablaggio → Task 7; sez.3 migrazione → Task 4 (+ rimozione Task 7); sez.4 pipeline+DAPDI-III → Task 3/5; sez.5 deploy → Task 1/6/8. Criteri di successo coperti da Task 8.
- **Placeholder:** nessun TODO/TBD nei passi; codice script e diff config completi.
- **Coerenza nomi:** collezione `dapdi`/permalink `/domeniche/:path/`, evento `2024-03-24-dapdi-iii`, sigla `ac`, path include `dapdi/img/2024-03-24-dapdi-iii/ac/` coerenti tra Task 5/7/8.
- **Rischio noto (Task 7 Step 1):** `git submodule add` può confliggere col repo locale `_dapdi` già presente nella cartella padre `leap/` (che NON è il repo principale). Il submodule va dentro `l-e-a-p.github.io/_dapdi`, path distinto da `leap/_dapdi`. Se si preferisce evitare due copie, in esecuzione si può spostare il repo locale dentro il main repo prima dell'add. Da decidere in fase di esecuzione.
