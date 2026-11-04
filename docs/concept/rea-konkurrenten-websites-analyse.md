# REA-Technikanalyse: Konkurrenten-Websites im DACH-Mietverwaltungsmarkt

**Datum:** 28.10.2026  
**Analyst:** Hermes Agent / REA 6.7.0 + Browser-CDP  
**Scope:** Technischer Reverse-Engineering-Scan der öffentlichen Marketing-Websites von 7 Wettbewerbern. Keine Authentifizierung, keine Anmeldung, keine Brute-Force-Versuche.  
**Methodik:**
1. Browser-Öffnung via `browser_exec` + Tech-Stack-Extraktion (`window`, `document.scripts`, `performance`).
2. HTTP-Header-Erfassung via `curl -IL` (finaler Endpunkt nach Redirect).
3. CDP-Target-Listing via `rea list-browser-targets` (CDP-Port 39067) – Zugang vorhanden.
4. REA `analyze-web-bundle` auf ausgewählten SPA-Zielen (teilweise OOM, dokumentiert).
5. REA `analyze-javascript-application` auf heruntergeladenen JS-Bundles.
6. Statische String-Analyse der Bundles (Library-Erkennung, API-URLs, Source-Map-Checks).

---

## Zusammenfassung Matrix

| Site | CMS/Framework | Build-Tool | Hosting | API-Backend | Auth-Muster | CSP | Source-Maps | Auffälligkeit |
|---|---|---|---|---|---|---|---|---|
| immocloud.de | WordPress + WP Rocket | WP Rocket (PHP) | Apache/AlmaLinux | WordPress REST (geschützt 401) | PHP-Session/Cookie | ❌ | ❌ | klassisches WordPress-Setup |
| rentab.ly | React Router 7 SPA | Vite | Netlify Edge | **Supabase** `mypuvkzsgwanilduniup.supabase.co` | Supabase Auth (JWT) | ❌, aber HSTS | ❌ (SPA-Fallback auf .map) | komplett BaaS-Backend |
| hellohousing.de | WordPress + Custom Theme | Custom WP-Theme | Apache/Unix | WordPress REST (`wp-json`) | PHP-Session/Cookie | ❌ | ❌ | Intercom-Widget, CF7 |
| objego.de | TYPO3 CMS | TYPO3 | Platform.sh (Varnish) | keine öffentliche API erkennbar | Cookie-basiert | Report-Only (sehr lang) | ❌ | Marketing-Pixel-Wahnsinn |
| verwaltio.de | React SPA | Vite | nginx | SPA-Intern (keine `/api` erreichbar) | unbekannt | ❌ | ❌ | kleines Single-Chunk-Bundle |
| aedium.ai | React + Zustand SPA | Vite | nginx | `/zaehler/api/send` (Analytics) | unbekannt | ❌ | ❌ | eigene Mini-Analytics |
| immoware24.de | Next.js (Turbopack) | Next.js 15+ | nginx/Node.js | `/api` → Homepage-Fallback | externes Login-Portal `awi-rems.de` | ❌ | ❌ | separates Legacy-Login |

---

## 1. immocloud.de

### Browser-Analyse
- **URL geladen:** `https://www.immocloud.de/`
- **Title:** 🐴 Digitale Immobilienverwaltung mit immocloud » online & sicher
- **Meta-Generator:** WP Rocket 3.23.5.1
- **SPA-Root:** none (klassisches serverseitiges HTML)
- **Frameworks im `window`:** keine (kein Vue/React/Angular)
- **Externe Scripts:** Usercentrics CMP Loader, Google Tag Manager (`GTM-PWFC25V`), WP Rocket LazyLoad
- **Stylesheets:** keine externen CSS-Dateien, vermutlich inline/concatenated

