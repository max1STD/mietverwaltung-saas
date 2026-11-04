# Markt- und Preisanalyse v2 — MietVerwaltung SaaS DACH

**Projekt:** MietVerwaltung SaaS für private Kleinvermieter in Deutschland, Österreich und Schweiz  
**USP:** „KI-gestützte Mietverwaltung, die 80 % der Vermieter-Arbeit automatisch erledigt — DSGVO-konform, made in DACH."  
**Dokumentstatus:** v2, November 2026  
**Basis:** Bestehende interne Analysen + aktuelle Web-Recherche (Q3/Q4 2026)

---

## Zusammenfassung auf einen Blick

| Kennzahl | Wert |
|---|---|
| Private Vermieter DACH | **~6,35 Mio.** |
| Privat vermietete Wohnungen DACH | **~18,0 Mio.** |
| Marktvolumen (TAM) bei Ø 15 €/Monat | **~1,14 Mrd. €/Jahr** |
| Serviceable Addressable Market (SAM) | **~2,36 Mio. Kunden / ~425–566 Mio. €/Jahr** |
| Realistisches SOM Jahr 3 | **~30.000 Kunden / ~5,4–7,2 Mio. € ARR** |
| Unsere Preise (empfohlen) | **9,75 €/WE (1–5) · 7,50 €/WE (6–25) · 5,90 €/WE (26–100) · Custom ab 100 WE** |
| Wettbewerbs-Preisniveau (5 WE) | **Ø ~15,5 €/Monat** |
| Wettbewerbs-Preisniveau (25 WE) | **Ø ~30 €/Monat** |
| Break-even | **~2 zahlende Kunden** (Pro-WE-Ø) |
| LTV : CAC (Pro-WE, 5 % Churn) | **5,2 : 1** |

---

## 1. Total Addressable Market (TAM)

### 1.1 Anzahl privater Kleinvermieter in DACH

| Land | Private Vermieter (Haushalte) | Privat vermietete Wohnungen | Anteil am Mietbestand | Quelle |
|---|---|---|---|---|
| Deutschland | **~5,5 Mio.** | **~16,1 Mio.** | 64,4 % | IW Köln / Bundestagsdrucksache 21/8091, Zensus 2022 [1][2][3] |
| Österreich | **~470.000** | **~810.000** | ~45 % | Statistik Austria Mikrozensus Wohnen 2024/2025 [4][5] |
| Schweiz | **~380.000** | **~1,125 Mio.** | ~45 % | BFS / JLL Wohnmarkt Schweiz 2025 [6][7] |
| **DACH gesamt** | **~6,35 Mio.** | **~18,0 Mio.** | — | Eigene Hochrechnung |

**Definition:** Private Kleinvermieter sind natürliche Personen oder kleine WEG-Gemeinschaften, die selbst vermieten — im Gegensatz zu gewerblichen Wohnungsunternehmen, Genossenschaften, professionellen Hausverwaltungen oder REITs.

### 1.2 Verteilung der Wohnungsanzahl in Deutschland

Laut Vermieterreport 2026 (IW/Deutschland.Immobilien, n > 1.000) ist der Markt extrem kleinteilig [2][8]:

| Wohnungen pro Vermieter | Anteil | Kumuliert |
|---|---|---|
| 1 Wohnung | 58 % | 58 % |
| 2 Wohnungen | 19 % | 77 % |
| 3–5 Wohnungen | 16 % | 93 % |
| 6–10 Wohnungen | 4 % | 97 % |
| 11–50 Wohnungen | 2 % | 99 % |
| > 50 Wohnungen | 1 % | 100 % |

**Fazit:** 93 % aller privaten Vermieter besitzen 1–5 Wohnungen. Das ist ein Massenmarkt im niedrigen Preissegment, aber mit hohen Stückzahlen.

### 1.3 Marktvolumen (TAM) in Euro

| Szenario | Annahme | Jährliches Marktvolumen DACH |
|---|---|---|
| Konservativ | 6,35 Mio. Vermieter × 120 €/Jahr | **~762 Mio. €** |
| Realistisch (Basis) | 6,35 Mio. Vermieter × 180 €/Jahr (15 €/Mo) | **~1,14 Mrd. €** |
| Optimistisch | 6,35 Mio. Vermieter × 240 €/Jahr | **~1,52 Mrd. €** |

Vergleich mit Branchenstudien:

- **Deutschland Property-Management-Software-Markt 2025:** ca. **210 Mio. €** (USD 225,2 Mio., Wechselkurs ~0,93) bei CAGR 7,6 % bis 2033 [9].
- **Europa Property-Management-Software-Markt 2025:** ca. **0,95 Mrd. €** (USD 1,02 Mrd.) bei CAGR 6,87 % [10].
- **Globaler Markt 2025:** Studien reichen von USD 3,6 Mrd. (Grand View) bis USD 6,5 Mrd. (Mordor) [11][12].

Die Bottom-Up-Schätzung (1,14 Mrd. €) liegt deutlich über dem deutschen Software-Markt allein, weil sie neben reinem SaaS-Abo auch Add-ons (Bank-API, eID, Handwerker-Vermittlung, Steuer-Export) und AT/CH einschließt. Sie ist realistisch für den gesamten adressierbaren Bedarf privater Vermieter.

---

## 2. Serviceable Addressable Market (SAM)

### 2.1 Abgrenzung: Was gehört rein, was nicht?

| Segment | Einordnung | In SAM? |
|---|---|---|
| Private Kleinvermieter mit 1–25 WE | Kernzielgruppe | ✅ |
| Private Vermieter mit 26–50 WE | Semi-professionell | ✅ (teilweise, über Pro/Business) |
| Gewerbliche Vermieter / Wohnungsunternehmen / REITs | Professionelle Portfolios | ❌ Ausgeschlossen |
| Professionelle Hausverwaltungen | B2B-ERP-Segment | ❌ Ausgeschlossen (außer Business-Piloten) |
| WEG-Selbstverwaltungen | Eigentümergemeinschaften, Hausgeld | ❌ Ausgeschlossen (Fokus Mietverwaltung) |
| Vermieter ohne Internet-Affinität / rein analog | Nicht erreichbar per SaaS | ❌ Ausgeschlossen |

### 2.2 Größe des SAM

| Filter | Kunden | Begründung |
|---|---|---|
| Private Vermieter DACH | 6,35 Mio. | TAM |
| Davon 1–25 WE | ~5,9 Mio. | 93 % der privaten Vermieter |
| Davon online-affin & digitalisierungsbereit (40 %) | **~2,36 Mio.** | Konservative Adoptionsannahme |

| ARPU-Annahme | SAM/Jahr |
|---|---|
| 15 €/Monat (180 €/Jahr) | **~425 Mio. €** |
| 20 €/Monat (240 €/Jahr, Pro-Mix) | **~566 Mio. €** |

**Empfohlene Planungsgröße:** **SAM ≈ 2,36 Mio. potenzielle Kunden, ≈ 450–570 Mio. €/Jahr**. Für die folgenden SOM-Rechnungen nutzen wir **2,5 Mio. Kunden / 450 Mio. €/Jahr** (konservativer Endwert), um Planungssicherheit zu wahren.

### 2.3 Warum nur 40 % Online-Affinität?

- Laut Haus & Grund Vermieterbefragung 2026 nutzen zwar viele Vermieter digitale Tools, aber nur ein Teil zahlt aktiv für Software [13].
- Ältere Kleinvermieter (Altersvorsorge-Eigentümer) bleiben bei Excel/Papier.
- Der Software-Adoptionsgrad bei Privatvermietern liegt geschätzt bei 20–30 %. Mit wachsender Digitalisierung (KI-Hype, Steuer-Digitalisierung) steigt er auf 40 %.

---

## 3. Serviceable Obtainable Market (SOM)

### 3.1 Realistisch erreichbare Kunden und ARR

| Zeitraum | Kunden | Penetration SAM | Penetration TAM | ARPU Ø | ARR |
|---|---|---|---|---|---|
| **Jahr 1** | **2.500** | 0,10 % | 0,04 % | 15–20 €/Mo | **0,45–0,60 Mio. €** |
| **Jahr 3** | **30.000** | 1,20 % | 0,47 % | 15–20 €/Mo | **5,4–7,2 Mio. €** |
| **Jahr 5** | **75.000** | 3,00 % | 1,18 % | 15–20 €/Mo | **13,5–18,0 Mio. €** |

### 3.2 Vergleich mit Go-to-Market-Zielen

Die interne Go-to-Market-Strategie plant:

- Monat 1–6: 0 → 100 zahlende Kunden
- Monat 6–18: 100 → 1.000 Kunden
- Jahr 2–3: 1.000 → 10.000 Kunden

Das ist konservativer als das obige SOM-Szenario. **Empfehlung:** Das SOM von 30.000 Kunden in Jahr 3 ist ambitioniert, aber machbar, wenn SEO, Empfehlungsmarketing und gezielte Google Ads ab Monat 6 laufen. Jahr 1 sollte realistisch bei 1.000–2.500 Kunden liegen.

### 3.3 Break-even und Skalierung

| Kennzahl | Wert | Quelle/Begründung |
|---|---|---|
| Fixkosten/Monat (MVP) | ~24 € | Hosting, E-Mail, Basis-Tools |
| Gewichteter Deckungsbeitrag | ~23 €/Mo | Abo-Modell v3 [14] |
| Break-even-Kunden | **1 Kunde** | Gewichteter Mix |
| Break-even bei reinem Basis-Kunden | **2 Kunden** | 13,53 € Deckungsbeitrat |

---

## 4. Kleinster machbarer Markt (Beachhead Market)

### 4.1 Definition

**Beachhead Market:** Private Kleinvermieter in **Hamburg und Niedersachsen** mit **2–10 Wohnungen**, die selbst verwalten und bereits digitale Kanäle (Online-Banking, E-Mail, WhatsApp) nutzen.

### 4.2 Warum Hamburg / Niedersachsen?

| Kriterium | Bewertung |
|---|---|
| **Beta-Tester-Pool** | Lokales Netzwerk, persönliche Einladung, schnelles Feedback |
| **Digitale Affinität** | Hamburg ist überdurchschnittlich digitalisiert; Niedersachsen repräsentativ für breite Mittelschicht |
| **Gebäude-Mix** | Altbau + Neubau, Einfamilienhäuser mit Einliegerwohnung, kleine Mehrfamilienhäuser |
| **Verbands-Präsenz** | Haus & Grund Hamburg, Haus & Grund Niedersachsen, IVVD-Regionalgruppen |
| **Marketing-Reichweite** | Lokal bezahlbar bei Google Ads; regionale Immobilien-Portale, Makler-Netzwerke |
| **Rechtliche Homogenität** | Innerhalb Deutschlands gleiches Mietrecht; späterer AT/CH-Rollout separat |

### 4.3 Größe des Beachhead-Marktes

Hamburg hat ca. 1,9 Mio. Wohnungen, Niedersachsen ca. 4,0 Mio. Wohnungen. Bei 60–65 % Mietanteil und hohem Privatanteil (ähnlich DE-Durchschnitt) ergeben sich vereinfacht:

