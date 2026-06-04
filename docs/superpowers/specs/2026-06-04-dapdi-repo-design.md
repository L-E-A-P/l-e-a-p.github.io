# Design — Repo `_dapdi` per "le domeniche alla periferia dell'impero"

Data: 2026-06-04
Stato: approvato (brainstorming), in attesa di review dello spec scritto.

## Obiettivo

Trasformare la collezione `domeniche` — oggi **dentro** il repo principale `l-e-a-p.github.io` come cartella `_domeniche/` — in un **repo dedicato `_dapdi`** agganciato come git submodule, con la struttura degli asset ereditata da `_archi-di-pietra`, e versarci le foto delle domeniche (su Nextcloud, una cartella alla volta). DAPDI = **D**omeniche **A**lla **P**eriferia **D**ell'**I**mpero.

## Vincoli e decisioni (dal brainstorming)

- **Migrazione completa**: tutto `_domeniche` migra in `_dapdi` (non solo le foto).
- **Cartella `_dapdi`, URL invariati**: il submodule/cartella si chiama `_dapdi`; gli URL pubblici restano `/domeniche/...`. Vincolo Jekyll (cartella = `_<chiave-collezione>`) → la chiave collezione diventa `dapdi`, ma un `permalink` esplicito tiene gli URL su `/domeniche/`.
- **Approccio A — eredita gli asset, pagine alla radice**: si eredita la tassonomia asset di archi (`img/` con `org/edit/thumb` per fotografo, `src/`, `doc/`), ma le pagine markdown restano alla **radice** del submodule (come l'attuale `_domeniche/`), NON in `web/`, per non aggiungere `/web/` agli URL. (Mirror esatto di archi con `web/` scartato: cambierebbe gli URL e richiederebbe redirect.)
- **Foto incrementali**: si costruisce la struttura pronta a ricevere; le cartelle foto arrivano da Nextcloud una alla volta. Prima cartella già su disco: DAPDI-III.
- **Convenzione immagini**: invariata e condivisa con gli altri repo — `EVENTO/<sigla-fotografo>/{org,edit,thumb}`, `org` originali (sorgente, non watermarkati), `edit` resize altezza 1080 con (in futuro) logo+nome, `thumb` 400×300. Watermark automatizzato in un passo successivo.

## 1. Struttura del repo `_dapdi`

Nuovo repo GitHub `L-E-A-P/_dapdi`, agganciato come submodule in `l-e-a-p.github.io`.

```
_dapdi/
  001-prima-domenica.md        # pagine collezione alla RADICE → URL /domeniche/<slug>/ invariati
  002-seconda-domenica.md
  003-terza-domenica.md
  004-quarta-domenica.md
  005-quinta-domenica.md
  img/
    <evento>/<sigla>/org/      # originali da Nextcloud (full-res, sorgente)
    <evento>/<sigla>/edit/     # resize altezza 1080 (watermark in futuro)
    <evento>/<sigla>/thumb/    # 400x300 crop
  src/                          # hero / locandine (come archi)
  doc/                          # PDF programmi/slide (come archi)
  bin/import-domenica.sh        # script org->edit->thumb, riusato a ogni cartella
  CLAUDE.md                     # convenzione immagini (come _lazzaro/_archi-di-pietra)
  .gitignore  LICENSE  README.md
```

Convenzione `<evento>`: `AAAA-MM-GG-dapdi-<n-romano>` (es. `2024-03-24-dapdi-iii`), con sottocartella `<sigla>` del fotografo (es. `ac` = Alice Cortegiani).

## 2. Cablaggio nel sito (`l-e-a-p.github.io`)

**`.gitmodules`** — aggiungere:
```ini
[submodule "_dapdi"]
	path = _dapdi
	url = git@github.com:L-E-A-P/_dapdi.git
```

**`_config.yml`** — la collezione `domeniche` diventa `dapdi`, URL su `/domeniche/` via permalink esplicito:
```yaml
collections:
  dapdi:                          # era: domeniche
    output: true
    permalink: /domeniche/:path/  # era: /:collection/:path/  → preserva /domeniche/

defaults:
  - scope:
      path: "_dapdi"              # era: _domeniche  (pagine alla radice)
      type: dapdi                 # era: domeniche
    values:
      layout: project
      comments: true
      share: true
      author: LEAP
```

**`domeniche.md`** (landing) — unica modifica:
```yaml
collection: dapdi                 # era: domeniche ; permalink /domeniche/ resta invariato
```

**`_data/navigation.yml`** — invariato (`/domeniche/` resta valido).

**`TECHNICAL_REPORT.md`** — aggiornare le citazioni di `_domeniche` (nota documentale, non influisce sul build).

**Rimozione** della cartella in-repo `_domeniche/` dopo la migrazione dei .md.

## 3. Migrazione contenuti

- `git mv` dei 5 file `_domeniche/00N-*.md` → `_dapdi/00N-*.md` (radice del submodule). Front-matter e testo identici, nessuna riscrittura.
- **Riferimenti immagine nei testi** (`images/leviatano-hero.jpg`, `images/vituccif.jpg`): vivono nel repo principale, risolti via `absolute_url`, continuano a funzionare dopo lo spostamento → si lasciano invariati. Spostamento opzionale in `_dapdi/src/` rimandato.
- **Galleria**: l'`{% include gallery path="dapdi/img/<evento>/<sigla>/" %}` si aggiunge a una pagina **solo quando** arrivano le foto di quella domenica (no include vuoti).
- **`_posts/*-domenica.md` fuori scope**: 5 post nel feed (categoria *Saltati*, tag *Workshop*), entità distinta dalle pagine-archivio della collezione. Restano nel repo principale invariati. Eventuale link post→pagina-domenica aggiunto in futuro.

Nota: duplicazione storica (collezione *e* post per gli stessi eventi) lasciata convivere come già per archi/lazzaro — fuori scope la sua risoluzione.

## 4. Pipeline foto (org → edit → thumb)

Script riusabile `bin/import-domenica.sh`, contratto:

```
import-domenica.sh <cartella-originali> <evento> <sigla>
  es: import-domenica.sh ~/Downloads/3a-domenica 2024-03-24-dapdi-iii ac
```

Produce in `_dapdi/img/<evento>/<sigla>/`:

| sottocartella | come | dimensione |
|---|---|---|
| `org/`   | copia gli originali, rinominati `<evento>-NN.jpg` (indice zero-padded, ordine alfabetico) | full-res |
| `edit/`  | da `org/`, `sips --resampleHeight 1080` | altezza 1080 (come archi/lazzaro) |
| `thumb/` | da `edit/`, resize+crop a 400×300 | 400×300 |

Stessi nomi file tra le tre cartelle. Lo script stampa la riga `{% include gallery path=... %}` da incollare nella pagina. Il watermark (logo+nome fotografo) sarà un passo successivo che rigenera solo `edit/` da `org/`.

### Prima cartella: DAPDI-III (caso parziale, già su disco)

`images/posts/2024-03-24-DAPDI-III` (nel main repo) ha già `org/` + `edit/` (26 foto `2024-03-24-dapdi3-NN.jpg`) ma **manca `thumb/`**.

- evento: `2024-03-24-dapdi-iii` — sigla: `ac` (confermati).
- Passi:
  1. spostare `org/` + `edit/` in `_dapdi/img/2024-03-24-dapdi-iii/ac/`
  2. generare `thumb/` dalle `edit/` esistenti (le `edit/` sono già a posto, non si rigenerano)
  3. aggiungere l'include alla pagina `003-terza-domenica.md`

## 5. Integrazione e deploy

Ordine (catena di deploy LEAP: tema → contenuti/submodule → bump nel main → rebuild):

1. **Creare il repo remoto** `L-E-A-P/_dapdi` (`gh repo create`) — azione esterna, da confermare prima.
2. **Costruire `_dapdi`** in locale: struttura (sez. 1), `git mv` dei 5 .md (sez. 3), import DAPDI-III (sez. 4), `CLAUDE.md`. Primo commit + push.
3. **Agganciare il submodule** nel main repo (`git submodule add … _dapdi`), aggiornare `_config.yml` + `domeniche.md` + `.gitmodules` (sez. 2), **rimuovere** `_domeniche/`.
4. **Commit + push** del main repo (bump del puntatore submodule incluso): triggera il rebuild Pages (commit reale, niente commit vuoto).
5. **Monitorare la build** e verificare gli URL: `/domeniche/` (landing), `/domeniche/003-terza-domenica/` (con galleria), e che gli altri `/domeniche/00N-*/` rispondano come prima.

**Motore gallerie**: nessuna modifica. `_dapdi` è una collezione → le sue `img/` sono in `site.collections[].files` (già letto dal motore source-agnostic). Path servito `/dapdi/img/…` (invisibile all'utente, gli URL pagina restano `/domeniche/`).

**Rollback**: se il build fallisce o gli URL `/domeniche/` cambiano, ripristinare il blocco collezione `domeniche` in `_config.yml` e la cartella `_domeniche/`; il submodule resta inerte.

## Criteri di successo

- `/domeniche/` e `/domeniche/00N-*/` rispondono come prima (URL invariati).
- `/domeniche/003-terza-domenica/` mostra la galleria DAPDI-III (griglia + lightbox single, 4 colonne).
- `_dapdi` è un submodule autonomo con struttura archi e `CLAUDE.md`; `_domeniche/` non esiste più nel main repo.
- Build Pages `built` senza errori.
- La pipeline `bin/import-domenica.sh` è pronta per le prossime cartelle Nextcloud.

## Fuori scope (passi successivi)

- Watermark automatico logo+nome sulle `edit/`.
- Import delle altre domeniche (foto da Nextcloud, una cartella alla volta).
- Eventuale unificazione/collegamento tra post `_posts/*-domenica.md` e pagine collezione.
- Spostamento degli hero/ritratti dei testi in `_dapdi/src/`.
