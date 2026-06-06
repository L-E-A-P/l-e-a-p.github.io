#!/usr/bin/env python3
"""
Applica il watermark LEAP (logo monogramma + nome fotografo) alle foto.

Riproduce il watermark storico fatto a mano: monogramma LEAP bianco in basso a
sinistra e, sotto, il nome del fotografo in Datalegreya Thin (carattere che mostra
glifi maiuscoli dai tasti minuscoli -> il testo viene reso minuscolo prima del
disegno).

Risoluzione del nome fotografo (in ordine):
  1. --name "Nome Cognome"            esplicito, ignora tutto il resto
  2. cartella "nome-cognome"          normalizzata al volo (contributori occasionali)
  3. sigla nel percorso .../<sigla>/  cercata in photographers.yml (core LEAPHZ)
  4. sigla ignota                     chiede il nome e lo salva nello yaml (se TTY)

Esempi:
    ./watermark.py images/posts/2024-03-24-DAPDI-III/ac/edit
    ./watermark.py images/posts/EVENTO/marco-iacobucci/edit
    ./watermark.py foto_in/ -n "Alice Cortegiani" -o foto_out/
    ./watermark.py .../ac/edit --in-place        # sovrascrive (serve sorgente in org/)

Geometria (frazioni della larghezza immagine salvo nota), tarata sugli esempi storici:
    --logo-w   0.060   larghezza del logo
    --margin   0.009   margine da sinistra e dal fondo
    --gap      0.0035  spazio fra logo e nome
    --name-h   0.0105  altezza nominale del testo del nome
    --tracking 0.005   spaziatura fra lettere (frazione della cap height)
    --stroke   0.4     spessore effettivo del nome in px (faux-bold via supersampling SS×)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent  # .../l-e-a-p.github.io
DEFAULT_LOGO = HERE / "leap-logo-w.png"
DEFAULT_FONT = SITE / "assets" / "fonts" / "Datalegreya-Thin.otf"
DB_PATH = HERE / "photographers.yml"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


# --------------------------------------------------------------------------- #
# Risoluzione sigla / nome fotografo
# --------------------------------------------------------------------------- #
def load_db() -> dict[str, str]:
    if not DB_PATH.exists():
        return {}
    return yaml.safe_load(DB_PATH.read_text()) or {}


def save_to_db(sigla: str, name: str) -> None:
    """Aggiunge una entry in coda al file, preservando commenti e ordine."""
    text = DB_PATH.read_text()
    sep = "" if text.endswith("\n") else "\n"
    DB_PATH.write_text(f"{text}{sep}{sigla}: {name}\n")


def normalize_full_name(token: str) -> str | None:
    """'marco-iacobucci' -> 'Marco Iacobucci'. None se non sembra un nome-cognome."""
    parts = [p for p in token.split("-") if p]
    if len(parts) < 2 or not all(p.isalpha() for p in parts):
        return None
    return " ".join(p.capitalize() for p in parts)


def folder_token(path: Path) -> str:
    """La cartella-fotografo: il genitore di 'edit'/'thumb'/'org', altrimenti la cartella stessa."""
    p = path.resolve()
    base = p if p.is_dir() else p.parent
    if base.name in {"edit", "thumb", "org", "full"}:
        base = base.parent
    return base.name


def resolve_name(path: Path, db: dict[str, str], *, interactive: bool, autosave: bool) -> str:
    token = folder_token(path)
    if token in db:
        return db[token]
    full = normalize_full_name(token)
    if full:
        return full
    # sigla ignota
    if not interactive:
        sys.exit(
            f"Sigla sconosciuta '{token}' in {path}.\n"
            f"  Usa -n \"Nome Cognome\", oppure rinomina la cartella in 'nome-cognome',\n"
            f"  oppure esegui in un terminale interattivo per aggiungerla a {DB_PATH.name}."
        )
    name = input(f"Sigla sconosciuta '{token}'. Nome esteso del fotografo: ").strip()
    if not name:
        sys.exit("Nessun nome fornito.")
    if autosave or input(f"Salvo '{token}: {name}' in {DB_PATH.name}? [Y/n] ").strip().lower() in ("", "y", "s"):
        save_to_db(token, name)
        print(f"  + salvato {token}: {name}")
    return name


# --------------------------------------------------------------------------- #
# Disegno
# --------------------------------------------------------------------------- #
def fit_font(font_path: Path, target_cap_px: int) -> ImageFont.FreeTypeFont:
    """Font dimensionato perché l'altezza dei glifi sia ~target_cap_px."""
    probe = 200
    f = ImageFont.truetype(str(font_path), probe)
    bbox = f.getbbox("abcdefghilmnopqrstuvz")  # Datalegreya: glifi maiuscoli su tasti minuscoli
    cap_h = bbox[3] - bbox[1]
    size = max(8, round(probe * target_cap_px / cap_h))
    return ImageFont.truetype(str(font_path), size)


# Fattore di supersampling del nome: il testo viene disegnato a SS× e poi
# rimpicciolito con anti-aliasing, così lo stroke (faux-bold) diventa di fatto
# "frazionario" e si può regolare il corpo con continuità invece che a salti di 1px.
SS = 8