| Region | Geschätzte private Vermieterhaushalte | Geschätzte privat vermietete Wohnungen |
|---|---|---|
| Hamburg | ~180.000 | ~520.000 |
| Niedersachsen | ~380.000 | ~1.100.000 |
| **Beachhead gesamt** | **~560.000** | **~1.620.000** |

Innerhalb des Beachheads zielen wir auf das Segment **2–10 WE** ab (~20 % aller privaten Vermieter ≈ **112.000 potenzielle Beachhead-Kunden**). Das ist groß genug für Skalierung, aber klein genug für fokussierte Akquise.

---

## 5. Konkurrenz-Analyse (aktualisiert)

### 5.1 Wettbewerber-Übersicht

| Anbieter | Zielsegment | Preis (5 WE/Monat) | Preis (25 WE/Monat) | KI-Stärke | Besonderheit |
|---|---|---|---|---|---|
| **immocloud** | 1–50 WE, Privat+Gewerblich | 9,99 € netto (~11,89 € brutto) | 25,99 € netto (~30,93 € brutto) | ⚪ nur Beleg-OCR | Testsieger, starke UX, native App |
| **rentably** | 1–30+ WE, Privat | 0 € (Basic) / 9,00 € netto (~10,71 €) Pro | 0 € (Basic) / 9,00 € netto (~10,71 €) Pro Flatrate | 🟡 extern via MCP | Dauerhaft kostenloser Basic, sehr günstig |
| **hellohousing** | 1–50 WE, Privat | ab 4,50 € (Starter) / 9,50 € (Premium) | ab 19,50 € (Professional) | 🟡 KI-OCR + Assistent | Einziger Funkzähler/UVI-Anbieter |
| **objego (ista)** | 1–70 WE, Privat | 0 € (Basics) / 7,95 € + 0,95 €/WE = 12,70 € | 7,95 € + 0,95 €/WE = 31,70 € | 🔴 kaum KI | Modular, kostenloser Einstieg, Heizkosten-Fokus |
| **verwaltio** | 10–50+ WE, Investor+Verwaltungen | 24,90 € + 1,30 €/WE = 31,90 € netto (~37,96 € brutto) | 24,90 € + 1,30 €/WE = 57,40 € netto (~68,31 € brutto) | 🟢 KI-Assistent | Transparente Pro-Einheit-Preise, Open Banking |
| **Immoware24** | 10–1.000+ WE, ERP | ab ~350 €/Monat | ab 500–900 €/Monat | 🟢 KI-Chatbot, OCR | Profi-ERP, WEG, DATEV |
| **VermietenPlus (ImmoScout24)** | 1–30 WE, IS24-Nutzer | 9,90 € + 0,99 €/WE = 13,86 € | 9,90 € + 0,99 €/WE = 33,66 € | 🔴 keine echte KI | IS24-Ökosystem, Reichweite |
| **WISO Vermieter / Lexware** | 1–10 WE, Privat | ca. 5–15 €/Monat bzw. Jahreslizenz | ca. 10–25 €/Monat | 🔴 Desktop-/Steuer-Fokus | Bekannt, aber nicht cloud-nativ |
| **aedium** | WEG, Hausverwaltungen, Pilotphase | Auf Anfrage | Auf Anfrage | 🟢🟢 30 KI-Agenten | Stärkster zukünftiger KI-Konkurrent |
| **MietVerwaltung Basis** | 1–5 WE | **14,90 €** | — | 🟢 voll integriert | KI-Beleg, Tickets, DSGVO-KI |
| **MietVerwaltung Pro** | 6–25 WE | **29,90 €** (für bis 25 WE) | **29,90 €** | 🟢🟢 volle KI | Smart Insights, Mahnungen, Mieterhöhung, eID |
| **MietVerwaltung Business** | 25+ WE | **49,90 €** | **49,90 €** | 🟢🟢 volle KI + Team | API, Custom Reports |

> Alle Wettbewerberpreise ohne MwSt. wurden mit 19 % MwSt. hochgerechnet, um Vergleichbarkeit zu gewährleisten. Preise in Klammern sind Nettopreise der Anbieter.

### 5.2 Detaillierte Stärken und Schwächen

**immocloud**  
- ✅ Stärken: Testsieger, intuitive UX, DATEV, native App, transparente Staffelpreise.  
- ❌ Schwächen: KI nur Beleg-OCR, kein echtes Ticketsystem, kein ROI-Dashboard, kein Free-Tier.

**rentably**  
- ✅ Stärken: Dauerhaft kostenloser Basic, günstige Pro-Flatrate, moderne UX.  
- ❌ Schwächen: KI nur extern (MCP), keine eingebaute Automatisierung, keine DSGVO-KI-Dokumentation, kaum Bewertungen.

**hellohousing**  
- ✅ Stärken: Günstiger Einstieg, Funkzähler/UVI, gute Bewertungen.  
- ❌ Schwächen: Kein Mahnwesen, kein DATEV, Mieterportal erst teuer, kein echtes Ticketsystem.

**objego**  
- ✅ Stärken: Ehrlich kostenlos, ista-Backung, günstige Nebenkosten-Abrechnung.  
- ❌ Schwächen: Keine echte KI, kein Mieterportal, lineare Kosten, schlechte Skalierung.

**verwaltio**  
- ✅ Stärken: Open Banking, KI-Assistent, transparente Preise, MCP/API.  
- ❌ Schwächen: Hoher Einstieg (24,90 €), Fokus Mittelstand, Datenschutz-Risiko durch MCP mit echten Daten.

**Immoware24**  
- ✅ Stärken: Voll-ERP, WEG, 4.500+ Kunden, professionelle Buchhaltung.  
- ❌ Schwächen: Ab 350 €/Monat, lange Bindung, komplex, für Kleinvermieter überdimensioniert.

**VermietenPlus**  
- ✅ Stärken: IS24-Reichweite, günstiges Add-on, kostenlose Inserate.  
- ❌ Schwächen: Trustpilot 1,4/5, Bugs in NK-Abrechnung, keine echte Verwaltungs-Automation.

**aedium**  
- ✅ Stärken: Stärkste KI-Story, 30 Agenten, kompletter Lebenszyklus.  
- ❌ Schwächen: Noch in geschlossener Pilotphase bis Frühjahr 2027, keine öffentlichen Preise, keine Bewertungen.

### 5.3 Preis-Landschaft

| Segment | Preisspanne/Monat | Beispiele |
|---|---|---|
| Kostenlos / Freemium | 0 € | rentably Basic, objego Basics |
| Einstiegs-Tools (1–5 WE) | 4,50–15 € | hellohousing Starter, immocloud Starter, objego, VermietenPlus |
| Mittelklasse (6–30 WE) | 15–35 € | immocloud Manager, hellohousing Premium, objego, VermietenPlus |
| Profi-Mittelstand (30–100 WE) | 35–100 € | verwaltio, hausify, Immoware24 Klein |
| ERP / Enterprise | 350 €+ | Immoware24, Domus, aedium Enterprise |

- **Durchschnittspreis bei 5 WE:** ~**15,5 €/Monat** (brutto, gewichtet).
- **Durchschnittspreis bei 25 WE:** ~**30 €/Monat** (brutto, gewichtet).
- **Oberes Ende:** ERP-Lösungen ab 350 €/Monat.

### 5.4 Wo stehen wir im Vergleich?

| Plan | Preis | Marktpositionierung |
|---|---|---|
| **Basis 14,90 €** | Leicht unter dem 5-WE-Durchschnitt (~15,5 €) | Guter Einstieg mit KI-Mehrwert; nicht „zu günstig" |
| **Pro 29,90 €** | Exakt am 25-WE-Durchschnitt (~30 €) | Mid-Market-Sweet-Spot mit voller KI |
| **Business 49,90 €** | Deutlich unter Pro-Einheit-Preisen der Konkurrenz | Günstig für 25–50 WE, aber **zu günstig für unbegrenzte Portfolios** |

### 5.5 Bewertung: Sind wir „viel zu günstig"?

**Fazit:** Die v3-Preise **14,90 / 29,90 / 49,90 €** sind gegenüber der alten v2 (9,90 / 19,90 / 39,90 €) bereits um **+50 % angehoben**. Sie sind **im Einstiegs- und Mittelsegment marktgerecht**, aber im Enterprise-Segment weiterhin unter dem Wettbewerb.

| Bereich | Einschätzung | Handlungsempfehlung |
|---|---|---|
| Basis 14,90 € | Richtig positioniert, leicht unter Durchschnitt | **Nicht weiter erhöhen** vor Launch; würde Akquisition gegen rentably/objego/immocloud bremsen |
| Pro 29,90 € | Im Markt-Mittelfeld, fair für 25 WE | **Beibehalten**, „Beliebtester Plan"-Badge nutzen |
| Business 49,90 € | Zu günstig für unbegrenzte Portfolios | **Erhöhen auf 79,90 €** oder **Grenze bei 50 WE** einführen |
| Overage / Add-ons | Fehlt fast vollständig | **1 €/WE/Monat** ab der 6. bzw. 26. Wohnung einführen |

---

## 6. Preis-Analyse und Empfehlung

### 6.1 Unsere aktuellen Preise im Vergleich

| Vergleich | MietVerwaltung | Konkurrent | Unsere Position |
|---|---|---|---|
| 5 WE / Basis | 14,90 € | immocloud 11,89 €, rentably 10,71 €, objego 12,70 €, VermietenPlus 13,86 € | Im Mittelfeld, aber mit KI |
| 5 WE / Pro | 29,90 € | hellohousing 19,50 €, verwaltio 37,96 € | Premium, aber für bis 25 WE gedacht |
| 25 WE / Pro | 29,90 € | immocloud 30,93 €, objego 31,70 €, VermietenPlus 33,66 €, verwaltio 68,31 € | **Sehr konkurrenzfähig** |
| 50+ WE / Business | 49,90 € | verwaltio ~94 €, Immoware24 ab 350 € | **Deutlich zu günstig** |

### 6.2 Durchschnittspreise und Premium-Spielraum

| Segment | Ø Marktpreis/Monat | MietVerwaltung | Premium-Spielraum |
|---|---|---|---|
| 1–5 WE | ~15,5 € | 14,90 € (Basis) | Max. +2–3 €, sonst Conversion sinkt |
| 6–25 WE | ~30 € | 29,90 € (Pro) | Max. +5 € (34,90 € testbar) |
| 26–50 WE | ~45–75 € | 49,90 € (Business) | **+30 € möglich** (79,90 €) |
| 50+ WE | 100–350+ € | 49,90 € (Business) | **+200–300 € nötig** → Custom Pricing |

### 6.3 Empfohlene Preisanpassung

