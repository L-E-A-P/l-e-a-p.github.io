# REPORT TECNICO - SITO LEAP

**Data**: 2025-11-05
**Revisore**: Claude Code
**Versione Sito**: Jekyll 3.9.5 + So Simple Theme 3.2.0

---

## Stack Tecnologico

### Core
- **Jekyll**: 3.9.5
- **GitHub Pages**: 231
- **Tema**: So Simple 3.2.0 (remote theme)
- **Gestione dipendenze**: Ruby/Bundler con github-pages gem

### Frontend
- **SASS**: Con compilazione compressa
- **Skin**: Dark personalizzata (`assets/css/skins/dark.scss`)
- **Font**: Alegreya Sans, Alegreya, Ubuntu Mono (Google Fonts)
- **JavaScript**: Lunr search, Lity lightbox, smooth scroll

### Architettura
- **Collezioni**: 5 collezioni (`_salti`, `_saltati`, `_archidipietra`, `_domeniche`, `_lazzaro`)
- **Layout custom**: `postnoauth`, `project`
- **Configurazione**: Dual configuration (development/production)

---

## Questioni da Correggere

### 1. Web Manifest Incompleto ⚠️ PRIORITÀ ALTA

**File**: `site.webmanifest:2-3`
**Problema**: Campi `name` e `short_name` vuoti
**Impatto**: PWA/mobile experience compromessa

```json
{
    "name": "",  // ← vuoto
    "short_name": "",  // ← vuoto
    "icons": [...]
}
```

**Fix suggerito**:
```json
{
    "name": "LEAP - Laboratorio ElettroAcustico Permanente",
    "short_name": "LEAP",
    "icons": [...]
}
```

---

### 2. Timezone Duplicato ⚠️ PRIORITÀ MEDIA

**File**: `_config.yml:23` e `:93`
**Problema**: `timezone: Europe/Rome` dichiarato due volte
**Fix**: Rimuovere la duplicazione alla riga 93

---

### 3. Collezione Inutilizzata ⚠️ PRIORITÀ BASSA

**File**: `_config.yml:108-110`
**Problema**: Collezione `_saltati` configurata ma directory vuota
**Fix**:
- Opzione A: Rimuovere configurazione se non necessaria
- Opzione B: Popolare la collezione se serve

---

### 4. Node.js Requirement Obsoleto ⚠️ PRIORITÀ BASSA

**File**: `package.json:22`
**Problema**: `"node": ">= 0.10.0"` (versione del 2013)
**Fix**: Aggiornare a versione moderna (es. `">= 14.0.0"`)

---

## Raccomandazioni Architetturali

### A. Struttura Collezioni

**Permalink structure attuale**:
- Posts: `/:categories/:title/`
- Collections: `/:collection/:path/` oppure `/:collection/:title/`

**Osservazione**: La collezione `salti` è utilizzata come collezione per la homepage (`index.html:6`) ma anche come collezione separata. Verificare se questa sovrapposizione è intenzionale.

**Collezioni attive**:
```yaml
collections:
  salti:
    output: true
    permalink: /:collection/:title/
  saltati:
    output: true
    permalink: /:collection/:title/  # ← vuota
  archidipietra:
    output: true
    permalink: /:collection/:path/
  domeniche:
    output: true
    permalink: /:collection/:path/
  lazzaro:
    output: true
    permalink: /:collection/:path/
```

---

### B. Layout `postnoauth`

**File**: `_layouts/postnoauth.html:24-26`

Codice social sharing commentato:
```liquid
<!-- {% if page.share %}
  {% include social-share.html %}
{% endif %} -->
```

**Azioni possibili**:
- Rimuovere il codice commentato se non serve
- Riabilitarlo se necessario
- Valutare se il layout `postnoauth` è ancora necessario o se consolidare con `post`

---

### C. SEO e Performance

#### ✅ Aspetti Positivi

- Google Analytics configurato (G-QZM89XVDCT)
- jekyll-seo-tag installato e attivo
- Sitemap e feed RSS configurati
- Favicon completo con tutti i formati
- Disqus comments configurati (shortname: leap-2)
- Social share buttons implementati

#### 🔧 Da Migliorare

**1. Canonical URLs**

Configurati solo in production (`_config_production.yml:26`):
```yaml
canonical_url: "https://www.leaphz.net"
```
Verificare che in development non creino problemi di indicizzazione.