def render_name_layer(text, font_path, cap_px, tracking_frac, stroke_px, fill, ss=SS):
    """Disegna il nome con tracking e stroke su un layer sovracampionato, poi lo riduce."""
    font = fit_font(font_path, cap_px * ss)
    tracking = cap_px * tracking_frac * ss
    stroke = round(stroke_px * ss)

    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    total_w = sum(d.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1) + stroke * 2
    bbox = font.getbbox(text)
    h = (bbox[3] - bbox[1]) + stroke * 2

    layer = Image.new("RGBA", (round(total_w) + 2, round(h) + 2), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    x, y = stroke, stroke - bbox[1]
    for ch in text:
        dl.text((x, y), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=fill)
        x += dl.textlength(ch, font=font) + tracking

    return layer.resize((round(layer.width / ss), round(layer.height / ss)), Image.LANCZOS)


def watermark_image(
    src: Path,
    dst: Path,
    name: str,
    logo_img: Image.Image,
    font_path: Path,
    *,
    logo_w_frac: float,
    margin_frac: float,
    gap_frac: float,
    name_h_frac: float,
    tracking_frac: float,
    stroke_px: float,
    opacity: int,
    jpeg_quality: int,
):
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    margin = round(W * margin_frac)
    gap = round(W * gap_frac)

    # logo ridimensionato (mantiene l'alpha proprio, eventualmente attenuato)
    logo_w = round(W * logo_w_frac)
    logo_h = round(logo_w * logo_img.height / logo_img.width)
    logo = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
    if opacity < 255:
        a = logo.split()[3].point(lambda p: round(p * opacity / 255))
        logo.putalpha(a)

    # nome (Datalegreya rende maiuscolo dai tasti minuscoli), supersampled
    cap_px = round(W * name_h_frac)
    fill = (255, 255, 255, opacity)
    name_layer = render_name_layer(name.lower(), font_path, cap_px, tracking_frac, stroke_px, fill)

    # blocco ancorato in basso a sinistra: logo sopra, nome sotto
    name_y = H - margin - name_layer.height
    logo_y = name_y - gap - logo_h
    im.alpha_composite(logo, (margin, logo_y))
    im.alpha_composite(name_layer, (margin, name_y))

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.suffix.lower() in {".jpg", ".jpeg"}:
        im.convert("RGB").save(dst, quality=jpeg_quality, subsampling=0)
    else:
        im.save(dst)


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Watermark LEAP (logo + nome fotografo).")
    ap.add_argument("input", type=Path, help="file o cartella di immagini")
    ap.add_argument("-n", "--name", help="nome fotografo esplicito (salta la risoluzione)")
    ap.add_argument("-o", "--output", type=Path, help="cartella d'uscita (default: accanto, suffisso _wm)")
    ap.add_argument("--in-place", action="store_true", help="sovrascrive i file di input")
    ap.add_argument("-y", "--yes", action="store_true", help="conferma in automatico il salvataggio di sigle nuove")
    ap.add_argument("--logo", type=Path, default=DEFAULT_LOGO)
    ap.add_argument("--font", type=Path, default=DEFAULT_FONT)
    ap.add_argument("--logo-w", type=float, default=0.060)
    ap.add_argument("--margin", type=float, default=0.009)
    ap.add_argument("--gap", type=float, default=0.0035)
    ap.add_argument("--name-h", type=float, default=0.0105)
    ap.add_argument("--tracking", type=float, default=0.005, help="spaziatura fra lettere (frazione cap height)")
    ap.add_argument("--stroke", type=float, default=0.4, help="spessore effettivo del nome in px (faux-bold via supersampling)")
    ap.add_argument("--opacity", type=int, default=235)
    ap.add_argument("--quality", type=int, default=88)
    args = ap.parse_args()

    if not args.font.exists():
        sys.exit(f"Font non trovato: {args.font}")
    if not args.logo.exists():
        sys.exit(f"Logo non trovato: {args.logo}")
    logo_img = Image.open(args.logo).convert("RGBA")

    files = [args.input] if args.input.is_file() else sorted(
        p for p in args.input.iterdir() if p.suffix.lower() in IMG_EXTS
    )
    if not files:
        sys.exit(f"Nessuna immagine in {args.input}")

    db = load_db()
    interactive = sys.stdin.isatty()
    # risolve il nome una volta sola sulla cartella (tutte le foto stesso fotografo)
    name = args.name or resolve_name(args.input, db, interactive=interactive, autosave=args.yes)

    for src in files:
        if args.in_place:
            dst = src
        elif args.output:
            dst = args.output / src.name
        else:
            dst = src.with_name(src.stem + "_wm" + src.suffix)
        watermark_image(
            src, dst, name, logo_img, args.font,
            logo_w_frac=args.logo_w, margin_frac=args.margin, gap_frac=args.gap,
            name_h_frac=args.name_h, tracking_frac=args.tracking, stroke_px=args.stroke,
            opacity=args.opacity, jpeg_quality=args.quality,
        )
        print(f"  {src.name} -> {dst.name}  [{name}]")


if __name__ == "__main__":
    main()