| Maßnahme | Aktuell | Empfohlen | Delta | Begründung |
|---|---|---|---|---|
| Basis | 14,90 € | **14,90 €** | 0 % | Akquisitionshebel, nicht weiter erhöhen |
| Pro | 29,90 € | **29,90 €** (ggf. 34,90 € nach PMF) | 0 % | Markt-Sweet-Spot, profitabelster Plan |
| Business | 49,90 € | **79,90 €** für 25–100 WE | +60 % | Unbegrenzt zu günstig, gedeckt durch Konkurrenz |
| Enterprise | — | **Custom Pricing ab 100 WE** | — | Große Portfolios brauchen SLA, Onboarding, dedizierte Ressourcen |
| Overage | — | **1 €/WE/Monat** ab Plan-Limit | — | Erhöht ARPU ohne Headline-Preiserhöhung |
| Jährlicher Rabatt | 20 % | **20 % beibehalten** | — | Senkt Churn, verbessert Cashflow [14] |

**Gesamteffekt:** Durch Business-Preiserhöhung und Overage steigt das geschätzte ARPU im Kunden-Mix um **+25–40 %**, ohne die Akquisition im unteren Segment zu bremsen.

### 6.4 Preis-Elastizität der Vermieter

Die Nachfrage nach Vermieter-Software ist im DACH-Markt **preisinelastisch** für die Zielgruppen Pro und Business, aber **preiselastisch im Basis-Segment**:

- **Basis-Segment (1–2 WE):** Vermieter vergleichen 10–15 €/Monat mit „kostenlosem" objego/rentably. Hier zählt jeder Euro.
- **Pro-Segment (6–25 WE):** Vermieter sparen mit KI >500 €/Jahr pro Wohnung. Preisschwankungen von ±5 € haben geringen Einfluss.
- **Business-Segment (25+ WE):** Preis ist sekundär gegenüber Zuverlässigkeit, Support-SLA und Skalierung.

**Empfehlung:** Value-Based Pricing kommunizieren — nicht „15 €/Monat", sondern „sparen Sie 645 €/Jahr pro Wohnung".

### 6.5 Value-Based Pricing

| Wert für den Kunden | Euro/Jahr/Wohnung | Unsere Kosten |
|---|---|---|
| Zeitersparnis durch KI (12,9 h/WE/Jahr × 50 €/h) | ~645 € | 14,90–29,90 €/Monat |
| Vermeidung teurer Fehler (NK-Abrechnung, Mahnungen) | 200–1.000 €/Jahr | 14,90–29,90 €/Monat |
| Entfallende Hausverwaltung (15–25 €/WE/Jahr) | 375–625 €/Jahr | 14,90–29,90 €/Monat |

Selbst der teuerste Pro-Plan (29,90 €/Monat für 25 WE = 14,35 €/WE/Jahr) liegt weit unter dem Wert, den der Kunde realisiert. Das rechtfertigt die Preise und erlaubt sogar eine weitere Erhöhung im Business-Segment.

> **Wichtiger Nachtrag:** Die aktuellen Festpreise sind für eine Premium-KI-Lösung zu niedrig. Eine gründliche Analyse des **Pro-WE-Preismodells** (Kapitel 6.5) und der **technischen Abo-Verknüpfung** (Kapitel 6.6) folgt unten.

---

## 6.5 Pro-WE-Preismodell — Ausführliche Analyse

> **Auslöser dieser Analyse:** Die aktuellen Festpreis-Tarife (14,90 / 29,90 / 49,90 €) decken den KI-Mehrwert und die Wettbewerbsposition nicht ausreichend ab. Die Frage ist: Sollten wir statt fester Pläne auf eine **Preis pro Wohneinheit (WE)** umstellen?

---

### 6.5.1 Grundmodell Pro-WE

Beim Pro-WE-Modell zahlt der Kunde nicht eine pauschale Plan-Gebühr, sondern einen **Preis pro verwalteter Wohnung pro Monat**. Die Rechnung ist damit direkt an Portfolio-Größe gekoppelt:

| WE | bei 9,75 €/WE | bei 7,50 €/WE | bei 5,90 €/WE |
|---|---|---|---|
| 1 | 9,75 € | — | — |
| 3 | 29,25 € | — | — |
| 5 | 48,75 € | — | — |
| 10 | — | 75,00 € | — |
| 25 | — | 187,50 € | — |
| 50 | — | — | 295,00 € |
| 100 | — | — | 590,00 € |

> Staffelpreise werden **graduiert** (nicht Block-Staffel) abgerechnet: Die ersten 5 WE kosten 9,75 €/WE, die WE 6–25 kosten 7,50 €/WE, die WE 26–100 kosten 5,90 €/WE.

**Beispielrechnung 10 WE:**  
5 × 9,75 € = 48,75 €  
+ 5 × 7,50 € = 37,50 €  
**= 86,25 €/Monat**

**Beispielrechnung 50 WE:**  
5 × 9,75 € = 48,75 €  
+ 20 × 7,50 € = 150,00 €  
+ 25 × 5,90 € = 147,50 €  
**= 346,25 €/Monat**

### 6.5.2 Vergleich: Feste Pläne vs. Pro-WE

#### A) Vergleich mit aktuellen v3-Festpreisen (14,90 / 29,90 / 49,90 €)

| WE | Aktuell Basis/Pro/Business v3 | Pro-WE (9,75/7,50/5,90) | Verhältnis |
|---|---|---|---|
| 1 | 14,90 € (Basis) | 9,75 € | Pro-WE 35 % günstiger |
| 2 | 14,90 € (Basis) | 19,50 € | Pro-WE 31 % teurer |
| 3 | 14,90 € (Basis) | 29,25 € | Pro-WE 96 % teurer |
| 5 | 14,90 € (Basis) | 48,75 € | Pro-WE 3,3× teurer |
| 10 | 29,90 € (Pro) | 86,25 € | Pro-WE 2,9× teurer |
| 25 | 29,90 € (Pro) | 198,75 € | Pro-WE 6,6× teurer |
| 50 | 49,90 € (Business) | 346,25 € | Pro-WE 6,9× teurer |

**Fazit:** Gegenüber den aktuell viel zu günstigen Festpreisen ist Pro-WE bei fast allen Mehr-WE-Portfolios deutlich teurer — das ist beabsichtigt, weil v3 unter dem Markt liegt.

#### B) Vergleich mit höheren Festpreisen (24,90 / 49,90 / 99,90 €)

| WE | Festpreis-Premium | Pro-WE | Verhältnis |
|---|---|---|---|
| 1 | 24,90 € (Basis) | 9,75 € | Pro-WE 61 % günstiger |
| 2 | 24,90 € (Basis) | 19,50 € | Pro-WE 22 % günstiger |
| 3 | 24,90 € (Basis) | 29,25 € | Pro-WE 17 % teurer |
| 5 | 49,90 € (Pro) | 48,75 € | Pro-WE 2 % günstiger |
| 6 | 49,90 € (Pro) | 45,00 € | Pro-WE 10 % günstiger |
| 10 | 49,90 € (Pro) | 86,25 € | Pro-WE 73 % teurer |
| 25 | 99,90 € (Business) | 198,75 € | Pro-WE 99 % teurer |
| 50 | 99,90 € (Business) | 346,25 € | Pro-WE 3,5× teurer |

**Fazit:** Pro-WE ist für **1–2-WE-Vermieter attraktiver** als jeder Festpreis, für **5–6 WE annähernd gleich**, ab **10 WE deutlich teurer**. Wer größere Portfolios haben will, zahlt bei Pro-WE entsprechend mehr.

### 6.5.3 Konkurrenz: Wer rechnet pro WE?

| Anbieter | Preismodell | Pro-WE-Preis (brutto) |
|---|---|---|
| **immocloud** | Staffelpauschalen (bis 5/15/30/50 WE) | Entspricht ~2,00–2,40 €/WE bei 5 WE, sinkt mit mehr WE |
| **rentably** | Flatrate (ab 9 € unbegrenzt) | Effektiv ~0,90 €/WE bei 10 WE |
| **hellohousing** | Pro Immobilie (1/2/5 Objekte) | Entspricht ~0,40–1,90 €/WE |
| **objego** | Modul: 7,95 € Pauschale + 0,95 €/WE Nebenkosten | ~2,54 €/WE bei 5 WE |
| **verwaltio** | 24,90 € Grundpreis + 1,30 €/WE | ~6,38 €/WE bei 5 WE, sinkt auf ~2,30 €/WE bei 50 WE |
| **VermietenPlus** | 9,90 € Grundpreis + 0,99 €/WE | ~2,77 €/WE bei 5 WE |
| **Immoware24** | ERP, individuell | ~7–12 €/WE bei kleinen Portfolios |
| **ImmoApp** | **Reines Pro-WE-Modell** | **5,00 € netto/WE (1–49), 3,00 € netto/WE (50–99)** |
| **hausify** | Feste Pläne (0/19/49/79 €) | Effektiv ~0–7,90 €/WE |

**Erkenntnis:** Reines Pro-WE ist im DACH-Raum eher selten (ImmoApp, verwaltio teilweise). Die meisten Anbieter nutzen **Pauschal-Tarife oder Grundpreis + Pro-WE-Add-on**. US-Plattformen (Yardi Breeze, AppFolio, Rentvine) arbeiten dagegen klassisch mit 1–3 $/unit/month [19][20].

### 6.5.4 Kombinations-Modelle im Vergleich

| Modell | Vorteil | Nachteil | Bewertung |
|---|---|---|---|
| **Reine Festpreise** | Einfach, Plan-Badge, Decoy-Effekt | Kunden mit 1 WE subventionieren Kunden mit 25 WE; ungerecht | ❌ Keine faire Skalierung |
| **Reines Pro-WE** | Transparent, fair, skaliert natürlich, kein Upgrade-Druck | Kein „Beliebtester Plan"-Badge, Sticker-Schock bei vielen WE | ✅ Premium + fair |
| **Festpreis + Overage** | Plan-Psychologie bleibt, aber Skalierung fair | Komplexer, mehr Edge Cases | ⚠️ Pragmatisch, aber weniger klar |
| **Pro-WE mit Plan-Bändern** | Pro-WE-Logik + Plan-Badge (z. B. „1–5 WE", „6–25 WE") | Innerhalb eines Bands variiert der Preis — muss erklärt werden | ✅ **Empfohlen** |

### 6.5.5 BWL-Analyse: Pro-WE vs. Festpreise

#### Annahmen

| Parameter | Pro-WE-Modell | Festpreis-Premium (24,90/49,90/99,90) |
|---|---|---|
| Ø ARPU (1–25 WE-Segment) | **~22 €/Mo** | **~49 €/Mo** (bei 35/50/15 Mix) |
| Variable Kosten/Kunde | ~2,50 €/Mo | ~2,50 €/Mo |
| Deckungsbeitrag | ~19,50 €/Mo | ~46,50 €/Mo |
| Monatliche Churn | 5 % | 5 % |
| Customer Lifetime | 20 Monate | 20 Monate |
| **CLV** | **~390 €** | **~930 €** |
| CAC | 75 € | 75 € |
| **LTV:CAC** | **5,2 : 1** | **12,4 : 1** |
| Break-even-Kunden | **~2 Kunden** | **~1 Kunde** |