**2. Image Optimization**

Logo caricato da GitHub raw:
```yaml
logo: https://raw.githubusercontent.com/L-E-A-P/logo/main/2023-11-21-logo-web-sqare-key.png
```
- Considerare cache/CDN o hosting locale per performance
- Valutare formato WebP per dimensioni ridotte

**3. Theme Color Inconsistenza**

Web manifest (`site.webmanifest:16`):
```json
"theme_color": "#ffffff",
"background_color": "#ffffff"
```

Tema dark usa (`assets/css/skins/dark.scss:15`):
```scss
$background-color: #230031;
$accent-color: #89FF59;
```

**Fix suggerito**:
```json
"theme_color": "#230031",
"background_color": "#230031"
```

---

### D. Configurazione Dual Environment

Ottima implementazione development/production.

#### Suggerimenti

**1. Email Production**

`_config_production.yml:34`:
```yaml
email: info@leaphz.net  # Consider using production email
```
Commentato "Consider using..." - decidere email definitiva.

**2. URL Configuration**

Development (`_config.yml:26`):
```yaml
url: "https://l-e-a-p.github.io"
```

Production (`_config_production.yml:5`):
```yaml
url: "https://www.leaphz.net"
```

**3. Canonical URL nei Defaults**

`_config_production.yml:26` imposta canonical_url come valore nei defaults globali.
Potrebbe generare duplicazioni. Verificare output con:

```bash
bundle exec jekyll build --config _config.yml,_config_production.yml
grep -r "canonical" _site/ | head -5
```

---

## Ottimizzazioni Possibili

### 1. Performance

✅ **Già implementato**:
- CSS compression attiva (`sass: style: compressed`)
- Minification configurata (`package.json:35` - uglify script)

🔧 **Da considerare**:
- Lazy loading per immagini nelle collezioni
- Ottimizzazione immagini (WebP, compressione)
- Service Worker per PWA completa

### 2. Accessibilità

✅ **Già implementato**:
- Skip links presenti (`_layouts/default.html:15`)
- ARIA labels configurati (`aria-label="Content"`)
- Struttura semantica corretta (article, header, main)

