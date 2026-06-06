#!/usr/bin/env python3
"""
Organizza una galleria nella convenzione LEAP org/edit/thumb.

Versione generale e portabile (Pillow) di _domeniche/bin/import-domenica.sh:
funziona per qualsiasi repo (lazzaro, domeniche, archi-di-pietra, images/posts…)
perché la destinazione è un argomento esplicito.

Dato un insieme di originali, crea:
    <cartella-evento>/<sigla>/
    ├── org/    originali rinominati <evento>-NN.<ext>  (copia byte-per-byte)
    ├── edit/   resize ad altezza --edit-h (default 1080), SENZA watermark
    └── thumb/  resize lato lungo --thumb-max (default 400)

`org/`, `edit/`, `thumb/` hanno gli STESSI nomi file. Lo step di watermark
(tools/watermark) si applica DOPO, alle immagini in edit/.

Esempi:
    # originali in una cartella esterna
    ./organize.py ~/Downloads/lazzaro-2025 _lazzaro/img/2025-09-22-lazzaro ac

    # originali già dentro il repo (layout grezzo org/<sigla>)
    ./organize.py _lazzaro/img/2025-09-22-lazzaro/org/ac \
                  _lazzaro/img/2025-09-22-lazzaro ac

Lo slug EVENTO usato per rinominare è il nome della cartella-evento di
destinazione (es. 2025-09-22-lazzaro -> 2025-09-22-lazzaro-01.jpg).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:
    import yaml
except ImportError:
    yaml = None

HERE = Path(__file__).resolve().parent
DB_PATH = HERE.parent / "watermark" / "photographers.yml"  # database condiviso col watermark

IMG_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def known_sigle() -> dict:
    if yaml and DB_PATH.exists():
        return yaml.safe_load(DB_PATH.read_text()) or {}
    return {}


def looks_like_full_name(token: str) -> bool:
    """True per cartelle 'nome-cognome' (contributori occasionali)."""
    parts = [p for p in token.split("-") if p]
    return len(parts) >= 2 and all(p.isalpha() for p in parts)


def collect_sources(src: Path) -> list[Path]:
    files = sorted(p for p in src.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS)
    if not files:
        sys.exit(f"Nessuna immagine in {src}")
    return files


def save_resized(img: Image.Image, dst: Path, *, quality: int):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.suffix.lower() in {".jpg", ".jpeg"}:
        img.convert("RGB").save(dst, quality=quality, subsampling=0)
    else:
        img.save(dst)


def main():
    ap = argparse.ArgumentParser(description="Organizza una galleria in org/edit/thumb.")
    ap.add_argument("src", type=Path, help="cartella con gli originali")
    ap.add_argument("event_dir", type=Path, help="cartella EVENTO di destinazione (es. _lazzaro/img/2025-09-22-lazzaro)")
    ap.add_argument("sigla", help="sigla fotografo (o cartella nome-cognome)")
    ap.add_argument("--edit-h", type=int, default=1080, help="altezza delle immagini edit (px)")
    ap.add_argument("--thumb-max", type=int, default=400, help="lato lungo delle thumb (px)")
    ap.add_argument("--quality", type=int, default=88, help="qualità JPEG")
    ap.add_argument("--start", type=int, default=1, help="numero di partenza per la rinominazione")
    ap.add_argument("-n", "--dry-run", action="store_true", help="mostra cosa farebbe, senza scrivere")
    args = ap.parse_args()

    src: Path = args.src
    if not src.is_dir():
        sys.exit(f"Sorgente non valida (serve una cartella): {src}")

    evento = args.event_dir.resolve().name
    dest = args.event_dir / args.sigla
    sigle = known_sigle()
    if args.sigla not in sigle and not looks_like_full_name(args.sigla):
        print(f"⚠️  Sigla '{args.sigla}' non in {DB_PATH.name} e non in forma 'nome-cognome'.")
        print("    Procedo comunque (verifica che sia corretta).")

    files = collect_sources(src)
    print(f"Evento '{evento}', fotografo '{args.sigla}': {len(files)} immagini")
    print(f"  -> {dest}/{{org,edit,thumb}}")
    if args.dry_run:
        for i, f in enumerate(files, args.start):
            print(f"    {f.name} -> {evento}-{i:02d}{f.suffix.lower()}")
        print("(dry-run: niente scritto)")
        return

    for i, f in enumerate(files, args.start):
        stem = f"{evento}-{i:02d}"
        # org: copia byte-per-byte dell'originale, estensione originale conservata
        # (es. i TIFF restano TIFF: org è la sorgente lossless).
        org_path = dest / "org" / f"{stem}{f.suffix.lower()}"
        org_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, org_path)

        # edit/thumb: derivati SEMPRE in JPEG (web), con orientamento EXIF applicato
        im = ImageOps.exif_transpose(Image.open(f))
        w, h = im.size

        edit = im.resize((round(w * args.edit_h / h), args.edit_h), Image.LANCZOS)
        save_resized(edit, dest / "edit" / f"{stem}.jpg", quality=args.quality)

        scale = args.thumb_max / max(w, h)
        thumb = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        save_resized(thumb, dest / "thumb" / f"{stem}.jpg", quality=args.quality)

        print(f"  {f.name} -> {stem} (org{f.suffix.lower()}, edit/thumb .jpg)")

    print(f"\nFatto. Ora applica il watermark agli edit:")
    print(f"  python3 tools/watermark/watermark.py {dest}/edit --in-place")


if __name__ == "__main__":
    main()