> ARPU Pro-WE: Gewichtet über die deutsche Verteilung (58 % × 1 WE, 19 % × 2 WE, 16 % × 4 WE, 4 % × 8 WE, 2 % × 25 WE) mit den Staffelpreisen 9,75 / 7,50 / 5,90 €.

#### Was bringt mehr MRR?

Bei **gleicher Conversion** bringen die höheren Festpreise deutlich mehr MRR pro Kunde. Aber die Conversion ist kritisch:

- **Festpreis-Premium 24,90 € für 1 WE:** 58 % des Marktes hat nur 1 WE. Ein Einstieg bei 24,90 € ist gegenüber immocloud (11,89 €) und objego (0 €) sehr hart.
- **Pro-WE 9,75 € für 1 WE:** Konkurrenzfähiger Einstieg, aber ab 3–5 WE deutlich teurer als die meisten Wettbewerber.

**Szenario-Rechnung:**

| Modell | 1.000 Kunden | MRR | ARR |
|---|---|---|---|
| Pro-WE (Ø ARPU 22 €) | 1.000 | 22.000 € | 264.000 € |
| Festpreis-Premium (Ø ARPU 49 €) | 500 (50 % Conversion) | 24.500 € | 294.000 € |
| Festpreis-Premium (Ø ARPU 49 €) | 1.000 (gleiche Conversion) | 49.000 € | 588.000 € |

**Interpretation:** Wenn die höheren Festpreise die Conversion **nicht halbieren**, sind sie lukrativer. Wenn die Conversion um mehr als 50 % sinkt, gewinnt Pro-WE.

### 6.5.6 Preispsychologie bei Pro-WE

| Psychologischer Hebel | Umsetzung bei Pro-WE | Effekt |
|---|---|---|
| **Anchor „Ab 9,75 € pro Wohnung"** | Niedriger Einstiegs-Anchor, aber totaler Betrag steigt | Erhöht Trial-Entry, reduziert Absprungrate |
| **Fairness / „Nur was du nutzt"** | Keine Subventionierung großer Portfolios durch Kleine | Vertrauen, höhere Zufriedenheit |
| **Volumenrabatt sichtbar** | 9,75 → 7,50 → 5,90 €/WE | Anreiz zum Wachstum ohne Wechselangst |
| **Loss Aversion** | Kunde sieht: „Bei 10 WE spare ich mit 7,50 €/WE gegenüber 9,75 €/WE" | Bindung an Plattform |
| **Status-Quo-Bias** | Automatische Rechnung anhand aktueller WE | Weniger Kündigungsimpulse |
| **Charm Pricing** | 9,75 € statt 10,00 € | Unter psychologischer 10-€-Schwelle |

**Kommunikations-Empfehlung:**
- Headline: **„Ab 9,75 € pro Wohnung im Monat"**
- Subline: **„Je mehr Wohnungen, desto günstiger pro Einheit"**
- Preisrechner auf der Landingpage: Kunde gibt WE-Zahl ein, sieht sofort Monats- und Jahrespreis.
- Nie nur den Gesamtbetrag zeigen — immer **Preis/WE + Gesamtpreis** kombinieren.

### 6.5.7 Mengenrabatt-Staffel

| Band | Preis/WE/Monat | Warum |
|---|---|---|
| **1–5 WE** | **9,75 €** | Premium-Einstieg, wertebasiert, unter 10-€-Marke |
| **6–25 WE** | **7,50 €** | 23 % Rabatt — Anreiz für Portfolio-Wachstum |
| **26–100 WE** | **5,90 €** | 39 % Rabatt — professionelle Vermieter |
| **100+ WE** | **Custom Pricing** | Enterprise, Anfragepflicht, SLA |

**Vergleich mit Hausverwaltungskosten:** Eine professionelle Hausverwaltung kostet ca. 15–25 €/WE/Jahr. Unser Pro-WE-Modell liegt bei 117–702 €/WE/Jahr (je nach Band) — also 5–10× teurer als eine Verwaltung? Nein: Hausverwaltung kostet **pro Jahr**, unsere Preise sind **pro Monat**.  
**Wichtig:** Das ist ein bewusster Positionierungswechsel: Wir sind keine Ersatz-Hausverwaltung, sondern eine **KI-gestützte Premium-Software**, die proaktiv Mahnungen, Abrechnungen und Fristen automatisiert. Der Kunde muss diesen Wert verstehen.

### 6.5.8 Empfehlung

**Empfohlene Strategie: Reines, graduiertes Pro-WE-Modell als primäres Preismodell.**

| Band | Preis/WE/Monat | Zielgruppe |
|---|---|---|
| 1–5 WE | 9,75 € | Kleinvermieter, Einstieg |
| 6–25 WE | 7,50 € | Multi-Vermieter |
| 26–100 WE | 5,90 € | Semi-professionelle Portfolios |
| >100 WE | Custom Pricing | Enterprise, Hausverwaltungen |

**Begründung:**
1. **Fairness:** Nur für tatsächlich genutzte WE zahlen.
2. **Premium-Positionierung:** Der Gesamtbetrag für 5+ WE ist deutlich höher als bei günstigen Konkurrenten — das signalisiert Premium-KI.
3. **Skalierung:** MRR wächst automatisch mit dem Kundenportfolio (Expansion Revenue).
4. **Einfacher Checkout:** Keine Plan-Auswahl, nur WE-Zahl eingeben.
5. **Enterprise-Gating:** Ab 100 WE zwingt das Modell zur Anfrage (siehe Kapitel 9).

**Risiken & Gegenmaßnahmen:**
- **Conversion-Risiko bei 3–5 WE:** 9,75 €/WE × 5 = 48,75 €/Monat ist 3× teurer als objego/rentably. Gegenmaßnahme: KI-Value-Story und ROI-Rechner prominent.
- **Fehlender Decoy-Effekt:** Kein „Business"-Plan als Anker. Gegenmaßnahme: Bänder als „Solo" / „Multi" / "Portfolio" verpacken und „Most Popular" auf 6–25-WE-Band setzen.
- **Jahreszahlung:** 20 % Rabatt auf den Gesamtbetrag anbieten, nicht auf WE-Preis, um Cashflow zu sichern.

**Falls Conversion im unteren Segment zu stark sinkt:** Back-up-Option „Solo"-Tarif: **1 WE für 9,75 €/Monat** (gleicher Preis, aber einfacher zu kommunizieren).

---

## 6.6 Abo-Verknüpfung und WE-Downgrade-Szenarien

> **Ziel:** Das System muss jederzeit wissen, welches Abo ein Kunde hat, wie viele Wohnungen aktuell aktiv sind und welcher Betrag monatlich fällig wird — inklusive reibungslosem Umgang mit WE-Reduzierungen.

---

### 6.6.1 Account weiß jederzeit, welches Abo aktiv ist

#### Datenmodell

**Tabelle `subscriptions`**
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    plan_type TEXT NOT NULL DEFAULT 'per_we',   -- 'per_we', 'fixed', 'enterprise'
    billing_interval TEXT NOT NULL DEFAULT 'yearly', -- 'monthly', 'yearly', 'two_yearly'
    status TEXT NOT NULL DEFAULT 'active',        -- active, paused, canceled, past_due
    base_amount_cents INT,                       -- für feste Pläne; bei per_we NULL
    unit_price_tier JSONB,                       -- {"1-5":975, "6-25":750, "26-100":590}
    max_auto_units INT DEFAULT 100,              -- ab hier Enterprise-Anfrage
    current_units INT DEFAULT 0,
    computed_amount_cents INT DEFAULT 0,           -- live berechneter monatlicher Betrag
    currency TEXT DEFAULT 'eur',
    next_billing_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Tabelle `plan_usage` (Audit-Trail & Live-Berechnung)**
```sql
CREATE TABLE plan_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES subscriptions(id),
    user_id UUID NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW(),
    unit_count INT NOT NULL,
    active_unit_count INT NOT NULL,              -- ohne soft-deleted
    tier_snapshot JSONB NOT NULL,                -- {"1-5":5,"6-25":0,"26-100":0}
    computed_amount_cents INT NOT NULL,          -- brutto in Cent
    billing_interval TEXT,
    source TEXT DEFAULT 'cron'                   -- 'cron', 'webhook', 'manual', 'stripe_sync'
);
```

**Tabelle `units` / `wohnungen`**
```sql
ALTER TABLE units ADD COLUMN user_id UUID REFERENCES users(id);
ALTER TABLE units ADD COLUMN status TEXT DEFAULT 'active'; -- active, archived, pending_deletion
ALTER TABLE units ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE units ADD COLUMN has_active_lease BOOLEAN DEFAULT FALSE;
ALTER TABLE units ADD COLUMN open_ticket_count INT DEFAULT 0;
```

#### Live-Berechnung

1. **Cron-Job** läuft 1×/Stunde: zählt `active` Units pro User, schreibt `plan_usage`, aktualisiert `subscriptions.computed_amount_cents`.
2. **Echtzeit-Invalidierung:** Bei Anlage/Löschung/Archivierung einer WE wird der Cache gelöscht und `computed_amount_cents` neu berechnet.
3. **Redis-Cache:**
   - Schlüssel: `subscription:{user_id}:summary`
   - Wert: `{unit_count: 7, amount_cents: 5175, tier:"6-25", next_billing:"2027-01-15"}`
   - TTL: 5 Minuten
   - Invalidierung via Event-Listener auf Unit-Änderungen.
4. **Dashboard-Widget:**
   - API `/api/subscription/summary` liest aus Redis oder berechnet live.
   - UI: **„Dein Abo: Pro-WE · 7 Wohnungen · 51,75 €/Monat"**.
   - Wenn sich die Anzahl ändert, erscheint ein Toast: *„Dein Abo wurde angepasst: 7 WE · 51,75 €/Monat"*.

#### Stripe-Synchronisation

- **Bei Unit-Zuwachs:** Stripe-Subscription-Item-Quantity erhöhen oder neues `price` anlegen. Stripe erstellt automatisch eine Pro-rata-Rechnung.
- **Bei Unit-Abnahme:** Stripe-Quantity verringern. Je nach Einstellung gibt es sofortigen Preisnachlass oder Gutschrift.
- **Webhook-Handler:**
  - `invoice.created` / `invoice.paid` → Sync in `plan_usage`.
  - `customer.subscription.updated` → Update `subscriptions` Record.
  - `customer.subscription.deleted` → Status auf `canceled` setzen, Daten-Sperre + Aufbewahrung.

---

### 6.6.2 Downgrade-Szenario: Kunde reduziert WE

#### Beispiel-Szenario

- Kunde hat **10 WE** → berechnet nach Staffel:  
  5 × 9,75 € + 5 × 7,50 € = **86,25 €/Monat**.
- Kunde löscht/verkauft **5 WE**.
- Kunde hat jetzt **5 WE** → neuer Preis:  
  5 × 9,75 € = **48,75 €/Monat**.

#### Wann wirkt die Preisänderung?

