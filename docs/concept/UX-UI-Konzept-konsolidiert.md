# Konsolidiertes UX/UI-Konzept für MietVerwaltung

**Ziel:** UX/UI-Strategie für die MietVerwaltung SaaS (Apple-Style, Navy #0D3B70, DACH-Kleinvermieter), synthetisiert aus 5 Recherchen.

**Quellen:**
- Harvard UI Research (HBR, Harvard HCI, NN/g, Don Norman, Jakob Nielsen, BJ Fogg, akademische Studien)
- Psychology Tricks (Cognitive Load, Hick, Fitts, Gestalt, Farbpsychologie, Zeigarnik, Social Proof, Loss Aversion, Anchoring, Microinteractions)
- Google SaaS Design (Material 3, HEART, Core Web Vitals, Design Sprint, Workspace UX, Onboarding/Empty/Error States)
- Experts Social (X/Twitter, Reddit, HN, Indie Hackers, Product Hunt)
- SaaS Best Practices (YC, 12-Factor, B2B SaaS UX, Lean Startup, Pricing, Feature Flags, Retention, Anti-Patterns)

---

## 1. TOP 20 UX/UI-Regeln für MietVerwaltung (priorisiert)

| # | Regel | Konkrete Umsetzung in MietVerwaltung | Quelle |
|---|-------|--------------------------------------|--------|
| 1 | **Time-to-Value < 5 Minuten** | Nach erstem Login: Demo-Dashboard mit 1 Objekt + 1 Einheit + 1 Mieter + 1 Beispiel-Ticket sofort anzeigen. Nutzer kann sofort klicken, ohne Daten einzugeben. | Experts Social, SaaS Best Practices |
| 2 | **Lernen durch Tun, nicht Tutorials** | Keine 10-Schritt-Tour erzwingen. Stattdessen: interaktive Checkliste im Dashboard, die den Nutzer direkt ins Produkt führt. | NN/g, HN |
| 3 | **Progressive Disclosure** | Objekt anlegen: zuerst nur Adresse + Bezeichnung; Kaufpreis, Baujahr, Energieausweis erst auf Klick. Abrechnung in 4 Schritten, nie alle Felder auf einmal. | Alle Quellen |
| 4 | **Max. 5–7 Top-Nav-Items** | Vermieter-Portal: Dashboard, Objekte, Mieter, Tickets, Kosten & Abrechnung, Dokumente. Keine weiteren Hauptpunkte. | Hick's Law, NN/g |
| 5 | **Dashboard zeigt nur das Wichtigste** | Genau 3–4 Widgets: offene Tickets/Fristen, Cashflow-Status, nächste Aktion, Setup-Fortschritt. Keine Chart-Wüste. | Cognitive Load, Experts Social |
| 6 | **Workflows statt Pages** | „Abrechnung erstellen“ als durchgängiger Flow (Objekt wählen → Kosten prüfen → PDF generieren → versenden), nicht als isolierte Menüpunkte. | r/UXDesign, SaaS Best Practices |
| 7 | **KI: Human-in-the-Loop** | KI-Vorschläge immer mit „Von KI vorgeschlagen“-Label. Mahnungen, Kündigungen, Mieterhöhungen erst als Vorschau, dann manuell freigeben. | Harvard HCI, SaaS Best Practices |
| 8 | **Explainable AI** | Bei jeder automatischen Berechnung erklären: „Umlage nach qm: 320 € × 45 m² / 120 m² = 120 €“. | Harvard HCI |
| 9 | **Sofortiges Feedback** | Jede Aktion zeigt Toast/Status-Update: „Objekt gespeichert“, „Abrechnung erstellt“, „Ticket zugewiesen“. Keine stille Speicherung. | Don Norman, NN/g |
| 10 | **Große, nah platzierte Primary-CTAs** | Buttons „Objekt anlegen“, „Abrechnung starten“, „Ticket erstellen“ mindestens 44 px hoch, direkt im Lese- oder Interaktionsfluss, Navy #0D3B70. | Fitts's Law |
| 11 | **Inline-Validierung & Error Prevention** | IBAN-Fehler sofort rot markieren; Datum per Datepicker; Umlageschlüssel als Auswahl, nicht Freitext. | NN/g, SaaS Best Practices |
| 12 | **Undo bei Löschung & Statusänderung** | Soft-Delete + 10-Sekunden-Toast „Rückgängig?“. Status-Wechsel bei Tickets rückgängig machbar. | NN/g, Don Norman |
| 13 | **EAS-Formulare** | Eliminate (nur Pflichtfelder), Automate (OCR, Autocomplete, Adressvorschläge), Simplify (Smart Defaults wie Umlage nach qm). | NN/g |
| 14 | **Consistent Design System** | Navy #0D3B70, Hover #2a5a9e, Background #f5f5f7, 12–16 px Radius, system-ui/SF Pro, einheitliche Buttons/Cards/Badges. | Apple-Style, Google Material, Experts Social |
| 15 | **Mobile-First** | Alle Create-Forms, Tabellen und Dashboards müssen am Tablet und Handy funktionieren. Mieter-Portal mit Bottom-Tabbar. | Google, Experts Social |
| 16 | **Real-World-Begriffe** | „Mietvertrag“, „Nebenkostenabrechnung“, „Mahnung“, „Kaltmiete“, „Nebenkostenvorauszahlung“ statt internem Jargon. | Jakob Nielsen, B2B SaaS UX |
| 17 | **Contextual Help statt Handbuch** | Tooltips direkt am Feld („Was ist umlagefähig?“), wiederaufrufbare Hilfe-Panels neben komplexen Formularen. | HBR, NN/g |
| 18 | **Kontextuelle Prompts (BJ Fogg)** | Erinnerungen erscheinen genau dann, wenn relevant: „Miete für Mieter Müller fällig morgen – Zahlung erfassen?“. | Fogg Behavior Model |
| 19 | **Aesthetic & Minimalist Design** | Jedes zusätzliche Element muss sich rechtfertigen. „Ruthless subtraction“ – keine überflüssigen Charts, keine Neon-Farben. | NN/g, Randy J. Hunt |
| 20 | **Sticky Dashboard** | Dashboard ist der tägliche Anlaufpunkt: offene Fristen, Cashflow-Warnung, Smart Insights, schnelle Aktionen. Ziel: Vermieter schaut morgens als Erstes rein. | Experts Social |

---

## 2. Onboarding-Konzept (Schritt für Schritt, mit Psychologie-Tricks)

### Ziele
- Time-to-Value < 5 Minuten
- Activation Event erreichen: „Erstes Objekt angelegt + erste sichtbare Fälligkeitsübersicht"
- Keine Pflicht-Tour, keine langen Videos

### Onboarding-Fluss

| Schritt | Screen/Aktion | Psychologie-Trick | Konkrete Umsetzung |
|---------|---------------|-------------------|--------------------|
| 1 | Registrierung | **Endowed Progress Effect** | Nur E-Mail + Passwort + Einwilligung. Checkliste zeigt bereits: „Konto erstellt ✓, E-Mail bestätigt ✓“ (33 % erledigt). |
| 2 | Willkommen (3 Sekunden) | **Peak-End Rule** + **Spark (Motivation)** | Headline: „Willkommen – Ihre Vermieter-Arbeit wird jetzt einfacher.“ Subheadline: „In den nächsten 5 Minuten sehen Sie, wie MietVerwaltung 80 % Ihrer Arbeit automatisiert.“ |
| 3 | Eine Frage zum Use Case | **Self-Select (Google)** + **Personalization** | „Sind Sie Vermieter, Mieter oder Verwalter?“ + „Wie viele Wohnungen verwalten Sie?“ → Dashboard wird vorbefüllt. |
| 4 | Demo-Dashboard laden | **Aha-Moment < 5 Min** | Sofort befülltes Dashboard mit 1 Beispiel-Objekt, 1 Einheit, 1 Mieter, 1 offenem Ticket, 1 anstehender Frist. Keine Daten nötig. |
| 5 | Erste Aktion anbieten | **Tiny Habits + Choice Architecture** | „Was möchten Sie als Erstes tun?“ mit 3 großen Buttons: „Erstes Objekt anlegen“, „Beleg hochladen“, „Demo-Abrechnung testen“. |
| 6 | Interaktiver Walkthrough (optional) | **Learning by Doing** | Wenn Nutzer „Objekt anlegen“ wählt: Inline-Formular öffnet sich, Tooltip zeigt genau das nächste Feld. Kein separates Tutorial-Fenster. |
| 7 | Erster Erfolg feiern | **Peak-End Rule + Behavioral Delight** | Nach Objekt-Anlage: Success-Screen „Ihr erstes Objekt ist bereit“ + Dashboard zeigt Rendite-Kachel und „Smart Insights“. |
| 8 | Setup-Checkliste im Dashboard | **Zeigarnik-Effekt** | Checkliste bleibt sichtbar, bis alle 5 Schritte erledigt: Objekt ✓, Einheit, Mieter, Bankverbindung (optional), erste Abrechnung. |
| 9 | E-Mail-Drip (Tage 1, 3, 7) | **Kontextuelle Prompts** | Tag 1: „So laden Sie Ihren ersten Beleg hoch“. Tag 3: „Erstellen Sie Ihre erste Abrechnung in 3 Klicks“. Tag 7: „Was fehlt Ihnen?“ |

### Verboten im Onboarding
- Keine Pflicht-Video-Tours
- Keine 10-Schritt-Checklisten
- Kein Add-on-Push in Woche 1 (Extra-Wohnung, Storage, eID erst nach erstem Wert)
- Keine Kreditkarte für Free-Tier

---

## 3. Dashboard-Design-Prinzipien (was zeigt man auf einen Blick?)

### Aufbau: 4 Widgets maximal

| Widget | Inhalt | Warum |
|--------|--------|-------|
| **Aktionskarte oben** | „Nächste empfohlene Aktion“ + großer CTA-Button | BJ Fogg: Prompt genau dann, wenn motiviert |
| **Fristen & Tickets** | Offene Tickets, überfällige Mieten, anstehende Kündigungsfristen | Wichtigster Job: nichts verpassen |
| **Cashflow-Snapshot** | Offene Posten, erwartete Einnahmen, Bankkonto-Status | Finanzüberblick auf einen Blick |
| **Setup-Fortschritt** | Fortschrittsbalken „Ihr Vermieter-Setup“ (nur für neue Nutzer) | Zeigarnik + Endowed Progress |

### Design-Regeln
- Keine 5+ Charts auf dem Dashboard. Erweiterte KPIs (Rendite, DSCR etc.) auf separatem „Portfolio“-Tab.
- Karten mit gleichem Padding, einheitlichem Radius (16 px), konsistenten Status-Badges.
- Wichtige Fristen rot/orange markieren, erledigte grün.
- Mobile: Widgets untereinander, Bottom-Tabbar für Mieter-Portal.

### „Sticky“-Elemente (Experten-Social)
- „Sie haben diese Woche 2 h Arbeit gespart“ ( nach Abrechnung)
- „Morgen fällt die Miete für Objekt X – Zahlung erfassen?"
- „3 offene Fristen diese Woche"

---

## 4. Farb- und Design-System (Navy #0D3B70, Apple-Style)

### Primärfarben

| Farbe | Hex | Verwendung |
|-------|-----|------------|
| **Navy Primary** | `#0D3B70` | Header, Primary-Buttons, Markenfarbe, Vertrauen/Professionalität |
| **Navy Hover** | `#2a5a9e` | Hover-States, aktive Tabs, sekundäre Akzente |
| **Navy Light** | `#e8eff8` | Hintergründe für selektierte Zeilen, Subtle-Badges |
| **Background** | `#f5f5f7` | Apple-Style Seitenhintergrund |
| **Surface/Card** | `#ffffff` | Karten, Modals, Slide-overs |
| **Text Primary** | `#1d1d1f` | Haupttext |
| **Text Secondary** | `#6e6e73` | Labels, Hilfetexte, Meta-Informationen |
| **Border** | `#d2d2d7` | Trennlinien, Input-Borders |

### Semantische Farben

| Farbe | Hex | Verwendung |
|-------|-----|------------|
| **Erfolg Grün** | `#34c759` | Erfolgs-Toasts, erledigte Status, positive Cashflow-Indikatoren |
| **Warnung Gelb/Orange** | `#ff9500` | Offene Tickets, anstehende Fristen, Hinweise |
| **Fehler Rot** | `#ff3b30` | Fehler, überfällige Mieten, Dringend-Priorität, Kündigungsfristen |
| **Info Blau** | `#007aff` | In-Bearbeitung, Links, sekundäre Hinweise (iOS-Blau) |

### Typografie
- **Font:** `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", system-ui, sans-serif`
- **Headlines:** 600–700 weight, eng geführt
- **Body:** 400–500 weight, 16 px Standard
- **Labels/Helper:** 13–14 px, `#6e6e73`
- **Sentence Case** für alle UI-Texte in Deutsch (außer Eigennamen)

### Form & Spacing
- **Border-Radius:** 12 px (Inputs, Buttons), 16 px (Cards, Modals), 20 px (Dashboard-Karten)
- **Spacing-System:** 4 px Basiseinheit (4, 8, 12, 16, 24, 32, 48, 64)
- **Shadows:** Sehr subtil (0 1px 3px rgba(0,0,0,0.04)), keine harten Schatten
- **Whitespaces:** Großzügig – edel, ruhig, reduziert kognitive Last

### Button-Hierarchie
- **Primary:** Navy #0D3B70, weißer Text, 12 px Radius, 44 px min-height
- **Secondary:** Weißer Hintergrund, Navy-Border, Navy-Text
- **Tertiary:** Nur Text + Icon, für weniger wichtige Aktionen
- **Danger:** Rot #ff3b30, klein, abseits vom Primary-Flow platziert
- **Disabled:** 50 % Opacity, Cursor not-allowed

---

## 5. Microinteraction-Liste (welche Animationen, wo, warum)

| Animation | Wo | Dauer | Warum |
|-----------|-----|-------|-------|
| **Button Press** | Jeder Klick auf Primary-Button | 80–100 ms | Scale 0.97 + Farbdunkelung → Feedback, dass Aktion registriert wurde |
| **Ripple/Highlight** | Touch-Targets auf Mobile | 150 ms | Apple-Style, bestätigt Tap |
| **Toast-Einblendung** | Erfolgsmeldungen | 200 ms Slide-in, 4 s sichtbar | Sofortiges Feedback, aber nicht aufdringlich |
| **Success-Häkchen** | Nach Speichern, Erstellen, Versenden | 300 ms | Completion Bias, Dopamin |
| **Upload-Fortschritt** | Beleg-Upload, CSV-Import | 200–500 ms | Sichtbarer Fortschritt, Vertrauen |
| **Status-Farbwechsel** | Ticket-Status offen → in Bearbeitung → erledigt | 300 ms | Mentales Modell verstärken, was passiert ist |
| **Modal/Slide-over öffnen** | Neues Objekt, Mieter, Kosten | 250 ms ease-out | Kontextwechsel angenehm, keine abrupte Sprünge |
| **Dashboard-Karten fade-in** | Beim Laden des Dashboards | 300 ms gestaffelt | Reduziert Wartegefühl |
| **Progress-Balken füllen** | Onboarding, Abrechnungs-Wizard | 400 ms | Zeigarnik-Effekt, Momentum |
| **Konfetti/Success-Animation** | Nach erster Abrechnung, Jahresbericht | 1 s | Peak-End Rule, tiefere emotionale Verankerung |
| **Pull-to-Refresh** | Mieter-Portal auf Mobile | iOS-Standard | Vertraute mobile Interaktion |

### Regeln
- Dauer: 100–300 ms für Feedback, maximal 500 ms für Übergänge.
- Keine übermäßige Animation (Motion Fatigue vermeiden).
- `prefers-reduced-motion` respektieren.

---

## 6. Psychologie-Tricks die WIR einsetzen (mit konkreter Umsetzung)

| Trick | Konkrete Umsetzung in MietVerwaltung |
|-------|--------------------------------------|
| **Cognitive Load Reduction** | Dashboard nur 3–4 Widgets; Modals statt Seitenwechsel; erweiterte Einstellungen ausklappbar. |
| **Hick's Law** | Max. 6 Hauptnav-Items, 4 Ticket-Kategorien, 3 Prioritätsstufen, 4 Pricing-Tiers. |
| **Fitts's Law** | Primary-CTAs 44+ px hoch, direkt unter Formular, mobile Bottom-Tabbar. |
| **Zeigarnik-Effekt** | Setup-Checkliste bleibt sichtbar, bis 100 % erledigt; Abrechnungs-Wizard zeigt „Schritt 2 von 4“. |
| **Endowed Progress** | Checkliste startet mit „Konto erstellt ✓, E-Mail bestätigt ✓“; Demo-Dashboard ist sofort befüllt. |
| **Social Proof** | Landingpage: „Mehr als X Vermieter verwalten Y Wohnungen mit MietVerwaltung“ + Testimonials deutscher Kleinvermieter. |
| **Loss Aversion** | Trial-E-Mail: „In 3 Tagen läuft Ihr Pro-Zugang ab – Ihre KI-Features werden dann eingeschränkt.“ |
| **Anchoring** | Pricing: Business 49,90 € als Anker, Pro 29,90 € als „Most Popular“, Basis 14,90 €, Free. |
| **Default Bias** | Umlage nach qm, Kalenderjahr 1.1.–31.12., wichtige E-Mails per Default aktiv, Marketing per Default inaktiv (DSGVO). |
| **Choice Architecture** | „Nächste empfohlene Aktion“-Karte; KI schlägt nächsten Schritt bei Tickets vor; Jahresabo als Default. |
| **Peak-End Rule** | Onboarding endet mit Success-Screen + erstem Objekt; Abrechnungsabschluss mit PDF-Download + Erfolgsmeldung. |
| **Microinteractions** | Button-Press, Success-Häkchen, Status-Farbwechsel, Upload-Fortschritt. |
| **Color Psychology** | Navy für Trust, Grün für Erfolg, Rot für Dringlichkeit, Orange für Warnung. |
| **Gestalt-Prinzipien** | Karten mit konsistentem Layout, Label+Input eng zusammen, Fortschrittsbalken als Continuity. |

---

## 7. Anti-Patterns die WIR vermeiden

| Anti-Pattern | Warum schädlich | Wie wir es vermeiden |
|--------------|-----------------|----------------------|
| **Mandatory Onboarding Tours** | Nutzer schließen sofort (HN: „Just let me get to work“) | Demo-Dashboard + optionale Tooltips; Checkliste jederzeit schließbar. |
| **Jargon Dump** | Verwirrung bei nicht-digitalen Vermietern | „Mietzahlung erfassen“ statt „Transaktion buchen“; deutsche Fachbegriffe erklären. |
| **Feature Creep auf dem Dashboard** | Kognitive Überlastung | Max. 4 Widgets; erweiterte KPIs auf separatem Tab. |
| **Inconsistent Interaction Model** | Nutzer müssen neu lernen, je nach Modul | Einheitliches Design-System; gleiche Aktionen funktionieren überall gleich. |
| **False Defaults** | Nutzer verliert Vertrauen | Defaults nutzen dem Nutzer (Umlage qm, Kalenderjahr), nicht dem Anbieter. |
| **Dark Patterns** | Rechtliches/Vertrauensrisiko | Keine versteckten Auto-Renewals, transparente Preiserhöhungen, einfache Kündigung. |
| **Overwhelming Choices** | Auswahl-Lähmung | 4 Pläne, 4 Ticket-Kategorien, 3 Prioritäten. |
| **Silent Actions** | Nutzer wiederholt Aktionen oder bricht ab | Toast nach jedem Speichern/Erstellen/Versenden. |
| **Feature Trap** | Produkt wird langsamer und komplexer | Roadmap priorisiert nach „Jobs to be Done“; jedes Feature muss an einem Workflow hängen. |
| **Generic SaaS Look** | Keine Wiedererkennung | Navy-Primary, Apple-Style, eigene Komponenten; Qualitätsfrage: „Könnte man dieses UI mit einem anderen SaaS tauschen?" |
| **Mobile als Nachtrag** | Viele Vermieter arbeiten am Tablet/Handy | Mobile-first Wireframes; Mieter-Portal Bottom-Tabbar. |
| **KI entscheidet für mich** | Falsches mentales Modell, rechtliches Risiko | Label „KI-Vorschlag“, Human-in-the-Loop, Vorschau vor Versand. |

---

## 8. Mobile-First-Regeln

### Grundannahme
Viele Kleinvermieter arbeiten vor Ort am Tablet oder Handy. Mieter nutzen fast ausschließlich Mobile.

### Regeln

| Bereich | Regel | Konkrete Umsetzung |
|---------|-------|--------------------|
| **Touch-Targets** | Mindestens 44 × 44 px | Alle Buttons, Listeneinträge, Badges ausreichend Padding. |
| **Navigation** | Bottom-Tabbar für Mieter-Portal | 3 Tabs: Start, Tickets, Dokumente. |
| **Vermieter-Navigation** | Sidebar kollabiert zu Hamburger | Hauptpunkte im Drawer, Suchleiste prominent. |
| **Formulare** | Einspaltig, große Inputs | Objekt-Anlage am Handy in einem durchgängigen Scroll-Formular, keine mehrspaltigen Layouts. |
| **Tabellen** | Karten statt Tabellen | Mieter-Liste auf Mobile als Karten mit Name, Einheit, Status; horizontales Scrollen vermeiden. |
| **Schnellaktionen** | Floating Action Button (FAB) | „+“-Button unten rechts für schnelles Objekt/Mieter/Ticket anlegen. |
| **Beleg-Upload** | Kamera direkt aus App | „Beleg fotografieren“ als primäre Option auf Mobile; OCR sofort ausführen. |
| **Offline-Resilienz** | Status kommunizieren, Tasks queuen | Bei schlechtem Netz: „Wird synchronisiert…“ + Retry-Button; keine Datenverluste. |
| **Core Web Vitals** | LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 | Skelett-Screens, lazy loading, schnelle APIs. |
| **Responsive Breakpoints** | Desktop ≥ 1280 px, Tablet ≥ 768 px, Mobile < 768 px | Sidebar bei ≥ 1024 px sichtbar, darunter Drawer. |

---

## 9. Empty-State-Konzept

### Grundprinzip
Empty States sind keine leeren Seiten – sie sind Onboarding-Momente.

### Komponenten einer guten Empty State
1. **Illustration/Icon:** Freundlich, markenkonsistent, nicht zu verspielt.
2. **Positive Headline:** Zweck vermitteln, nicht wie ein CTA wirken.
3. **Kurze Erklärung:** Was fehlt, warum es wichtig ist.
4. **Primary Aktion:** Genau eine nächste logische Aktion.
5. **Optional:** Template/Sample-Daten laden.

### Konkrete Empty States

| Bereich | Empty-State-Headline | Erklärung | Primary Action | Secondary Option |
|---------|----------------------|-----------|----------------|------------------|
| **Dashboard (neuer Nutzer)** | „Willkommen bei MietVerwaltung" | „Legen Sie Ihr erstes Objekt an, um Ihre Fristen und Einnahmen zu sehen.“ | „Erstes Objekt anlegen" | „Demo-Dashboard laden" |
| **Objekt-Liste** | „Noch keine Objekte" | „Hier verwalten Sie Häuser, Wohnungen und Gewerbeimmobilien.“ | „Objekt anlegen" | „Beispiel-Objekt importieren" |
| **Mieter-Liste** | „Noch keine Mieter" | „Fügen Sie Mieter hinzu, um Mietverträge und Zahlungen zu verknüpfen.“ | „Mieter hinzufügen" | „Mieter aus CSV importieren" |
| **Tickets** | „Keine offenen Tickets" | „Sobald ein Mieter ein Ticket erstellt, erscheint es hier.“ | „Ticket erstellen" | – |
| **Kosten** | „Noch keine Kosten erfasst" | „Erfassen Sie Nebenkosten, damit die Abrechnung automatisch erstellt werden kann.“ | „Kosten erfassen" | „Beleg scannen" |
| **Abrechnungen** | „Noch keine Abrechnung" | „Erstellen Sie Ihre erste Nebenkostenabrechnung mit einem Klick.“ | „Abrechnung starten" | – |
| **Dokumente** | „Noch keine Dokumente" | „Laden Sie Mietverträge, Übergabeprotokolle oder Belege hoch.“ | „Dokument hochladen" | – |
| **Mieter-Portal Start** | „Willkommen in Ihrem Mieter-Portal" | „Hier finden Sie Tickets, Dokumente und Nachrichten zu Ihrer Mietwohnung.“ | „Ticket erstellen" | „Dokumente ansehen" |
| **Suchergebnisse** | „Keine Ergebnisse für „Müller"" | „Versuchen Sie einen anderen Suchbegriff oder prüfen Sie die Schreibweise.“ | „Suche zurücksetzen" | – |

### Regeln
- Nie nur „Noch keine Daten“ anzeigen.
- Illustrationen sollen neutral/positiv sein, keine Entschuldigung vermitteln.
- Demo-Daten/Samples immer anbieten, um Exploration zu ermöglichen.

---

## 10. Error-State-Konzept

### Grundprinzip
Fehlermeldungen müssen: Was ist passiert → Was bedeutet das → Was kann ich tun.

### Fehler-Taxonomie & Umsetzung

| Fehler-Typ | Beispiel | Meldung | Recovery |
|------------|----------|---------|----------|
| **Validierungsfehler (Inline)** | IBAN ungültig | „Die IBAN ist ungültig. Bitte prüfen Sie die 22 Stellen.“ | Feld rot markieren, Beispiel-Format anzeigen. |
| **Fehlende Pflichtangabe** | Keine Mieter-E-Mail | „E-Mail benötigt, um die Abrechnung zu versenden. E-Mail nachtragen →" | Direktlink zum Mieter-Formular. |
| **Netzwerkfehler** | API nicht erreichbar | „Verbindung unterbrochen. Ihre Änderungen werden automatisch gespeichert, sobald die Verbindung zurückkehrt." | Retry-Button, Offline-Queue. |
| **Berechtigungsfehler** | Kein Zugriff auf Pro-Feature | „Diese Funktion ist im Pro-Plan enthalten. Mehr erfahren →" | Upsell-Pfad, aber nicht aufdringlich. |
| **Plan-Limit erreicht** | 6 Wohnungen im Basis-Plan | „Sie haben das Limit von 5 Wohnungen erreicht. Upgrade auf Pro für 29,90 €/Monat ermöglicht 50 Wohnungen." | „Upgrade"-Button + „Später"-Option. |
| **Upload-Fehler** | Beleg zu groß | „Das Bild ist zu groß (max. 10 MB). Bitte verkleinern Sie es oder laden Sie eine PDF hoch." | Alternative Aktion. |
| **Rechtlicher Fehler** | Kündigung ohne Pflichtangaben | „Für eine rechtssichere Kündigung fehlt: Kündigungsfrist, ordentlich/außerordentlich. Korrigieren →" | Formular springt zu fehlenden Feldern. |
| **Systemfehler** | 500 beim Abrechnung erstellen | „Die Abrechnung konnte nicht erstellt werden. Wir haben den Fehler protokolliert. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support." | Retry + Support-Link. |

### Allgemeine Error-State-Regeln
1. **Keine technischen Exceptions anzeigen** („500 Internal Server Error“ → vermeiden).
2. **Fehler nicht mit Toast allein** kommunizieren, wenn Aktion blockiert ist.
3. **Inline-Validierung** vor Absenden, nicht erst nach Submit.
4. **Bestätigungsdialoge** bei rechtlich kritischen Aktionen (Mahnung, Kündigung, Löschung).
5. **Undo-Option** bei Löschung und Massenaktionen.
6. **Kontext erhalten:** Modal bleibt geöffnet, Formulardaten bleiben erhalten.
7. **Loading, Empty, Error visuell klar trennen** – nie denselben Zustand für mehrere Bedeutungen verwenden.

### Error-State-Komponente (Template)
```
[Icon: Rot / Orange je nach Schwere]
Headline: Kurz und klar
Beschreibung: Was passiert ist + was es bedeutet
Primary Action: Konkreter Lösungsweg
Secondary Action: Alternative oder „Ignorieren" (wo sinnvoll)
```

---

## 11. Conversion-Optimierung (Free → Basis → Pro)

### Pricing-Struktur

| Plan | Preis | Limitierung | Konversion-Trigger |
|------|-------|-------------|-------------------|
| **Free** | 0 € | 2 Wohneinheiten, Basis-Funktionen, begrenzte Historie | Sampling ohne Kreditkarte |
| **Basis** | 14,90 €/Monat | bis 5 WE, Mietzahlungen, Mahnungen, Mieter-Portal | Limit-Trigger bei 3 WE |
| **Pro** | 29,90 €/Monat | bis 50 WE, KI-Abrechnung, API, erweiterte Kennzahlen | „Most Popular"-Badge |
| **Business** | 49,90 €/Monat | unbegrenzte WE, SSO, Audit-Logs, dedizierter Support | Enterprise-Anker |

### Conversion-Mechanismen

| Mechanismus | Umsetzung |
|-------------|-----------|
| **Free als Sampling** | 2 WE kostenlos, sofort nutzbar, keine Kreditkarte → niedrige Einstiegshürde (HBR). |
| **Value Metric** | Preis nach Wohneinheiten – wächst mit dem Kunden, klar verständlich. |
| **Limit-Trigger** | Bei 3 WE im Free-Plan sanfter Hinweis: „Mit Basis verwalten Sie bis zu 5 Wohnungen." |
| **Feature-Gating** | KI-Belegauswertung, erklärende Abrechnung, API, erweiterte Kennzahlen nur in Pro/Business. |
| **Trial ohne Kreditkarte** | 14 Tage Pro kostenlos testen; Daten bleiben erhalten, Verlust bei Downgrade spürbar (Loss Aversion). |
| **Jahresabo-Default** | Preise als Jahrespreis anzeigen („11,88 €/Monat, 142,56 €/Jahr – 2 Monate geschenkt"); Monat als Toggle. |
| **Anchoring** | Business 49,90 € als linker Anker macht Pro 29,90 € attraktiv. „Most Popular"-Badge auf Pro. |
| **Add-ons günstig wirken lassen** | Extra-Wohnung 1 €, eID 2 €, Storage 1 €/5 GB – gegenüber Planpreis vernachlässigbar. |
| **Plan-Limit erreicht** | Soft-Gate: „Sie haben 5 von 5 Wohnungen angelegt. Upgrade ermöglicht 50." |
| **Social Proof auf Pricing** | Testimonials, G2/Capterra-Badges, Nutzerzahlen. |
| **Transparente Vergleichstabelle** | Begriffe in Käufersprache: „Wohneinheiten", „Nebenkostenabrechnung", „API", „Support". |
| **Kündigung einfach** | Keine Dark Patterns; transparente Kündigung erhöht Vertrauen und Conversion. |

### Conversion-Funnel
1. **Landingpage:** Hero mit Outcome + Social Proof + CTA „Kostenlos starten"
2. **Signup:** Nur E-Mail + Passwort
3. **Onboarding:** Demo-Dashboard + erster Aha-Moment < 5 Min
4. **First Value:** Objekt anlegen → erste sichtbare Fälligkeitsübersicht
5. **Habit Loop:** Wöchentliche E-Mail/Erinnerung bei Mietfälligkeit
6. **Upsell Trigger:** Limit, Feature-Gating, Trial-Countdown
7. **Upgrade:** Einfacher 1-Klick-Upgrade mit Stripe

---

## 12. Retention-Strategien (was hält User aktiv)

### Definition „aktiv"
Ein Vermieter gilt als aktiv, wenn er in 7 Tagen mindestens eine der folgenden Aktionen ausführt:
- Zahlung erfasst
- Mahnung erstellt
- Ticket geöffnet/bearbeitet
- Abrechnung/Bericht geöffnet

### Retention-Mechanismen

| Mechanismus | Umsetzung |
|-------------|-----------|
| **Sticky Dashboard** | Täglicher Anlaufpunkt: Fristen, Cashflow, Smart Insights, nächste Aktion. |
| **Verhaltensgetriggerte E-Mails** | 2 Tage vor Mietfälligkeit: „Morgen fällt die Miete – Zahlung erfassen"; 7 Tage nach Import: „Erstellen Sie Ihre erste Mahnung". |
| **Kontextuelle In-App-Prompts** | „Offene Mahnung für Mieter Müller" direkt im Dashboard; „Nebenkostenabrechnung für 2025 starten" im Januar. |
| **Habit Loops** | Wiederkehrende Aktionen extrem einfach: „Mahnung in 1 Klick", „Abrechnung in 3 Klicks". |
| **Milestone & Progress** | „Nur noch 1 Schritt bis zur vollständigen Abrechnung"; Jahresbericht mit Portfolio-Rendite. |
| **Deep Delight durch Automation** | „KI hat aus Ihrem Beleg 3 Kostenpositionen erkannt – prüfen und übernehmen"; „Sie haben 2 h Arbeit gespart". |
| **Continuous Onboarding** | Neue Features werden kontextuell vorgestellt („Neu: Belege per Foto hochladen"), nicht per E-Mail-Bombe. |
| **Gespeicherte Ansichten & Quick-Links** | Letzte Filter/Ansicht merken; Favoriten für häufige Objekte. |
| **Mieter-Portal als Lock-in** | Sobald Mieter eingeladen sind, erhöht sich Wechsel-Friction (Netzwerkeffekt im Free-Tier). |
| **Jahresbericht / Reflective Delight** | „Ihre Immobilien haben 2026 eine Nettomietrendite von X % erzielt." |
| **Exit-Survey & Retention Offer** | Bei Kündigungsabsicht: „Was fehlt Ihnen?" + Angebot Pause oder Downgrade auf Basis/Free. |
| **Dunning & Zahlungserinnerung** | Automatische Wiederholung bei fehlgeschlagener Zahlung + in-App-Hinweis. |
| **Feature-Adoption-Tracking** | PostHog-Events: Wer nutzt KI-Features? Wer hat noch keine Abrechnung erstellt? Zielgruppen gezielt ansprechen. |

### Retention-Ziele (frühe Phase)
- Day-7-Retention ≥ 40 %
- Day-30-Retention ≥ 25 %
- Monatlicher Churn < 5 %
- Stickiness (DAU/MAU) für Mieter-Portal ≥ 20 %

### Re-Engagement-Frequenz
- Mietverwaltung ist kein tägliches Tool. Trigger müssen sich an Ereignissen orientieren (Mietfälligkeit, Fristen, Abrechnungszeit), nicht an täglichen Remindern.
- Max. 1–2 relevante E-Mails pro Woche; alles darüber ist Spam.

---

## Zusammenfassung: Das UX/UI-Konzept in einem Satz

> **MietVerwaltung ist eine KI-gestützte, vertrauenswürdige Apple-Style SaaS für DACH-Kleinvermieter, die durch ein sticky Dashboard, extrem schnelles Onboarding, human-in-the-loop-Automation und konsequent reduzierte Komplexität Vermieter täglich zurückholt und sanft von Free zu Pro führt.**

---

## Quellen

- Harvard UI Research: `/root/mietverwaltung/research-harvard-ui-research.md`
- Psychology Tricks: `/root/mietverwaltung/research-psychology-tricks.md`
- Google SaaS Design: `/root/mietverwaltung/research-google-saas-design.md`
- Experts Social: `/root/mietverwaltung/research-experts-social.md`
- SaaS Best Practices: `/root/mietverwaltung/research-saas-best-practices.md`

---

*Dokument erstellt: 2026-10-28*
*Zweck: Konsolidierte UX/UI-Strategie für MietVerwaltung SaaS*