### Network/CDP
- **Protokoll:** HTTP/1.1
- **Hauptdokument-Status:** 200
- **DOM Complete:** ~359 ms, Load: ~359 ms
- **Resource-Initiatoren:** 11× link, 4× img, 3× script, 3× css, 2× fetch, 1× iframe
- **Cookies:** keine bei erstem Besuch
- **localStorage:** `ucData`, `ucString` (Usercentrics)
- **API-Calls:** keine öffentlichen `/api/`-Endpunkte im initialen Load

### HTTP-Header (final)
```
HTTP/1.1 200 OK
Server: Apache/2.4.37 (AlmaLinux) OpenSSL/1.1.1k
X-Powered-By: PHP/8.4.27
Cache-Control: max-age=0
Vary: Accept-Encoding
```

### REA / Bundle-Analyse
- Keine SPA-Bundles vorhanden; Haupt-JS ist WP Rocket LazyLoad + CMP.
- `rea analyze-web-bundle` nicht sinnvoll anwendbar (kein SPA-Bundle).
- **Source-Maps:** keine.

### Security
- **CSP:** nicht gesetzt.
- **HSTS:** nicht gesetzt.
- **X-Frame-Options:** nicht gesetzt.
- **X-Content-Type-Options:** nicht gesetzt.

### Learnings für uns
- WordPress + WP Rocket ist schnell aufgesetzt, aber ein Sicherheits-Nachteil: kein HSTS, kein CSP, kein X-Frame.
- PHP/Apache-Stack ohne modernes CDN-Edge-Caching.

---

## 2. rentab.ly

### Browser-Analyse
- **URL geladen:** `https://rentab.ly/`
- **Title:** 🐴 Kostenlose Mietverwaltung Software für Vermieter | rentably
- **SPA-Root:** DIV (React Router SPA)
- **React Router Version:** 7.18.2 (im `window.__reactRouterVersion`)
- **Scripting:** ein einziges `type="module"`-Script (`/assets/index-CpHvY0wb.js` + dynamische Chunks)
- **Stylesheets:** `/assets/root-C0CubdmM.css`
- **Fonts:** Manrope (selbst gehostet)
- **Badges:** `bolt.new/badge.js` (StackBlitz/Bolt Marketing-Badge)

### Network/CDP
- **Protokoll:** HTTP/2
- **DOM Complete:** ~796 ms, Load: ~796 ms
- **Initiatoren:** 4× link, 1× script, 7× img, 47× other (viele preload/modulepreload), 3× fetch
- **Cookies:** keine initial
- **localStorage/sessionStorage:** leer

### HTTP-Header (final)
```
HTTP/2 200
server: Netlify
strict-transport-security: max-age=31536000
cache-control: public,max-age=0,must-revalidate
cache-status: "Netlify Edge"; hit; ttl=31535428
etag: "a709a515f0710dff8300d144e3d5f386-ssl"
```

### JavaScript-Bundles
| Bundle | Größe | Inhalt |
|---|---|---|
| `entry.client-CDex1E6d.js` | 5,8 KB | React Router Entry-Client |
| `index-CpHvY0wb.js` | 130,8 KB | Haupt-App |
| `supabase-BATMLokT.js` | 122,3 KB | Supabase-Client |
| `root-DDGFaF6E.js` | variabel | Root-Route |
| `AuthContext-DAb4lJq0.js` | variabel | Authentifizierungs-Kontext |
| `LanguageContext-CuN3Ex2t.js` | variabel | i18n |

**Erkannte Libraries:** React, React Router, Framer Motion, Lodash, Supabase.

### API-Backend
- Kein eigenes `/api`-Backend erreichbar.
- **Backend = Supabase:** `https://mypuvkzsgwanilduniup.supabase.co`
- `/api/health` liefert SPA-Fallback-HTML (Netlify rewrite), kein echtes Health-API.
- Authentifizierung läuft über Supabase Auth (JWT in localStorage/Cookie bei Login).

