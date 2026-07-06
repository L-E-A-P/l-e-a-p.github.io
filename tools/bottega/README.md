# 🏺 Bottega — pipeline dei progetti di Bottega Radicale

Script per pubblicare le sessioni di lavoro della bottega
([leaphz.net/bottega](https://www.leaphz.net/bottega/), submodule `_bottega`).
Si appoggiano a [organize](../organize/) e [watermark](../watermark/): questa
è la loro orchestrazione specifica per la struttura a progetti/sessioni.

## `process-session.sh` — una sessione, dall'inizio alla fine

```bash
tools/bottega/process-session.sh _bottega/img/<progetto>/<sessione> <sigla>
# es.
tools/bottega/process-session.sh _bottega/img/flux-ferracuti/2024-02-12 ac
```

In ordine: converte gli eventuali **HEIC** in jpg (`sips`, con gli originali
`.heic` archiviati in `raw/` e guard anti-overwrite per i doppi export
iPhone), lancia `organize.py` (rinomina `<sessione>-NN`, genera
`org/edit/thumb`), **verifica i conteggi** (org = edit = thumb = sorgenti),
elimina i file sorgente ormai duplicati e applica il **watermark** agli
`edit/`. Idempotente nel senso che rifiuta di girare se `org/` esiste già.

## `make-hero.py` — testata e thumbnail di un progetto

```bash
python3 tools/bottega/make-hero.py <foto-sorgente> _bottega/img/<progetto>
# es.
python3 tools/bottega/make-hero.py \
  _bottega/img/flux-ferracuti/2024-02-12/ac/org/2024-02-12-16.jpg \
  _bottega/img/flux-ferracuti
```

Genera `<progetto>-hero.jpg` (1600×800) e `<progetto>-t.jpg` (800×800) con
taglio centrale (convenzione hero/-t di lazzaro). Sorgente consigliata: il
file in `org/` (piena risoluzione); per soggetti verticali il taglio hero
sarà una fascia centrale — sceglere foto orizzontali quando possibile.

## In arrivo

- `cull.sh` — sfinimento di gallerie pubblicate col metodo *demote, non
  delete*: `org/NN` → `raw/`, rimozione di `edit/NN` e `thumb/NN`, numeri
  mai riassegnati. Finché non esiste: fare i tre passaggi a mano.
