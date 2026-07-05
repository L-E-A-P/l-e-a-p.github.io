# Design: popolamento della Bottega

Data: 2026-07-05 · Validato con Alice in sessione

## Obiettivo

Trasformare `/bottega/` da pagina con un solo placeholder (Bertoncini) nel
collettore delle attività del LEAP: ogni progetto (costruzione/manutenzione di
strumenti, produzioni, ricerche) ha il suo spazio — un lungo post che alterna
testi, gallerie fotografiche, in futuro video e documentazione PDF, organizzato
per sessioni di lavoro. Un diario di laboratorio, organizzato per attività.

## Stato di partenza

- Landing `/bottega/`: `bottega.md` (repo principale), layout `collection`,
  griglia delle entry di `_bottega/web/*.md` (defaults già cablati in
  `_config.yml`: layout `project`, tipo `bottega`).
- `_bottega` è un submodule con doppia anima: `src/` (sistema LaTeX dei
  fascicoli d'intervento) e `web/` (pagine del sito). Unica entry attuale:
  `web/mb.md` (placeholder Mario Bertoncini).
- In `_bottega/img/` Alice ha già caricato ~2.7 GB di materiale non tracciato,
  8 cartelle progetto (una vuota), foto in jpg/jpeg/HEIC + 62 video `.mov`.
- Pipeline immagini consolidata nel repo principale: `tools/organize/organize.py`
  (genera `org/edit/thumb`, rinomina `EVENTO-NN`) + `tools/watermark/watermark.py`
  (watermark su `edit/`, nomi da `tools/watermark/photographers.yml`).
- Vincolo del motore gallerie (`so-leap-theme/_includes/gallery`): il match su
  `thumb/` NON è ricorsivo → un include per cartella-fotografo.

## Decisioni (validate una a una)

1. **Cartelle progetto senza data**: `img/<progetto>/` con slug semplice
   (`flux-ferracuti`, `tbdc-citera`, `upu-ads`, `luccello`,
   `anapnoe-somafonico-petalonio`, `stoned`, `mario-bertoncini`,
   `interfantasia-ferracuti`). La nota archivistica (data) vive nel front
   matter dei post, dove è usabile dal motore per l'ordinamento.
2. **Sessioni sempre datate** dentro il progetto, anche se una sola:
   `img/<progetto>/<YYYY-MM-DD[-slug]>/<sigla>/{org,edit,thumb}/`.
   Suffissi descrittivi ammessi (`-prelievo`, `-riconsegna`); normalizzare
   `-STONED` in minuscolo.
3. **Post = slug della cartella**: `_bottega/web/<progetto>.md` + campo `date:`
   nel front matter. Rinominare `mb.md` → `mario-bertoncini.md`
   (⚠ cambia l'URL pubblico da `/bottega/mb/` a `/bottega/mario-bertoncini/`;
   accettato).
4. **Griglia in ordine inverso** (più recente in cima): `sort_by: date` +
   `sort_order: reverse` in `bottega.md`. Semantica `date:` = data dell'ultima
   sessione pubblicata del progetto (aggiornabile: un progetto "risale" quando
   ci si rilavora).
5. **Tutto in git, come lazzaro** (org/ e .mov compresi: il repo è anche
   archivio), MA `org/` e `.mov` esclusi dal sito pubblicato via `exclude:` in
   `_config.yml` (tetto GitHub Pages: 1 GB di sito pubblicato). Pattern esatti
   da tarare con build locale; valutare la stessa regola per gli `org/` delle
   altre collezioni. Push iniziale ~2.7 GB da spezzare (limite git ~2 GB/push).
6. **Strategia incrementale**: un progetto alla volta, end-to-end, dal semplice
   al complesso. Ordine: `tbdc-citera` → `flux-ferracuti` → `upu-ads` →
   `luccello` → `anapnoe-somafonico-petalonio` → `stoned` → `mario-bertoncini`.
   Ogni progetto va online appena pronto.
7. **STONED**: mini-selezione provvisoria (~6–8 foto/sessione, a cura di
   Claude, scartando sfocate/doppioni) per pubblicare subito; selezione fine di
   Alice in seguito. Le foto non selezionate restano in cartella, non
   processate.
8. **HEIC → jpg con `sips` prima di `organize.py`** (convenzione nota):
   riguarda `upu-ads` (29), `luccello` (6), `mario-bertoncini` (17).
9. **Video fuori scope per ora**: i `.mov` restano in git come archivio, non
   pubblicati. Le sessioni solo-video (`luccello/2025-06-19`,
   `anapnoe-somafonico-petalonio/2025-04-30`) entreranno nei post quando i
   video avranno un canale (embed YouTube, pattern `responsive-embed` già in
   uso).
10. **`interfantasia-ferracuti`**: nessun post finché non arrivano i materiali.
11. **Testi**: due righe di contesto per post (bozza da questa sessione),
    cura redazionale di Alice in seguito.

## Convenzione hero e thumbnail

```
img/<progetto>/<progetto>-hero.jpg   ← hero del post (da una foto edit/ watermarked)
img/<progetto>/<progetto>-t.jpg      ← thumbnail griglia
```

Copie rinominate di una foto scelta del progetto (proposta da Claude in fase
di lavorazione, veto/scelta finale di Alice); nessun formato nuovo.

## Template del post

```markdown
---
title: "FLUX"
date: 2024-02-12
image:
  path: bottega/img/flux-ferracuti/flux-ferracuti-hero.jpg
  thumbnail: bottega/img/flux-ferracuti/flux-ferracuti-t.jpg
  caption: ""
---

Due righe di contesto sul progetto.

<!--more-->

## 28 settembre 2023

{% include gallery path="bottega/img/flux-ferracuti/2023-09-28/ac/" %}

## 14 ottobre 2023
…
```

- Sessioni in ordine cronologico crescente (il diario si legge in avanti).
- Un `{% include gallery %}` per ogni cartella-sigla della sessione.
- `<!--more-->` dopo l'intro (excerpt in griglia).
- `mario-bertoncini.md` linka anche i fascicoli PDF (`src/interventi/mb/…`),
  stile "cliccami" di archi-di-pietra.

## Contenuti: titoli e contesto (bozze)

| Progetto | Titolo | date: | Sessioni foto | Contesto (bozza da rifinire) |
|---|---|---|---|---|
| `tbdc-citera` | The Big Data Cookbook | 2023-12-08 | 2 (dic 2023) | Prove al LEAP del lavoro di Pasquale Citera |
| `flux-ferracuti` | FLUX | 2024-02-12 | 3 (set 2023–feb 2024) | Strumento-progetto di Francesco Ferracuti, progetto di laurea (triennio) |
| `upu-ads` | Umano Post Umano | 2024-09-14 | 2 (giu/set 2024) | Performance distribuita per un teatro sonoro corpo/macchina/spazio di Agostino Di Scipio, prima assoluta 19/12/2024 (Nuova Consonanza); al LEAP stralci del lavoro di ricerca con Agostino |
| `stoned` | STONED | 2024-09-16 | 6 (ago–set 2024) | Altoparlante a diffusione sferica/tetraedrica di Giuseppe Silvi, per un'installazione al Festival ArteScienza 2024 |
| `anapnoe-somafonico-petalonio` | Anapnoe, Somafonico, Petalonio | 2025-04-27 | 4 con foto (apr 2025) | Sordina elettroacustica, corpetto elettroacustico e trombino per clarinetto contrabbasso (alloggio dell'anapnoe), costruiti per *Canto alla durata* di Giuseppe Silvi |
| `luccello` | Luccello | 2025-05-28 | 1 con foto (mag 2025) | Per *Canto alla durata* di Giuseppe Silvi, al violoncello: feedback acustico per induzione elettromagnetica |
| `mario-bertoncini` | Mario Bertoncini | 2025-10-29 | 11 (giu–ott 2025, prelievo→riconsegna) | Conservazione e restauro degli strumenti della collezione Mario Bertoncini (fascicoli d'intervento in PDF) |

Sigle presenti: `ac` (Alice Cortegiani), `gs` (Giuseppe Silvi), `mdg` (Marco Di
Gasbarro) — tutte già in `photographers.yml`.

## Pipeline per progetto (ripetibile)

1. HEIC → jpg (`sips`) dove serve
2. `organize.py` → `<sessione>/<sigla>/{org,edit,thumb}` con rinomina `SESSIONE-NN`
3. `watermark.py` su `edit/` (`--in-place`, nome dedotto dalla sigla)
4. Hero + `-t` (solo alla prima pubblicazione del progetto)
5. Post `.md` (creazione o aggiunta sessione)
6. Build locale di verifica (dimensione `_site`, rendering gallerie) → commit
   `_bottega` → push → bump puntatore submodule nel repo principale → push →
   verifica online

## Verifiche tecniche rimandate alla fase di piano/implementazione

- Comportamento di `organize.py` con originali già dentro la cartella di
  destinazione (le foto sono ora loose in `<sigla>/`); gestione estensioni
  `.jpeg`/`.JPG` e nomi file con spazi (es. `IMG_5284 2.HEIC`).
- Pattern `exclude:` efficaci sui file statici delle collezioni (verifica con
  build locale prima/dopo, misura `_site`).
- Che la build Pages regga il primo push grosso; push a tappe.

## Fuori scope (annotato per dopo)

- Video su YouTube + embed nei post.
- `interfantasia-ferracuti` quando arrivano i materiali.
- Selezione fine di STONED (Alice).
- Aggiornamento CLAUDE.md: convenzioni bottega + lista sigle datata nel
  CLAUDE.md principale (da fare comunque a fine lavori).