### REA-Analyse
- `rea list-browser-targets` erfolgreich; Target-ID `14BE08FF746448C4B8B43BB97A0A72E8`.
- `rea analyze-web-bundle` auf dem Target OOM (Bundle zu groß, 38 MB Heap-Limit).
- `rea analyze-javascript-application` auf `entry.client` erfolgreich: Lädt dynamisch `chunk-62JRHF6Z-BsNiBn-p.js`, `index-CpHvY0wb.js` etc.
- `rea analyze-javascript-application` auf `index-CpHvY0wb.js` OOM (Bundle zu groß).
- **Source-Maps:** `.js.map`-Probe liefert HTTP 200, aber der Body ist HTML (Netlify-SPA-Fallback). **Keine echten Source-Maps** öffentlich.

### Security
- **HSTS:** ✅ `max-age=31536000`
- **CSP:** ❌ nicht gesetzt.
- **X-Frame-Options:** nicht gesetzt (Netlify-Default fehlt).

### Performance
- Schnell durch Netlify-Edge-Caching und kleine initiale Payload.
- Viele Module werden vorgeladen (`modulepreload`).

### Learnings für uns
- **Supabase-BaaS-Architektur** ermöglicht sehr schlankes Frontend; man spart sich ein eigenes Backend.
- React Router 7 + Vite + Netlify ist ein modernes, schnelles Marketing-Site-Setup.
- Source-Map-Produktionsfallen vermeiden: Netlify-SPA-Fallback kann `.map`-URLs fälschlich als 200 ausliefern.

---

## 3. hellohousing.de

### Browser-Analyse
- **URL geladen:** `https://hellohousing.de/`
- **Title:** 🐴 Immobilienverwaltungssoftware mit KI-Assistent | hellohousing
- **Meta-Generator:** Site Kit by Google 1.189.0
- **SPA-Root:** DIV (nur Container, keine echte SPA)
- **CMS:** WordPress (Redirect von www auf non-www, PHP 8.4)
- **Theme:** Custom `hello-housing` (`/wp-content/themes/hello-housing/public/js/app.js`)
- **Plugins:** Contact Form 7, Complianz GDPR Premium, OMGF (Google Fonts lokal), Google Site Kit
- **Chat:** Intercom Widget (`vvrs5bx3`)
- **Tracking:** GTM `GTM-5FQGQLL`, GA4 `G-GRPRYDP4ZB`, Awin, Google Fonts lokal via OMGF

### Network/CDP
- **Protokoll:** HTTP/2
- **DOM Complete:** ~3.129 s, Load: ~3.131 s (langsamster in der Reihe)
- **Initiatoren:** 7× link, 13× script, 25× img, 7× video, 1× iframe, 5× fetch, 5× css, 1× xmlhttprequest
- **Cookies:** `_gcl_au`, `_ga`, `_ga_*`, `AwinChannelCookie`, `cmplz_consent_mode`
- **localStorage:** `_gcl_ls`
- **sessionStorage:** `cmplz_user_data`, `wpEmojiSettingsSupports`, `cmplz_id`
- **API-Calls:**
  - `https://hellohousing.de/wp-json/complianz/v1/banner?lang=de&locale=de_DE&token=...`
  - `https://hellohousing.de/wp-json/contact-form-7/v1/contact-forms/83/feedback/schema`

### HTTP-Header (final)
```
HTTP/2 200
server: Apache/2.4.68 (Unix)
x-powered-by: PHP/8.4.27
link: <https://hellohousing.de/wp-json/>; rel="https://api.w.org/"
vary: User-Agent
```

### JavaScript-Bundles
| Asset | Größe |
|---|---|
| `public/js/app.js` | 623,9 KB |
| `public/css/app.css` | 243,9 KB |

**Erkannte Libraries im Theme-JS:** Lodash (vermutlich WordPress-Core/Plugin-Inlining, keine klaren Framework-Marker).

