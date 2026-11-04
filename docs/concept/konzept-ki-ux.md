# KI-UX-Konzept für MietVerwaltung

## Design-Prinzip: „KI, die da ist — aber nicht auffällt“

MietVerwaltung richtet sich an private Kleinvermieter, oft über 50, selten digital native. KI darf nicht als Gadget wirken, sondern als verlässlicher Helfer im Hintergrund. Sie wird nur dort sichtbar, wo sie dem Nutzer echte Arbeit abnimmt oder Vertrauen schafft. Alle KI-Ergebnisse bleiben überprüfbar und editierbar: Der Vermieter entscheidet, die KI macht den Rest.

Dieses Konzept baut auf:
- HBR: Kontextuelle Hilfe, niedrige Einstiegshürden, produktinterner Dialog
- Harvard HCI: Human-in-the-Loop, transparente KI, kontrollierbare Defaults
- NN/g: Progressive Disclosure, EAS-Framework, Status-Sichtbarkeit, Real-World-Sprache
- Don Norman: Klares mentales Modell, Feedback, Constraints
- BJ Fogg: Ability erhöhen, Prompts kontextuell setzen
- Psychologie-Tricks: Cognitive Load, Hick's Law, Zeigarnik, Peak-End, Microinteractions

---

## 1. KI-Sichtbarkeit

### Grundregel: Sichtbar nur bei Mehrwert

KI wird nicht mit Robotern, Sternen oder „Powered by AI“-Bannern angepriesen. Stattdessen zeigt die App an den Stellen, an denen etwas automatisch passiert, ein dezentes Erklär-Label.

### Sichtbarkeits-Stufen

| Stufe | Beispiel | Wann |
|---|---|---|
| Stumm | OCR erkennt Betrag im Hintergrund | Während des Hochladens |
| Hinweis | „Automatisch erkannt“ | Neben vorausgefülltem Feld |
| Bestätigung | „KI-Vorschlag — prüfen und übernehmen?“ | Vor Versand rechtlicher Dokumente |
| Transparenz | „Personenbezogene Daten wurden anonymisiert" | In Insights / Verarbeitungsprotokoll |

### Text-Beispiele

- „Wir haben aus dem Foto Betrag, Datum und Lieferanten erkannt. Bitte prüfen Sie die Angaben."
- „Dieser Entwurf wurde automatisch auf Basis Ihrer Vertragsdaten erstellt. Sie können jeden Satz bearbeiten."
- „Vorgeschlagene Kategorie: Heizung / Wartung"

### UI-Regeln

- Keine „KI"-Labels allein; immer in Kombination mit der Nutzer-Aktion: „Automatisch erkannt", „Vorschlag", „Vorausgefüllt"
- KI-gestützte Felder erhalten eine zarte gepunktete Rahmenfarbe (z. B. `--color-ai-hint: #7EB8FF`) oder ein kleines Sparkle-Icon nur bei Hover
- Keine blinkenden Animationen; nur subtile Shimmer während der Verarbeitung

---

## 2. KI-Beleg-Scan UX

### Workflow

```
[+] Beleg hochladen
      │
      ▼
[Foto / PDF / Kamera]
      │
      ▼
┌────────────────────────────┐
│  Scan läuft...             │  ← Shimmer auf Vorschaukarte
│  Betrag • Datum • Anbieter │
└────────────────────────────┘
      │
      ▼
┌────────────────────────────┐
│  Erkannt:                  │
│  Betrag: 249,80 € ✓        │
│  Datum: 14.03.2026 ✓       │
│  Anbieter: Heizungsbau     │
│  Schmidt GmbH ✓            │
│  Kategorie: Heizung/Wartung│
│  (vorgeschlagen)           │
└────────────────────────────┘
      │
      ▼
[Übernehmen] [Bearbeiten] [Nicht passend – manuell eingeben]
```

### Mockup-Ideen

