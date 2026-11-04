# Onboarding-Konzept MietVerwaltung

**Ziel:** Nutzer von der Registrierung bis zum ersten messbaren Mehrwert führen – in unter 5 Minuten zum "Aha-Moment", in unter 15 Minuten zur ersten produktiven Aktion. Onboarding soll nicht wie eine Schulung wirken, sondern wie ein Dialog: der Nutzer lernt durch Tun, die KI assistiert dezent im Hintergrund, Fortschritt bleibt sichtbar.

**Design-Prinzipien (aus Recherche):**
- Interactive Walkthrough statt vollbildiger Pflicht-Tour (studienbasiert höchste Completion Rate)
- Zeigarnik-Effekt + Endowed Progress: Checkliste startet nicht bei 0 %
- Progressive Disclosure: nur Pflichtfelder sofort, erweiterte Einstellungen auf Wunsch
- Kontextuelle Pull-Hilfe statt externer Dokumentation
- Peak-End-Rule: jeder Workflow endet mit einem positiven Abschluss
- Human-in-the-Loop: KI schlägt vor, der Nutzer entscheidet
- Kein Add-on/Upsell-Push in Woche 1

**Style:** Apple-Style, Navy `#0D3B70`, Background `#f5f5f7`, abgerundete Cards (12–16 px), System-Font, großzügiger Whitespace.

---

## 1. Registrierungs-Flow

### Strategie
- So wenig Felder wie nötig: E-Mail + Passwort + Name + rechtliche Einwilligungen.
- Keine Kreditkarte im Free-Tier (Sampling-Prinzip laut HBR).
- 2FA-Pflicht ist Teil des Registrierungs-Flows, aber mit klarem Nutzen-Versprechen.
- Social Login optional, nie exklusiv (DACH-Zielgruppe >50, oft misstrauisch gegenüber Social-Logins).

### Screen 1: Kostenlos registrieren

**Kopfzeile:**
- Logo + Claim: „Ihre Vermieter-Arbeit. 80 % automatisch.“

