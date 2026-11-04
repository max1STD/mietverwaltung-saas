# Conversion-Optimierungs-Konzept — MietVerwaltung SaaS

> Ziel: Free-User in zahlende Kunden verwandeln, zahlende Kunden halten und auf höhere Pläne upgraden.
> Ausgangslage: Free 2 WE / Basis 14,90 € (5 WE) / Pro 29,90 € (25 WE) / Business 49,90 € (∞). KI als USP. DACH-Markt, 6,3 Mio. private Vermieter.
> Design-Prinzipien: Apple-Style, niedrige kognitive Belastung, Social Proof, Loss Aversion, Anchoring, Default Bias, progressive Disclosure.

---

## 1. Pricing-Page-Design

### Strategische Ziele
- Business als visueller Preisanker setzen → Pro wirkt wie der „kluge Kompromiss“.
- Pro als „Most Popular“ markieren → ca. 60–70 % wählen die Mittelstufe.
- Jahreszahlung als Default wählen, Monatszahlung als sekundäre Option.
- Preis zuerst, Features danach, keine Textwüste.

### Layout (Desktop → Mobile)

```
HERO-BEREICH
Headline: „Wählen Sie den Plan, der Ihr Vermieter-Leben leichter macht."
Subline:  „Starten Sie kostenlos. Upgraden Sie, wenn Ihr Portfolio wächst."

Jahres/Monat-Toggle  [Jährlich bezahlen — 2 Monate geschenkt]  [Monatlich]

┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  ┌──────────────┐
│   FREE       │  │   BASIS      │  │      PRO          │  │  BUSINESS    │
│   0 €/Monat  │  │  11,88 €/Mo  │  │   23,92 €/Mo      │  │  39,92 €/Mo  │
│   0 €/Jahr   │  │ 142,56 €/Jahr│  │  287,04 €/Jahr    │  │ 479,04 €/Jahr│
│              │  │  (statt 14,90)│  │  (statt 29,90)    │  │ (statt 49,90)│
│  2 Wohnungen │  │  5 Wohnungen │  │ 25 Wohnungen      │  │ Unbegrenzt   │
│  1 Objekt    │  │  ∞ Objekte   │  │  ∞ Objekte        │  │  ∞ Objekte   │
│              │  │              │  │  ★ Beliebtester   │  │              │
│              │  │              │  │     Plan          │  │              │
│ [Kostenlos   │  │ [14 Tage     │  │ [14 Tage          │  │ [14 Tage     │
│  starten]    │  │  testen]     │  │   kostenlos       │  │  testen]     │
│              │  │              │  │   testen]         │  │              │
└──────────────┘  └──────────────┘  └───────────────────┘  └──────────────┘

Darunter: Kurze Feature-Bullets pro Plan (max. 5 pro Karte).
```

### Decoy-Effekt
- **Business 49,90 €** wirkt als Anker. Daneben wirkt Pro 29,90 € fast „geschenkt" für die doppelte Wohnungsanzahl und fast alle Features.
- **Basis 14,90 €** wirkt als „Einstieg" – Free-User, die an Grenzen stoßen, springen leichter auf 14,90 € als auf 29,90 €.
- Wichtig: Der Free-Plan darf nicht zu gut aussehen. Karte leicht ausgegraut, CTA sekundär gestylt.

### Microcopy
- Pro-Karte Badge: **„Meist gewählt"** + kleines Stern-Icon.
- Jahrespreis: groß, Monats-Äquivalent darunter klein: „*entspricht 14,90 €/Monat bei monatlicher Zahlung".
- Sicherheits-Label unter Preisen: „Jederzeit kündbar · Keine Einrichtungsgebühr · 14 Tage kostenlos testen".
- „Unsicher? Starten Sie kostenlos und upgraden Sie jederzeit."

### Vergleichstabelle
- Direkt unter den Karten, eingeklappt auf Mobilgeräten.
- Zeilen: Wohnungen, Objekte, Mieter, Storage, KI-Beleg-Scan, KI-Mahnungen, Smart Insights, Automatisches Mahnwesen, Custom Branding, eID, Support.
- Kurze, deutsche Begriffe. Kein Jargon.