### REA-Analyse
- Kein SPA-Bundle im klassischen Sinne; Theme-JS ist vermutlich jQuery/Vanilla-Mix.
- `rea analyze-javascript-application` auf `hellohousing.app.js` lieferte keine klaren Framework-Knoten (WordPress-Theme-JS).
- **Source-Maps:** keine.

### Security
- **CSP:** ❌
- **HSTS:** ❌
- **X-Frame-Options:** ❌
- WordPress-REST-API ist offen erreichbar (`wp-json/wp/v2/`), typisch für WordPress.

### Performance
- Mit ~3,1 s DOM Complete der langsamste; viele Bilder/Videos, 25+ Image-Requests.

### Learnings für uns
- WordPress + Custom Theme erlaubt schnelle Marketing-Iterationen, skaliert aber schlecht in Performance.
- Intercom als Support-Widget ist ein Muster, das wir für unseren KI-Chatbot berücksichtigen können.
- Complianz + CF7 zeigt, dass Consent-Management und Kontaktformulare Standard sind.

---

## 4. objego.de

### Browser-Analyse
- **URL geladen:** `https://www.objego.de/`
- **Title:** 🐴 objego Immobilienverwaltung | Für private Vermieter
- **Meta-Generator:** TYPO3 CMS
- **SPA-Root:** none (TYPO3 serverseitig)
- **Frameworks:** `hjBootstrap` (Hotjar-Bootstrap-Wrapper), sonst keine SPA-Frameworks
- **Tracking-Overload:** Taboola, Outbrain, HubSpot (hs-scripts, hs-banner, hs-analytics), Facebook Pixel, LinkedIn Insight, Bing Ads, Google Ads/GA4/GTM, Hotjar, Usercentrics CMP, Hyphenopoly

### Network/CDP
- **Protokoll:** HTTP/2
- **DOM Complete:** ~478 ms, Load: ~481 ms
- **Initiatoren:** 9× link, 27× script, 14× img, 18× fetch, 1× iframe, 2× other, 1× beacon, 2× xmlhttprequest
- **Cookies:** `_gcl_au`, `_ga`, `_ga_*`, `_fbp`, `_uetsid`, `_uetvid`, `aytcookie`, `ucData`, `ucString`
- **localStorage:** Tracking-Daten für Taboola, Bing, Usercentrics

### HTTP-Header (final)
```
HTTP/2 200
content-security-policy-report-only: ... (sehr lange Policy, viele erlaubte Drittanbieter)
referrer-policy: strict-origin-when-cross-origin
traceresponse: 00-... (OpenTelemetry)
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
x-xss-protection: 1; mode=block
via: 1.1 varnish, 1.1 varnish
x-served-by: cache-par-lfpb1150021-PAR, cache-fra-eddf8230025-FRA
x-cache: HIT, HIT
strict-transport-security: max-age=300
x-platform-cluster: tcj7t3lse6yx2-master-7rqtwti
```

### Hosting
- **Platform.sh** (erkennbar an `x-platform-*`-Headern und Varnish-Cache-Hits).
- **CDN/Cache:** Varnish mit Edge-Hits in Paris/Frankfurt.

### REA-Analyse
- Kein SPA-Bundle; TYPO3-Assets in `typo3temp/assets/js/...js?1793126629`.
- `rea analyze-web-bundle` nicht anwendbar.
- **Source-Maps:** keine.

### Security
- **CSP:** ✅ report-only, aber riesig und mit `'unsafe-inline'` / `'unsafe-eval'` (schwächt den Schutz ab).
- **HSTS:** ⚠️ nur `max-age=300` (5 Minuten, sehr kurz).
- **X-Frame-Options:** ✅ SAMEORIGIN.
- **X-Content-Type-Options:** ✅ nosniff.

### Learnings für uns
- TYPO3 + Platform.sh ist enterprise-tauglich, aber der Tracking-Overhead ist extrem.
- CSP `report-only` ist ein guter erster Schritt, aber die Policy ist zu permissive.
- Kurzes HSTS (300s) ist praktisch wirkungslos.