1. **Upload-Button**: Großer Button „Beleg erfassen" mit Kamera-/Upload-Icon, prominent in Kostenbereich und Dashboard
2. **Ladezustand**: Vorschaukarte mit abgedunkeltem Foto, zentralem Spinner und animiertem Text „Beleg wird gelesen…"
3. **Ergebnis-Karte**: Extrahierte Felder als Formular angezeigt, erkannte Werte mit kleinem Häkchen, unklare Werte mit gelbem „Unsicher"-Badge
4. **Bestätigung**: Primary-Button „3 Positionen übernehmen" oder „Nur ausgewählte übernehmen"

### Text-Beispiele

- „Beleg wird gelesen…"
- „Fast fertig — wir prüfen die erkannten Daten."
- „Diese Angaben wurden aus dem Foto übernommen:"
- „Hier waren wir uns nicht sicher. Bitte prüfen Sie das Feld selbst."
- „Beleg wurde gespeichert. Sie finden ihn unter Kosten > Heizung/Wartung."

### UX-Prinzipien

- **EAS-Framework**: Automatische Felder vorausgefüllt, Nutzer muss nur noch prüfen
- **Progressive Disclosure**: Erweiterte Felder (z. B. Umlageschlüssel) erst auf Wunsch einblenden
- **Feedback**: Sofortiges Toast „3 Kostenpositionen übernommen"

---

## 3. KI-Ticket-Klassifizierung

### Workflow

```
Ticket kommt rein
      │
      ▼
┌─────────────────────────────┐
│  Neues Ticket               │
│  „Wasserhahn tropft im Bad"   │
│                             │
│  KI-Vorschlag:              │
│  Kategorie: Wasser          │
│  Priorität: Normal          │
│  Zuständigkeit: Sie selbst  │
└─────────────────────────────┘
      │
      ▼
[Bestätigen] [Kategorie ändern] [Priorität ändern]
```

### UI-Komponenten

1. **Ticket-Eingang**: Badge „Neu" in gelb, darunter kleines Label „Von KI vorsortiert"
2. **Vorschlag-Block**: Kategorie-Icon, Priorität-Badge, vorgeschlagener Betreff
3. **Bearbeiten-Modus**: Dropdowns mit vorausgewählten Werten; bei Abweichung wird Badge auf „Manuell gesetzt" geändert
4. **Mieter-Portal**: Mieter bekommt Bestätigung „Ihr Anliegen wurde erfasst. Wir melden uns."

### Text-Beispiele

- „Wir haben das Ticket automatisch kategorisiert. Passt das?"
- „Vorgeschlagene Kategorie: Wasser"
- „Priorität: Normal — Reaktionszeit typisch innerhalb von 3 Tagen"
- „Sie haben die Kategorie geändert. Die KI merkt sich das für ähnliche Tickets."

### Psychologischer Hintergrund

- **Default Bias**: Vorschläge werden meist übernommen, aber der Nutzer behält die Kontrolle
- **Recognition rather than Recall**: Dropdown zeigt alle Optionen; Vorschlag hebt sich visuell ab
- **Hick's Law**: Nur 4–5 Kategorien, 3 Prioritätsstufen

---

## 4. KI-Antwort-Entwürfe

### Workflow

```
Vermieter öffnet Ticket
      │
      ▼
[„Antwort entwerfen"-Button]
      │
      ▼
┌─────────────────────────────────────┐
│  KI-Vorschlag                       │
│                                     │
│  Sehr geehrte/r Frau/Herr [Name],   │
│                                     │
│  vielen Dank für Ihre Mitteilung.   │
│  Ich kümmere mich um die            │
│  Organisation eines Handwerkers     │
│  und melde mich bis [Datum].        │
│                                     │
│  Mit freundlichen Grüßen            │
│  [Name Vermieter]                   │
└─────────────────────────────────────┘
      │
      ▼
[Bearbeiten] [Als Entwurf speichern] [Senden]
```

### UI-Elemente

1. **Button**: „Antwort entwerfen" als sekundäre Aktion neben dem Textfeld, nicht ersetzend
2. **Editor**: Eingebetteter Rich-Text-Editor mit markierten Platzhaltern `[Name]`, `[Datum]`
3. **Varianten**: „Freundlich", „Formell", „Kurz" — vorausgewählt: „Passend zum Kontext"
4. **Nach dem Senden**: Toast „Antwort gesendet. Sie finden sie im Ticket-Verlauf."

