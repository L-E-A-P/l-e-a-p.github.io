# Convenzione immagini gallerie (repo `l-e-a-p.github.io`)

I **post** (`_posts/`) di questo repo pubblicano le gallerie usando immagini che vivono qui come **file statici**, sotto `images/posts/`. Organizzazione **sempre** uguale, una cartella per **fotografo** identificato dalla sua sigla:

```
images/posts/EVENTO/<sigla-fotografo>/org/    foto originali scattate (full-res) — NON pubblicate, sorgente
images/posts/EVENTO/<sigla-fotografo>/edit/   resize alleggerite, CON logo + nome del fotografo — aperte nel lightbox
images/posts/EVENTO/<sigla-fotografo>/thumb/  miniature mostrate nella griglia
```

`org/`, `edit/`, `thumb/` contengono gli **stessi nomi file**. Questa struttura deve valere SEMPRE.
(NB: la vecchia cartella `full/` è legacy, va rinominata in `edit/`.)

## Sigle fotografo
La fonte di verità è `tools/watermark/photographers.yml` (ac, dt, gs, lz,
mdg, grdm, ff, pc, ml, sla, sl, …). Mai duplicare o invertire sigle
esistenti; le nuove ricorrenti si aggiungono lì.

## Uso nei post
Si imposta `gallery_path` nel front-matter e si fa un include **per cartella-fotografo** (il match `thumb/` del motore NON è ricorsivo):

```liquid
---
gallery_path: /images/posts/EVENTO/ac/
---
{% include gallery path=page.gallery_path %}
```

Il motore del tema (`so-leap-theme/_includes/gallery`) è *source-agnostic*: prende le miniature da `thumb/` e le immagini complete del lightbox da `edit/`, scorrendo sia le collezioni sia i **file statici** di questo repo (`site.static_files`). Le immagini delle pagine delle collezioni (`_lazzaro`, `_archi-di-pietra`) stanno invece nei rispettivi submodule.

## Pipeline immagini (`tools/`)
Due passi separati, stack Python + Pillow (`pip3 install --user Pillow pyyaml`):

**1. Organizzazione** — `tools/organize/organize.py` (vedi `tools/organize/README.md`): da un mucchio di originali genera `<evento>/<sigla>/{org,edit,thumb}` (org = copia, edit = altezza 1080, thumb = lato lungo 400), rinominando in `EVENTO-NN`. È la versione generale e cross-platform dello storico `_domeniche/bin/import-domenica.sh` (bash+`sips`).
```bash
python3 tools/organize/organize.py <originali> _lazzaro/img/EVENTO ac
```

**2. Watermark** — `tools/watermark/watermark.py` (vedi `tools/watermark/README.md`): applica il watermark storico (monogramma LEAP bianco in basso a sinistra + nome del fotografo in Datalegreya Thin) alle immagini in `edit/`. Sostituisce il vecchio flusso manuale con app a pagamento.

```bash
# nome dedotto dalla sigla nel percorso (.../<sigla>/edit/)
python3 tools/watermark/watermark.py images/posts/EVENTO/ac/edit --in-place
# contributore occasionale: cartella nome-cognome, normalizzata da sola
python3 tools/watermark/watermark.py images/posts/EVENTO/marco-iacobucci/edit --in-place
# nome esplicito + cartella d'uscita separata
python3 tools/watermark/watermark.py foto_in/ -n "Alice Cortegiani" -o foto_out/
```

Mappa sigla→nome in `tools/watermark/photographers.yml`; le sigle nuove vengono chieste e salvate (in TTY). Asset: font in `assets/fonts/Datalegreya-Thin.otf`, logo in `tools/watermark/leap-logo-w.png`. Dipendenze: `pip3 install --user Pillow pyyaml`.

## Bottega (progetti del laboratorio sul sito)

Convenzioni complete in `_bottega/CLAUDE.md` (sezione «Web»). In sintesi:
un post per progetto in `_bottega/web/<slug>.md` (URL `/bottega/web/<slug>/`,
griglia per `date:` decrescente), immagini in
`_bottega/img/<progetto>/<sessione>/<sigla>/{org,edit,thumb}` processate con
`tools/bottega/process-session.sh` e hero/-t con `tools/bottega/make-hero.py`.
`org/`, `raw/`, `*.mov`, `*.heic` restano in git ma sono esclusi dal sito
(exclude a livello FILE in `_config.yml`, es. `**/org/**`).