---

## 5. verwaltio.de

### Browser-Analyse
- **URL geladen:** `https://verwaltio.de/`
- **Title:** 🐴 Hausverwaltungssoftware mit KI kostenlos testen | Verwaltio
- **SPA-Root:** DIV
- **Frameworks:** React Router (`__reactRouterVersion`)
- **Build:** Vite (gehashte `assets/index-*.js`)
- **Icons:** Boxicons (`/boxicons/css/boxicons.min.css`)
- **Scripting:** ein einziges `type="module"`-Script `assets/index-wLutFtdc.js`

### Network/CDP
- **Protokoll:** HTTP/2
- **DOM Complete:** ~707 ms, Load: ~708 ms
- **Initiatoren:** 3× link, 3× script, 25× img, 27× css (Boxicons-Sprites/Fonts)
- **Cookies:** keine
- **localStorage/sessionStorage:** leer
- **API-Calls:** keine öffentlichen APIs im initialen Load

### HTTP-Header (final)
```
HTTP/2 200
server: nginx
strict-transport-security: max-age=31536000; includeSubDomains
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
x-xss-protection: 1; mode=block
alt-svc: h3=":443"; ma=2592000
```

### JavaScript-Bundles
| Bundle | Größe | Inhalt |
|---|---|---|
| `assets/index-wLutFtdc.js` | 284,8 KB | React SPA (Single-Chunk) |

**Erkannte Libraries:** React, Lodash.

### API-Backend
- `/api/` liefert 301 → `/api` → 404 (kein öffentliches API erreichbar).
- Keine Backend-URL im Bundle sichtbar (vermutlich Same-Origin oder versteckt im Login-Flow).

### REA-Analyse
- `rea list-browser-targets` erfolgreich; Target-ID `0EBDC2B95F71C45566EF6750C631B961`.
- `rea analyze-web-bundle` lieferte leeres Ergebnis (vermutlich wegen Bundle-Größe/Transfer-Limit).
- `rea analyze-javascript-application` auf dem 284-KB-Bundle erfolgreich; Evidence-ID `ev_e6d739dbd1f45d45a2de1c24449c44b71fa7f762105dd712baf820c432afbc57`.
  - Graph enthält Modulexporte `T`, `y`, `a`, `e`, etc.
  - Viele statische Beziehungen, aber keine offenen Endpunkte im öffentlichen Bundle.
- **Source-Maps:** `index-wLutFtdc.js.map` → 404.

### Security
- **HSTS:** ✅ mit `includeSubDomains`.
- **X-Frame-Options:** ✅ SAMEORIGIN.
- **X-Content-Type-Options:** ✅ nosniff.
- **CSP:** ❌ nicht gesetzt.

### Performance
- Kleines, monolithisches Bundle (284 KB) – schnell, aber wenig code-splitting.

### Learnings für uns
- Single-Chunk React SPA ist einfach, aber nicht optimal für größere Features.
- Gute Security-Basisheaders (HSTS, X-Frame, XCTO) ohne CSP.

---

## 6. aedium.ai

### Browser-Analyse
- **URL geladen:** `https://aedium.ai/`
- **Title:** 🐴 aedium — WEG-Selbstverwaltung, Hausverwaltung, Vermietung & Hausakte
- **SPA-Root:** DIV
- **Frameworks:** React (erkennbar an Bundle-Inhalten)
- **State-Management:** Zustand
- **Build:** Vite (gehashte `assets/index-*.js`)
- **Analytics:** Eigener Zähler-Server `/zaehler/script.js` + `/zaehler/api/send`

### Network/CDP
- **Protokoll:** HTTP/1.1 (Auffälligkeit: kein HTTP/2 trotz nginx)
- **DOM Complete:** ~649 ms, Load: ~652 ms
- **Initiatoren:** 2× script, 9× other, 3× link, 1× video, 6× css, 1× fetch
- **Cookies:** keine
- **localStorage/sessionStorage:** leer
- **API-Calls:** `https://aedium.ai/zaehler/api/send` (eigene Analytics)