### Text-Beispiele

- „Möchten Sie eine Antwortvorschlag erstellen?"
- „Hier ist ein passender Entwurf — bitte vor dem Senden prüfen."
- „Tonalität: freundlich-sachlich"
- „[Platzhalter] ersetzen wir automatisch durch die Daten aus dem Vertrag."

### Sicherheitsregeln

- Keine automatische Antwort ohne Bestätigung
- Bei rechtlich relevanten Themen (Mietminderung, Kündigung) nur formelle Vorlagen ohne Wertungen
- Vermieter muss den Senden-Button aktiv betätigen

---

## 5. KI-Smart-Insights

### Prinzip: Tägliche, aktionable Kurznachrichten

Das Dashboard zeigt jeden Tag max. 3 Insights. Keine generischen Charts, sondern konkrete Hinweise, die zu einer Handlung einladen.

### Kategorien

| Kategorie | Beispiel | Aktion |
|---|---|---|
| Fristen | „Mietzahlung für Mieter Müller (Wohnung 2) ist überfällig seit 5 Tagen." | Mahnung erstellen |
| Cashflow | „Dieser Monat: 4.280 € Miete eingegangen, 1.120 € Ausgaben." | Details ansehen |
| Instandhaltung | „Jahreswartung Heizung fällig in 30 Tagen." | Termin planen |
| Vertrag | „Mietvertrag für Wohnung 3 endet in 90 Tagen." | Verlängerung prüfen |
| Optimierung | „Ihre Nebenkostenabrechnung 2025 ist noch offen." | Abrechnung starten |

### Darstellung

```
┌─────────────────────────────────────────┐
│  Heute für Sie relevant                 │
│                                         │
│  🔴  Miete überfällig — Mahnung prüfen  │
│  💰  4.280 € Miete eingegangen          │
│  📅  Heizungswartung in 30 Tagen        │
│                                         │
│  [Alle Insights ansehen]                │
└─────────────────────────────────────────┘
```

### Formulierungsregeln

- Kein „Die KI empfiehlt…", sondern sachliche Fakten
- Konkrete Namen, Wohnungen und Beträge
- Jeder Insight endet mit einer klickbaren Aktion
- Keine Ablenkung durch überflüssige Visuals

### Peak-End-Moment

Wenn alle Fristen erledigt sind, erscheint ein positiver Abschluss-Insight:

> „Alles im grünen Bereich. Keine offenen Fristen, keine überfälligen Mieten."

---

## 6. KI-NK-Abrechnung

### Workflow

```
Abrechnungsperiode wählen
      │
      ▼
KI sammelt alle Kostenbelege der Periode
      │
      ▼
┌─────────────────────────────────────┐
│  Automatisch zugeordnet:            │
│  ✓ Heizung → qm → 2.400 €           │
│  ✓ Wasser → Verbrauch → 890 €       │
│  ✓ Müll → Personen → 320 €          │
│  ? Dachreparatur 1.800 €            │
│    (keine klare Zuordnung)          │
└─────────────────────────────────────┘
      │
      ▼
Nutzer prüft / korrigiert / ergänzt
      │
      ▼
KI prüft Vollständigkeit
      │
      ▼
KI generiert Abrechnungstext
      │
      ▼
Vorschau → Bestätigen → Versand
```

### UI-Komponenten

1. **Wizard**: 4 Schritte — (1) Periode, (2) Kosten zuordnen, (3) Verteilen, (4) Text & Versand
2. **Zuordnungs-Liste**: Jede Kostenposition als Karte mit Icon, Betrag, vorgeschlagener Verteilung
3. **Unsicher-Badge**: Gelbes „Bitte prüfen" neben unklaren Belegen
4. **Vollständigkeits-Check**: Liste mit Häkchen
   - Alle umlagefähigen Kosten erfasst
   - Verteilungsschlüssel geprüft
   - Mieterdaten aktuell
   - Abrechnungstext erstellt
5. **Abrechnungstext-Vorschau**: Lesbarer Fließtext mit Erklärung der Verteilung

