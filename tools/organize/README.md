# 🗂 Organize — da originali a `org/edit/thumb`

Primo passo della pipeline immagini LEAP: prende un mucchio di **foto originali** e
le organizza nella convenzione del sito, pronte per il [watermark](../watermark/).

È la versione **generale e cross-platform** (Python + Pillow) dello storico
`_domeniche/bin/import-domenica.sh` (bash + `sips`, solo macOS): qui la destinazione
è un argomento, quindi funziona per **qualsiasi** repo/galleria.

```
<cartella-evento>/<sigla>/
├── org/     originali rinominati <evento>-NN.<ext>  (copia byte-per-byte)
├── edit/    resize ad altezza 1080, SENZA watermark  ← lightbox
└── thumb/   resize lato lungo 400                     ← griglia
```

I tre folder hanno gli **stessi nomi file**. Lo slug `EVENTO` per la rinominazione è
il nome della cartella-evento di destinazione.

---

## 🔧 Requisiti
```bash
pip3 install --user Pillow pyyaml
```
(`pyyaml` è opzionale: serve solo per validare la sigla contro
[`../watermark/photographers.yml`](../watermark/photographers.yml).)

---

## 🚀 Uso

```bash
python3 tools/organize/organize.py  <originali>  <cartella-evento>  <sigla>  [opzioni]
```

**Originali in una cartella esterna:**
```bash
python3 tools/organize/organize.py ~/Downloads/lazzaro-2025 \
        _lazzaro/img/2025-09-22-lazzaro ac
```

**Originali già dentro il repo** (layout grezzo `org/<sigla>` da riordinare):
```bash
python3 tools/organize/organize.py \
        _lazzaro/img/2025-09-22-lazzaro/org/ac \
        _lazzaro/img/2025-09-22-lazzaro ac
```

**Anteprima senza scrivere** (`--dry-run` / `-n`): mostra la rinominazione e basta.

Al termine lo script stampa il comando di watermark da lanciare sugli `edit/`.

---

## 🎛 Parametri

| Flag | Default | Descrizione |
|---|---|---|
| `src` | *(obbligatorio)* | cartella con gli originali |
| `event_dir` | *(obbligatorio)* | cartella EVENTO di destinazione (es. `_lazzaro/img/2025-09-22-lazzaro`) |
| `sigla` | *(obbligatorio)* | sigla fotografo (o cartella `nome-cognome`) |
| `--edit-h` | `1080` | altezza delle immagini `edit/` (px) |
| `--thumb-max` | `400` | lato lungo delle `thumb/` (px) |
| `--quality` | `88` | qualità JPEG |
| `--start` | `1` | numero di partenza per la rinominazione |
| `-n`, `--dry-run` | off | mostra cosa farebbe, senza scrivere |

---

## 🔁 La pipeline completa

```bash
# 1) organizza gli originali di ogni fotografo
python3 tools/organize/organize.py <originali-ac> _lazzaro/img/EVENTO ac
python3 tools/organize/organize.py <originali-gs> _lazzaro/img/EVENTO gs

# 2) applica il watermark agli edit (vedi tools/watermark/README.md)
python3 tools/watermark/watermark.py _lazzaro/img/EVENTO/ac/edit --in-place
python3 tools/watermark/watermark.py _lazzaro/img/EVENTO/gs/edit --in-place
```

---

## 📝 Note
- **`org/` è la copia di sicurezza**: byte-per-byte dell'originale, nessuna
  trasformazione. `edit/` e `thumb/` sono derivati (con orientamento EXIF applicato).
- Un fotografo per esecuzione: per gallerie con più fotografi, lancia lo script una
  volta per sigla (ogni sigla è una cartella separata).
- Le immagini `edit/` escono **senza watermark**: è lo step successivo a metterlo.
- L'altezza fissa a 1080 fa sì che i verticali abbiano lato lungo 1080 e gli
  orizzontali 1440 — il watermark si adatta perché è scalato sul lato lungo.
