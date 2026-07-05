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