### Text-Beispiele

- „Wir haben 12 Belege für 2025 gefunden und 10 automatisch zugeordnet."
- „Diese Position konnte nicht eindeutig zugeordnet werden. Bitte wählen Sie die Kategorie."
- „Verteilung nach Quadratmeter (Standard) — passt das zu Ihrem Mietvertrag?"
- „Der Abrechnungstext erklärt Mietern verständlich, wie die Kosten entstanden sind."

### UX-Prinzipien

- **Explainable AI**: Bei jeder Verteilung wird ein kurzer Rechenweg gezeigt
- **Human-in-the-Loop**: Unsichere Zuordnungen stoppen den Prozess, bis der Nutzer entscheidet
- **Zeigarnik-Effekt**: Fortschrittsbalken zeigt „Schritt 2 von 4"

---

## 7. KI-Mahnwesen

### Workflow

```
Offene Miete erkannt
      │
      ▼
Dashboard-Insight: „Mietzahlung überfällig"
      │
      ▼
Vermieter klickt „Mahnung prüfen"
      │
      ▼
KI generiert Mahnungstext
      │
      ▼
┌─────────────────────────────────────┐
│  Mahnung vom [Datum]                │
│                                     │
│  Sehr geehrte/r [Mieter],           │
│                                     │
│  für die Wohnung [Adresse] ist die   │
│  Miete für [Monat] in Höhe von       │
│  [Betrag] bislang nicht eingegangen. │
│                                     │
│  Wir bitten um Zahlung innerhalb     │
│  von 7 Tagen.                        │
│                                     │
│  [PDF-Vorschau]                     │
└─────────────────────────────────────┘
      │
      ▼
[Bearbeiten] [Entwurf speichern] [PDF erstellen & senden]
```

### UI-Elemente

1. **Mahnungs-Assistent**: Dialog mit Schritten
   - Fristen prüfen
   - Mahnstufe wählen (1. freundlich, 2. förmlich, 3. letzte Mahnung)
   - Text prüfen
   - PDF erstellen
2. **Rechtliche Hinweise**: Banner „Bitte prüfen Sie den Mahntext vor dem Versand. Rechtliche Verantwortung liegt bei Ihnen."
3. **Vorschau**: Originalgetreue PDF-Vorschau mit Platzhaltern aufgelöst
4. **Sende-Log**: „Mahnung an Max Müller gesendet am 14.03.2026, 09:42 Uhr"

### Text-Beispiele

- „Mietzahlung für Februar 2026 noch nicht eingegangen."
- „Wir empfehlen eine freundliche 1. Mahnung."
- „Möchten Sie den Text anpassen? Rechtlich relevante Formulierungen bleiben erhalten."
- „Mahnung wurde als Entwurf gespeichert. Sie können sie später versenden."

### Human-in-the-Loop

- Keine automatische Mahnung ohne explizite Freigabe
- System warnt, wenn Fristen noch nicht abgelaufen sind
- Vermieter muss PDF-Vorschau gesehen haben, bevor Senden aktiv wird (Constraint)

---

## 8. KI-Dokument-Generierung

### Workflow

```
Dokumente > Neu erstellen
      │
      ▼
Template wählen:
• Mietvertrag
• Kündigung (eigenbedarf / ordentlich)
• Mieterhöhung
• Einzugsbestätigung
      │
      ▼
KI füllt ausgehend von Objekt / Mieter / Vertrag
      │
      ▼
┌─────────────────────────────────────┐
│  Vorschau                           │
│                                     │
│  [PDF-Thumbnail mit markierten      │
│   Platzhaltern, die bereits         │
│   ersetzt wurden]                   │
│                                     │
│  Ausgefüllt: 18 von 20 Feldern      │
│  Unklar: 2 Felder                   │
└─────────────────────────────────────┘
      │
      ▼
[Felder bearbeiten] [Als Entwurf] [PDF erstellen]
```

### UI-Elemente