### CTA-Hierarchie
- Pro: Primary Button (Navy #0D3B70, weiße Schrift).
- Basis: Secondary Button (weiß, Navy-Border).
- Business: Secondary Button oder „Sales kontaktieren"-Link.
- Free: Tertiary Link-Style-Button.

---

## 2. Free-Tier-Strategie

### Was ist kostenlos?
- **2 Wohnungen** in **1 Objekt**.
- **1 Mieter** pro Wohnung.
- Basis-Dashboard: Mieteinnahmen, offene Tickets, anstehende Fristen.
- Manuelle Kosten-Erfassung ohne Beleg-Scan.
- Einfache Nebenkostenabrechnung (manuelle Berechnung, kein KI-Erklärungstext).
- Basis-Ticket-System ohne KI.
- Dokumenten-Upload (1 GB Storage).
- E-Mail-Support (48 h Antwortzeit).

### Was ist NICHT kostenlos?
- KI-Features (Auto-Kategorisierung, Beleg-Scan, Antwort-Entwürfe, Smart Insights).
- PDF-Export mit Briefkopf.
- Automatisches Mahnwesen.
- Fristen-Warner.
- eID-Verifikation.
- Mehr als 2 Wohnungen / 1 Objekt.

### Wert schaffen ABER Upgrade-Drang erzeugen
| Free-Feature | Upgrade-Drang |
|--------------|---------------|
| 2 Wohnungen | Private Vermieter mit 1–2 Wohnungen fühlen sich bedient; bei 3. Wohnung entsteht sofort Reibung. |
| Manuelle Kosten-Erfassung | Nach 3–5 Kosten pro Jahr will niemand mehr manuell tippen. |
| Einfache NK-Abrechnung | Ohne KI-Erklärungstext müssen Vermieter selbst erklären – fehleranfällig und zeitaufwändig. |
| Basis-Tickets ohne KI | Mieter-Anfragen häufen sich; manuelle Kategorisierung nervt. |
| 1 GB Storage | Nach wenigen Dokumenten + Fotos ist Schluss. |
| 48 h Support | Dringende Fragen vor Abrechnungsfristen → schneller Support lockt. |

### Free-Tier-Philosophie
> „Genug, um den Job zu erledigen – aber langsam genug, dass man merkt, wie viel besser es mit KI wäre."

- Free muss **funktionieren**, sonst verlassen Nutzer die App.
- Free darf **nicht angenehm genug** sein, um nie zu upgraden.
- Der Aha-Moment („Das spart mir Zeit") kommt durch Basis/Pro, nicht durch Free.

---

## 3. Upgrade-Triggers

### In-App-Trigger-Matrix

| Nr. | Aktion / Zustand | Trigger-Bedingung | Gezeigte Nachricht / Modal | Ziel-Plan |
|-----|------------------|-------------------|----------------------------|-----------|
| T1 | 3. Wohnung anlegen | Aktuell 2 Wohnungen, User klickt „+ Wohnung" | Inline Banner: „Im Free-Plan sind 2 Wohnungen inklusive. Upgrade auf Basis für 5 Wohnungen — 14 Tage kostenlos testen." | Basis |
| T2 | 2. Objekt anlegen | Aktuell 1 Objekt, User klickt „+ Objekt" | Modal: „Mehrere Objekte verwalten? Basis erlaubt unbegrenzte Objekte." | Basis |
| T3 | Beleg-Scan versuchen | User lädt Rechnung hoch | Teaser: „Beleg-Scan spart 5 Min pro Kostenbeleg. Ab Basis verfügbar." | Basis |
| T4 | 6. Wohnung anlegen | Aktuell 5 Wohnungen (Basis) | Banner: „Basis deckt 5 Wohnungen ab. Für 25 Wohnungen upgraden Sie auf Pro." | Pro |
| T5 | Automatische Mahnung erstellen | Basis-User klickt „Mahnung" | Modal: „KI-Mahnungen inkl. Fristberechnung ab Pro." | Pro |
| T6 | Smart Insights öffnen | Basis-User sieht „Insights"-Tab | Teaser: „Tägliche KI-Analyse Ihres Portfolios — nur in Pro." | Pro |
| T7 | Mieterbewerbung starten | User will Ausweis-Upload / Schufa | Modal: „Mieterbewerbung mit eID & KI-Extraktion ab Pro." | Pro |
| T8 | 26. Wohnung anlegen | Aktuell 25 Wohnungen (Pro) | Banner: „Ihr Portfolio wächst. Business bietet unbegrenzte Wohnungen + Team-Funktion." | Business |
| T9 | Team-Nutzer einladen | Pro-User klickt „Team" | Modal: „Mehrere Nutzer pro Portfolio ab Business." | Business |
| T10 | API-Zugang anfragen | Pro-User öffnet Einstellungen → API | Teaser: „API-Zugang für Integrationen ab Business." | Business |
| T11 | Storage-Limit 80 % erreicht | Jeder Plan | Banner: „Speicher fast voll. Extra-Speicher oder höherer Plan." | passend |
| T12 | Support-Antwort >24h | Free-User wartet auf Support | E-Mail: „Schnellerer Support mit Basis (24 h) oder Pro (12 h)." | Basis/Pro |

### Trigger-Design-Regeln
- **Kontextuell**: Trigger direkt an der Aktion, nicht als Pop-up aus dem Nichts.
- **Hilfreich, nicht aggressiv**: „Diese Funktion spart Zeit" statt „Kaufe jetzt!".
- **Ein-Klick-Trial**: Aus jedem Trigger direkt „14 Tage kostenlos testen" möglich.
- **Nicht bei jedem Klick**: Max. 1 Upgrade-Nudge pro Session; sonst Frust.

### Spezielle Trigger: Fälligkeiten & Abrechnungszeit
- 2 Tage vor Mietfälligkeit: „Morgen fällt die Miete. Upgrade auf Basis, um Mahnungen zu automatisieren."
- Dezember: „Erstellen Sie Ihre Nebenkostenabrechnung mit KI bis Weihnachten."

---

## 4. Feature-Gating

### Gating-Philosophie
- Nicht hinter verschlossenen Türen verstecken – Features sichtbar machen, aber als „Pro-Feature" oder „Basis-Feature" kennzeichnen.
- Jede gesperrte Funktion ist ein **Upgrade-Teaser**, der den Wert verspricht.
- Keine leeren Buttons. Gesperrte Features zeigen Mini-Vorschau oder Tooltip.

### Gating-UI-Muster

#### Muster A: Inline-Teaser mit Lock-Icon
```
[🔒 KI-Beleg-Scan]      Rechnung fotografieren – Betrag & Kategorie automatisch erkannt.
                        Ab Basis-Plan verfügbar. [14 Tage testen]
```

#### Muster B: Upsell-Banner im Workflow
```
┌─────────────────────────────────────────────────────────────┐
│  💡 Tipp: Bei 3+ Kostenbelegen im Monat spart der Beleg-Scan  │
│     durchschnittlich 25 Minuten.                            │
│     [Jetzt Basis testen — 14 Tage kostenlos]                │
└─────────────────────────────────────────────────────────────┘
```

#### Muster C: Premium-Label im Menü
```
Dashboard | Objekte | Mieter | Tickets | Kosten & Abrechnung
                                  ↑
                         [PRO] Smart Insights
```

#### Muster D: Modal bei Aktion
```
Titel: „KI-Mahnung erstellen"
Body:  „Automatische Mahnstufe 1–3 mit Fristberechnung und E-Mail-Versand.
        Verfügbar ab Pro (29,90 €/Monat)."
CTA:   [14 Tage kostenlos testen] [Zurück zur Übersicht]
```

### Feature-Matrix (vereinfachte Gating-Logik)

| Feature | Free | Basis | Pro | Business |
|---------|------|-------|-----|----------|
| Wohnungen | 2 | 5 | 25 | ∞ |
| Objekte | 1 | ∞ | ∞ | ∞ |
| Mieter | 1 pro WE | ∞ | ∞ | ∞ |
| Kosten manuell erfassen | ✅ | ✅ | ✅ | ✅ |
| KI-Beleg-Scan | ❌ | ✅ | ✅ | ✅ |
| Ticket Auto-Kategorisierung | ❌ | ✅ | ✅ | ✅ |
| Antwort-Entwürfe Tickets | ❌ | ✅ | ✅ | ✅ |
| Smart Insights | ❌ | ❌ | ✅ | ✅ |
| KI-Mahnungen Stufe 1–3 | ❌ | ❌ | ✅ | ✅ |
| Mieterhöhung §558 BGB | ❌ | ❌ | ✅ | ✅ |
| Automatisches Mahnwesen | ❌ | ❌ | ✅ | ✅ |
| Mieter-Bewerbung + eID | ❌ | ❌ | ✅ (3 eID/Monat) | ✅ (10 eID/Monat) |
| Custom Branding | ❌ | ❌ | ✅ | ✅ |
| API-Zugang | ❌ | ❌ | ❌ | ✅ |
| Team-Nutzer | ❌ | ❌ | ❌ | 5 + 5 €/Nutz |
| White-Label | ❌ | ❌ | ❌ | ✅ |
| Storage | 1 GB | 5 GB | 25 GB | 100 GB |
| Support | 48 h | 24 h | 12 h | 4 h + Telefon |

### Kommunikation von Limits
- **Nicht**: „Du hast keine Berechtigung."
- **Sondern**: „Diese Funktion ist im [Plan]-Plan enthalten. Wechseln Sie, um sie zu nutzen."
- **Bei Wohnungs-Limit**: „2 von 2 Wohnungen belegt."
- **Bei eID-Limit**: „3 von 3 eID-Verifikationen diesen Monat genutzt."

---

## 5. Trial-Strategie

### 14-Tage-Pro-Trial für alle neuen Free-Registrierungen?

**Empfohlene Variante: Self-serve Trial auf dem gewählten Plan.**

| Plan | Trial-Laufzeit | Kreditkarte |
|------|----------------|-------------|
| Basis | 14 Tage | Optional (Conversion ↑, wenn nicht nötig; Fraud-Risiko beachten) |
| Pro | 14 Tage | Optional |
| Business | 14 Tage | **Erforderlich** (B2B, höheres Commitment, weniger Abuse) |

> Alternative: Pro-Trial für alle neuen User – „14 Tage volle KI-Power testen", danach Free-Fallback. Das erzeugt starken Loss-Aversion-Effekt, weil Nutzer die Features kennenlernen und dann verlieren.

### Empfohlener Ablauf: „Pro-Trial für alle"

```
Tag 0: Registrierung
  → Willkommens-E-Mail: „Willkommen bei MietVerwaltung. 14 Tage Pro kostenlos."
  → Dashboard-Checkliste mit 5 Schritten, davon 2 vorausgefüllt.

Tag 1: Onboarding-Mail
  → „So legen Sie Ihr erstes Objekt an"

Tag 3: Aktivierungs-Mail
  → „Erstellen Sie Ihre erste Nebenkostenabrechnung in 10 Minuten"

Tag 7: Mid-Trial-Mail
  → „Noch 7 Tage volle KI-Power"
  → Social Proof: „Andere Vermieter sparen 5 Stunden/Monat."

Tag 11: Loss-Aversion-Mail
  → „In 3 Tagen läuft Ihr Pro-Zugang ab"
  → Liste: „Das verlieren Sie: Beleg-Scan, KI-Mahnungen, Smart Insights, 25 Wohnungen"

Tag 13: Letzte Chance
  → „Letzter Tag: Pro für 23,92 €/Monat (jährlich) sichern"
  → Countdown-Timer im E-Mail-Header (statisches Bild, 24 h gültig)

Tag 14: Trial endet
  → In-App-Banner: „Ihr Pro-Zugang ist abgelaufen. Ihre Daten sind sicher – upgrade jederzeit."
  → Free-Fallback: alle über 2 Wohnungen gesperrt, KI-Features deaktiviert.
  → E-Mail: „Willkommen im Free-Plan – so holen Sie das meiste raus"
```

### Loss-Aversion-Elemente
- Während des Trials: Nutzer dazu bringen, **Daten anzulegen** (Objekte, Mieter, Kosten). Je mehr sie investieren, desto schmerzhafter ist der Verlust.
- „Ihre Abrechnungen bleiben gespeichert – aber der KI-Export ist jetzt gesperrt."
- Trial-Ende-Countdown im Dashboard-Header: „Noch X Tage volle KI-Power".

### Trial-Reminder in der App
- Dashboard-Header während Trial: blaues Banner „Pro-Trial aktiv – noch 9 Tage".
- Am letzten Tag: rotes Banner „Letzter Tag Ihres Pro-Trials".
- Settings → Abonnement: Fortschrittsbalken „Trial läuft ab in X Tagen".

---

## 6. In-App-Upgrades

### Upgrade-Modal-Design

```
┌─────────────────────────────────────────────────────────────┐
│  ✨ Mehr Zeit für das, was zählt                           │
│                                                             │
│  Sie nutzen gerade den Free-Plan.                           │
│  Für 3 Wohnungen brauchen Sie den Basis-Plan.               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Ihr aktueller Plan: Free (2 Wohnungen)              │   │
│  │  Empfohlener Plan:   Basis (5 Wohnungen)            │   │
│  │                                                     │   │
│  │  ✓ 3 weitere Wohnungen                             │   │
│  │  ✓ KI-Beleg-Scan                                   │   │
│  │  ✓ Antwort-Entwürfe für Tickets                    │   │
│  │  ✓ PDF-Export mit Briefkopf                        │   │
│  │  ✓ Fristen-Warner                                  │   │
│  │  ✓ Support innerhalb 24 h                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [14 Tage kostenlos testen]      [Später entscheiden]       │
│                                                             │
│  ↳ Oder sofort auf Jahresabo wechseln: 142,56 €/Jahr        │
│    (2 Monate geschenkt)                                     │
└─────────────────────────────────────────────────────────────┘
```

### Gestaltungsregeln
- **Titel**: Benefit-oriented, nicht „Upgrade erforderlich".
- **Kontext**: Warum wird das Modal gezeigt? (z. B. „Sie wollen eine 3. Wohnung anlegen.")
- **Wertliste**: 5–6 konkrete Vorteile, keine generischen Buzzwords.
- **CTA**: „14 Tage kostenlos testen" als Primary, „Später entscheiden" als Tertiary (kein „Abbrechen"-Gefühl).
- **Preis**: Jahrespreis groß, monatliche Alternative klein darunter.
- **Keine Scroll-Wut**: Modal max. 60 % Viewport-Höhe.

### Varianten des Modals
| Auslöser | Modal-Titel | Hauptargument |
|----------|-------------|---------------|
| Wohnungslimit | „Ihr Portfolio wächst" | Mehr Wohnungen verwalten |
| KI-Feature | „Lassen Sie die KI arbeiten" | Zeit sparen, Fehler vermeiden |
| Storage-Limit | „Mehr Platz für Ihre Unterlagen" | Dokumente sicher speichern |
| Support | „Schnellerer Support" | Sicherheit bei Fragen |

### Soft-Upgrade vs. Hard-Upgrade
- **Soft**: Banner/Teaser, die jederzeit weggeklickt werden können.
- **Hard**: Modal nur bei tatsächlicher Blockade (Limit erreicht).
- Verhältnis: 80 % Soft, 20 % Hard.

---

## 7. E-Mail-Sequenzen

### Drip-Campaign für Free-User

#### Tag 0: Willkommen
- Betreff: „Willkommen bei MietVerwaltung – so starten Sie"
- Inhalt: Bestätigung Registrierung, Link zum Dashboard, 3 erste Schritte (Objekt, Mieter, Kosten).
- CTA: „Jetzt erstes Objekt anlegen"

#### Tag 1: Setup-Hilfe
- Betreff: „Haben Sie Ihr erstes Objekt angelegt?"
- Inhalt: 60-Sekunden-Video, Demo-Daten-Button, FAQ.
- CTA: „Demo-Daten laden und ausprobieren"

#### Tag 3: Erster Erfolg
- Betreff: „So erfassen Sie Ihre erste Mietzahlung"
- Inhalt: Schritt-für-Schritt-Anleitung, Screenshot.
- CTA: „Mietzahlung erfassen"

#### Tag 7: KI-Vorschau
- Betreff: „Diese 3 KI-Features sparen Vermietern am meisten Zeit"
- Inhalt: Beleg-Scan, KI-Mahnung, Smart Insights. Kurze Beispiele.
- CTA: „14 Tage Pro kostenlos testen"

#### Tag 14: Limit-Check
- Betreff: „2 Wohnungen sind bequem – wie sieht es bei Ihnen aus?"
- Inhalt: Falls 2 Wohnungen angelegt: „Upgrade auf Basis für 5 Wohnungen". Falls nur 1: „So erweitern Sie Ihr Portfolio".
- CTA: Plan-Upgrade oder Objekt anlegen.

#### Tag 21: Social Proof
- Betreff: „„Endlich keine Excel-Tabellen mehr" — so sagt ein Vermieter aus München"
- Inhalt: Testimonial, kurze Zahlen.
- CTA: „Auch Sie sparen Zeit? Basis testen"

#### Tag 30: Monatsrückblick
- Betreff: „Ihr erster Monat bei MietVerwaltung"
- Inhalt: Persönliche Statistik: „Sie haben X Kosten erfasst, Y Tickets verwaltet."
- CTA: „Mit KI noch mehr automatisieren"

#### Tag 45: Limited Offer
- Betreff: „20 % Rabatt auf Ihr erstes Jahr – noch 5 Tage"
- Inhalt: Jahresabo-Vorteil, Vergleich Monat vs. Jahr.
- CTA: „Jahresabo sichern"

#### Tag 60: Re-Engagement
- Betreff: „Wir vermissen Sie in MietVerwaltung"
- Inhalt: Falls inaktiv: „Hier sind 3 Dinge, die Sie heute erledigen können."
- CTA: „Zurück zum Dashboard"

### Trial-User E-Mail-Sequenz
(siehe Punkt 5)

### Zahlende Kunden E-Mail-Sequenz
- Tag 0: „Danke für Ihr Vertrauen – hier ist Ihr Startpaket"
- Tag 7: „So nutzen Sie Smart Insights" (Pro/Business)
- Tag 30: „Ihr erster Monat – so steht's um Ihr Portfolio"
- Vor Abo-Verlängerung: „Ihr Abo verlängert sich morgen – Danke, dass Sie dabei sind"

---

## 8. Social Proof

### Wo Social Proof einsetzen

#### 1. Landingpage / Pricing
- Logo-Bar bekannter Partner/Kunden (sobald verfügbar).
- Statistik: „X Vermieter verwalten Y Wohnungen mit MietVerwaltung."
- G2/Capterra/Trusted-Badges.
- Trust-Label: „Made in Germany · DSGVO-konform · Hosting in Deutschland".

#### 2. Dashboard (leichter Social Proof)
- Tooltip: „Vermieter wie Sie schließen ihre Abrechnung in durchschnittlich 12 Min ab."
- Banner: „3.456 Vermieter haben diese Woche eine KI-Abrechnung erstellt."

#### 3. Upgrade-Modals
- Einzeiler unter CTA: „Mehr als 60 % unserer zahlenden Kunden nutzen den Pro-Plan."
- Testimonial mit Foto: „„Mit Pro spare ich pro Jahr mindestens 20 Stunden." — Klaus M., Vermieter aus Hamburg"

#### 4. Checkout / Trial-Seite
- Sicherheits-Badges: Stripe, SSL, DSGVO.
- „Keine Kreditkarte nötig · Jederzeit kündbar".
- Bewertungen: „„Super Support, einfache Bedienung." — Google-Bewertung"

### Testimonials sammeln
- Nach erfolgreicher Abrechnung: In-App-Prompt „Wie zufrieden sind Sie?"
- Bei gutem NPS (9–10): Bitte um Google/G2-Review + kurzes Zitat.
- Incentive: 1 Monat Extra-Speicher oder 5 € Gutschrift für verifizierte Bewertung.

### Nutzerzahlen kommunizieren
- Ab 100 Nutzern: „Bereits über 100 Vermieter"
- Ab 1.000: „1.000+ Vermieter vertrauen uns"
- Ab 10.000: „10.000+ Vermieter · 50.000+ verwaltete Wohnungen"
- Immer aktuell halten, niemals erfinden.

---

## 9. Referral-Programm

### Konzept: „Lade einen Vermieter ein – 1 Monat Pro gratis"

#### Für Wen?
- Alle zahlenden Kunden (Basis, Pro, Business) und aktive Trial-User.
- Free-User erhalten 1 Monat Basis gratis, keine Pro-Prämie.

#### Ablauf
1. User öffnet „Einladen" im Dashboard.
2. Generiert persönlichen Link: `mietverwaltung.de/ref/MAX123`.
3. Teilt Link per E-Mail, WhatsApp, Kopieren.
4. Eingeladener registriert sich und bleibt 30 Tage aktiv.
5. Beide erhalten Gutschrift: Einlader +1 Monat auf aktuellem Plan, Neukunde +1 Monat Basis/Pro (je nach Plan des Einladers).

### UI-Mockup
```
┌─────────────────────────────────────────────────────────────┐
│  🎁 Einen Vermieter einladen                                │
│                                                             │
│  Geben Sie 1 Monat Pro weiter – und erhalten Sie selbst    │
│  1 Monat gratis.                                            │
│                                                             │
│  Ihr persönlicher Link:                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  mietverwaltung.de/ref/MAX123                         │  │
│  │                                          [Kopieren]   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Link per E-Mail senden]  [WhatsApp]  [Auf X teilen]      │
│                                                             │
│  Status: 3 Freunde eingeladen · 1 erfolgreich registriert  │
│  Gutschrift: +1 Monat Pro (wird nach Zahlung des Freunds   │
│  freigeschaltet)                                            │
└─────────────────────────────────────────────────────────────┘
```

### Regeln
- Neukunde muss 30 Tage aktiv bleiben und mind. 1 Objekt anlegen → Prämie wird ausgezahlt.
- Max. 12 Monate Prämie pro Jahr kumulierbar.
- Bei Kündigung innerhalb der ersten 30 Tage verfällt die Prämie.
- Transparenz: „Ihr Freund erhält ebenfalls 1 Monat gratis."

### Anti-Gaming
- Ein Gerät / E-Mail / IP nur einmal als Neukunde zählen.
- Selbst-Einladungen werden erkannt und disqualifiziert.

---

## 10. Jahresabo-Vorteil

### Angebot: 2 Monate gratis bei Jahreszahlung

| Plan | Monatlich ×12 | Jährlich | Ersparnis | Effektiver Monatspreis |
|------|---------------|----------|-----------|------------------------|
| Basis | 178,80 € | 142,56 € | 36,24 € (20 %) | 11,88 € |
| Pro | 358,80 € | 287,04 € | 71,76 € (20 %) | 23,92 € |
| Business | 598,80 € | 479,04 € | 119,76 € (20 %) | 39,92 € |

### Kommunikation
- Preis-Seite: Jahrespreis **groß**, Monatspreis klein darunter.
- Badge: „2 Monate geschenkt" oder „20 % Rabatt".
- Toggle-Label: „Jährlich bezahlen & sparen" (Default ON).
- Checkout: „Sie sparen 71,76 €/Jahr gegenüber monatlicher Zahlung".

### Motivation zusätzlich verstärken
- „Nur bei Jahreszahlung: SEPA-Lastschrift verfügbar."
- „Jahreskunden erhalten Priority-Support."
- „Keine Unterbrechung im Januar – Ihre Abrechnungen laufen weiter."

### UX-Patterns
- Default-Bias: Jahreszahlung vorausgewählt.
- Loss Aversion: „Nur noch 5 Tage: 20 % Rabatt auf das erste Jahr".
- Trust: „Jederzeit innerhalb der ersten 30 Tage widerrufbar."

---

## 11. Churn-Prevention

### Ziele
- Kündigungen verhindern, bevor sie passieren.
- Bei Kündigungsabsicht Downgrade/Pause statt kompletten Verlust anbieten.
- Daten erhalten, damit ein Wiedereinstieg leicht ist.

### Churn-Frühwarnsystem
| Signal | Maßnahme |
|--------|----------|
| Login nicht seit 21 Tagen | Re-Engagement-E-Mail + In-App-Banner |
| Support-Ticket mit „Frust"-Sentiment | Persönliche E-Mail vom Support |
| Zahlung fehlgeschlagen | Dunning-Sequenz (siehe unten) |
| Nutzer öffnet Abo-Einstellungen | Retention-Offer-Modal |
| Nutzer klickt „Kündigen" | Exit-Interview + Gegenangebot |

### Dunning-Management (fehlgeschlagene Zahlungen)
- Tag 0: In-App-Banner + E-Mail „Zahlung konnte nicht eingezogen werden"
- Tag 1: Retry automatisch
- Tag 3: E-Mail „Bitte aktualisieren Sie Ihre Zahlungsmethode"
- Tag 7: Letzte E-Mail vor Plan-Downgrade auf Free
- Tag 10: Downgrade auf Free, Daten gesperrt (nicht gelöscht)

### Kündigungs-Workflow
```
User klickt „Abo kündigen"
    ↓
Modal 1: „Was können wir besser machen?"
  → Optionen: Zu teuer / Features fehlen / Nutze es nicht mehr / Andere Lösung
    ↓
Je nach Antwort:
  → „Zu teuer": „20 % Rabatt für 3 Monate" oder Downgrade auf Basis anbieten
  → „Features fehlen": Roadmap zeigen, Beta-Access anbieten
  → „Nutzung gering": Pause-Modus 3 Monate kostenlos
  → „Andere Lösung": Export-Assistent + „Wir würden uns freuen, Sie zurückzugewinnen"
    ↓
Modal 2: „Sind Sie sicher?"
  → Warnung: „Ihre 5 Wohnungen werden auf 2 gesperrt. KI-Features werden deaktiviert."
  → CTA: [Jetzt doch bleiben] [Trotzdem kündigen]
    ↓
Bestätigungs-E-Mail mit Hinweis auf Daten-Erhaltung und Reaktivierungsmöglichkeit
```

### Win-Back-Mails
| Zeitpunkt | Betreff | Inhalt |
|-----------|---------|--------|
| 7 Tage nach Kündigung | „Ihre Daten warten auf Sie" | Daten bleiben 90 Tage, Upgrade jederzeit möglich. |
| 30 Tage nach Kündigung | „Neues Feature: [X]" | Produkt-Update, keine Preisdiskussion. |
| 90 Tage nach Kündigung | „50 % Rabatt auf 3 Monate – zurückkehren?" | Letztes Win-Back-Angebot. |

### Pause statt Kündigung
- „3 Monate Pause" für zahlende Kunden anbieten (keine Kosten, Daten erhalten).
- Nach Pause automatische Rückkehr, sofern nicht vorher gekündigt.

---

## 12. KI-Usage-Limits

### Warum Limits?
- Missbrauch verhindern.
- Kosten kontrollieren (Pay-per-Use bei Ollama Cloud).
- Upsell-Motivation: Wer viel KI nutzt, ist bereit zu zahlen.

### KI-Calls pro Plan

| KI-Funktion | Free | Basis | Pro | Business |
|-------------|------|-------|-----|----------|
| Ticket Auto-Kategorisierung | 0 | 50/Monat | 200/Monat | 1.000/Monat |
| Antwort-Entwürfe Tickets | 0 | 30/Monat | 150/Monat | 750/Monat |
| Beleg-Scan OCR+KI | 0 | 20/Monat | 100/Monat | 500/Monat |
| Smart Insights | 0 | 0 | 30/Monat | 150/Monat |
| KI-Mahnungen | 0 | 0 | 50/Monat | 300/Monat |
| KI-Dokumente (Mieterhöhung etc.) | 0 | 0 | 20/Monat | 100/Monat |
| Mieterbewerbung KI-Extraktion | 0 | 0 | 10/Monat | 50/Monat |

> Hinweis: Keyword-Classifier (lokal, keine KI-API) zählt nicht als KI-Call.

### Anzeige des Verbrauchs

#### Widget im Dashboard
```
┌─────────────────────────────────────────────┐
│  🤖 Ihre KI-Nutzung diesen Monat            │
│                                             │
│  Beleg-Scan      ████████░░  16/20          │
│  Antwort-Entwürfe █████░░░░   15/30         │
│  Smart Insights  —           0/30           │
│                                             │
│  [Upgrade auf Pro für mehr KI-Power]        │
└─────────────────────────────────────────────┘
```

#### Bei 80 % Verbrauch
- Inline-Hinweis: „Sie haben 80 % Ihrer KI-Calls verbraucht. Upgrade auf Pro für unbegrenztere Nutzung."
- Keine harte Sperre, aber deutlicher Hinweis.

#### Bei 100 % Verbrauch
- Banner: „KI-Limit erreicht. Ihre Daten bleiben gespeichert. Upgrade für weitere KI-Calls."
- Falls Basis-Limit erreicht: Upsell auf Pro.
- Falls Pro-Limit erreicht: Add-on „Extra KI-Aufrufe" anbieten (z. B. 0,10 €/Call) oder Upgrade auf Business.

### Fair-Use-Grenze
- Falls ein Vermieter im Basis-Plan plötzlich 500 KI-Calls benötigt, automatischer Hinweis: „Sie nutzen viel KI – der Pro-Plan ist für Sie günstiger."

---

## Zusammenfassung der wichtigsten Maßnahmen

| # | Maßnahme | Erwartete Wirkung |
|---|----------|-------------------|
| 1 | Pro als „Most Popular" mit Business-Anker | ↑ Conversion auf Pro |
| 2 | Free mit 2 WE + sichtbaren Premium-Features | ↑ Upgrade-Drang |
| 3 | Kontextuelle Trigger bei Grenzen | ↑ Trial-Starts |
| 4 | Sichtbares Feature-Gating statt Verstecken | ↑ Upgrade-Intention |
| 5 | 14-Tage-Pro-Trial für alle + Loss-Aversion-Reminder | ↑ Trial→Paid |
| 6 | Upgrade-Modal mit Wertliste + Sofort-Trial | ↑ Conversion |
| 7 | Drip-E-Mail-Folge für Free-User | ↑ Aktivierung & Conversion |
| 8 | Social Proof + Testimonials in Upgrade-Flow | ↑ Vertrauen |
| 9 | Referral-Programm „1 Monat gratis" | ↓ CAC, ↑ Wachstum |
| 10 | Jahresabo als Default mit 2 Monate geschenkt | ↑ Retention & Cashflow |
| 11 | Exit-Interview + Pause/Downgrade + Win-Back | ↓ Churn |
| 12 | Transparente KI-Usage-Limits + Verbrauchs-Widget | ↑ Upsell, ↓ Missbrauch |

---

## Nächste Schritte

1. Mockup der Pricing-Page in `/root/mietverwaltung/mockup/pricing.html` erstellen.
2. Trigger-Logik im Backend als Entitlement-Service implementieren.
3. E-Mail-Templates in Postfix/Template-Engine definieren.
4. PostHog-Events für jeden Trigger und jeden Conversion-Schritt tracken.
5. A/B-Test: Jahresabo-Default vs. Monatsabo-Default.
6. A/B-Test: Pro-Trial für alle vs. selbstgewählter Plan-Trial.
