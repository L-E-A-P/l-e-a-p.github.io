# Guida per i contributori — LEAP / Bottega Radicale

Questa guida accompagna passo dopo passo chi contribuisce ai repo del sito
[www.leaphz.net](https://www.leaphz.net), in particolare ai progetti di
**Bottega Radicale** (`/bottega/`). È pensata per non dare nulla per
scontato: se un passaggio non ti torna, è la guida che va corretta —
segnalalo.

Documenti di dettaglio a cui questa guida rimanda:

- [`tools/bottega/README.md`](tools/bottega/README.md) — gli script della pipeline bottega
- [`tools/organize/README.md`](tools/organize/README.md) e [`tools/watermark/README.md`](tools/watermark/README.md) — i due attrezzi di base
- [`_bottega/CLAUDE.md`](https://github.com/L-E-A-P/_bottega/blob/main/CLAUDE.md) — convenzioni complete della bottega (sezione «Web»)

---

## 1. Com'è fatto il sito (architettura)

- **Repo principale**: `l-e-a-p.github.io` — il sito Jekyll, pubblicato con
  **GitHub Pages build legacy**: Jekyll gira sui server di GitHub a ogni
  push sul repo principale. Non serve (e non si usa) Jekyll in locale.
- **Submodule** (repo separati, agganciati al principale):
  - `_bottega` — progetti di Bottega Radicale (immagini + post + LaTeX)
  - `_lazzaro`, `_archi-di-pietra`, `_domeniche` — le altre collezioni
- **Regola d'oro dei submodule**: un push dentro un submodule **da solo NON
  muove il sito**. Il sito si muove solo quando il repo principale aggiorna
  il *puntatore* al submodule (il «bump», § 7).

## 2. Primo setup

Requisiti: `git`, `python3` con Pillow e PyYAML, e su macOS `sips` (già di
sistema, serve per gli HEIC). Facoltativo ma comodo: `gh` (GitHub CLI)
autenticato, per controllare le build.

```bash
# clona TUTTO, submodule inclusi
git clone --recurse-submodules git@github.com:L-E-A-P/l-e-a-p.github.io.git
cd l-e-a-p.github.io

# se avevi già clonato senza submodule:
git submodule update --init --recursive

# dipendenze python
pip3 install --user Pillow pyyaml
```

## 3. Tenersi allineati (ogni volta che riprendi il lavoro)

I submodule appena clonati o aggiornati sono in *detached HEAD*: prima di
lavorarci **mettiti sul branch `main`**.

```bash
# nel repo principale
git pull

# nel submodule dove lavorerai (es. _bottega)
cd _bottega
git checkout main
git pull
cd ..
```

Se `git status` nel repo principale mostra `modified: _bottega (new
commits)` che **non hai fatto tu**, probabilmente il tuo submodule è
avanti o indietro rispetto al puntatore: riallineati con i comandi sopra
prima di iniziare.

## 4. Convenzioni della bottega

### Struttura delle cartelle

```
_bottega/img/<progetto>/<YYYY-MM-DD[-slug]>/<sigla>/
    (foto originali sciolte — prima del processamento)
    org/     originali rinominati (full-res) — in git, MAI pubblicati
    edit/    versioni web (h 1080) CON watermark — quelle del lightbox
    thumb/   miniature (lato lungo 400) — quelle della griglia
    raw/     archivio non pubblicato (HEIC originali, foto sfinite)
```

### Naming

- **Progetto**: `<nome>-<cognome-artista>` tutto minuscolo
  (es. `thin-branchi`, `mop-citera`). Il titolo pubblico va nel post, lo
  slug resta tecnico.
- **Sessione**: `YYYY-MM-DD`, con eventuale slug descrittivo in coda
  (es. `2022-09-28-epitaffio-mb-fis`). Una cartella per data.
- **Sigla fotografo**: la tua cartella dentro la sessione (es. `ac/`,
  `dt/`). La fonte di verità è `tools/watermark/photographers.yml`:
  se la tua sigla non c'è ancora, **chiedila/aggiungila lì** — mai
  duplicare o invertire sigle esistenti. I contributori occasionali
  possono usare una cartella `nome-cognome/` (viene normalizzata da sola).
- **Numerazione foto**: la fa la pipeline (`<sessione>-NN`). I numeri sono
  identificatori stabili: **mai rinumerare**, i buchi sono ok.

### Cosa NON fare

- Non committare file **> 100 MB**: GitHub li rifiuta (errore GH001).
  I video oltre soglia restano in archivio locale e si aggiungono a
  `.gitignore` con una nota.
- Non pubblicare video: i `.mov` restano in git come archivio (sono
  esclusi dal sito) in attesa del canale video.
- Non toccare `org/` e `raw/` a mano: sono l'archivio.
- Non rinominare/rinumerare foto già pubblicate: gli URL devono restare
  stabili.
- `.DS_Store` è già gitignorato: se lo vedi in `git status`, qualcosa non
  va.

## 5. Aprire un nuovo progetto (passo dopo passo)

1. **Prepara le cartelle** con le foto originali sciolte:

   ```
   _bottega/img/<progetto>/<YYYY-MM-DD>/<tua-sigla>/*.jpg|*.heic
   ```

2. **Processa ogni coppia sessione/sigla** (dal repo principale):

   ```bash
   tools/bottega/process-session.sh _bottega/img/<progetto>/<sessione> <sigla>
   ```

   Fa tutto lui: HEIC→jpg (originali in `raw/`), rinomina e genera
   `org/edit/thumb`, verifica i conteggi, elimina i sorgenti sciolti,
   applica il watermark. Se `org/` esiste già si rifiuta: è il segno che
   quella sessione è già stata processata (vedi § 6.2 per aggiungere foto).

3. **Genera hero e thumbnail del progetto** da una foto scelta (meglio se
   orizzontale, sorgente in `org/`):

   ```bash
   python3 tools/bottega/make-hero.py \
     _bottega/img/<progetto>/<sessione>/<sigla>/org/<foto>.jpg \
     _bottega/img/<progetto>
   ```

4. **Scrivi il post** in `_bottega/web/<progetto>.md` (stesso slug della
   cartella immagini). Modello:

   ```markdown
   ---
   title: "Titolo Pubblico del Progetto"
   date: YYYY-MM-DD          # = data dell'ULTIMA sessione pubblicata
   image:
     path: bottega/img/<progetto>/<progetto>-hero.jpg
     thumbnail: bottega/img/<progetto>/<progetto>-t.jpg
     caption: ""
   ---

   Una riga di introduzione (artista, contesto, periodo).

   <!--more-->

   ## 12 febbraio 2024

   {% include gallery path="bottega/img/<progetto>/2024-02-12/<sigla>/" %}
   ```

   Regole: sessioni in **ordine cronologico**; un heading `##` per data;
   **un include per cartella-sigla** (il match di `thumb/` non è
   ricorsivo: un include non può coprire due sigle); la `date:` del
   front-matter governa l'ordinamento della griglia `/bottega/` e **non
   deve mai essere nel futuro** (occhio a non invertire giorno e mese:
   una data futura fa sparire la pagina con un 404 — vedi § 7).

5. **Pubblica** (§ 7).

## 6. Contribuire a un progetto esistente

### 6.1 Nuova sessione

Come § 5 punti 1–2, poi nel post: aggiungi heading + include nella
posizione cronologica giusta e, **se la sessione è la più recente**,
aggiorna la `date:` del front-matter (il progetto risale in griglia).

### 6.2 Aggiungere foto a una sessione già processata

`process-session.sh` si rifiuterà (org/ esiste). Percorso chirurgico:

```bash
# 1. se hai HEIC: convertili e archivia gli originali
sips -s format jpeg -s formatOptions best FOTO.heic --out FOTO.jpg
mkdir -p <sessione>/<sigla>/raw && mv FOTO.heic <sessione>/<sigla>/raw/

# 2. guarda l'ultimo numero esistente in org/ e riparti dal successivo
ls _bottega/img/<progetto>/<sessione>/<sigla>/org/ | tail -1
python3 tools/organize/organize.py \
  _bottega/img/<progetto>/<sessione>/<sigla> \
  _bottega/img/<progetto>/<sessione> <sigla> --start <ultimo+1>

# 3. elimina i sorgenti sciolti ormai copiati in org/
# 4. watermark SOLO sulle foto nuove: spostale in una cartella
#    temporanea, watermarka lì, riportale in edit/
mkdir /tmp/wm && mv .../edit/<sessione>-06.jpg /tmp/wm/
python3 tools/watermark/watermark.py /tmp/wm -n "Nome Cognome" --in-place
mv /tmp/wm/*.jpg .../edit/ && rmdir /tmp/wm
```

Attenzione: `--start` non deve mai riusare numeri esistenti **né numeri
finiti in `raw/`** con lo sfinimento (guarda anche lì).
Le foto già pubblicate non si toccano.

### 6.3 Togliere o ripescare foto pubblicate (sfinimento)

```bash
tools/bottega/cull.sh    _bottega/img/<progetto>/<sessione> <sigla> NN [NN ...]
tools/bottega/restore.sh _bottega/img/<progetto>/<sessione> <sigla> NN [NN ...]
```

Metodo *demote, non delete*: `cull.sh` sposta gli org in `raw/` (nulla si
perde) ed elimina edit+thumb; `restore.sh` è l'inverso esatto, stesso
numero. Mai cancellare a mano da `edit/`: se succede, va completato il
demote (org→raw, via il thumb) per ripristinare l'invariante.

## 7. Pubblicare: commit → push → bump → build

Il giro completo, **nell'ordine**. Conviene raggruppare più modifiche in un
solo giro: una build copre tutto.

```bash
# A. commit e push NEL SUBMODULE
cd _bottega
git status          # controlla: solo i file che ti aspetti
git add -A
git commit -m "Nuovo progetto: <titolo> (N foto, sessioni ...)"
git push

# B. bump del puntatore NEL REPO PRINCIPALE
cd ..
git add _bottega
git commit -m "bump _bottega: <cosa è cambiato>"
git push
```

Il push del repo principale fa partire la build di GitHub Pages (~5 min).

**Controllare la build** (serve `gh` autenticato):

```bash
gh api repos/l-e-a-p/l-e-a-p.github.io/pages/builds/latest   # stato
gh api -X POST repos/l-e-a-p/l-e-a-p.github.io/pages/builds  # rebuild forzata
```

Problemi noti e rimedi:

- **La build non parte** dopo il push del bump (capita), oppure resta
  `building` per più di 10 minuti: **rebuild forzata** (comando sopra),
  risolve sempre.
- `Deployment failed, try again later` nelle Actions: transitorio lato
  GitHub, non è colpa dei contenuti — un nuovo push o la rebuild lo supera.
- **La CDN cachea ~10 minuti**: se non vedi le modifiche (o vedi ancora
  foto tolte), aggiungi `?v=<numero-qualsiasi>` all'URL per verificare.
  Non è un errore.
- **Il progetto appare in griglia `/bottega/` ma la sua pagina dà 404**
  (mentre le immagini nuove rispondono): quasi sempre la `date:` del
  front-matter è **nel futuro** — tipicamente giorno e mese invertiti
  (es. `2026-08-07` scritto al posto di `2026-07-08`). GitHub Pages builda
  con `future: false`: il documento viene elencato in griglia ma la sua
  pagina non viene scritta. Non è un problema di submodule o di build.
  Rimedio: correggi la `date:` (= ultima sessione pubblicata, mai futura)
  e rifai il giro del § 7 (commit nel submodule → push → bump → push).

**Verifica finale** sul sito vivo: la pagina del progetto risponde
(`https://www.leaphz.net/bottega/web/<progetto>/`), le foto nuove ci sono,
la griglia `/bottega/` mostra il progetto nella posizione attesa.

## 8. Checklist prima del push

- [ ] `git status` nel submodule: solo file attesi (niente `.DS_Store`,
      niente file sciolti dimenticati, niente >100 MB)
- [ ] ogni galleria toccata rispetta l'invariante **org = edit = thumb**
- [ ] gli `edit/` nuovi hanno il watermark
- [ ] il post ha: heading in ordine cronologico, un include per
      cartella-sigla, `date:` = ultima sessione pubblicata
- [ ] hero e `-t` esistono per i progetti nuovi
- [ ] commit nel submodule **prima**, bump nel principale **dopo**
- [ ] build verde, pagina verificata

---

*Se qualcosa in questa guida non corrisponde a quello che vedi nei repo, la
guida è indietro: apri una issue o correggi qui. Buona bottega!* 🛠️