1. **Template-Galerie**: Kacheln mit Icon, Name, kurzer Zweckbeschreibung
2. **Ausfüll-Fortschritt**: „18 von 20 Feldern automatisch ausgefüllt"
3. **Formular-Seite**: Felder gruppiert; ausgefüllte Felder mit „Automatisch"-Badge
4. **PDF-Vorschau**: Großes Thumbnail, Seitenwechsel möglich
5. **Finaler Dialog**: Bestätigung mit Datum, Empfänger, Speicherort

### Text-Beispiele

- „Wir haben den Mietvertrag mit Daten aus Objekt und Mieter vorausgefüllt."
- „Diese Felder konnten wir nicht automatisch ergänzen — bitte ergänzen Sie sie."
- „Vor dem Erstellen: Bitte prüfen Sie alle Angaben."
- „Dokument erstellt und unter Dokumente > Mietverträge gespeichert."

### Rechtssicherheit

- Rechtlich sensible Templates enthalten einen Disclaimer
- Keine automatische Unterzeichnung oder Versand
- Platzhalter für Notar / Zeugen / Termine müssen manuell geprüft werden

---

## 9. KI-Fehler: Graceful Degradation

### Prinzip: Niemals falsche Daten ungeprüft übernehmen

Wenn die KI unsicher ist oder fehlschlägt, fällt die UX auf manuelle Eingabe zurück — ohne Frustration und ohne den Nutzer als „Ersatz" erscheinen zu lassen.

### Fehler-Stufen

| Situation | UX-Reaktion | Badge |
|---|---|---|
| OCR konnte keinen Betrag erkennen | Feld bleibt leer, Fokus gesetzt, Hinweis: „Bitte Betrag eingeben" | „Nicht erkannt" |
| KI ist bei Kategorie unsicher (z. B. 60 %) | Dropdown mit Top-3-Vorschlägen, kein Auto-Auswahl | „Unsicher" |
| Kein Text für Antwort generierbar | Button inaktiv mit Tooltip „Für dieses Ticket steht noch kein Vorschlag bereit" | — |
| Abrechnungsbeleg unklar | Karte wird als „Bitte prüfen" markiert, Prozess kann nicht abgeschlossen werden | „Bitte prüfen" |
| KI-Generierung liefert rechtlich problematischen Text | Warnung: „Bitte prüfen Sie diesen Abschnitt besonders sorgfältig." | „Manuell prüfen" |

### Text-Beispiele

- „Das Foto war unscharf. Bitte laden Sie es erneut hoch oder geben Sie die Daten manuell ein."
- „Wir sind uns hier nicht sicher. Bitte wählen Sie aus den Vorschlägen oder geben Sie es selbst ein."
- „Kein Vorschlag möglich — Sie können den Text selbst schreiben."
- „Diese Angabe wurde nicht automatisch übernommen, damit keine Fehler entstehen."

### UI-Muster

- Gelbe „Unsicher"-Badges statt roter Fehler, um Panik zu vermeiden
- Bei Unsicherheit wird der Primär-Button auf „Manuell fortfahren" umgestellt
- „Nicht sicher?" als freundliche Hilfe-Frage, nicht als Schuldzuweisung

---

## 10. KI-Transparenz & DSGVO

### Prinzip: Datenschutz als Vertrauensmerkmal sichtbar machen

MietVerwaltung nutzt Presidio für Anonymisierung. Das wird nicht versteckt, sondern als Qualitätsmerkmal kommuniziert.

### Sichtbare Elemente

| Element | Wo | Text/Icon |
|---|---|---|
| Anonymisierungs-Status | Insights-Panel | „Personenbezogene Daten vor Analyse anonymisiert" |
| Verarbeitungsprotokoll | Einstellungen > KI & Datenschutz | „Letzte Anonymisierung: Heute, 08:14" |
| Datenschutz-Hinweis | Beim ersten KI-Feature | „Ihre Daten werden DSGVO-konform verarbeitet." |
| Einwilligung | Registrierung | Checkbox „KI-Features nutzen (optional)" |
| Export & Löschung | Einstellungen | „Meine KI-Daten herunterladen / löschen" |

### Mockup-Idee: Verarbeitungs-Karte

