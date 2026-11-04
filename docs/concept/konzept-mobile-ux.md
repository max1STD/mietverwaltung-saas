# Mobile-UX-Konzept für MietVerwaltung

**Projekt:** MietVerwaltung SaaS — Apple-Style, Responsive für PC/Handy/iPad  
**Brand:** Navy `#0D3B70`, Background `#f5f5f7`, Font `-apple-system, SF Pro, system-ui`  
**Ziel:** „Auf dem Handy genauso schnell und ruhig wie auf dem MacBook“ — <30-Sekunden-Flows, keine Reibung, offline-resilient.

---

## 0. Design-Grundlagen & Token-System (Mobile-first)

Wir gehen Mobile-first, aber die Tokens gelten für alle Breakpoints. Damit bleiben Layout, Farbe und Motion konsistent.

```css
:root {
  /* Brand */
  --navy: #0D3B70;
  --navy-light: #2a5a9e;
  --navy-dark: #082a52;
  --bg: #f5f5f7;
  --card: #ffffff;
  --text: #1d1d1f;
  --text2: #86868b;
  --border: #d2d2d7;

  /* Semantik */
  --success: #34c759;
  --warning: #ff9500;
  --danger: #ff3b30;
  --info: #007aff;
  --highlight: #ffcc00;

  /* Radius */
  --radius-xl: 24px;
  --radius-lg: 18px;
  --radius-md: 12px;
  --radius-sm: 8px;

  /* Schatten */
  --shadow-card: 0 1px 3px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
  --shadow-float: 0 8px 30px rgba(0,0,0,0.12);

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Touch */
  --touch-min: 44px;
  --touch-comfort: 48px;

  /* Safe-Area */
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left: env(safe-area-inset-left, 0px);
  --safe-right: env(safe-area-inset-right, 0px);
}

/* iOS: Zoom auf Inputs verhindern */
input, select, textarea { font-size: 16px; }
```

---

## 1. Responsive-Breakpoints

| Breakpoint | Gerät | Layout-Strategie | Sidebar | Navigation |
|------------|-------|------------------|---------|------------|
| `< 640px` | Smartphone | Single-Column, Full-Screen Cards, Bottom-Tabbar | ❌ keine | Bottom-Tabbar (Mieter) / Drawer (Vermieter) |
| `640px – 1024px` | Tablet (iPad) | Adaptive 2-Spalten, größere Cards | Collapsible Rail (72px) oder Drawer | Rail + Overflow-Menü |
| `> 1024px` | Desktop | Multi-Spalten-Dashboard, Sidebar offen | ✅ 260px Sidebar | Sidebar-Navigation |

**Media Queries (Tailwind-CSS / Custom):**

```css
/* Mobile-first Standard */
.page { padding: 16px; padding-bottom: calc(80px + var(--safe-bottom)); }

/* Tablet */
@media (min-width: 640px) {
  .page { padding: 24px; padding-bottom: 24px; }
  .cards-grid { grid-template-columns: repeat(2, 1fr); gap: 20px; }
  .rail { width: 72px; display: flex; }
}

/* Desktop */
@media (min-width: 1024px) {
  .sidebar { display: flex; width: 260px; }
  .main { margin-left: 260px; }
  .cards-grid { grid-template-columns: repeat(3, 1fr); gap: 24px; }
}
```

### Layout-Verhalten pro Gerät

**Smartphone:**
- Eine Spalte, Cards übers ganze Display (`margin: 0 12px`).
- Header ist sticky oben, 56px hoch.
- Inhaltscrollbarer Bereich endet **oberhalb** der Bottom-Tabbar.
- Modale öffnen sich Bottom-Sheet von unten (`border-radius: 24px 24px 0 0`).

**Tablet:**
- Dashboard-KPIs in 2 Spalten, Listen nehmen 60 %, Details 40 % bei Split-View.
- Sidebar wird zum 72px-Rail mit Icons + Labels unter dem Icon.
- Bottom-Tabbar entfällt.

**Desktop:**
- Volle 260px-Sidebar mit Gruppen, Search, Profil-Footer.
- Dashboard mit 3-Spalten-KPIs, rechte Seite Quick-Actions / Aktivitäten.
- Modale zentriert (`max-width: 560px`).

---

## 2. Mobile-Navigation

### 2.1 Vermieter auf Handy

Vermieter brauchen mehr Features als Mieter. Eine Bottom-Tabbar mit 5 Items wird zu voll. Lösung: **Kombination aus Bottom-Tabbar (Top-4) + zentralem Floating-CTA + Drawer für den Rest.**

```css
.mobile-tabbar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: calc(64px + var(--safe-bottom));
  padding-bottom: var(--safe-bottom);
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}

.mobile-tabbar-item {
  flex: 1;
  height: var(--touch-min);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text2);
  position: relative;
}

.mobile-tabbar-item.active { color: var(--navy); }
.mobile-tabbar-item svg { width: 22px; height: 22px; }
```