### HTTP-Header (final)
```
HTTP/1.1 200 OK
Server: nginx
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-cache
```

### JavaScript-Bundles
| Bundle | Größe | Inhalt |
|---|---|---|
| `assets/index-BtIeFKyw.js` | 463,2 KB | React SPA mit Zustand |
| `assets/LandingRahmen-CRtHVV-w.css` | variabel | Landing-Page-CSS |

**Erkannte Libraries:** React, Zustand, Lodash, i18next (Deutsche Modulnamen wie `vorverarbeitung`, `LandingRahmen` deuten auf Vite + i18n hin).

### API-Backend
- `/api/` → 404.
- Eigener Analytics-Endpunkt `/zaehler/api/send` (POST-only, 405 auf GET).
- Kein öffentliches App-API erkennbar.

### REA-Analyse
- `rea analyze-web-bundle` OOM (Bundle zu groß).
- **Source-Maps:** `index-BtIeFKyw.js.map` → 404.

### Security
- **HSTS:** ✅.
- **X-Frame-Options:** ✅.
- **X-Content-Type-Options:** ✅.
- **CSP:** ❌.
- **HTTP/1.1:** überraschend; moderne nginx-Setups sollten HTTP/2 unterstützen.

### Performance
- Bundle 463 KB relativ groß für eine Landing Page; vermutlich viel i18n + UI-Komponenten.

### Learnings für uns
- Eigene, datenschutzfreundliche Analytics (`/zaehler`) statt Google Analytics ist ein starkes DSGVO-Muster.
- HTTP/1.1 ist ein klarer Performance-Nachteil – wir sollten HTTP/2 oder HTTP/3 erzwingen.

---

## 7. immoware24.de

### Browser-Analyse
- **URL geladen:** `https://www.immoware24.de/`
- **Title:** Immoware24 - Immobilienverwaltungssoftware für mehr Effizienz
- **SPA-Root:** none (Next.js serverseitig gerendert)
- **Framework:** Next.js (erkennbar an `__next_f`, `NEXT_DEPLOYMENT_ID`, `window.next`, `_next/static/chunks`)
- **Build:** Next.js mit Turbopack (`turbopack-3-ry682tkyiqk.js`)
- **CSS:** 54+ separate CSS-Chunks (CSS-Modules/Next.js-Chunking)
- **Login:** Externes Portal `https://www.awi-rems.de/` (vermutlich die eigentliche Anwendung)
- **Support:** Zendesk/HelpCenter `support.immoware24.de`
- **Content-Delivery:** `content.immoware24.de` (vermutlich CMS/Media-CDN)

### Network/CDP
- **Protokoll:** HTTP/2
- **DOM Complete:** ~852 ms, Load: ~852 ms
- **Initiatoren:** 58× link, 24× script, 2× other, 1× css, 2× fetch, 1× iframe, 1× xmlhttprequest, 1× beacon, 1× img
- **Cookies:** `first_touch_url=/`
- **localStorage/sessionStorage:** leer

### HTTP-Header (final)
```
HTTP/2 200
x-powered-by: Next.js
cache-control: s-maxage=360, stale-while-revalidate=31535640
x-nextjs-cache: HIT
x-nextjs-prerender: 1
x-nextjs-stale-time: 300
vary: rsc, next-router-state-tree, next-router-prefetch, next-router-segment-prefetch, Accept-Encoding
etag: "..."
strict-transport-security: max-age=31536000; includeSubDomains
```

### JavaScript-Bundles
- 24+ Next.js-Chunks (`/_next/static/chunks/*.js`), davon getestet:
  - `00dlb79z7y3s4.js` – 51 KB
  - `0a-rekt06v0sv.js` – 13,6 KB
  - `0cz1d0mv5g_q7.js` – 110 KB
  - `0jeeh9uatlf0l.js` – 5,2 KB
  - `0rm1vr52gy-hq.js` – 189,6 KB