🔧 **Da verificare**:
- Contrasto colori tema dark (Alice Blue #F0F8FF su viola #230031)
- Focus indicators per navigazione keyboard
- Alt text per tutte le immagini

### 3. Build Automation

**Stato attuale**: GitHub Pages build automatico (nessuna `.github/workflows/`)

**Considerare**:
- GitHub Actions workflow custom per controllo maggiore del build
- Preview deploy per pull requests
- Test automatici (link checker, HTML validator)

**Esempio workflow**:
```yaml
# .github/workflows/jekyll.yml
name: Build and Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
      - run: bundle exec jekyll build --config _config.yml,_config_production.yml
      - uses: actions/deploy-pages@v1
```

### 4. Documentazione

**README.md attuale**:
```bash
bundle exec jekyll build
bundle exec jekyll build --config _config.yml,_config_production.yml
```

**Suggerimenti per espansione**:

```markdown
# LEAP Website

## Setup
```bash
bundle install
```

## Development
```bash
bundle exec jekyll serve
# Visit http://localhost:4000
```

## Build
```bash
# Development build
bundle exec jekyll build

# Production build
bundle exec jekyll build --config _config.yml,_config_production.yml
```

## Struttura Collezioni

- `_salti/` - Eventi e attività del laboratorio
- `_lazzaro/` - Concerti e apparizioni LAZZARO
- `_archidipietra/` - Progetto Archi di Pietra
- `_domeniche/` - Domeniche al LEAP
- `_posts/` - Blog principale

## Convenzioni

### Naming Post
```
YYYY-MM-DD-titolo-del-post.md
```

### Front Matter Base
```yaml
---
title: "Titolo Post"
layout: post
image: path/to/image.jpg
excerpt_separator: "<!--more-->"
categories:
  - Categoria
tags:
  - Tag
---
```
```

---

## Struttura File Custom

### Layout Personalizzati

| Layout | Utilizzo | Note |
|--------|----------|------|
| `postnoauth.html` | Post senza autore/social | Social share commentato |
| `project.html` | Progetti collezioni | Include social + comments |
| `home.html` | Homepage | Usa collezione salti |
| `collection.html` | Pagine collezioni | Grid/list layout |

### Include Custom

| Include | Utilizzo |
|---------|----------|
| `home-saltati.html` | Lista saltati homepage |
| `home-salti.html` | Lista salti homepage |
| `home-leapers.html` | Lista leapers homepage |
| `documents-collection.html` | Display documenti collezione |
| `head-custom.html` | Favicon e meta custom |
| `footer-custom.html` | Footer personalizzazioni |

**Nota**: Verificare quali sono effettivamente utilizzati e considerare consolidamento.

---

## Plugin e Dipendenze

### Plugin Jekyll Attivi

```ruby
plugins:
  - jekyll-seo-tag
  - jekyll-sitemap
  - jekyll-feed
  - jekyll-paginate
  - jekyll-target-blank
```

### Dipendenze Node (package.json)

```json
"devDependencies": {
  "npm-run-all": "^4.1.5",
  "onchange": "^6.1.1",
  "uglify-js": "^3.13.6"
}
```

### Script NPM Disponibili

```bash
npm run uglify        # Minifica JavaScript
npm run add-banner    # Aggiunge banner copyright
npm run build:js      # Build completo JS (uglify + banner)
npm run watch:js      # Watch mode per sviluppo
```

---

## Configurazione Colori Tema Dark

**File**: `assets/css/skins/dark.scss`

```scss
/* Colors */
$base-color: #F0F8FF;           // Alice Blue
$text-color: #F0F8FF;           // Alice Blue
$accent-color: #89FF59;         // Verde lime
$nav-color: #F0F8FF;            // Alice Blue
$background-color: #230031;     // Viola scuro
$nav-background-color: mix(#000, $background-color, 40%);
$code-background-color: mix(#000, $background-color, 15%);
$border-color: tint($base-color, 80%);

/* Syntax Highlighting - Material Palenight */
$base00: #263238;
$base01: #2e3c43;
// ... altri colori
```

**Identità visiva coerente**: Viola #230031 come colore principale, verde lime #89FF59 come accent.

---

## Checklist Immediate

- [ ] Completare `site.webmanifest` (name/short_name)
- [ ] Rimuovere `timezone` duplicato in `_config.yml:93`
- [ ] Decidere destino collezione `_saltati` (rimuovere o popolare)
- [ ] Rimuovere codice commentato in `_layouts/postnoauth.html:24-26`
- [ ] Aggiornare Node.js requirement in `package.json:22`
- [ ] Allineare `theme_color` in manifest con tema dark (#230031)
- [ ] Decidere email production finale in `_config_production.yml:34`
- [ ] Verificare canonical URLs in build production

---

## Checklist Ottimizzazioni Future

### Breve Termine
- [ ] Ottimizzare immagini (WebP, compressione)
- [ ] Implementare lazy loading immagini
- [ ] Verificare contrasto colori per accessibilità
- [ ] Espandere README.md con documentazione completa
- [ ] Rimuovere include/layout non utilizzati

### Medio Termine
- [ ] Setup GitHub Actions per build custom
- [ ] Implementare preview deploy per PR
- [ ] Aggiungere test automatici (HTML validator, link checker)
- [ ] Considerare CDN per logo e immagini ricorrenti
- [ ] Service Worker per PWA completa

### Lungo Termine
- [ ] Valutare migrazione a Jekyll 4.x (quando compatibile con GitHub Pages)
- [ ] Internazionalizzazione (i18n) se necessario
- [ ] Analytics avanzati e privacy-focused (Plausible, Fathom)
- [ ] Sistema di newsletter integrato

---

## Note Finali

Il sito LEAP è **tecnicamente solido** e ben strutturato.

**Punti di forza**:
- Architettura collezioni ben pensata
- Dual configuration dev/production
- SEO e accessibilità di base implementati
- Tema custom coerente con identità visiva
- Documentazione codice presente

**Aree di miglioramento**:
- Alcune configurazioni incomplete (manifest, timezone)
- Potenziale per ottimizzazioni performance
- Documentazione utente da espandere

Tutte le questioni identificate sono **minori e facilmente risolvibili**. Non ci sono problemi critici che blocchino il funzionamento del sito.

---

**Report generato**: 2025-11-05
**Ultima revisione**: 2025-11-05
**Prossima revisione suggerita**: Dopo implementazione fix priorità alta/media