**Vermieter-Bottom-Tabbar (4 Items):**

| Tab | Icon | Ziel |
|-----|------|------|
| Dashboard | Haus | Start, KPIs, offene Tickets |
| Objekte | Gebäude | Objektliste, Einheiten, Mieter |
| Tickets | Werkzeug | Ticket-Inbox, Status |
| Mehr | Menü | Drawer öffnet: Kosten, Abrechnung, Dokumente, Einstellungen |

**Floating Action Button (FAB) für schnelles Erstellen:**

```css
.fab {
  position: fixed;
  bottom: calc(84px + var(--safe-bottom));
  right: 20px;
  width: 56px; height: 56px;
  border-radius: 50%;
  background: var(--navy);
  color: #fff;
  box-shadow: var(--shadow-float);
  display: flex; align-items: center; justify-content: center;
  z-index: 110;
}
```

Auf Tap öffnet sich ein **Speed-Dial** mit: Ticket, Kosten erfassen, Beleg scannen, Mieter anlegen, Dokument hochladen.

### 2.2 Mieter auf Handy

Mieter brauchen nur 3 Tabs — perfekt für eine ruhige Bottom-Tabbar (siehe Skill-Vorgabe).

| Tab | Icon | Inhalt |
|-----|------|--------|
| Start | Haus | Mietdaten, offene Tickets, nächste Zahlung |
| Tickets | Werkzeug | Tickets erstellen + Verlauf |
| Dokumente | Dokument | Abrechnungen, freigegebene Dokumente |