- Einige Chunks enthalten klar lesbare CSS-Modul-Namen (`S9bdca_topBar`, `bWmC4q_layout`, etc.) – kein Source-Map nötig, um Komponenten-Struktur zu erahnen.

### API-Backend
- `/api/` liefert die Next.js-Homepage zurück (Fallback-Rewrite), kein öffentliches API.
- Die eigentliche App läuft auf `awi-rems.de`.

### REA-Analyse
- `rea list-browser-targets` erfolgreich; Target-ID `479875553098D76438E471800B576D7A`.
- `rea analyze-web-bundle` OOM auf großem Next.js-Bundle.
- **Source-Maps:** keine `.map`-URLs in den Chunks.

### Security
- **HSTS:** ✅ mit `includeSubDomains`.
- **X-Frame-Options:** nicht explizit im finalen Header (Next.js-Default fehlt hier).
- **CSP:** ❌.
- **Next.js-spezifische Header:** `x-nextjs-prerender`, `x-nextjs-cache` (verrät Build/Cache-Strategie).

### Performance
- Viele kleine Chunks (24+ Scripts, 54+ CSS) – Next.js-Optimierung, aber viele Roundtrips.
- SWR-Caching (`stale-while-revalidate=31535640`) für statische Pages.

### Learnings für uns
- Next.js + Turbopack + SWR-Caching ist das modernste Setup im Vergleich.
- Marketing-Website und Anwendung sind getrennt (immoware24.de vs. awi-rems.de) – ein Muster, das wir für SEO/Performance prüfen sollten.
- CSS-Modul-Namen in Next.js-Chunks bleiben lesbar (keine Umbenennung), was Reverse Engineering erleichtert.

---

## Querschnittsbefunde

### Tech-Stack-Trends
- **React-Dominanz:** 4 von 7 modernen Wettbewerbern setzen React (rentab.ly, verwaltio.de, aedium.ai, immoware24.de).
- **Vite-Hegemonie:** 3 der 4 React-SPAs nutzen Vite (rentab.ly, verwaltio.de, aedium.ai).
- **WordPress bleibt relevant:** immocloud.de und hellohousing.de nutzen WordPress für Marketing.
- **TYPO3:** objego.de zeigt Enterprise-CMS mit starker Tracking-Integration.

### Backend-Architekturen
- **Supabase/BaaS:** rentab.ly setzt komplett auf Supabase.
- **WordPress REST:** hellohousing.de nutzt WP-REST für Consent + Kontaktformular.
- **Separate Legacy-App:** immoware24.de trennt Marketing (Next.js) und App (awi-rems.de).
- **Keine öffentliche API:** verwaltio.de und aedium.ai verbergen ihre APIs hinter Login.

### Auth-Muster
- **Session/Cookie:** WordPress/TYPO3-Seiten.
- **Supabase Auth/JWT:** rentab.ly (JWT wird im Login-Flow in localStorage/Cookie landen).
- **Externes SSO/Portal:** immoware24.de.
- **Unbekannt:** verwaltio.de, aedium.ai (keine öffentlichen Login-Seiten gescannt).

### Security-Gaps (branchenweit)
- **Keiner der 7 hat eine Content-Security-Policy (CSP) im Enforce-Modus.**
- **HSTS fehlt** bei immocloud.de und hellohousing.de (Apache/PHP).
- **X-Frame-Options** fehlt bei immocloud.de, hellohousing.de, rentab.ly.
- **Source-Maps** sind nirgends öffentlich verfügbar – alle sind produktionssicher.