```
┌─────────────────────────────────────┐
│  KI-Verarbeitung                    │
│                                     │
│  ✅  Beleg gescannt                 │
│  ✅  Personenbezogene Daten         │
│     anonymisiert                    │
│  ✅  Analyse durchgeführt           │
│  ⏳  Ergebnis wird geprüft          │
│                                     │
│  [Details ansehen]                  │
└─────────────────────────────────────┘
```

### Text-Beispiele

- „Bevor Daten analysiert werden, werden Namen, Adressen und Kontaktdaten unkenntlich gemacht."
- „Sie haben jederzeit die Kontrolle: KI-Features können einzeln deaktiviert werden."
- „Verarbeitung erfolgt in unserer DACH-Cloud."
- „Ihre Einwilligung können Sie in den Einstellungen widerrufen."

---

## 11. KI-Grenzen

### Prinzip: Rechtliche Verantwortung liegt immer beim Menschen

KI unterstützt, aber sie entscheidet nicht. Das muss an den kritischen Stellen klar kommuniziert werden.

### Was KI NICHT macht

| Bereich | KI macht | KI macht NICHT |
|---|---|---|
| Mietvertrag | Vorschläge, Platzhalter füllen | Vertrag unterschreiben oder als rechtsgültig deklarieren |
| Kündigung | Textbausteine aufbereiten | Kündigung aussprechen oder Fristen beurteilen |
| Mieterauswahl | Daten aus Dokumenten extrahieren | Empfehlung „annehmen / ablehnen" geben |
| Mahnung | Mahntext generieren | Mahnung automatisch versenden |
| Abrechnung | Kosten zuordnen und Texte vorschlagen | Abrechnung ohne Prüfung versenden |
| Rechtsfragen | Hilfestellung zu Prozessen | Rechtsberatung ersetzen |

### UI-Komponenten

1. **Disclaimer-Banner** bei Dokumenten, Mahnungen, Kündigungen:
   > „Dies ist ein unterstützender Entwurf. Bitte prüfen Sie alle Angaben. Rechtliche Verantwortung liegt bei Ihnen."
2. **Sende-Constraints**: Senden-Button bleibt inaktiv, bis Bestätigungs-Checkbox angeklickt wurde
3. **Hilfe-Link**: „Unsicher? Rechtlichen Rat einholen" verlinkt auf Vermieterverein / Anwaltssuche

### Text-Beispiele

- „MietVerwaltung hilft Ihnen bei der Erstellung, ersetzt aber keine Rechtsberatung."
- „Bitte prüfen Sie den Mahntext vor dem Versand."
- „Die endgültige Entscheidung liegt immer bei Ihnen."

---

## 12. KI-Personality

### Stimme der KI

- Professionell, aber nicht kühl
- Freundlich, aber nicht überfreundlich
- Dezent, nie aufdringlich
- Kein Roboter-Sprech, keine Fachjargon-Bombe
- Immer klar, wer entscheidet: der Nutzer

### Sprachregeln

| Statt… | Besser… |
|---|---|
| „KI hat erkannt…" | „Wir haben erkannt…" |
| „KI generiert Text…" | „Hier ist ein Vorschlag…" |
| „KI empfiehlt dringend…" | „Sie könnten als Nächstes…" |
| „AI-Processing läuft…" | „Wir prüfen das gerade…" |
| „92 % sicher" (siehe Punkt 14) | „Sehr wahrscheinlich richtig" |
| „Fehler! KI hat versagt." | „Hier waren wir uns nicht sicher." |

### Beispiele für Microcopy

- „Fast geschafft — nur noch kurz prüfen."
- „Wir haben Ihnen Arbeit abgenommen: 3 Felder vorausgefüllt."
- „Kein passender Vorschlag? Kein Problem — Sie können alles selbst eingeben."
- „Danke fürs Prüfen. So bleibt alles korrekt."

---

## 13. KI-Loading-States

### Prinzip: Wartezeiten als Fortschritt erlebbar machen

Während KI arbeitet, wird der Nutzer nicht im Unklaren gelassen. Keine bloßen Spinner, sondern sinnvolle Zwischenzustände.

