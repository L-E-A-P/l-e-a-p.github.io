# Watermark LEAP

Applica il watermark storico alle foto: monogramma **LEAP** bianco in basso a
sinistra e, sotto, il **nome del fotografo** in *Datalegreya Thin* (carattere che
mostra glifi maiuscoli dai tasti minuscoli — il testo viene reso minuscolo prima
del disegno). Sostituisce il flusso manuale con app a pagamento.

## Setup
```bash
pip3 install --user Pillow pyyaml
```

## Uso
```bash
# nome dedotto dalla sigla nel percorso (.../<sigla>/edit/)
./watermark.py ../../images/posts/EVENTO/ac/edit --in-place

# contributore occasionale: cartella "nome-cognome", normalizzata al volo
./watermark.py ../../images/posts/EVENTO/marco-iacobucci/edit --in-place

# nome esplicito + cartella d'uscita separata (default: copie con suffisso _wm)
./watermark.py foto_in/ -n "Alice Cortegiani" -o foto_out/
```

`--in-place` sovrascrive i file di input: usarlo sulle immagini in `edit/`,
tenendo gli originali senza logo in `org/`.

## Risoluzione del nome fotografo
1. `--name "Nome Cognome"` esplicito;
2. cartella `nome-cognome` → normalizzata (es. `marco-iacobucci` → *Marco Iacobucci*);
3. sigla nel percorso → cercata in [`photographers.yml`](photographers.yml);
4. sigla ignota → la chiede e (in terminale interattivo) la salva nello yaml
   (`-y` per salvare senza chiedere conferma).

**Convenzione:** core LEAPHZ con sigla breve nel yaml; contributori occasionali
con cartella `nome-cognome` (così il database resta pulito).

## Geometria
Parametri come frazioni del **lato lungo** dell'immagine (così il watermark è
coerente fra orizzontali e verticali; default tarati sugli esempi storici):
`--logo-w 0.060`, `--margin 0.009`, `--gap 0.0035`,
`--name-h 0.0105`, `--tracking 0.005` (spaziatura lettere, frazione cap height).

Il **corpo del nome** si regola con `--stroke` (default `0.4`), espresso in
**px effettivi**: il testo è disegnato a `SS×` (supersampling) e poi rimpicciolito
con anti-aliasing, così lo spessore è continuo invece che a salti di 1px — è ciò
che dà il peso "intermedio" tra Datalegreya Thin puro e il faux-bold a 1px.

Anche `--opacity` (default 235) e `--quality` (JPEG, 88).

## Asset
- Font: `../../assets/fonts/Datalegreya-Thin.otf`
- Logo: `leap-logo-w.png` (copia di `logo/2023-11-12-logo-kern-w.png`)