**Kein Hamburger-Menü für Mieter.** Alles ist in 3 Tabs erreichbar. Reduziert kognitive Belastung (Hick's Law).

### 2.3 Tablet

- 72px-Rail links, Icons + 9px-Label darunter.
- Aktiver Tab hat Navy-Hintergrund + weißes Icon.
- Overflow-Items (z. B. Abrechnung, Einstellungen) in einem „Mehr“-Menü unten.

### 2.4 Desktop

- Volle 260px-Sidebar wie im bestehenden Mockup.
- Maximal 5–7 Hauptpunkte (Cognitive Load Theory).
- Subnavigation via Tabs im Content-Bereich, nicht in der Sidebar.

---

## 3. Touch-Targets

### Mindestgrößen

| Element | Mindestgröße | Comfort-Size | Begründung |
|---------|--------------|--------------|------------|
| Buttons | 44 × 44 px | 48 × 48 px | Apple HIG / Material 3 |
| List-Items | 44 px hoch | 52 px hoch | Daumen-Tipp ohne Nachbarn |
| Tabbar-Items | 44 × 44 px | 56 × 48 px | Bottom-Bar muss treffsicher sein |
| FAB | 56 × 56 px | — | Prominenter CTA |
| Checkboxen / Switches | 44 × 44 px Tap-Area | — | Visuell kleiner, aber Hit-Area groß |
| Form-Inputs | 48 px hoch | 56 px hoch | Große Finger, schnelle Eingabe |
| Icon-Buttons | 44 × 44 px | — | Header-Icons |

```css
.touch-min {
  min-width: var(--touch-min);
  min-height: var(--touch-min);
}

.hit-area {
  position: relative;
}
.hit-area::after {
  content: '';
  position: absolute;
  inset: -8px; /* vergrößert tippbare Fläche um 8px */
}
```

### Abstände

- Zwischen zwei Touch-Targets: **mindestens 8 px**, besser 12 px.
- Card-Padding: 16 px (mobile), 20 px (tablet), 24 px (desktop).
- Section-Gap: 24 px.
- Form-Field-Gap: 20 px (Label + Input + Error enger zusammen, aber Felder untereinander mit 20 px).

### Daumen-Ergonomie

- Primäre Aktionen in der unteren Bildschirmhälfte platzieren.
- Submit-Buttons immer **direkt unter dem letzten Feld**, nicht oben rechts.
- Destruktive Aktionen (Löschen) weit weg vom Primary-Button, z. B. ganz unten links.
- Bottom-Sheets für modale Aktionen, damit der Daumen den Close-Button und die CTA erreicht.

---

## 4. Mobile-Forms

### Grundprinzipien

- Große Inputs, keine Zoom-Probleme (`font-size: 16px` auf iOS zwingend).
- Smart Defaults (Umlage nach qm, Abrechnungsperiode 1.1.–31.12.).
- Ein Feld pro Zeile auf Mobile.
- Tastatur-Typ passend zum Input (`type="tel"`, `type="email"`, `inputmode="numeric"`).
- Inline-Validierung nach Verlassen des Feldes, nicht erst beim Submit.

### Input-Styling

```css
.form-group { margin-bottom: 20px; }

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  height: 48px;
  padding: 0 14px;
  font-size: 16px; /* Verhindert iOS-Zoom */
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--text);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: var(--navy);
  box-shadow: 0 0 0 3px rgba(13,59,112,0.12);
}

.form-input::placeholder { color: var(--text2); }
```

### Floating Labels (optional, Apple-Style)

```html
<div class="float-group">
  <input id="kosten" class="float-input" placeholder=" " />
  <label for="kosten" class="float-label">Kostenbetrag</label>
</div>
```

```css
.float-group { position: relative; }
.float-label {
  position: absolute;
  left: 14px; top: 14px;
  font-size: 16px; color: var(--text2);
  pointer-events: none;
  transition: 0.15s;
}
.float-input:focus ~ .float-label,
.float-input:not(:placeholder-shown) ~ .float-label {
  top: 6px; font-size: 11px; color: var(--navy);
}
```

### Smart Defaults

| Feld | Default | Warum |
|------|---------|-------|
| Umlageart | `nach_qm` | Häufigste Regelung |
| Abrechnungszeitraum | 01.01.2026 – 31.12.2026 | Kalenderjahr |
| Kosten-Datum | Heute | Belege meist aktuell |
| Priorität | `normal` | Vermeidet Panik-Klicks |
| Ticket-Kategorie | Vorausgewählt per KI-Bildanalyse | Spart Zeit |

### Stepper-Formulare (Wizard)

Komplexe Flows (z. B. Abrechnung) werden als Bottom-Sheet-Wizard mit 3–4 Steps dargestellt.

```css
.wizard-stepper {
  display: flex; gap: 8px;
  margin-bottom: 24px;
}
.wizard-dot {
  flex: 1; height: 4px; border-radius: 2px;
  background: var(--border);
}
.wizard-dot.active { background: var(--navy); }
.wizard-dot.completed { background: var(--success); }
```

---

## 5. Mobile-Ticket-Flow: Foto → Ticket → Absenden in <30 Sekunden

### Flow-Schritte

1. **Start:** Mieter tippt im Ticket-Tab auf großen CTA „Neues Ticket“.
2. **Foto aufnehmen:** Native Kamera öffnet sich (via `<input type="file" accept="image/*" capture="environment">`).
3. **KI-Analyse:** Bild wird im Hintergrund analysiert (Schimmel? Heizung? Wasser?).
4. **Vorausgefülltes Formular:** Kategorie, Titel, Priorität werden vorgeschlagen.
5. **Bestätigen:** Mieter kann Beschreibung ergänzen, Kategorie korrigieren.
6. **Absenden:** Ein Tap, sofortige Bestätigung + Push.

### UI-Struktur

```css
.ticket-create-sheet {
  position: fixed; inset: 0; top: auto;
  height: 92vh;
  background: var(--card);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  padding: 16px 20px calc(20px + var(--safe-bottom));
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}
.ticket-create-sheet.open { transform: translateY(0); }
```

### Mockup-Beschreibung

- **Start-Screen:** Oben „Hallo [Name]“, darunter große Karte „Was ist passiert?“ mit Kamera-Icon. Darunter Liste offener Tickets.
- **Foto-Screen:** Vollbild-Kamera-Placeholder, großer Auslöser-Button unten mittig (80 px Kreis), Galerie-Icon links unten.
- **Vorschau-Screen:** Bild oben (40 % Höhe), darunter vorausgefüllte Felder: Kategorie (z. B. „Heizung“), Titel (KI-generiert: „Heizkörper im Wohnzimmer wird nicht warm“), Priorität (Badge).
- **Bestätigen:** Beschreibung als Textarea (optional), CTA „Ticket an Vermieter senden“ (volle Breite, 52 px hoch, Navy).
- **Success-Screen:** Grünes Häkchen, Text „Ticket TKT-2026-017 wurde erstellt.“, Button „Zurück zur Übersicht“.

### Performance-Ziel

```text
0.0s  Kamera öffnet
0.5s  Foto aufgenommen
1.5s  KI-Analyse abgeschlossen (Lokal/OCR + Keyword-Classifier)
3.0s  Vorschau sichtbar
5.0s  Ticket abgesendet
```

### Zusätzliche Inputs

- Voice-to-Text für Beschreibung (Icon neben Textarea).
- Schnell-Kategorie-Chips unter dem Bild (Heizung, Wasser, Elektrik, Schimmel, Sonstiges).
- „Dringend“-Switch mit Warnfarbe, falls KI „Wasser“ oder „Heizung im Winter“ erkennt.

---

## 6. Mobile-Kosten-Erfassung: Beleg fotografieren → KI extrahiert → bestätigen

### Flow

1. Vermieter tippt FAB → „Beleg scannen“.
2. Kamera öffnet, Foto vom Beleg.
3. Lokales OCR + KI extrahiert: Betrag, Datum, Anbieter, Kategorie, Umlagefähigkeit.
4. Vorschau-Formular mit extrahierten Werten.
5. Nutzer prüft/bearbeitet und tippt „Kosten speichern“.

### UI-Komponenten

```css
.scan-frame {
  position: absolute; inset: 10%;
  border: 2px solid var(--navy);
  border-radius: var(--radius-lg);
  box-shadow: 0 0 0 9999px rgba(0,0,0,0.5);
}

.scan-hint {
  position: absolute; bottom: 18%; left: 0; right: 0;
  text-align: center; color: #fff;
  font-size: 14px; text-shadow: 0 1px 3px rgba(0,0,0,0.4);
}
```

### Mockup-Beschreibung

- **Scan-Screen:** Kamera-Viewfinder mit weißem Rahmen und Hinweis „Beleg vollständig ins Rechteck halten“. Blitz-Icon, Galerie-Icon.
- **Verarbeitungs-Screen:** Belegbild oben, darunter animierte Scan-Leiste, Text „KI liest Beleg aus…". Skelett-Inputs für Betrag, Datum, Anbieter.
- **Bestätigungs-Screen:**
  - Beleg-Thumbnail oben rechts (zoombar).
  - Felder: Betrag, Datum, Anbieter, Kategorie (Dropdown), Umlagefähig (Switch), Umlageart (Dropdown).
  - Vorausgefüllte Werte sind grün markiert (`border-color: var(--success)`), falls KI-Confidence hoch.
  - CTA „Speichern & zur Abrechnung hinzufügen“.
- **Success-Screen:** „Kosten gespeichert“ + Badge „Verteilt nach qm“.

### KI-Fallback

- Wenn OCR keine Daten findet: „Wir konnten den Beleg nicht auslesen. Bitte Betrag manuell eingeben.“
- Bei Unsicherheit: Feld wird gelb markiert, Nutzer muss bestätigen.
- Kein Auto-Save ohne Bestätigung — Vermieter haftet für Zahlen.

---

## 7. Gestures

### 7.1 Swipe-to-Delete / Swipe-to-Archive

In Listen (Tickets, Kosten, Dokumente, Mieter) kann der Nutzer nach links swipen, um sekundäre Aktionen zu zeigen.

```css
.swipeable-row {
  position: relative;
  overflow: hidden;
}
.swipe-actions {
  position: absolute; right: 0; top: 0; bottom: 0;
  display: flex;
  background: var(--bg);
}
.swipe-action {
  width: 80px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: #fff; font-size: 11px;
}
.swipe-action.delete { background: var(--danger); }
.swipe-action.archive { background: var(--navy); }
```

**Verhalten:**
- Swipe 0–80 px: zeigt erstes Action-Icon.
- Swipe > 80 px: zeigt zweites Icon.
- Tap außerhalb schließt.
- Keine sofortige Löschung ohne Bestätigung — stattdessen „Löschen?“-Button im revealed State.

### 7.2 Pull-to-Refresh

```css
.ptr-spinner {
  height: 50px;
  display: flex; align-items: center; justify-content: center;
  color: var(--navy);
  transform: translateY(-50px);
  transition: transform 0.2s;
}
.ptr-pulling .ptr-spinner { transform: translateY(0); }
```

- Auf Ticket-Listen, Dashboard, Dokumenten-Liste.
- Nur wenn Netzwerk vorhanden; bei Offline zeigt stattdessen „Offline-Modus“-Chip.

### 7.3 Swipe zwischen Tabs

Im Mieter-Portal (Start / Tickets / Dokumente) kann der Nutzer horizontal swipen, um zwischen Tabs zu wechseln.

```css
.tab-panorama {
  display: flex;
  width: 300vw;
  transition: transform 0.25s ease;
}
.tab-panel { width: 100vw; }
```

- Threshold: 50 px Swipe.
- Indikator unterhalb der Tabbar folgt der Bewegung (Pan-Animation).
- Auf Vermieter-Seiten mit komplexen Listen deaktiviert, um versehentliches Wechseln zu vermeiden.

### 7.4 Long-Press für Quick-Actions

- Long-Press auf Ticket-Card → „Status auf erledigt setzen“ oder „Kommentar hinzufügen“.
- Long-Press auf Mieter → „Anrufen / E-Mail / Ticket erstellen“.
- Haptic Feedback bei Long-Press (`navigator.vibrate(50)`).

---

## 8. Offline-Fähigkeit (PWA + Service Worker)

### Was funktioniert offline?

| Feature | Offline-Verhalten |
|---------|-------------------|
| Tickets ansehen | ✅ Letzte 50 Tickets aus Cache |
| Ticket-Details | ✅ Wenn vorher geladen |
| Dokumente lesen | ✅ Nur bereits heruntergeladene / vorab gecachte PDFs |
| Neues Ticket erstellen | ✅ Wird in Outbox gespeichert, automatisch synchronisiert |
| Beleg-Scan / Kosten | ✅ Bild + Daten lokal gespeichert, später Upload |
| Dashboard | ✅ Letzter Stand aus Cache, mit „Stand von 14:32“ |
| Abrechnung starten | ❌ Blockiert, Hinweis „Verbindung nötig“ |
| Mieter einladen | ❌ E-Mail-Versand blockiert |
| Chat / Kommentar | ✅ Lokal gespeichert, später versendet |

### Service-Worker-Strategie

```javascript
// Workbox / custom SW
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/tickets')) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        return fetch(event.request)
          .then(response => updateCache(event.request, response))
          .catch(() => cached || offlineFallback());
      })
    );
  }
});
```

### Offline-UI

```css
.offline-chip {
  position: fixed; top: calc(56px + var(--safe-top));
  left: 50%; transform: translateX(-50%);
  background: var(--text);
  color: #fff; font-size: 13px;
  padding: 8px 16px;
  border-radius: 20px;
  z-index: 200;
  display: flex; align-items: center; gap: 8px;
  box-shadow: var(--shadow-float);
}
```

### Background Sync

- Tickets/Belege in IndexedDB speichern.
- `navigator.serviceWorker.ready.then(reg => reg.sync.register('sync-tickets'))`.
- Bei Wiederverbindung automatisch senden + Toast „3 ausstehende Aktionen synchronisiert“.

### Mockup-Idee

- Offline-Banner oben: „Sie sind offline. Ihre Änderungen werden später synchronisiert.“
- Offline-Tickets haben graue Cloud-Icons; „Wird synchronisiert“-Spinner.

---

## 9. Push-Benachrichtigungen

### Notification-Kategorien

| Kategorie | Auslöser | Frequenz | Wichtigkeit | Rolle |
|-----------|----------|----------|-------------|-------|
| Neues Ticket | Mieter erstellt Ticket | Bei Ereignis | Hoch | Vermieter |
| Status-Update | Ticket-Status ändert sich | Bei Ereignis | Hoch | Mieter |
| Neue Abrechnung | Abrechnung freigegeben | 1×/Jahr | Hoch | Mieter |
| Frist-Reminder | Kündigungsfrist, Abrechnungsfrist | Täglich um 8 Uhr | Mittel | Vermieter |
| Zahlungseingang | Miete eingegangen | Bei Ereignis | Mittel | Vermieter |
| Mahnstufe 1-3 | Automatisches Mahnwesen | Tag 3/7/14/21 | Hoch | Mieter |
| KI-Insight | „Nebenkostenabrechnung steht an“ | Max. 1×/Tag | Niedrig | Vermieter |
| Marketing / Upsell | Feature-Tipps, Trial-Ende | Max. 1×/Woche | Niedrig | Vermieter |

### DSGVO-konforme Defaults

- **Wichtige Pushs** (Tickets, Status, Abrechnung, Mahnung, Fristen) per Default **an**.
- **Marketing / KI-Tipps** per Default **aus** — Nutzer muss explizit aktivieren.
- Jede Kategorie einzeln abschaltbar.

### Badging API

```javascript
if ('setAppBadge' in navigator) {
  navigator.setAppBadge(unreadTickets);
}
```

- Zeigt offene Tickets auf App-Icon.
- Wird zurückgesetzt, wenn Nutzer den Ticket-Tab öffnet.

### Notification-Layout (Web Push)

```json
{
  "title": "Neues Ticket von Anna Müller",
  "body": "Heizung im Wohnzimmer wird nicht warm — Priorität: Dringend",
  "icon": "/icons/icon-192x192.png",
  "badge": "/icons/badge-72x72.png",
  "tag": "ticket-123",
  "data": { "ticketId": 123, "route": "/tickets/123" },
  "actions": [
    { "action": "open", "title": "Öffnen" },
    { "action": "done", "title": "Erledigt" }
  ]
}
```

---

## 10. PWA-Features: „Zum Home-Bildschirm hinzufügen“

### Web App Manifest

```json
{
  "name": "MietVerwaltung",
  "short_name": "MietV",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f5f5f7",
  "theme_color": "#0D3B70",
  "orientation": "portrait",
  "icons": [
    { "src": "/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icons/icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "categories": ["business", "finance"],
  "screenshots": [
    { "src": "/screenshots/mobile-dashboard.png", "sizes": "390x844", "type": "image/png", "form_factor": "narrow" },
    { "src": "/screenshots/desktop-dashboard.png", "sizes": "1280x720", "type": "image/png", "form_factor": "wide" }
  ]
}
```

### Install-Banner / Install-Button

```css
.install-banner {
  position: fixed; bottom: calc(72px + var(--safe-bottom));
  left: 12px; right: 12px;
  background: var(--navy);
  color: #fff;
  padding: 14px 16px;
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  box-shadow: var(--shadow-float);
  z-index: 90;
}

.install-banner button {
  background: #fff; color: var(--navy);
  border: none; border-radius: var(--radius-sm);
  padding: 8px 14px;
  font-weight: 600; font-size: 14px;
}
```

**Wann wird das Banner angezeigt?**
- Nach dem 2. Login auf Mobile.
- Nur, wenn `beforeinstallprompt` verfügbar ist.
- Einmal pro Woche, bis Nutzer installiert oder „Nicht mehr fragen“ tippt.
- In den Einstellungen jederzeit manuell wiederholbar.

### Launch Screen

- iOS: `apple-touch-startup-image` für verschiedene Auflösungen bereitstellen.
- Android: Splash-Screen generiert aus Theme-Color + Icon.

### Status Bar

```html
<meta name="theme-color" content="#0D3B70" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0A2540" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

### Mockup-Idee

- Banner-Text: „MietVerwaltung als App installieren — schneller Zugriff & Push-Benachrichtigungen.“
- Button: „Installieren“.
- Close-Icon rechts oben.
- Nach Installation: confetti-ähnliche Microinteraction + Toast „MietVerwaltung ist jetzt auf Ihrem Startbildschirm.“

---

## 11. Microinteractions auf Mobile

### Prinzip

Kleine, sinnvolte Rückmeldungen. Apple-Style: subtil, nicht verspielt. Dauer 100–300 ms.

### Haptic Feedback

```javascript
function haptic(type = 'light') {
  if (window.navigator.vibrate) navigator.vibrate(type === 'success' ? [50, 30, 50] : 50);
  if (window.TapticEngine?.notification) {
    const map = { success: 'success', error: 'error', warning: 'warning' };
    window.TapticEngine.notification({ type: map[type] || 'success' });
  }
}
```

| Aktion | Haptic |
|--------|--------|
| Button-Tap | `light` (50 ms) |
| Long-Press | `medium` (80 ms) |
| Success (Ticket erstellt) | `success` (Pattern 50,30,50) |
| Fehler / Löschen | `error` (Pattern 80,40,80) |
| Swipe-Threshold erreicht | `medium` |
| Pull-to-Refresh loslassen | `light` |

### Animationen

```css
/* Button Press */
.btn-press { transition: transform 0.1s; }
.btn-press:active { transform: scale(0.97); }

/* Page Transition */
.page-enter { animation: slideIn 0.25s ease; }
@keyframes slideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Modal / Bottom-Sheet */
.sheet-enter { animation: sheetUp 0.3s cubic-bezier(0.25, 1, 0.5, 1); }
@keyframes sheetUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

/* Status-Badge Wechsel */
.status-badge { transition: background 0.3s, color 0.3s; }

/* Skeleton Shimmer */
.skeleton {
  background: linear-gradient(90deg, #e5e5ea 25%, #f2f2f7 50%, #e5e5ea 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
```

### Transitions

- **View-Wechsel:** 250 ms, `ease`, leichtes Slide-Up + Fade.
- **Bottom-Sheet:** 300 ms, `cubic-bezier(0.25, 1, 0.5, 1)` — iOS-typisch.
- **List-Item-Eintritt:** Staggered 50 ms, Fade-Up.
- **Tab-Indikator:** 200 ms, Breite und Position animiert.

### Toast-Messages

```css
.toast {
  position: fixed; bottom: calc(90px + var(--safe-bottom));
  left: 50%; transform: translateX(-50%);
  background: var(--text); color: #fff;
  padding: 12px 18px; border-radius: 20px;
  font-size: 14px;
  box-shadow: var(--shadow-float);
  opacity: 0; transition: opacity 0.3s, transform 0.3s;
  z-index: 250;
}
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
```

- Dauer: 3 Sekunden.
- Position auf Mobile: über der Bottom-Tabbar, damit sichtbar.
- Erfolg-Toasts grünes Icon links, Fehler rot.

---

## 12. Performance

### Ziele

| Metrik | Ziel | Google-Empfehlung |
|--------|------|-------------------|
| LCP | < 2,0 s Mobile, < 1,5 s Desktop | ≤ 2,5 s |
| INP | < 150 ms | ≤ 200 ms |
| CLS | < 0,05 | ≤ 0,1 |
| TTFB | < 600 ms | — |
| First Contentful Paint | < 1,2 s | — |

### Konkrete Maßnahmen

1. **Code-Splitting**
   - `const LandlordApp = () => import('./LandlordApp.vue')`
   - `const TenantApp = () => import('./TenantApp.vue')`
   - Route-level Lazy Loading.

2. **Asset-Optimierung**
   - Icons als SVG-Sprite (eine Datei, nicht 40 Einzel-Requests).
   - Bilder im WebP/AVIF-Format, responsive `srcset`.
   - Schriftarten: System-Font-Stack, keine externe Font-Datei.

3. **CSS-Strategie**
   - Tailwind + PurgeCSS, nur verwendete Klassen im Bundle.
   - Kritisches CSS inline im `<head>` (erste 14 KB).

4. **JavaScript**
   - Virtual Scrolling für lange Listen (>50 Items).
   - `requestIdleCallback` für nicht-kritische Analytics/Logging.
   - Debounce 250 ms bei Suche.

5. **Backend**
   - Redis-Cache für Dashboard-Daten.
   - Pagination bei Listen (20 Items / Seite).
   - Server-Side Rendering für initialen HTML-Shell (optional, wenn SEO nötig).

6. **Bild-Upload**
   - Client-seitige Komprimierung vor Upload (max. 1920 px Breite, 80 % Qualität).
   - WebP-Konvertierung im Browser via Canvas.

### Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml (Idee)
- name: Lighthouse CI
  run: |
    lhci autorun --upload.target=temporary-public-storage
  env:
    LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

### Skeleton Screens

- Dashboard: 3 KPI-Skeleton-Cards + 5 List-Skeleton-Rows.
- Tickets: 8 Skeleton-Cards.
- Keine Spinners für initiales Laden — das ist langsamer wahrgenommen.

---

## 13. Dark Mode

### Aktivierung

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #000000;
    --card: #1c1c1e;
    --text: #ffffff;
    --text2: #8e8e93;
    --border: #38383a;
    --navy: #5ac8fa; /* Hellblau statt dunkles Navy, damit Kontrast passt */
    --navy-light: #7dd6ff;
    --navy-dark: #0a84ff;
  }
}
```

**Entscheidung:** Im Dark Mode wird Navy nicht als dunkles Blau verwendet, sondern als helleres Akkblau (`#5ac8fa` / iOS-System-Blue), damit der Brand-Farbkontrast auf schwarzem Hintergrund funktioniert. Formale Navy-Elemente (Header, Sidebar) werden zu dunkelgrau/schwarz mit blauem Accent.

### Dark-Mode-Regeln

| Element | Light | Dark |
|---------|-------|------|
| Hintergrund | `#f5f5f7` | `#000000` |
| Cards | `#ffffff` | `#1c1c1e` |
| Text | `#1d1d1f` | `#ffffff` |
| Secondary Text | `#86868b` | `#8e8e93` |
| Borders | `#d2d2d7` | `#38383a` |
| Primary Button | `#0D3B70` | `#0a84ff` |
| Success | `#34c759` | `#30d158` |
| Danger | `#ff3b30` | `#ff453a` |
| Warning | `#ff9500` | `#ff9f0a` |

### Komponenten-Anpassungen

- Bottom-Tabbar: Hintergrund `rgba(28,28,30,0.92)` mit Blur.
- Floating-Button: `#0a84ff`.
- Badges: Status-Farben leicht angehoben.
- Bilder in Tickets/Dokumenten: leichter weißer Rand (1 px) auf dunklem Hintergrund, damit Belege nicht „schweben“.
- Schatten: Ersetzt durch leichte Borders/Overlays, da dunkle Schatten nicht sichtbar sind.

### Toggle in Einstellungen

Neben `prefers-color-scheme` kann der Nutzer manuell wählen:

```javascript
const theme = localStorage.getItem('theme') || 'system';
if (theme === 'dark' || (theme === 'system' && matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark');
}
```

---

## 14. Accessibility

### Contrast Ratios

| Kombination | Ratio | WCAG 2.1 AA |
|-------------|-------|-------------|
| Navy `#0D3B70` auf Weiß | 8,5:1 | ✅ |
| Navy auf `#f5f5f7` | 7,8:1 | ✅ |
| Success `#34c759` auf Weiß | 2,8:1 | ❌ — nicht für kleinen Text |
| Success-Dark `#248a3d` auf Weiß | 4,6:1 | ✅ |
| Warning `#ff9500` auf Weiß | 2,0:1 | ❌ — nur für Icons/Badges |
| Danger `#ff3b30` auf Weiß | 3,7:1 | ❌ — nur für Icons/Badges |

**Konsequenz:** Grün/Rot/Gelb nur als Icons, Badges mit dunklem Hintergrund (`#34c759` Text auf hellgrünem Hintergrund) oder für große UI-Elemente nutzen. Fehlertext immer in Rot-Dark (`#c0392b`).

### Screen Reader

- Vue-App mit semantischem HTML: `<nav>`, `<main>`, `<section>`, `<article>`.
- ARIA-Labels für Icon-Buttons: `aria-label="Ticket erstellen"`.
- Tabbar: `role="tablist"`, `role="tab"`, `aria-selected="true/false"`.
- Modale: `role="dialog"`, `aria-modal="true"`, Fokus-Trap, initialer Fokus auf Titel.
- Toast: `role="status"`, `aria-live="polite"`.
- Form-Fehler: `aria-describedby="feld-fehler"`, `aria-invalid="true"`.

### Dynamic Type / Schriftgrößen

```css
html { font-size: 16px; }
body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif; }

/* Relative Einheiten für alles Textrelevante */
h1 { font-size: 1.75rem; line-height: 1.2; }
h2 { font-size: 1.4rem; }
h3 { font-size: 1.15rem; }
.body { font-size: 1rem; }
.caption { font-size: 0.8125rem; }

/* iOS Dynamic Type Support */
@media screen and (-webkit-min-device-pixel-ratio: 0) {
  html { -webkit-text-size-adjust: 100%; }
}
```

- Keine festen `px`-Angaben für Fließtext, wenn möglich `rem` nutzen.
- Layout muss bei 200 % Zoom noch funktionieren.
- Auf Mobile: Mindestens 16 px für Eingaben (verhindert Zoom).

### Reduzierte Bewegung

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Focus-Indikatoren

- Tastatur-Navigation sichtbar: `outline: 2px solid var(--navy)`, `outline-offset: 2px`.
- Touch-Devices: kein dauerhafter Focus-Ring, nur kurzes Ripple-Feedback.

### Voice Control / Switch Control

- Alle Aktionen haben sichtbare Labels oder `aria-label`.
- Bottom-Tabbar-Items als Buttons mit klarem Namen.
- FAB als „Schnellaktionen öffnen“.

---

## 15. Zusammenfassung: Mobile-UX-Prinzipien für MietVerwaltung

| # | Prinzip | Konkrete Umsetzung |
|---|---------|---------------------|
| 1 | Mobile-first Breakpoints | `<640px` Bottom-Tabbar, `640–1024px` Rail, `>1024px` Sidebar |
| 2 | Vermieter-Navigation | 4-Tabbar + FAB-Speed-Dial + Drawer für Rest |
| 3 | Mieter-Navigation | 3 Tabs: Start, Tickets, Dokumente |
| 4 | Touch-Targets | 44 px Minimum, 48 px Comfort, 12 px Abstand |
| 5 | Mobile-Forms | 16px-Inputs, Floating Labels, Smart Defaults, Inline-Validierung |
| 6 | Ticket-Flow | Kamera → KI-Analyse → vorausgefülltes Formular → Senden in <30s |
| 7 | Kosten-Erfassung | Beleg-Scan → OCR/KI → Bestätigen → Speichern |
| 8 | Gestures | Swipe-to-Actions, Pull-to-Refresh, Swipe-Tabs, Long-Press |
| 9 | Offline | IndexedDB + SW + Sync; Tickets/Dokumente lesen, Erstellen queued |
| 10 | Push | Wichtige Ereignis-Pushes, Fristen täglich, Marketing aus |
| 11 | PWA | Manifest, Install-Banner, Splash-Screen, Badging API |
| 12 | Microinteractions | Haptic, 100–300ms Transitions, Toasts, Button-Press |
| 13 | Performance | LCP <2s, INP <150ms, CLS <0.05, Lazy Loading, Skeletons |
| 14 | Dark Mode | `prefers-color-scheme`, Navy → Hellblau, manueller Toggle |
| 15 | Accessibility | WCAG AA, ARIA, Dynamic Type, reduced-motion, Focus-Ringe |

---

## 16. Nächste Schritte / Umsetzungsempfehlungen

1. **Mockup erweitern:** In `/root/mietverwaltung/mockup/index.html` die Mobile-Ansichten für Ticket-Erstellung, Beleg-Scan und Dark Mode ergänzen.
2. **Tailwind-Config:** Breakpoints, Farben, Safe-Area-Utilities definieren.
3. **Service Worker:** Workbox-Setup für Offline-Caching + Background Sync.
4. **Web App Manifest + Icons:** Generieren für alle Plattformen.
5. **Haptic-Wrapper:** Cross-Platform Haptic-Helper in `utils/haptic.js`.
6. **Lighthouse CI:** Performance-Budgets im Build-Prozess etablieren.
7. **Usability-Test:** Mockup auf iPhone + Android testen, Daumen-Reichweite und 30-Sekunden-Ticket-Flow messen.