### Loading-Patterns

| Dauer | Pattern | Beispiel |
|---|---|---|
| < 500 ms | Subtiler Shimmer auf Karte | Button-Label ändert sich kurz |
| 500 ms – 2 s | Inline-Spinner + Text | „Beleg wird gelesen…" |
| 2–6 s | Fortschrittsbalken + Schritte | „Belege sammeln → Daten erkennen → Zuordnen → Ergebnis prüfen" |
| > 6 s | Detaillierter Prozess + Abbrechen | „Abrechnung wird erstellt… Schritt 3 von 5" |

### UI-Elemente

1. **Skeleton**: Platzhalter-Karten während Insights geladen werden
2. **Shimmer**: Sanfte Wellen-Animation auf OCR-Vorschaukarten
3. **Progress-Stepper**: Sichtbare Schritte bei längeren Prozessen
4. ** Abbrechen-Option**: Bei > 6 s „Abbrechen" ermöglichen, ohne Datenverlust
5. **Estimated Time**: Bei längeren Vorgängen „Noch ca. 10 Sekunden"

### Text-Beispiele

- „Wir lesen den Beleg…"
- „Noch ca. 5 Sekunden."
- „Schritt 2 von 4: Kosten zuordnen"
- „Fast fertig — wir bereiten die Vorschau vor."

---

## 14. KI-Confidence-Scores

### Prinzip: Vertrauen durch ehrliche Unsicherheit

Confidence-Scores werden nicht als abstrakte Zahlen (z. B. „92 %") dargestellt, sondern in menschlich verständliche Stufen übersetzt.

### Confidence-Stufen

| Score | Anzeige | Farbe | Bedeutung |
|---|---|---|---|
| > 90 % | „Sehr wahrscheinlich richtig" | Grün | Auto-Auswahl, trotzdem editierbar |
| 70–90 % | „Wahrscheinlich richtig — bitte kurz prüfen" | Blau | Vorausgewählt, aber Badge sichtbar |
| 50–70 % | „Unsicher — bitte wählen" | Gelb | Kein Auto-Auswahl, Vorschläge angeboten |
| < 50 % | „Nicht erkannt" | Grau | Feld leer, Nutzer eingeben |

### UI-Muster

- Confidence wird nur bei Hover oder auf Anfrage als Zahl angezeigt; primär die Stufe
- „Sehr wahrscheinlich richtig"-Felder erhalten ein dezentes grünes Häkchen
- „Unsicher"-Felder erhalten einen gelben Rand und ein Fragezeichen-Icon
- Bei aggregierten Ergebnissen (z. B. OCR) zeigt die Karte eine Gesamtbewertung

### Text-Beispiele

- „Sehr wahrscheinlich richtig"
- „Bitte kurz prüfen"
- „Hier brauchen wir Ihre Hilfe"
- „Nicht erkannt — bitte eingeben"

### Warum keine Zahlen im UI?

- **Cognitive Load**: Zahlen erzeugen unnötige Fragen („Was bedeutet 87 % genau?")
- **Vertrauen**: Ehrliche Stufen wirken transparenter
- **Hick's Law**: Weniger Optionen schneller entscheidbar

---

## Zusammenfassung: Die 5 Goldenen Regeln der KI-UX in MietVerwaltung

1. **Human-in-the-Loop**: KI schlägt vor, der Vermieter entscheidet und sendet.
2. **Kontext statt Branding**: KI wird dort sichtbar, wo sie hilft — nicht als Marketing-Label.
3. **Ehrliche Unsicherheit**: Unsichere Ergebnisse werden klar markiert und zur manuellen Prüfung eingeladen.
4. **Rechtliche Verantwortung beim Menschen**: Bei Dokumenten, Mahnungen und Kündigungen gibt es klare Constraints und Bestätigungen.
5. **Professionell & dezent**: Die KI spricht wie ein kompetenter Assistent, nicht wie ein Roboter.

---

*Dokument erstellt am: 2026-10-28*
*Zweck: Komplettes UX-Konzept für KI-Sichtbarkeit und -Interaktion in MietVerwaltung SaaS*