| Option | Wirksamkeit | Kundenfreundlichkeit | Stripe-Umsetzung | Empfehlung |
|---|---|---|---|---|
| **A — Sofort** | Nächste Abbuchung bereits reduziert | Sehr hoch | `proration_behavior=always_invoice` oder Gutschrift | ✅ **Empfohlen** |
| **B — Periodenende** | Erst zum nächsten Abrechnungszeitraum | Mittel | Keine sofortige Aktion, Quantity wird zum Periodenende geändert | ❌ Weniger fair |

**Empfehlung: Option A (Sofort).** Im Pro-WE-Modell ist „nur für das zahlen, was man nutzt" die zentrale Versprechen. Eine sofortige Anpassung stärkt Vertrauen und reduziert Churn.

#### Stripe-Handling bei monatlichem Abo

1. Backend berechnet neuen Betrag (5 WE = 48,75 €).
2. Stripe `subscription_items` aktualisieren:
   - Entweder Quantity des bestehenden Items anpassen.
   - Oder neues Preis-Objekt für 5-WE-Band hinterlegen.
3. Stripe erzeugt automatisch eine Pro-rata-Rechnung oder Gutschrift für die laufende Periode.
4. Kunde erhält E-Mail: *„Dein Abo wurde angepasst: 5 Wohnungen · 48,75 €/Monat. Die nächste Abbuchung am 15.12. beträgt 48,75 €."*

#### Stripe-Handling bei jährlichem Abo

- Kunde hat Jahresabo bezahlt (z. B. 12 × 86,25 € × 0,8 Rabatt = 828,00 €/Jahr).
- Nach Reduzierung auf 5 WE bleibt der Jahresbetrag bestehen, aber:
  - **Option A:** Stripe erstellt eine Gutschrift (credit note) für die Differenz der bereits bezahlten Periode.
  - **Option B:** Differenz wird als Account-Guthaben gutgeschrieben und von der nächsten Jahresrechnung abgezogen.
- **Empfehlung:** Option B, weil sie weniger Erstattungs-Transaktionen auslöst und Cashflow schützt. Kommunikation: *„Du erhältst ein Guthaben von X €, das bei der nächsten Verlängerung angerechnet wird."*

#### Was passiert bei 0 WE?

| Szenario | Regelung |
|---|---|
| Kunde löscht alle WE | System setzt `min_billing_units = 1` (Account-Grundpreis 9,75 € bleibt bestehen) |
| Kunde bleibt 30 Tage bei 0 WE | Account wird in „Paused" versetzt; Login möglich, aber keine neue WE anlegbar |
| Nach weiteren 30 Tagen (60 total) | Account gesperrt, Daten 30 Tage aufbewahrt, dann DSGVO-konform gelöscht |
| Kunde meldet sich wieder an | Reaktivierung möglich, Abo läuft weiter |

**Empfehlung:** Einen **Mindestabrechnungsbetrag von 1 WE** beibehalten, solange der Account existiert. Das verhindert Missbrauch (kostenloser Cloud-Speicher ohne aktive Wohnungen) und deckt Fixkosten.

---

### 6.6.3 UX und Kommunikation

#### Warnung beim Löschen einer WE

Wenn der Kunde eine WE löschen will:

> „Wenn du diese Wohnung löschst, reduziert sich dein Abo von **10 auf 9 WE**.  
> Neuer Preis: **78,75 €/Monat** — du sparst **7,50 €/Monat**.  
> Hinweis: Wohnungen mit aktivem Mietvertrag oder offenem Ticket können nicht gelöscht, sondern nur archiviert werden."

#### E-Mail-Vorlagen

**Upgrade (WE hinzugefügt):**
> „Du hast eine neue Wohnung hinzugefügt. Dein Abo wurde automatisch angepasst: **11 WE · 86,25 €/Monat**. Die nächste Abbuchung erfolgt mit dem neuen Betrag."

**Downgrade (WE gelöscht):**
> „Du hast eine Wohnung gelöscht. Dein Abo wurde angepasst: **5 WE · 48,75 €/Monat**. Bei Jahreszahlung wurde ein Guthaben von X € gutgeschrieben."

#### Dashboard-Widget

```
┌─────────────────────────────────────────┐
│  Dein Abo: Pro-WE                       │
│  7 Wohnungen · Band 6–25 WE             │
│  51,75 €/Monat  (620,40 €/Jahr)         │
│  Nächste Abbuchung: 15.12.2026          │
└─────────────────────────────────────────┘
```

---

### 6.6.4 Edge Cases

| Edge Case | Regel |
|---|---|
| **WE in laufender NK-Abrechnung** | WE kann nicht gelöscht, nur archiviert werden. Archivierte WE zählen nicht mehr für Abrechnung, aber historische Daten bleiben erhalten. |
| **WE mit aktivem Mietvertrag** | Löschen blockiert; Mieter muss zuerst ausgezogen/ausgewiesen werden oder WE auf „inaktiv" gesetzt. |
| **Offenes Ticket an WE** | Löschen blockiert; Ticket muss geschlossen oder auf andere WE übertragen werden. |
| **Bulk-Import/Delete** | Max. 20 WE/Tag ohne manuelle Prüfung; darüber Rate-Limit + Admin-Benachrichtigung (Schutz gegen Manipulation). |
| **Rückgängig machen** | Soft-Delete für 7 Tage; Kunde kann WE selbst wiederherstellen; Stripe-Betrag wird automatisch neu berechnet. |
| **Preisänderung der Staffel** | Neue Staffel gilt nur für neu berechnete Perioden; laufende Perioden werden nicht rückwirkend angepasst (außer bei sofortiger Downgrade-Upsell-Logik). |

---

### 6.6.5 Szenario-Diagramm: 3 WE → 10 WE → 7 WE → 0 WE

```
START
 │
 ▼
3 WE × 9,75 €  = 29,25 €/Monat
 │
 ├─ +2 WE ──▶ 5 WE × 9,75 €  = 48,75 €/Monat
 │              │
 │              ├─ +5 WE ──▶ 10 WE
 │              │              5×9,75 + 5×7,50 = 86,25 €/Monat
 │              │              (Band 6–25 WE aktiviert)
 │              │                  │
 │              │                  ├─ -3 WE ──▶ 7 WE
 │              │                  │              5×9,75 + 2×7,50 = 51,75 €/Monat
 │              │                  │
 │              │                  └─ -7 WE ──▶ 0 WE
 │              │                                  Account: Pause nach 30 Tagen,
 │              │                                  Mindestabrechnung 1 WE (9,75 €)
 │              │
 └─ -3 WE ──▶ 0 WE
                Account: Pause / Mindestabrechnung
```

**Klare Regel:** Jede Änderung der WE-Anzahl wird sofort in den nächsten Stripe-Zyklus übernommen. Kunde sieht Live-Preis im Dashboard. Archivierung statt Löschung bei gebundenen WE.

---

### 6.6.6 Implementierungs-Checkliste

- [ ] `subscriptions` um `unit_price_tier`, `current_units`, `computed_amount_cents` erweitern
- [ ] `plan_usage` Tabelle für Audit-Trail und Rechnungsnachweis anlegen
- [ ] `units` um `status`, `deleted_at`, `has_active_lease`, `open_ticket_count` erweitern
- [ ] Service `calculateSubscriptionAmount(userId)` bauen (live + gecacht)
- [ ] Redis-Cache `subscription:{userId}:summary` mit Invalidierung
- [ ] Dashboard-Widget „Dein Abo" implementieren
- [ ] Stripe-Integration: Subscription-Items / Quantities aktualisieren
- [ ] Webhook-Endpunkte für `invoice.created`, `subscription.updated`, `subscription.deleted`
- [ ] Lösch-Dialog mit Preis-Vorschau bauen
- [ ] Soft-Delete + 7-Tage-Wiederherstellung für WE
- [ ] Regelwerk: archivierte/gelöschte WE bei NK-Abrechnung / aktivem Mietvertrag / offenem Ticket blockieren
- [ ] E-Mail-Templates für Upgrade/Downgrade

---

## 6.7 Preispsychologie und Verhaltensoekonomik im Pricing-UI

> **Ziel:** Unser Pricing-UI und Checkout-Flow sollen mit bewährten Verhaltensökonomik-Prinzipien so gestaltet werden, dass Kunden **zum profitabelsten Tarif gelenkt** werden, ohne dabei unethisch zu sein. Diese Methoden werden von Netflix, Spotify, Apple, Amazon und fast jedem SaaS-Anbieter genutzt [30][31][32].

---

### 6.7.1 Ankereffekt (Anchoring)

**Theorie:** Der erste Preis, den ein Kunde sieht, wird zum mentalen Anker. Alle folgenden Preise werden relativ dazu bewertet [33].

**Umsetzung bei MietVerwaltung:**
- Auf der Preisseite **zuerst den teuersten Wert** zeigen: z. B. „Enterprise bis 100+ WE · ab 590 €/Mo".
- Darunter folgt das Pro-WE-Modell: „Ab 9,75 €/WE — deutlich günstiger als Enterprise".
- Dadurch wirkt 9,75 €/WE plötzlich fair, weil der Kunde zuerst 590 € gesehen hat.

**UI-Beispiel:**
```vue
<div class="pricing-page">
  <!-- Anchor: teuerster Wert oben -->
  <div class="anchor-card">
    <span class="eyebrow">Enterprise-Portfolios</span>
    <div class="anchor-price">ab 590 €/Monat</div>
    <p>Für 100+ Wohnungen mit SLA & dediziertem Account Manager</p>
  </div>

  <!-- Hauptprodukt -->
  <div class="hero-price">Ab 9,75 € pro Wohnung/Monat</div>
  <p>Automatisiere deine Vermietung — ohne Enterprise-Kosten.</p>
</div>
```

**Checkout-Anker:** Im Upgrade-Modal „Statt 590 €/Mo nur 9,75 € pro Wohnung" — der hohe Enterprise-Preis macht den WE-Preis klein.

> Die ursprüngliche Idee „Business 79,90 €" als Anker wurde durch das Pro-WE-Modell ersetzt; der Enterprise-Preis (590 €/Mo für 100 WE) ist der stärkere Anker.

---

### 6.7.2 Decoy-Effekt (Asymmetric Dominance)

**Theorie:** Ein dritter, strategisch unattraktiver Plan macht den Ziel-Plan attraktiver. Apple nutzt das mit iPhone 15 / 15 Pro / 15 Pro Max: Das Pro-Modell ist der Decoy, der die Wahl zum teureren Pro Max lenkt [34].

**Umsetzung bei MietVerwaltung:**
- Drei Optionen: **Solo (1 WE)** · **Multi (6–25 WE)** · **Portfolio (26–100 WE)**.
- Der „Multi"-Tarif wird als **„Beliebtester"** markiert.
- Der „Portfolio"-Tarif ist bewusst hoch gepreist (5,90 €/WE × 50 WE = 295 €), damit „Multi" als vernünftiger Kompromiss wirkt.