**Formular (max. 4 Felder):**
1. **E-Mail-Adresse** (Inline-Validierung, Hinweis bei ungültigem Format)
2. **Passwort** (Strength-Meter, min. 12 Zeichen, Hinweis: „Sicher, damit Mieterdaten geschützt sind.")
3. **Passwort wiederholen** (Live-Abgleich, rotes Icon bei Nicht-Übereinstimmung)
4. **Vorname** (nur für persönliche Ansprache im Onboarding)

**Rechtliche Checkboxen (ungehakt, keine vorausgewählten Defaults):**
- [ ] Ich stimme den [AGB] und der [Datenschutzerklärung] zu.
- [ ] Ich möchte Tipps & Produkt-Updates per E-Mail erhalten (optional).

**Primary CTA:**
- Button: **„Kostenlosen Account erstellen“** (Navy `#0D3B70`, 48 px hoch, volle Breite)
- Subtext unter Button: „Kostenlos für bis zu 2 Wohnungen. Keine Kreditkarte nötig."

**Secondary:**
- Trennlinie „oder schnell mit"
- Buttons: **„Mit Apple anmelden“**, **„Mit Google anmelden“** (outline-Style, Apple/Google-Icon links)
- Link: „Bereits registriert? [Anmelden]"

**Verhalten:**
- Nach Klick: E-Mail-Verifizierungscode anfordern (nicht erst Dashboard). Button zeigt Spinner.
- Fehler: Inline-Feld-Fehler in Klartext (z. B. „Diese E-Mail ist bereits registriert – [zum Login]")

### Screen 2: E-Mail bestätigen

**Titel:** „Fast geschafft – bestätigen Sie Ihre E-Mail"
**Text:** „Wir haben einen 6-stelligen Code an [email] gesendet. Er ist 15 Minuten gültig."

**Input:** 6 Boxen für Code (automatischer Fokus-Wechsel)
**Buttons:**
- Primary: **„Code prüfen"**
- Text-Link: „Code erneut senden (00:58)"

**Fortschritt in Checkliste:** Schritt „E-Mail bestätigt" wird abgehakt.

### Screen 3: 2FA einrichten

**Titel:** „Einmaliger Sicherheits-Check"
**Text:** „Ihre Mieter- und Finanzdaten verdienen Banksicherheit. Richten Sie jetzt einen Authenticator ein."

**Darstellung:**
- QR-Code (Beispiel im Mockup)
- Secret-Code zum Kopieren
- Input: 6-stelliger TOTP-Code

**Buttons:**
- Primary: **„Sicherheit aktivieren“**
- Secondary: **„E-Mail-Code als Alternative nutzen"** (für Nutzer ohne Authenticator-App)

**Nach erfolgreicher 2FA:** Weiterleitung zum Welcome-Screen.

---

## 2. Welcome-Screen

**Wann:** Direkt nach erstem Login / 2FA-Verifizierung.
**Ziel:** Persönlicher Empfang, sofortige Orientierung, erste Aktion sichtbar.

### Layout

**Oben:**
- Avatar-Bubble mit Gruß: „Guten Tag, Max! Willkommen bei MietVerwaltung."
- Untertitel: „In 4 Schritten ist Ihre erste Immobilie eingerichtet."

**Mitte – zwei große Cards:**

| Card 1 | Card 2 |
|--------|--------|
| **„Erstes Objekt anlegen"** | **„Mit Demo-Daten erkunden"** |
| Icon: Haus (+) | Icon: Test-Datenbank |
| Text: „Legen Sie Ihr Haus oder Ihre Wohnung an." | Text: „Sehen Sie sofort, wie MietVerwaltung mit Beispieldaten aussieht." |
| Button: **„Los geht's"** (Primary, Navy) | Button: **„Demo öffnen"** (Secondary, Outline) |

**Rechts (oder darunter auf Mobile): Onboarding-Checkliste-Widget:**

```
Ihr Setup – 40 % erledigt
[████████░░░░░░░░░░]

[x] Konto erstellt
[x] E-Mail bestätigt
[x] 2FA aktiviert
[ ] Objekt anlegen
[ ] Erste Einheit hinzufügen
[ ] Mieter einladen
[ ] Mietvertrag erstellen
```

**Bottom-Right (floating):** KI-Assistenz-Bubble „Max“:
- Text: „Soll ich dir helfen, dein erstes Objekt anzulegen?"
- Buttons: **„Ja, zeig mir wie"** | **„Später"**

**Navigation:** Sidebar ist noch reduziert; Top-Nav zeigt nur Dashboard + Objekte + Hilfe. Weitere Menüpunkte erscheinen schrittweise.

---

## 3. Interactive Walkthrough

**Konzept:** Keine abstrakte Tour – der Nutzer legt echte Daten an. Jeder Schritt ist ein produktives Arbeiten im Produkt. Tooltips erscheinen kontextuell, nicht blockierend.

### Schritt A: Objekt anlegen

**Trigger:** Klick auf „Los geht's" oder KI-Bubble „Ja, zeig mir wie".
**Darstellung:** Slide-over/Modal von rechts (kein Tab-Wechsel).

**Modal-Header:**
- Titel: „Schritt 1 von 4: Objekt anlegen"
- Progress-Bar: 25 %
- Schließen-Icon oben rechts (Workflow kann jederzeit unterbrochen und später fortgesetzt werden)

**Formular (nur Pflichtfelder):**
1. **Objektbezeichnung** (Placeholder: „Mehrfamilienhaus Berlin")
2. **Adresse** (Autocomplete: Straße, PLZ, Ort)
3. **Baujahr** (Dropdown, optional – hinten mit „Erweiterte Einstellungen" versteckt)

**KI-Hilfe:**
- Tooltip neben Adresse: „Die Adresse wird später für Dokumente, Fristen und Renditeberechnungen genutzt."

**Buttons unten:**
- Primary: **„Objekt speichern & weiter"**
- Secondary: **„Überspringen"** (nur für Nutzer, die Demo-Daten nutzen wollen)

**Feedback nach Speichern:**
- Toast: „Objekt gespeichert" + Card erscheint im Hintergrund
- Progress-Checkliste: „Objekt anlegen" wird abgehakt
- KI-Assistent: „Super! Soll ich jetzt die erste Wohnung hinzufügen?"

### Schritt B: Erste Einheit hinzufügen

**Darstellung:** Im gleichen Modal/Slide-over, Header aktualisiert: „Schritt 2 von 4: Wohnung hinzufügen".

**Formular:**
1. **Einheit / Wohnungsnummer** (Placeholder: „Wohnung 1" oder „1. OG rechts")
2. **Wohnfläche in m²** (Input mit automatischer Formatierung)
3. **Anzahl Zimmer** (optional)
4. **Kaltmiete (€/Monat)** (optional im ersten Schritt; kann später ergänzt werden)

**Smart Defaults:**
- Umlageschlüssel: „Nach Quadratmeter" vorausgewählt (häufigste Regelung)
- Abrechnungsperiode: 01.01.–31.12.

**Buttons:**
- Primary: **„Wohnung speichern & weiter"**
- Text-Link: „Weitere Wohnung hinzufügen" (für MFH)

**Feedback:**
- Toast: „Wohnung hinzugefügt"
- Dashboard-Hintergrund zeigt Objekt-Kachel mit „1 Wohnung"
- Checkliste: „Erste Einheit hinzufügen" abgehakt

### Schritt C: Mieter einladen

**Darstellung:** Modal-Header „Schritt 3 von 4: Mieter einladen".

**Formular:**
1. **Vorname**
2. **Nachname**
3. **E-Mail-Adresse**
4. **Telefonnummer** (optional)

**Hinweis-Box (grau, freundlich):**
> „Ihr Mieter bekommt eine Einladung per E-Mail und kann sich sein eigenes Portal anlegen. Sie behalten die volle Kontrolle."

**Buttons:**
- Primary: **„Einladung senden"**
- Secondary: **„Mieter manuell ohne Portal anlegen"** (z. B. für alte Verträge)

**Feedback:**
- Toast: „Einladung an [Name] versendet"
- Checkliste: „Mieter einladen" abgehakt
- KI-Assistent: „Perfekt! Soll ich nun einen Mietvertrag-Entwurf erstellen?"

### Schritt D: Erster Mietvertrag

**Darstellung:** Modal-Header „Schritt 4 von 4: Mietvertrag anlegen".

**Formular (kompakt, gruppiert):**
- **Mieter:** Vorausgefüllt mit soeben eingeladenem Mieter
- **Wohnung:** Vorausgefüllt mit erster Einheit
- **Mietbeginn** (Datepicker, Default: heute)
- **Kaltmiete (€)**
- **Nebenkostenvorauszahlung (€)**
- **Kaution (€, optional)**
- **Zahlungsmodalität** (Dropdown: monatlich / quartalsweise)

**Erweiterte Einstellungen (ausklappbar):**
- Kündigungsfrist, Indexmiete-Klausel, Heizkosten-Umlageart

**Buttons:**
- Primary: **„Mietvertrag speichern"**
- Secondary: **„Als Entwurf speichern"**

**Abschluss:**
- Modal schließt sich
- Checkliste: „Mietvertrag erstellen" abgehakt
- Dashboard rendert mit echten Daten
- Success-Screen erscheint kurz: „Sie sind startklar!" + Button **„Zum Dashboard"**

### Optionaler Schritt E: Erste Kosten erfassen (Aha-Moment-Booster)

**Nur für motivierte Nutzer:** Nach Schritt D zeigt KI-Assistent:
> „Möchten Sie direkt einen Beleg scannen? Die KI erkennt Betrag, Kategorie und Umlagefähigkeit automatisch."

**Buttons:**
- **„Beleg scannen"**
- **„Später"**

---

## 4. Progress-Checkliste

**Strategie:** Kombination aus Zeigarnik-Effekt (offene Schleifen bleiben im Kopf) und Endowed Progress (Nutzer fühlt, er ist schon weiter, als er ist).

### Design

**Widget-Titel:** „Ihr Setup"
**Progress:** „40 % erledigt" (startet bereits nach Registrierung)

**Schritte (stets sichtbar, bis alles erledigt):**
1. [x] Konto erstellt *(geschenkt)*
2. [x] E-Mail bestätigt *(geschenkt)*
3. [x] 2FA aktiviert *(geschenkt)*
4. [ ] Objekt anlegen
5. [ ] Erste Einheit hinzufügen
6. [ ] Mieter einladen
7. [ ] Mietvertrag erstellen
8. [ ] Erste Abrechnung testen *(Bonus, abgehakt nach Demo-Klick)*

**UI-Details:**
- Abgehakte Schritte: Navy-Häkchen + ausgegrauter Text
- Offene Schritte: dunkle Schrift + kleiner Pfeil
- Hover/Click auf offenen Schritt: startet entsprechenden Workflow
- Fortschrittsbalken über der Liste
- Auf Mobile: kollabierbares Card-Widget unterhalb des Dashboard-Headers

**Verhalten:**
- Bleibt oben rechts im Dashboard fixiert, bis alle 7 Pflichtschritte erledigt.
- Nach Abschluss: Widget klappt ein zu „Setup abgeschlossen ✓“ mit Confetti-Microanimation.
- Nutzer kann Widget jederzeit über „×“ schließen; über „Setup wieder anzeigen" in den Einstellungen wiederherstellen.

---

## 5. Aha-Moment

**Definition:** Der erste Moment, in dem der Nutzer spürt: „Diese Software löst wirklich mein Problem."

**Trigger:** Direkt nach Speichern des ersten Mietvertrags (Schritt D).
**Ziel:** Innerhalb von < 5 Minuten nach Login.

### Was der Nutzer sieht

**Dashboard wird live:**
- Objekt-Kachel mit Adresse, Wohnungsanzahl, aktuellem Mieter
- Kennzahlen-Kachel:
  - **Bruttomietrendite:** X,XX %
  - **Erwartete Jahresmiete:** X.XXX €
  - **Nächste Mietfälligkeit:** in 30 Tagen / „Morgen fällig“
- **Smart Insight**-Box (KI-generiert, 1 Satz):
  > „Ihr Objekt in [Ort] hat eine geschätzte Bruttomietrendite von [X] %. Das liegt [über/unter] dem Durchschnitt der Region."

**Actionable Next Step:**
- Prominenter Button im Dashboard: **„Erste Nebenkostenabrechnung testen"**
- Alternativ: **„Mahnung in 1 Klick"** (falls Demo-Daten überfällig markieren)

**Aha-Moment-Screen (Overlay):**
- Titel: „Ihre erste Immobilie ist bereit"
- Subtitel: „MietVerwaltung übernimmt jetzt Fristen, Mahnungen und Abrechnungen für Sie."
- Buttons:
  - **„Dashboard ansehen"** (Primary)
  - **„Demo-Abrechnung erstellen"** (Secondary)
- Kleine Konfetti-Animation (dezent, 1,5 s)

**Warum das der Wow-Moment ist:**
- Nicht nur Daten erfasst, sondern sofort Rendite + Fristen + KI-Insights sichtbar.
- Der Nutzer sieht, dass die App aus Rohdaten sofort Entscheidungshilfen macht.
- Es ist kein leeres Dashboard – es ist sein eigenes Portfolio.

---

## 6. Time-to-Value

**Ziele:**
- **TTV zum Dashboard mit echten Daten:** < 5 Minuten
- **TTV zur ersten produktiven Aktion (Mietvertrag erstellt):** < 10 Minuten
- **TTV zur ersten simulierten Abrechnung:** < 15 Minuten

### Wie erreichen wir das?

| Maßnahme | Umsetzung |
|----------|-----------|
| Forced First Action | Registrierung führt direkt in Objekt-anlegen-Modal |
| Smart Defaults | Umlage nach qm, Kalenderjahr, monatliche Miete, heutiges Datum |
| Autocomplete | Adressvorschläge, IBAN-Check, Datum-Picker |
| Inline-Validierung | Fehler sofort, nicht erst beim Absenden |
| Demo-Modus | Ein Klick zeigt befülltes Dashboard, Nutzer kann sofort Wert erleben |
| KI-Vorausfüllung | Beleg-Scan erkennt Betrag/Kategorie, Vertrag vorausgefüllt mit Mieter+Wohnung |
| Keine Pflicht-Abrechnung | Nutzer kann nach Schritt D sofort aufhören und später weitermachen |

### Onboarding-Funnel & Events

| Funnel-Schritt | Erfolgs-Event |
|----------------|---------------|
| Signup abgeschlossen | `signup_completed` |
| E-Mail verifiziert | `email_verified` |
| 2FA aktiviert | `2fa_enabled` |
| Objekt angelegt | `property_created` |
| Einheit hinzugefügt | `unit_added` |
| Mieter eingeladen | `tenant_invited` |
| Mietvertrag erstellt | `lease_created` |
| Erste Abrechnung getestet | `nbk_demo_generated` |

**Zielwerte (frühe Phase):**
- Activation Rate (Mietvertrag in 7 Tagen): ≥ 40 %
- Onboarding-Completion (alle 4 Walkthrough-Schritte): ≥ 50 %
- Day-30-Retention bei Aha-Moment <5 Min: +40 %

---

## 7. Empty-States

**Prinzip:** Kein totes „Noch keine Daten". Jeder leere Zustand ist eine Handlungsaufforderung mit Erklärung, CTA und optionaler Hilfe.

### Objekte-Liste (noch kein Objekt)

**Darstellung (zentrale Card):**
- Illustration: Haus-Umriss (SVG, Navy)
- Headline: „Noch keine Immobilie hinterlegt"
- Subtext: „Legen Sie Ihr erstes Objekt an – MietVerwaltung berechnet dann automatisch Rendite, Fristen und Abrechnungen."
- Buttons:
  - **„Erstes Objekt anlegen"** (Primary)
  - **„Demo-Daten laden"** (Secondary)

### Einheiten-Liste innerhalb Objekt (noch keine Wohnung)

- Headline: „Diesem Objekt fehlt noch eine Wohnung"
- Subtext: „Jede Wohnung bekommt eigene Mietdaten, Mieter und Abrechnungen."
- Button: **„Wohnung hinzufügen"**

### Mieter-Liste (noch kein Mieter)

- Headline: „Noch keine Mieter erfasst"
- Subtext: „Laden Sie Ihren Mieter per E-Mail ins Portal ein oder erfassen Sie ihn manuell."
- Buttons:
  - **„Mieter einladen"**
  - **„Manuell hinzufügen"**

### Tickets (Vermieter)

- Headline: „Keine offenen Tickets"
- Subtext: „Sobald ein Mieter ein Ticket erstellt, erscheint es hier mit Priorität und Status."
- Button: **„Ticket manuell erstellen"**

### Tickets (Mieter-Portal)

- Headline: „Noch keine Tickets"
- Subtext: „Heizung defekt? Wasserschaden? Erstellen Sie hier direkt ein Ticket an Ihren Vermieter."
- Button: **„Neues Ticket erstellen"** (Primary)

### Kosten-Liste

- Headline: „Noch keine Kosten erfasst"
- Subtext: „Fotografieren Sie einen Beleg ab oder geben Sie die Kosten manuell ein. Die KI erkennt automatisch Betrag und Kategorie."
- Buttons:
  - **„Beleg scannen"**
  - **„Kosten manuell erfassen"**

### Abrechnungen-Liste

- Headline: „Noch keine Nebenkostenabrechnung"
- Subtext: „Sobald Kosten vorhanden sind, können Sie mit einem Klick die Abrechnung pro Wohnung erstellen."
- Button: **„Demo-Abrechnung erstellen"** (führt auch ohne echte Kosten durch)

### Dokumente-Liste

- Headline: „Noch keine Dokumente"
- Subtext: „Laden Sie Mietverträge, Übergabeprotokolle oder Belege hoch."
- Button: **„Dokument hochladen"**

### Dashboard (extremer Edge-Case: alles leer)

- Fokus auf Checkliste-Widget + Willkommens-Card
- Keine leeren Diagramme; stattdessen: „Sobald Objekte & Mietverträge vorhanden sind, sehen Sie hier Ihre Kennzahlen."
- Prominenter CTA: „Erstes Objekt anlegen"

---

## 8. KI-Assistent beim Onboarding

**Name:** „Max“ (freundlich, dezent, nie vollbildig)
**Position:** Floating Action Button unten rechts (Desktop + Mobile)
**Prinzip:** Kontextueller, jederzeit schließbarer Assistent – kein Chat-Zwang.

### Verhalten pro Onboarding-Phase

| Phase | Proaktive Nachricht | Buttons |
|-------|---------------------|---------|
| Willkommen | „Soll ich dir helfen, dein erstes Objekt anzulegen?" | „Ja, zeig mir wie" / „Später" |
| Nach Objekt | „Super! Soll ich jetzt die erste Wohnung hinzufügen?" | „Weiter" / „Später" |
| Nach Einheit | „Möchtest du jetzt Ihren Mieter einladen?" | „Einladen" / „Überspringen" |
| Nach Mieter | „Soll ich einen Mietvertrag-Entwurf vorbereiten?" | „Entwurf erstellen" / „Selbst ausfüllen" |
| Nach Vertrag | „Möchtest du eine Demo-Abrechnung testen?" | „Demo starten" / „Zum Dashboard" |
| Dashboard | Nur reaktiv: Nutzer kann Bubble klicken und Fragen stellen | Eingabefeld: „Wie funktioniert...?" |

### Konkretes Design

**Bubble (closed):**
- Runder FAB mit kleinem KI-Stern-Icon
- Subtiler Pulse-Effekt, wenn eine neue Nachricht vorhanden
- Tooltip: „Max – Ihr Assistent"

**Bubble (open):**
- Card 360×440 px
- Header: „Max“ + Schließen-Icon
- Nachrichten als Chat-Bubbles (KI-links, Nutzer-rechts)
- Eingabefeld unten: „Frage stellen..."

**KI-Antworten im Onboarding:**
- Kurz (max. 2 Sätze)
- Immer mit konkretem Button als nächstem Schritt
- Bei rechtlich relevanten Themen: Hinweis „Dies ist keine Rechtsberatung."

**Beispiel-Dialog:**
> **Max:** „Soll ich dir helfen, dein erstes Objekt anzulegen?"  
> **Nutzer:** „Ja"  
> **Max:** „Gut. Brauchen Sie nur Adresse und Bezeichnung – der Rest kann später ergänzt werden."  
> [Button: „Objekt-Formular öffnen"]

**Einstellungen:**
- Nutzer kann Max in den Account-Einstellungen auf „Nur auf Anfrage" stellen oder ganz deaktivieren.

---

## 9. Mieter-Onboarding

**Auslöser:** Vermieter lädt Mieter in Schritt C oder später über Mieter-Detail ein.

### Vermieter-Seite: Einladung

**Button in Mieter-Formular:** **„Mieter ins Portal einladen"**

**Dialog vor Versand:**
- Vorschau der E-Mail-Adresse
- Hinweis: „Der Mieter bekommt einen sicheren Link und richtet sein eigenes Konto ein."
- Button: **„Einladung senden"**

**Alternative für technisch weniger affine Mieter:**
- Button: **„Einladungslink kopieren"** (Vermieter kann Link per WhatsApp/E-Mail weitergeben)
- Hinweis: „Der Link ist 7 Tage gültig."

### Mieter-E-Mail (Template)

**Betreff:** „Ihr Vermieter [Name] lädt Sie zu MietVerwaltung ein"

**Body:**
```
Guten Tag [Mieter Name],

Ihr Vermieter [Vermieter Name] verwaltet Ihre Mietwohnung ab sofort 
mit MietVerwaltung. Im Mieter-Portal können Sie:

- Tickets an Ihren Vermieter senden
- Ihre Abrechnungen einsehen
- Wichtige Dokumente hochladen und herunterladen

[Kostenlos Portal öffnen]

Der Link ist 7 Tage gültig. Bei Fragen antworten Sie einfach auf diese E-Mail.

Mit freundlichen Grüßen
MietVerwaltung im Auftrag von [Vermieter Name]
```

### Mieter-Registrierung

**Flow:**
1. Link öffnet „Passwort setzen"-Seite (keine erneute E-Mail nötig, Token validiert E-Mail)
2. Passwort + Passwort wiederholen
3. 2FA einrichten (E-Mail-Code als bevorzugte Variante für Mieter)
4. Willkommens-Screen Mieter-Portal

**Mieter-Willkommens-Screen:**
- Titel: „Willkommen im Mieter-Portal"
- Subtext: „Hier sehen Sie Ihre Mietdaten, können Tickets erstellen und Dokumente einsehen."
- Kurze 3-Punkt-Checkliste:
  - [x] Konto erstellt
  - [x] Passwort gesetzt
  - [x] 2FA aktiviert
  - [ ] Profil vervollständigen (Telefon, Notfallkontakt)
- CTA: **„Zum Portal"**

### Mieter-Portal (First-Time)

- Oben: Kachel mit eigener Wohnung, Mieterhöhe, nächster Zahlungstermin
- Tabs: **Start**, **Tickets**, **Dokumente**
- Empty-State bei Tickets: „Noch keine Tickets – erstellen Sie bei einem Defekt direkt eines."
- Floating CTA auf Mobile: **„+ Ticket"**

---

## 10. Gamification

**Strategie:** Dezente Forward-Gamification – Fortschritt, Anerkennung und Gewohnheitsbildung, aber keine Punkte, Avatare oder Kinderzimmer-Optik.

### Fortschritts-Checkliste (primäres Gamification-Element)

Siehe Abschnitt 4. Hier geschieht die Hauptmotivierung: offene Schleifen, sichtbarer Fortschritt, bereits geschenkte Schritte.

### Badges & Achievements

**Darstellung:** In den Account-Einstellungen unter „Meine Erfolge" oder als kleines Ribbon im Dashboard. Keine Pop-ups außerhalb der App.

| Badge | Auslöser | Design |
|-------|----------|--------|
| **Objekt-Pionier** | Erstes Objekt angelegt | Haus-Icon mit kleinem Häkchen |
| **Erste Mieter** | Erster Mieter eingeladen | Personen-Icon |
| **Vertrags-Profi** | Erster Mietvertrag erstellt | Dokument-Icon |
| **Abrechnungs-Meister** | Erste Nebenkostenabrechnung versendet | Taschenrechner-Icon |
| **Mahnungs-Experte** | Erste Mahnung verschickt | Uhr-Icon |
| **KI-Early-Adopter** | Ersten Beleg per KI auswerten lassen | Stern-Icon |
| **Fristen-Experte** | 3 Monate ohne überfällige Fristen | Kalender-Icon |

**UI:**
- Graue, abgerundete Badges in einer Reihe
- Freigeschaltet: Navy-Farbe + Häkchen
- Noch gesperrt: ausgegraut mit Schloss-Icon
- Keine animierten Banner, nur dezente Toasts: „Abzeichen freigeschaltet: Abrechnungs-Meister"

### Streaks / Gewohnheitsmechanik

- „Mietverwaltung-Streak": Monatlich 1 produktive Aktion (Zahlung erfasst, Ticket bearbeitet, Dokument hochgeladen).
- Anzeige im Dashboard: „3 Monate in Folge aktiv" mit kleinem Flammen-Icon.
- Keine Bestrafung bei Unterbrechung – rein informativ.

### Milestone-Microinteractions

- Nach erster Abrechnung: dezente Success-Animation (sanftes Konfetti, 1,5 s)
- Nach 10 erfassten Zahlungen: Toast „10 Mietzahlungen erfasst – so behalten Sie den Überblick."
- Keine Level-Up-Screens, keine Soundeffekte.

### Upsell-Integration (dezent)

- Keine Gamification-Belohnungen, die auf Bezahlplänen verweisen.
- Stattdessen: Kontextuelle Hinweise nach erreichtem Wert: „Mit Pro können Sie Kosten per Beleg-Scan automatisch erfassen" erst nach erstem erfolgreichem Workflow.

---

## Zusammenfassung der Onboarding-Architektur

| Phase | Touchpoint | Ziel |
|-------|------------|------|
| Akquise | Landing Page / Demo-Modus | Vertrauen aufbauen vor Registrierung |
| Registrierung | Minimal-Formular + E-Mail + 2FA | Schneller, sicherer Account |
| Welcome | Personalisierter Screen + Checkliste | Orientierung, Motivation |
| Walkthrough | 4 Schritte im Produkt | Echte Daten anlegen, lernen durch Tun |
| Aha-Moment | Live-Dashboard nach Vertrag | Wert in <5 Min erleben |
| Verfeinerung | Empty-States, KI-Assistent, Badges | Tiefere Adoption ohne Druck |
| Mieter-Invite | E-Mail + Mieter-Portal | Netzwerkeffekt, Stickiness |

**Akzeptanzkriterien für das Onboarding:**
- Registrierung in ≤ 4 Feldern
- E-Mail + 2FA im Flow, aber nicht als Barriere
- Keine Pflicht-Tour vor dem Produkt
- Erstes Objekt in ≤ 3 Klicks erreichbar
- Checkliste startet bei ≥ 30 %
- Aha-Moment < 5 Min nach Login
- Mieter kann in ≤ 3 Schritten eigenes Portal nutzen
- Gamification ist dezent und nie kindisch
