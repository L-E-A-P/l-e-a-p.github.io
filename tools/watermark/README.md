# 🅻 Watermark LEAP

Strumento da riga di comando per applicare il **watermark storico LEAP** alle foto
delle gallerie del sito: il monogramma **LEAP** bianco in basso a sinistra e, subito
sotto, il **nome del fotografo**. Sostituisce il vecchio flusso manuale fatto con
un'app a pagamento — ora è uno script gratuito, ripetibile e versionato col progetto.

```
┌────────────────────────────────────────┐
│                                         │
│              (la foto)                  │
│                                         │
│                                         │
│  ▟▛ LEAP                                │   ← monogramma bianco
│  alice cortegiani                       │   ← nome in Datalegreya Thin
└────────────────────────────────────────┘
```

> [!NOTE]
> Il nome è scritto in **Datalegreya Thin**, un carattere display che disegna i
> glifi maiuscoli sui tasti **minuscoli**: per questo lo script trasforma il nome in
> minuscolo prima di disegnarlo (`Alice Cortegiani` → `alice cortegiani` → render in
> stampatello). Il "corpo" del testo è un peso intermedio ottenuto via supersampling
> (vedi [Stile e geometria](#-stile-e-geometria)).

---

## 📑 Indice
- [Cosa produce](#-cosa-produce)
- [Requisiti e installazione](#-requisiti-e-installazione)
- [Avvio rapido](#-avvio-rapido)
- [Dove vivono le immagini](#-dove-vivono-le-immagini)
- [Uso dettagliato](#-uso-dettagliato)
- [Come si risolve il nome del fotografo](#-come-si-risolve-il-nome-del-fotografo)
- [Riferimento completo dei parametri](#-riferimento-completo-dei-parametri)
- [Stile e geometria](#-stile-e-geometria)
- [Ricettario (casi tipici)](#-ricettario-casi-tipici)
- [⚠️ Errori da evitare](#️-errori-da-evitare)
- [Risoluzione problemi](#-risoluzione-problemi)
- [Come funziona dentro](#-come-funziona-dentro)
- [Asset e licenze](#-asset-e-licenze)

---

## 🎯 Cosa produce
Per ogni immagine in ingresso lo script genera una copia con:
1. il **logo monogramma LEAP** (bianco, semitrasparente) in basso a sinistra;
2. il **nome del fotografo** sotto al logo, allineato a sinistra.

Dimensioni e posizione sono espresse come **frazioni del lato lungo** dell'immagine,
così il watermark appare coerente sia sulle foto **orizzontali** sia su quelle
**verticali**.

---

## 🔧 Requisiti e installazione

| Cosa | Dettaglio |
|---|---|
| **Python** | 3.x (testato col `python3` di sistema su macOS) |
| **Pillow** | libreria immagini |
| **PyYAML** | per leggere/scrivere il database delle sigle |
| **Font** | `Datalegreya-Thin.otf` — già versionato in `assets/fonts/` (nessuna installazione di sistema necessaria) |
| **Logo** | `leap-logo-w.png` — già qui nella cartella del tool |

Installa le due dipendenze Python (a livello utente, senza permessi di root):
```bash
pip3 install --user Pillow pyyaml
```
Su sistemi con [MacPorts](https://www.macports.org/) in alternativa:
`sudo port install py-Pillow py-yaml`.

Verifica che sia tutto a posto:
```bash
python3 tools/watermark/watermark.py --help
```

---

## 🚀 Avvio rapido

Dalla **radice del repo** `l-e-a-p.github.io`:

```bash
# Marca tutte le foto di una galleria, sovrascrivendole (nome dedotto dalla sigla)
python3 tools/watermark/watermark.py images/posts/EVENTO/ac/edit --in-place
```

Tutto qui. Il nome "Alice Cortegiani" viene dedotto dalla sigla `ac` nel percorso,
e le immagini in `edit/` vengono marcate sul posto. Gli originali senza logo restano
al sicuro in `org/`.

---

## 🗂 Dove vivono le immagini

Le gallerie seguono **sempre** questa struttura (una cartella per fotografo,
identificato dalla sua sigla — vedi [`../../CLAUDE.md`](../../CLAUDE.md)):

```
.../EVENTO/<sigla-fotografo>/
├── org/     foto originali full-res, SENZA logo  ← sorgente di sicurezza, non pubblicate
├── edit/    versioni alleggerite CON logo + nome ← QUI si applica il watermark
└── thumb/   miniature per la griglia
```

`org/`, `edit/` e `thumb/` contengono gli **stessi soggetti**. Il watermark si applica
sempre alle immagini in **`edit/`**: `org/` è la rete di salvataggio da cui ripartire
se qualcosa va storto.

---

## 📖 Uso dettagliato

Sintassi generale:
```bash
python3 tools/watermark/watermark.py  <input>  [opzioni]
```

### Input: file singolo o cartella
- **Cartella** → processa tutte le immagini contenute (`.jpg .jpeg .png .tif .tiff`),
  in ordine alfabetico.
- **File singolo** → processa solo quel file (comodo per fare prove).

### Output: tre modalità
| Modalità | Flag | Effetto |
|---|---|---|
| **Sul posto** | `--in-place` | sovrascrive i file di input (uso tipico su `edit/`) |
| **Cartella separata** | `-o CARTELLA` | scrive le copie marcate in `CARTELLA/`, stesso nome file |
| **Default** | *(nessuno)* | crea copie accanto agli originali col suffisso `_wm` |

```bash
# sul posto (tipico)
python3 tools/watermark/watermark.py images/posts/EVENTO/ac/edit --in-place

# in una cartella di prova, senza toccare gli originali
python3 tools/watermark/watermark.py images/posts/EVENTO/ac/edit -o /tmp/prova

# copie _wm accanto (es. 2024-..-01.jpg -> 2024-..-01_wm.jpg)
python3 tools/watermark/watermark.py una_foto.jpg
```

### Batch su un intero submodule
Per marcare tutte le `edit/` di un submodule (es. `_domeniche`) in un colpo:
```bash
for e in $(find _domeniche/img -type d -name edit | sort); do
  python3 tools/watermark/watermark.py "$e" --in-place
done
```

---

## 👤 Come si risolve il nome del fotografo

Lo script determina il nome **in quest'ordine**, fermandosi al primo che funziona:

1. **`-n "Nome Cognome"`** — nome esplicito da riga di comando (ha la precedenza su tutto).
2. **Cartella `nome-cognome`** — se la cartella-fotografo si chiama `marco-iacobucci`,
   viene normalizzata al volo in *Marco Iacobucci* (nessuna voce da aggiungere al database).
3. **Sigla nel percorso** — la cartella-fotografo (es. `ac`) viene cercata in
   [`photographers.yml`](photographers.yml).
4. **Sigla sconosciuta** — in un terminale interattivo lo script **chiede** il nome
   esteso e si offre di **salvarlo** nel database; con `-y` lo salva senza chiedere
   conferma. In modalità non interattiva (es. dentro un `for`/CI) esce con un errore
   che spiega le alternative.

### Convenzione LEAP
- **Core LEAPHZ** → sigla breve registrata in `photographers.yml` (`ac`, `dt`, `gs`, …).
- **Contributori occasionali** → cartella `nome-cognome`, normalizzata al volo, **senza**
  sporcare il database.

### Il database `photographers.yml`
Mappa semplice `sigla: Nome Cognome`. Puoi modificarlo a mano (è commentato) oppure
lasciare che lo script aggiunga in coda le sigle nuove. Esempio:
```yaml
ac: Alice Cortegiani
dt: Davide Tedesco
gs: Giuseppe Silvi
# ...
```

---

## 🎛 Riferimento completo dei parametri

| Flag | Default | Descrizione |
|---|---|---|
| `input` | *(obbligatorio)* | file o cartella di immagini |
| `-n`, `--name` | — | nome fotografo esplicito (salta la risoluzione automatica) |
| `-o`, `--output` | — | cartella d'uscita (altrimenti: copie con suffisso `_wm`) |
| `--in-place` | off | sovrascrive i file di input |
| `-y`, `--yes` | off | salva in automatico le sigle nuove nel database |
| `--logo` | `leap-logo-w.png` | PNG del logo (bianco su trasparente) |
| `--font` | `assets/fonts/Datalegreya-Thin.otf` | font del nome |
| `--logo-w` | `0.060` | larghezza del logo (frazione del lato lungo) |
| `--margin` | `0.009` | margine da sinistra e dal fondo (frazione lato lungo) |
| `--gap` | `0.0035` | spazio fra logo e nome (frazione lato lungo) |
| `--name-h` | `0.0105` | altezza del testo del nome (frazione lato lungo) |
| `--tracking` | `0.005` | spaziatura fra le lettere (frazione della cap height) |
| `--stroke` | `0.4` | **corpo** del nome in px effettivi (faux-bold via supersampling) |
| `--opacity` | `235` | opacità di logo e nome (0–255) |
| `--quality` | `88` | qualità JPEG in uscita |

> I default sono **già tarati** sul look approvato: nella maggior parte dei casi non
> serve toccare nessun parametro. Le opzioni servono per casi particolari o per
> ri-tarare lo stile.

---

## 🎨 Stile e geometria

**Scala sul lato lungo.** Tutte le misure geometriche sono frazioni del lato lungo
dell'immagine (`max(larghezza, altezza)`). Sugli orizzontali il lato lungo è la
larghezza; sui verticali è l'altezza. Così il watermark ha **dimensioni coerenti** a
prescindere dall'orientamento (sugli orizzontali il comportamento è identico a una
scala sulla larghezza).

**Corpo del nome (supersampling).** Datalegreya esiste solo in peso *Thin*. Per dargli
un filo di corpo senza renderlo "cicciotto", il nome viene disegnato su un layer
ingrandito **8×** (costante `SS` nello script), con un contorno (`stroke`) applicato a
quella scala, e poi rimpicciolito con anti-aliasing. Risultato: lo spessore diventa
**continuo** invece che a salti di 1 pixel, ed è regolabile con precisione tramite
`--stroke` (espresso in px effettivi). Il valore di default `0.4` è il peso "intermedio"
scelto come definitivo — più presente del Thin puro, più sottile del faux-bold a 1px.

**Allineamento.** Logo e nome sono allineati a sinistra sullo stesso margine. Con i
default, in "Alice Cortegiani" la parola *cortegiani* inizia poco prima della seconda
gamba della **A** del logo.

---

## 🧑‍🍳 Ricettario (casi tipici)

**Provare lo stile su una sola foto senza rischi**
```bash
python3 tools/watermark/watermark.py una_foto.jpg -o /tmp/prova --stroke 0.5
```

**Marcare una galleria**
```bash
python3 tools/watermark/watermark.py images/posts/EVENTO/ac/edit --in-place
```

**Marcare un intero submodule** — vedi [Batch](#batch-su-un-intero-submodule).

**Annullare un errore su una galleria** (i file sono tracciati in git):
```bash
git -C _domeniche checkout -- img/EVENTO/ac/edit/
```

**Rifare una foto da zero** (quando l'`edit` è già marcato e non si può "smarcare"):
rigenera l'`edit` pulito dal corrispondente `org` (resize alla stessa dimensione) e poi
ri-applica il watermark a quel singolo file.

---

## ⚠️ Errori da evitare

> [!CAUTION]
> **Non lanciare `--in-place` due volte sulla stessa cartella.** Ogni esecuzione
> aggiunge un watermark: la seconda crea un **doppione**. Se hai un dubbio, ripristina
> con `git checkout -- <cartella>` e rilancia una volta sola.

> [!WARNING]
> **Verifica che le `edit/` non siano GIÀ marcate** prima di un batch. Alcune vecchie
> gallerie potrebbero avere il watermark del flusso manuale precedente: ri-applicarlo
> creerebbe un doppione. Controlla a **piena risoluzione** (una griglia di miniature
> può ingannare).

> [!WARNING]
> **Gallerie in B/N:** non rigenerare gli `edit` partendo da `org` se gli `org` sono a
> colori e gli `edit` in bianco e nero — la conversione B/N potrebbe non combaciare con
> quella del fotografo. In quei casi parti da un `edit` pulito o chiedi conferma.

---

## 🩺 Risoluzione problemi

| Sintomo | Causa probabile / Rimedio |
|---|---|
| `Font non trovato` / `Logo non trovato` | lancia lo script dalla radice del repo, o passa `--font`/`--logo` espliciti |
| `Sigla sconosciuta '...'` (in batch) | aggiungi la sigla a `photographers.yml`, oppure usa `-n "Nome Cognome"`, oppure rinomina la cartella `nome-cognome` |
| `ModuleNotFoundError: PIL` / `yaml` | `pip3 install --user Pillow pyyaml` |
| `TypeError: 'type' object is not subscriptable` | Python troppo vecchio: lo script usa già `from __future__ import annotations`; aggiorna a Python 3.x recente |
| Watermark **doppio** | la cartella è stata processata due volte o era già marcata → `git checkout` e rilancia una volta sola |
| Watermark troppo piccolo su un verticale | aggiorna lo script (la scala è ora sul lato lungo) |

---

## 🛠 Come funziona dentro
1. Apre l'immagine in RGBA e calcola `ref = max(larghezza, altezza)`.
2. Ridimensiona il logo a `logo-w × ref` e ne attenua l'alpha all'`opacity`.
3. Disegna il nome (minuscolo) su un layer **8×**, con `tracking` e `stroke`, poi lo
   riduce con anti-aliasing → corpo "frazionario".
4. Compone logo e nome in basso a sinistra, ancorati al margine.
5. Salva in JPEG (o PNG) con la qualità richiesta.

Codice in [`watermark.py`](watermark.py) — funzioni chiave: `resolve_name`,
`render_name_layer`, `watermark_image`.

---

## 📦 Asset e licenze
- **Font:** [`../../assets/fonts/Datalegreya-Thin.otf`](../../assets/fonts/Datalegreya-Thin.otf)
  — Datalegreya di Figs (basato su Alegreya), font libero.
- **Logo:** [`leap-logo-w.png`](leap-logo-w.png) — copia del monogramma bianco
  `2023-11-12-logo-kern-w.png` dal repo `logo` di LEAP.
- **Database sigle:** [`photographers.yml`](photographers.yml).