**UI-Beispiel:**
```vue
<div class="plans">
  <plan-card name="Solo" :price="9.75" unit="WE">1 Wohnung · für Einsteiger</plan-card>
  <plan-card name="Multi" :price="7.50" unit="WE" popular
    >6–25 Wohnungen · volle KI · beliebt</plan-card>
  <plan-card name="Portfolio" :price="5.90" unit="WE"
    >26–100 Wohnungen · Team + API</plan-card>
</div>
```

**Regel:** Der „Portfolio"-Plan darf nicht viel häufiger gekauft werden als Multi. Falls doch, ist er zu günstig — dann Multi-Preis anheben.

---

### 6.7.3 Verlustaversion (Loss Aversion)

**Theorie:** Menschen vermeiden Verluste stärker, als sie gleich große Gewinne anstreben (Kahneman & Tversky: Verluste wiegen etwa 2× so schwer wie Gewinne) [35].

**Umsetzung:**
- Nicht: „Du sparst 645 €/Jahr"  
  Sondern: „Ohne Pro-WE **verlierst du 645 €/Jahr** an manueller Arbeit."
- Trial-Ende: Nicht „Dein Testzeitraum endet morgen", sondern „Du **verlierst morgen** KI-Beleg-Scan, automatische Mahnungen und Smart Insights."

**UI-Texte:**
```text
❌ Ohne Upgrade verlierst du:
   • Automatische KI-Beleg-Scans (Wert: 5h/Monat)
   • Smart Insights für Mieterhöhungen (Wert: 200 €/Jahr)
   • Automatisiertes Mahnwesen (Wert: 8h/Monat)

✅ Mit Multi für 7,50 €/WE behältst du alles.
```

**Checkout:** Auf der Kündigungsseite „Wenn du jetzt kündigst, verlierst du sofort Zugriff auf 18 automatisierte Prozesse".

---

### 6.7.4 Endowment Effect (Besitztumseffekt)

**Theorie:** Menschen bewerten Dinge höher, sobald sie ihnen gehören [36]. Ein 14-Tage-Trial mit allen Features macht den Kunden zum „Besitzer" der KI-Features.

**Umsetzung:**
- Während Trial: Dashboard zeigt **„Deine KI-Features sind aktiv"** mit grünen Badges.
- Nach Trial-Ablauf: Dieselben Features sind **gesperrt** mit grauem Overlay und Schloss-Icon.
- Upgrade-CTA: **„Hol dir deine KI-Features zurück"** statt „Upgrade auf Pro".

**UI-Beispiel:**
```vue
<feature-card
  :locked="!subscription.isPro"
  title="KI-Beleg-Scan"
  description="Scannt Rechnungen automatisch">
  <div v-if="subscription.isPro">
    <span class="badge-active">✓ Aktiv</span>
  </div>
  <div v-else>
    <span class="badge-locked"><i class="icon-lock"></i> Gesperrt</span>
    <button @click="upgrade">Features zurückholen</button>
  </div>
</feature-card>
```

---

### 6.7.5 Status-Quo-Bias (Beharrungstendenz)

**Theorie:** Menschen bleiben lieber bei der aktuellen Situation, weil Wechsel Aufwand und Unsicherheit bedeutet [37].

**Umsetzung:**
- **Default-Auswahl:** Im Checkout ist „Multi" vorausgewählt (Radio-Button checked).
- **Jährliche Zahlung als Default:** Der Toggle ist auf „Jährlich" voreingestellt.
- **Automatische Verlängerung:** Kunde muss aktiv kündigen; Kündigungsprozess mit Bestätigungs-Fragen und optionaler Umfrage.
- **Upgrade sofort, Downgrade Periodenende:** Upsell-Reibung minimieren, Kündigungsimpulse bremsen.

**UI-Beispiel:**
```vue
<billing-toggle v-model="interval" default="yearly" />

<plan-selector v-model="selectedPlan" default="multi" />
```

---

### 6.7.6 Herdentrieb (Social Proof)

**Theorie:** Menschen orientieren sich am Verhalten anderer [38].

**Umsetzung:**
- **Badge „Beliebtester Plan"** auf dem Multi-Tarif.
- „Über **12.000 Vermieter** vertrauen MietVerwaltung."
- „**75 % unserer Neukunden** wählen Multi."
- „In den letzten 24h schlossen sich **247 Vermieter** an."
- Testimonials unterhalb der Preise: „Ich habe mit Solo angefangen, aber nach 2 Wochen auf Multi gewechselt — die KI-Mahnungen allein lohnen sich."

**UI-Beispiel:**
```vue
<plan-card name="Multi" :price="7.50" unit="WE" popular>
  <div class="social-proof">
    <span class="pulse-dot"></span>
    75 % der Neu-Kunden wählen diesen Plan
  </div>
</plan-card>
```

---

### 6.7.7 Knappheit (Scarcity)

**Theorie:** Knappheit erhöht wahrgenommenen Wert und Dringlichkeit [39].

**Umsetzung:**
- „Nur noch **23 Plätze** zum Einführungspreis in deiner Region."
- „Beta-Zugang endet am **31.12.2026** — danach Anmeldegebühr."
- Trial-Countdown: „Dein 14-Tage-Trial endet in **2 Tagen, 4 Stunden**.
- „Kostenloses Onboarding nur für die ersten 100 Kunden."

**UI-Beispiel:**
```vue
<div class="scarcity-banner">
  <span>⏰ Nur noch 14 Plätze zum Einführungspreis (9,75 €/WE)</span>
</div>
```

**Wichtig:** Knappheit muss echt oder transparent als „künstlich limitiertes Angebot" kommuniziert werden. Faken zerstört Vertrauen.

---

### 6.7.8 Charm Pricing (9-Endung)

**Theorie:** Preise mit 9-Endung wirken deutlich günstiger, weil der linke Ziffern-Effekt die erste Ziffer überbetont [40].

**Bewertung unserer Preise:**

| Preis | Wirkung | Empfehlung |
|---|---|---|
| 9,75 € | Unter 10 €, charmig, premium | ✅ **Optimal für Pro-WE-Einstieg** |
| 9,90 € | Noch unter 10 €, aber „billiger" assoziiert | ⚠️ Könnte Wert mindern |
| 9,99 € | Maximale Charm-Wirkung, aber „Schnäppchen"-Image | ❌ Nicht für Premium-Positionierung |
| 10,00 € | Runder Preis, Qualitätssignal, aber verliert Charm-Effekt | ⚠️ Für Enterprise-Custom denkbar |

**Empfehlung:**
- **9,75 €/WE** für Band 1–5 (Premium-Charm unter 10 €).
- **7,50 €/WE** und **5,90 €/WE** für Bänder (klare Staffel, Endung ,50 / ,90).
- **29,90 € / 49,90 €** als Fallback-Festpreise (falls A/B-Test nötig).

---

### 6.7.9 Zero-Price-Effekt (FREE-Trick)

**Theorie:** „Kostenlos" ist ein extrem starker psychologischer Trigger — er übertrumpft oft rationale Rabattberechnungen [41].

**Umsetzung ohne dauerhaftem Free-Plan:**
- **14 Tage kostenlos ohne Kreditkarte** — das ist die kostenlose Version des vollen Produkts.
- Während Trial wird der reguläre Preis durchgestrichen angezeigt: ~~86,25 €/Mo~~ → **0 € für 14 Tage**.
- Nach Trial-Ablauf: „Weiter für 9,75 €/WE" — Kunde hat den Wert bereits erlebt.

**UI-Beispiel:**
```vue
<div class="trial-badge">
  <span class="strike">86,25 €/Mo</span>
  <span class="free">14 Tage kostenlos</span>
</div>
```

---

### 6.7.10 Framing (Rahmung)

**Theorie:** Derselbe Preis wirkt je nach Darstellung anders [42].

**Umsetzung:**

| Schlechtes Framing | Gutes Framing |
|---|---|
| „117 € pro Jahr pro Wohnung" | „Nur 9,75 € pro Wohnung im Monat" |
| „86,25 €/Monat" | „10 Wohnungen für weniger als 3 € pro Tag" |
| „Du zahlst 51,75 €/Monat" | „7 Wohnungen für 51,75 €/Monat — das sind 32 Cent pro Tag und Wohnung" |
| „Jährlich 620,40 €" | „20 % sparen — 2 Monate geschenkt" |

**Daily-Framing:** 9,75 €/30 Tage = **0,33 €/Tag**. Das ist psychologisch vernachlässigbar.

**UI-Beispiel:**
```vue
<price-display
  :monthly="51.75"
  :units="7"
  daily-text="Nur 32 Cent pro Tag und Wohnung"
/>
```

---

### 6.7.11 Preisanpassungs-Psychologie

**Problem:** Wenn wir später Preise erhöhen, droht Churn.

**Lösungen:**

| Taktik | Umsetzung |
|---|---|
| **Grandfathering** | Bestehende Kunden behalten alten Preis (z. B. 9,75 €/WE), nur Neukunden zahlen mehr. |
| **Einführungspreis** | Kommunikation: „9,75 €/WE ist der Einführungspreis für die ersten 1.000 Vermieter." Das setzt einen Erwartungsanker für spätere Erhöhungen. |
| **Feature-Lock** | Preiserhöhung wird mit neuen Features begründet: „Preis bleibt für dich, Plus-Features kommen neu dazu." |
| **Loyalty-Rabatt** | Kunden, die 12 Monate bleiben, erhalten „Founder-Status" mit dauerhaftem Rabatt. |

**UI-Beispiel:**
```text
✅ Du bist ein „Founder" — du zahlst dauerhaft 9,75 €/WE.
   Neue Kunden zahlen ab Q2 2027 11,90 €/WE.
```

---

### 6.7.12 Upsell-Psychologie

**Theorie:** Upsells funktionieren am besten im Moment der höchsten Relevanz — z. B. wenn ein Limit erreicht wird [43].

**Umsetzung:**
- WE-Limit-Progressbar: „5/5 WE genutzt" in rot/gelb.
- Tooltip beim Hinzufügen der 6. WE: „Eine Wohnung mehr kostet nur 7,50 €/Mo — das sind 25 Cent pro Tag."
- Upgrade-Modal nicht als Strafe, sondern als „natürliches Wachstum" framen: „Glückwunsch, dein Portfolio wächst!"

**UI-Beispiel:**
```vue
<div class="upsell-modal">
  <h3>🎉 Dein Portfolio wächst!</h3>
  <p>Du hast 6 Wohnungen. Ab jetzt zahlst du nur 7,50 € pro Wohnung.</p>
  <div class="price-comparison">
    <span>Alt: 6 × 9,75 € = 58,50 €</span>
    <span>Neu: 6 × 7,50 € = 45,00 €</span>
  </div>
  <button @click="confirmUpgrade">Abo anpassen</button>
</div>
```

---

### 6.7.13 Checkout-Psychologie

**Reihenfolge der Zahlungsmethoden:**
1. Apple Pay / Google Pay (1-Klick, höchste Conversion)
2. Kreditkarte
3. SEPA-Lastschrift
4. PayPal