### Performance-Vergleich (gemessene DOM-Complete)
| Site | DOM Complete | Protokoll | Bemerkung |
|---|---|---|---|
| immocloud.de | ~359 ms | HTTP/1.1 | schlankes WP |
| rentab.ly | ~796 ms | HTTP/2 | SPA + Preloads |
| hellohousing.de | ~3.129 ms | HTTP/2 | viele Medien |
| objego.de | ~478 ms | HTTP/2 | viele Tracker |
| verwaltio.de | ~707 ms | HTTP/2 | kleines Bundle |
| aedium.ai | ~649 ms | HTTP/1.1 | großes Bundle |
| immoware24.de | ~852 ms | HTTP/2 | viele Chunks |

---

## Empfehlungen: Was wir übernehmen sollten

1. **Frontend-Stack:** React + Vite für Marketing-SPA, Next.js für SEO-starke Content-Seiten. Kombination aus beiden ist sinnvoll.
2. **Backend:** Supabase als BaaS-Option prüfen (rentab.ly-Vorbild) für schnelles MVP; langfristig eigene API für komplexe Mietverwaltungslogik.
3. **Security-Headers:** Mindestens HSTS (1 Jahr, includeSubDomains), X-Frame-Options, X-Content-Type-Options, Referrer-Policy. CSP im Report-Only-Modus als nächster Schritt.
4. **Performance:** HTTP/2 oder HTTP/3 erzwingen, Assets komprimieren, Code-Splitting nutzen (Next.js/Vite), CSP-konforme eigene Analytics wie aedium.ai erwägen.
5. **Marketing/App-Trennung:** Wie immoware24.de – Landing-Page vom produktiven Tenant-Portal trennen (bessere SEO, Sicherheit, Skalierung).
6. **Source-Maps:** Produktions-Builds ohne öffentliche `.map` ausliefern (alle Konkurrenten machen das richtig).
7. **Consent-Management:** Usercentrics oder Complianz als CMP einplanen, da alle Konkurrenten CMPs einsetzen.

---

## REA-Einsatz: Ergebnisse & Limitationen

- **CDP-Zugang:** ✅ vorhanden über `http://127.0.0.1:39067` (DevToolsActivePort aus Chrome-Profil).
- **Browser-Targets:** Alle 7 Seiten gleichzeitig als CDP-Targets gelistet.
- **`analyze-web-bundle`:** Auf rentab.ly, aedium.ai und immoware24.de mit **JavaScript-Heap-OOM** abgebrochen (Bundles zu groß für Standard-Heap). Auf verwaltio.de lieferte es leeres Ergebnis.
- **`analyze-javascript-application`:**
  - ✅ rentab.ly entry client (5,8 KB): erfolgreich analysiert, Evidence-ID `ev_767ca0cc2257574e9d88953ed2cbce5e4c3ed93ece1d58a6f716f81e3a203637`.
  - ✅ verwaltio.de index (284 KB): erfolgreich analysiert, Evidence-ID `ev_e6d739dbd1f45d45a2de1c24449c44b71fa7f762105dd712baf820c432afbc57`.
  - ❌ aedium.ai / rentab.ly index / hellohousing.app.js: OOM oder keine klaren Framework-Knoten.
- **Source-Map-Recovery:** Nicht möglich, da keine echten `.map` öffentlich verfügbar.
- **Fazit:** REA liefert beste Ergebnisse bei kleinen bis mittleren SPA-Bundles; für große Next.js/Vite-Chunks ist statische String-Analyse + Browser-Daten effizienter.

---

## Anhang: Untersuchte Dateien & Befehle

- Browser-Performance-Daten: `/root/mietverwaltung/rea-perf-data.json`
- Heruntergeladene JS-Bundles: `/root/mietverwaltung/rea-bundles/`
- REA-Analyse-Verzeichnisse: `/root/mietverwaltung/rea-apps/`
- REA-Evidence-Ausgaben: `/root/mietverwaltung/rea-rentab-js.json`, `/root/mietverwaltung/rea-verwaltio-js.json`