**Reibungsreduktion:**
- „14 Tage kostenlos — keine Kreditkarte nötig" reduziert Angst vor Bindung.
- „Jederzeit kündbar" als Sicherheitssignal.
- Trust-Badges: „Sicher über Stripe", „DSGVO-konform", „Server in Deutschland".
- Grüner Haken nach Abschluss + kurze Animation = Dopamin-Release.

**UI-Beispiel:**
```vue
<div class="checkout">
  <trust-row>
    <badge><i class="icon-lock"></i> SSL-verschlüsselt</badge>
    <badge>DSGVO-konform</badge>
    <badge>Server in Deutschland</badge>
  </trust-row>

  <payment-methods default="apple_pay" />

  <div class="cancel-note">
    <i class="icon-check"></i> Jederzeit kündbar · Keine Einrichtungsgebühr
  </div>

  <button class="cta">14 Tage kostenlos starten</button>
</div>
```

---

### 6.7.14 Konkrete UI-Implementierung: Wo welcher Trick sitzt

| UI-Bereich | Psychologischer Trick | Konkretes Element |
|---|---|---|
| **Pricing-Page Hero** | Ankereffekt | Enterprise-Preis (590 €/Mo) oben, dann „Ab 9,75 €/WE" |
| **Plan-Karten** | Decoy + Social Proof | „Multi" als „Beliebtester", „Portfolio" als teurer Anker |
| **Trial-Dashboard** | Endowment + Loss Aversion | „Deine KI-Features sind aktiv" → nach Ablauf gesperrt |
| **Checkout** | Status-Quo + Zero-Price | Default „Multi", Jahreszahlung, 14 Tage kostenlos |
| **Upsell-Modal** | Loss Aversion + Framing | „Glückwunsch, dein Portfolio wächst — nur 25 Cent/Tag mehr" |
| **Kündigungsseite** | Loss Aversion + Status-Quo | Liste der verlorenen Features, „Pause statt kündigen"-Button |
| **Preisrechner** | Framing + Charm Pricing | Monatlicher Betrag + täglicher Betrag/WE |
| **Trial-Ende-E-Mail** | Scarcity + Loss Aversion | „In 2 Tagen verlierst du KI-Beleg-Scan + Mahnwesen" |
| **Landingpage** | Social Proof + Scarcity | Live-Zähler „X Vermieter in deiner Stadt nutzen uns" |

**Zusammenfassendes Code-Snippet für die Pricing-Page:**

```vue
<template>
  <div class="pricing">
    <!-- Anchor -->
    <enterprise-anchor price="590" />

    <h1>Ab 9,75 € pro Wohnung im Monat</h1>
    <p class="subline">Nur was du nutzt. Je mehr Wohnungen, desto günstiger.</p>

    <billing-toggle default="yearly" />

    <div class="plans">
      <plan-card
        v-for="plan in plans"
        :key="plan.id"
        :plan="plan"
        :selected="selectedPlan === plan.id"
        @select="selectedPlan = plan.id"
      />
    </div>

    <calculator :units="units" />

    <trust-row />

    <button class="cta" @click="startTrial">14 Tage kostenlos starten</button>
  </div>
</template>
```

---

### 6.7.15 Fazit: Psychologie-Stack für MietVerwaltung

Der optimale Pricing-UI-Stack kombiniert:
1. **Anker** (Enterprise 590 €) → macht 9,75 €/WE klein.
2. **Decoy** (Portfolio 5,90 €/WE × 100 WE = 590 €) → macht Multi attraktiv.
3. **Social Proof** („Beliebtester") → reduziert Entscheidungsangst.
4. **Loss Aversion** → Trial-Ende und Kündigung hebeln Verlustangst.
5. **Endowment** → 14 Tage volle Features machen Kunden zu „Besitzern".
6. **Status Quo** → Default = Multi + Jährlich.
7. **Charm Pricing** → 9,75 / 7,50 / 5,90 €.
8. **Framing** → „32 Cent pro Tag und Wohnung".

**Wichtig:** Alle Tricks müssen transparent und rechtlich unbedenklich sein (§ 307 BGB, AGB-Recht). Keine falschen Knappheits-Angaben, keine versteckten Preise. Psychologie darf manipulieren, aber nicht täuschen.

---

## 7. Alle Key-Kennzahlen auf einer Seite grafisch zusammengefasst

Die grafische Zusammenfassung aller Key-Kennzahlen ist als eigenständiges Dashboard verfügbar:

**`/root/mietverwaltung/Markt-Kennzahlen-Dashboard.html`**

Das Dashboard enthält:
- TAM / SAM / SOM als Trichter
- Konkurrenz-Preisvergleich bei 5 und 25 WE
- Positionierung der drei Pläne (Basis / Pro / Business)
- Marktwachstum Deutschland 2025–2033
- Zielgruppen-Verteilung nach Wohnungsanzahl
- Break-even-Punkt
- CLV vs. CAC
- Upsell-Pfad

Es ist responsiv, im Apple-Design (Navy #0D3B70, Dark Mode) und ohne externe Bibliotheken.

---

## 8. USP und Positionierung

### 8.1 Warum MietVerwaltung statt Konkurrenz?

| Differentiator | Was wir bieten | Konkurrenz |
|---|---|---|
| **Echte KI-Automatisierung** | Belege → Abrechnung, Mahnungen, Mieterhöhungen, Ticket-Antworten eingebaut | immocloud/objego kaum KI; rentably nur extern; aedium noch in Pilotphase |
| **DSGVO-konforme KI** | Anonymisierungsschicht vor KI-API, Vermieter bleibt Entscheider | Kaum ein Anbieter kommuniziert das transparent |
| **Echtes Ticket-System** | Mieter meldet Schaden → KI kategorisiert → Entwürfe → Status-Workflow | immocloud nur Vorgänge; hellohousing/VermietenPlus gar nicht |
| **ROI-Dashboard** | Brutto-, Netto-, Eigenkapitalrendite, DSCR, LTV, Cash-on-Cash | Fehlt bei fast allen Wettbewerbern |
| **Mieter-Onboarding ohne Scoring** | Ausweis/Lohn/Schufa → KI strukturiert, Mensch entscheidet (DSGVO Art. 22) | aedium macht Eignungs-Check, aber DSGVO-Status unklar |
| **14 Tage kostenlos ohne Kreditkarte** | No-CC-Trial, volle Pro-Features testbar | immocloud 45 Tage Test (stark), aber die meisten haben nur 30 Tage oder gar kein Trial |
| **DACH-Lokalisierung** | Deutsche, österreichische und schweizerische Mietrechtsvorlagen | Die meisten Konkurrenten sind nur für DE optimiert |
| **Handwerker-Ökosystem (Roadmap)** | Ticket → Handwerker-Empfehlung → Auftrag → Provision | Niemand bietet das integriert |

### 8.2 Kern-Claims

1. **„KI-gestützte Mietverwaltung — 80 % der Vermieter-Arbeit automatisch erledigt."**
2. **„Die einzige Mietverwaltung mit DSGVO-konformer KI, eID und automatisiertem Mahnwesen."**
3. **„Vermieten statt verwalten."**

### 8.3 Positionierungs-Matrix

| Dimension | Position |
|---|---|
| **Preis** | Mid-Market mit Premium-Features (nicht Preisbrecher) |
| **Technologie** | KI-First, DSGVO-konform, Cloud-native |
| **Zielgruppe** | Private Kleinvermieter 1–50 WE, später kleine Hausverwaltungen |
| **Geografie** | DACH-Fokus, DE-Launch, AT/CH danach |
| **Wettbewerbsvorteil** | Geschwindigkeit + KI + Datenschutz + ROI-Dashboard + Ticketsystem |

---

## 9. Grosse-Kunden-Schutz (WE-Begrenzung und Anfrage-Pflicht)

### 9.1 Problemstellung

Große Portfolios (50+ WE) haben andere Anforderungen:
- Mehr Nutzer, Rollen & Rechte
- Höhere Performance- und Verfügbarkeitsanforderungen
- Mandantenfähigkeit, WEG, Sondereigentum
- Höheres Support- und Onboarding-Aufwand
- Risiko, dass ein einzelner Kunde die Infrastruktur überlastet

### 9.2 Empfohlener Schwellenwert

| Schwellenwert | Regelung |
|---|---|
| **Ab 100 Wohnungen** | Kein automatischer Self-Service-Abschluss mehr. Kunde muss **Anfrage stellen**. |
| **26–100 Wohnungen** | Automatisch per WE: **5,90 €/WE/Monat**. |
| **Ab 100 Wohnungen** | **Enterprise / Custom Pricing** — individuelles Angebot, SLA, Onboarding. |

> **Hintergrund:** 99 % der privaten Vermieter haben ≤50 WE. Eine Grenze bei 100 WE schließt praktisch den gesamten Privatvermieter-Markt ein (99 % haben ≤100 WE) und fängt nur echte Enterprise-Portfolios ab.

### 9.3 Was passiert bei Überschreitung?

**Frontend-Verhalten:**
1. Beim Anlegen der 51. Wohnung erscheint ein Modal:
   > „Du hast viele Wohnungen! 🎉  
   > Ab 50 Wohnungen bieten wir dir ein maßgeschneidertes Business- oder Enterprise-Paket mit persönlichem Onboarding.  
   > Kontaktiere uns für ein unverbindliches Angebot."
2. Der „Upgrade“-Button leitet zum Anfrageformular.
3. Bestehende Wohnungen bleiben lesbar; neue Wohnungen können erst nach Freigabe angelegt werden.

**Backend-Verhalten:**
- Subscription hat Feld `max_auto_wohnungen` (default 5 / 25 / 50 je nach Plan).
- API-Endpoint `/api/wohnungen` prüft Limit. Überschreitung → 403 mit Hinweis auf Enterprise-Anfrage.
- Rate-Limit für Importe/Massen-Uploads verschärft, um Missbrauch zu verhindern.
- Manuelle Freigabe durch Admin nach Identitäts- und Nutzungszweck-Prüfung.

### 9.4 Was wird bei der Anfrage geprüft?

| Prüfung | Methode | Ziel |
|---|---|---|
| **Identity-Check** | Handelsregisterauszug (Gewerbe), Personalausweis (Privat), WEG-Beschluss | Sicherstellen, dass ein echter Vermieter/Verwalter fragt |
| **Nutzungszweck** | Kurzes Gespräch / Fragebogen | Kein Konkurrent, kein Scraper, kein Test-Account-Missbrauch |
| **Portfolio-Nachweis** | Mietverträge, Grundbuch, Objektliste (stichprobenartig) | Echte Größe des Portfolios bestätigen |
| **DSGVO/Compliance-Check** | Verarbeitung > 5.000 Personen? Dann ggf. DSFA nötig | Rechtliche Risiken früh erkennen |
| **Technische Eignung** | Peak-Nutzer, erwartete Dokumentenmenge | Kapazitätsplanung |

### 9.5 Business- und Enterprise-Plan

| Plan | WE-Grenze | Preis | Inkludiert |
|---|---|---|---|
| **Portfolio** | 26–100 WE | **5,90 €/WE** | Volle KI, 5 Nutzer, API, Priority-Support 4h |
| **Enterprise** | ab 50–100 WE | **Individuell** | 10+ Nutzer, SLA, dedizierter Account Manager, Custom Reports, WEG-Option |
| **Enterprise Plus** | ab 100 WE | **Individuell + Setup-Fee** | White-Label, API-Limits erhöht, Onboarding-Workshop |

### 9.6 Datenbank-Schema-Vorschlag

**Option A: Einfaches Feld in `subscriptions`**
```sql
ALTER TABLE subscriptions ADD COLUMN max_auto_wohnungen INT DEFAULT 25;
ALTER TABLE subscriptions ADD COLUMN enterprise_requested BOOLEAN DEFAULT FALSE;
ALTER TABLE subscriptions ADD COLUMN enterprise_approved BOOLEAN DEFAULT FALSE;
```

**Option B: Separate Tabelle `enterprise_requests` (empfohlen)**
```sql
CREATE TABLE enterprise_requests (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    requested_wohnungen INT NOT NULL,
    current_wohnungen INT NOT NULL,
    legal_form TEXT,            -- 'privat', 'gewerbe', 'weg'
    identity_verified BOOLEAN DEFAULT FALSE,
    use_case TEXT,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected, escalated
    reviewed_by UUID REFERENCES admins(id),
    reviewed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Empfehlung:** Option B, weil Anfragen auditiert, mehrere Review-Runden möglich und spätere Integration in ein CRM/Vertriebstool einfacher sind.

### 9.7 Implementierungs-Checkliste

- [ ] Frontend: Limit-Warning bei 90 / 100 / 110 WE
- [ ] Frontend: Anfrage-Modal mit Formular (Kontakt, Portfolio-Größe, Nutzungszweck)
- [ ] Backend: `max_auto_wohnungen` pro Subscription
- [ ] Backend: API-Guard für Wohnungs-Anlage
- [ ] Backend: Rate-Limit auf Massen-Importe
- [ ] Admin-Panel: Übersicht offener Enterprise-Anfragen
- [ ] Admin-Panel: Freigabe/Ablehnung mit Notiz
- [ ] E-Mail-Workflow: Bestätigung Anfrage + Entscheidung
- [ ] Stripe: Custom-Preis-Subscription für freigegebene Enterprise-Kunden

---

## 10. Zusammenfassung und Empfehlung

### 10.1 Ein-Satz-Zusammenfassung pro Kapitel

| Kapitel | Kernaussage |
|---|---|
| **1. TAM** | DACH hat ~6,35 Mio. private Vermieter mit ~18 Mio. Wohnungen; das jährliche Marktpotenzial liegt bei ~1,14 Mrd. €. |
| **2. SAM** | Ca. 2,36 Mio. online-affine Kleinvermieter mit 1–25 WE sind adressierbar; Marktvolumen ~450–570 Mio. €/Jahr. |
| **3. SOM** | Realistisch erreichbar: 2.500 Kunden in Jahr 1, 30.000 in Jahr 3, 75.000 in Jahr 5 — entspricht 0,1–3 % des SAM. |
| **4. Beachhead** | Hamburg + Niedersachsen, 2–10 WE: groß genug für Skalierung, klein genug für fokussierte Akquise. |
| **5. Konkurrenz** | Markt ist fragmentiert; niemand kombiniert KI-Automation, DSGVO-KI, Ticketsystem und ROI-Dashboard. |
| **6. Preise** | v3-Festpreise sind für Premium-KI zu niedrig; empfohlen wird **graduiertes Pro-WE-Modell: 9,75 / 7,50 / 5,90 €/WE** mit Custom ab 100 WE. |
| **7. Dashboard** | Alle Kennzahlen sind in `/root/mietverwaltung/Markt-Kennzahlen-Dashboard.html` visuell aufbereitet. |
| **8. USP** | Unser differenzierter Wert ist eingebaute KI-Automation + DSGVO-Anonymisierung + Ticket-System + ROI-Dashboard. |
| **6.7 Preispsychologie** | Pricing-UI nutzt Anker, Decoy, Loss Aversion, Endowment, Social Proof, Charm Pricing und Framing — alles transparent und DSGVO-konform. |
| **9. Grosse-Kunden-Schutz** | Ab 100 WE Custom Pricing / Anfragepflicht; technisch via `subscriptions.max_auto_units`, `enterprise_requests`-Tabelle und API-Guard umsetzen. |

### 10.2 Klare Empfehlungen

1. **Preise / Modell:** Auf **graduiertes Pro-WE-Modell** umstellen: **9,75 €/WE (1–5) · 7,50 €/WE (6–25) · 5,90 €/WE (26–100) · Custom ab 100 WE**. Pricing-UI mit Anker, Decoy, Social-Proof und Loss-Aversion gestalten (Kapitel 6.7).
2. **Markt:** Fokus auf **1–25 WE** behalten. Erst nach PMF (Jahr 2) gezielt Hausverwaltungen/Enterprise ansprechen.
3. **Positionierung:** Als **„Mid-Market mit Premium-Features"** positionieren — nicht als billigster Anbieter, sondern als wertvollster KI-Automatisierer.
4. **Launch:** Sofort den 14-Tage-No-CC-Trial für alle Bänder kommunizieren und **„Multi" (6–25 WE) als „Beliebtester Plan"** markieren. Pricing-Page mit Enterprise-Anker (590 €) und Live-Preisrechner bauen.
5. **Beachhead:** In Hamburg/Niedersachsen mit 2–10-WE-Segment starten; dort Beta-Tester, regionale Verbände und gezielte Google Ads aufbauen.
6. **Abo-Engine:** `subscriptions`, `plan_usage`, Redis-Cache und Stripe-Webhooks implementieren, damit der Account live weiß: „7 WE · Band 6–25 · 51,75 €/Monat". Soft-Delete, Preis-Vorschau beim Löschen und sofortige Downgrade-Anpassung (Option A) umsetzen.
7. **Nächster Schritt:** Pro-WE-Preismodell und Abo-Engine mit 50 Beta-Nutzern testen. Metriken: Conversion-Rate, Trial-to-paid, durchschnittliche WE-Zahl, MRR, Churn. Bei guter Conversion v3-Festpreise abschaffen.

---

## Quellen

[1] Institut der deutschen Wirtschaft (IW Köln): „Private Vermieter in Deutschland", 2025 — https://www.iwkoeln.de/studien/christian-oberst-pekka-sagner-michael-voigtlaender-private-vermieter-in-deutschland.html  
[2] Deutscher Bundestag, Drucksache 21/8091, 2026 — https://dserver.bundestag.de/btd/21/080/2108091.pdf  
[3] Statistisches Bundesamt (Destatis), Zensus 2022 — https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Wohnen.html  
[4] Statistik Austria: „Wohnen 2024“, Mikrozensus-Wohnungserhebung — https://www.statistik.at/fileadmin/publications/Wohnen_2024_Web-barrierefrei.pdf  
[5] Statistik Austria: „Wohnen 2025" — https://www.statistik.at/fileadmin/publications/Wohnen_2025_bf.pdf  
[6] Bundesamt für Statistik Schweiz (BFS): Wohnverhältnisse — https://www.bfs.admin.ch/bfs/de/home/statistiken/bau-wohnungswesen/wohnungen/wohnverhaeltnisse.html  
[7] JLL Schweiz: „Facts about the housing market in Switzerland", 2025/2026 — https://www.jll.com/en-ch/insights/facts-about-the-housing-market-in-switzerland  
[8] IW / Deutschland.Immobilien: „Vermieterreport 2026" — https://www.bca.de/wp-content/uploads/2026/06/Deutschland.Immobilien_Vermieterreport_2026.pdf  
[9] Grand View Research: Germany Property Management Software Market 2025–2033 — https://www.grandviewresearch.com/horizon/outlook/property-management-software-market/germany  
[10] Market Data Forecast: Europe Property Management Software Market 2025–2034 — https://www.marketdataforecast.com/market-reports/europe-property-management-software-market  
[11] Grand View Research: Global Property Management Software Market 2025–2033 — https://www.grandviewresearch.com/industry-analysis/property-management-software-market  
[12] Mordor Intelligence: Property Management Software Market 2025–2031 — https://www.mordorintelligence.com/industry-reports/property-management-software-market  
[13] Haus & Grund Deutschland: „Vermieterbefragung 2026" — https://www.hausundgrund.de/sites/default/files/downloads/20260504-hug-vermieterbefragung-2026-alle-ergebnisse.pdf  
[14] Internes Dokument: Abo-Modell v3 — `/root/mietverwaltung/Abo-Modell-v3.md`  
[15] Internes Dokument: Competitor Deep-Dive 2026 — `/root/mietverwaltung/competitor-deep-dive-2026.md`  
[16] Internes Dokument: Go-to-Market-Strategie — `/root/mietverwaltung/go-to-market-strategie.md`  
[17] Internes Dokument: Über-Agent-Report — `/root/mietverwaltung/Ueber-Agent-Report.md`  
[18] Internes Dokument: Pain-Point-Analyse — `/root/pain_point_analyse.md`  
[19] ManageCasa: „Property Management Software Pricing Under 100 Doors" — https://managecasa.com/articles/property-management-software-pricing-what-it-actually-costs-for-under-100-doors  
[20] Rankite: „Best Software for Property Managers in 2026" — https://rankite.com/blog/best-software-for-property-managers  
[30] Netflix / Spotify / Apple: Standard-SaaS-Pricing-UX (öffentlich beobachtbar)
[31] ProfitWell / Paddle: SaaS Pricing Psychology Studien — https://www.profitwell.com  
[32] SaaS Pricing Pages Repo: Pricing-Pattern-Sammlung — https://github.com/bdebout/gauthier-quiz-funnel-expert  
[33] Kahneman, D. & Tversky, A.: „Judgment under Uncertainty: Heuristics and Biases" (Anchoring)  
[34] Apple iPhone Pricing Strategy: Product-line Decoy-Effekt (Marktbeobachtung)  
[35] Kahneman, D. & Tversky, A.: „Prospect Theory: An Analysis of Decision under Risk" (Loss Aversion)  
[36] Thaler, R.: „Toward a Positive Theory of Consumer Choice" (Endowment Effect)  
[37] Samuelson, W. & Zeckhauser, R.: „Status Quo Bias in Decision Making"  
[38] Cialdini, R.: „Influence: The Psychology of Persuasion" (Social Proof)  
[39] Cialdini, R.: „Influence" (Scarcity)  
[40] Anderson, E. & Simester, D.: „Mind Your Pricing Cues" (Charm Pricing / 9-Endung)  
[41] Ariely, D.: „Predictably Irrational" (Zero-Price Effect)  
[42] Tversky, A. & Kahneman, D.: „The Framing of Decisions and the Psychology of Choice"  
[43] ProfitWell: Upsell-Timing und Expansion-Revenue-Studien
