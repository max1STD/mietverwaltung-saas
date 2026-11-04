# Abo-Modell v3 — MietVerwaltung SaaS

> **Status:** Konzept (Entscheidungsgrundlage)  
> **Gültig ab:** Konzept-Phase  
> **Strategische Richtung:** Kein Free-Plan mehr. Einstieg direkt zahlend, aber mit **14 Tage kostenlosem Trial ohne Kreditkarte**. Fokus auf schnelle Break-even-Marge, niedrigen Churn und klarem Upsell-Pfad.  
> **Zielgruppe:** Private Kleinvermieter, Semi-Professionelle und kleine Hausverwaltungen in DACH.

---

## 1. Executive Summary

Die v2 mit Free-Plan war zu akquisitionslastig: Free-User generieren Support- und Infrastrukturkosten, ohne Umsatz zu bringen. Mit den neuen Konkurrenten-Preisen (rentably 0–9 €, hellohousing 4,50–19,50 €, objego 0–12,70 €) kann ein dauerhaft kostenloser Plan nicht mehr das Alleinstellungsmerkmal sein — unsere Differenzierung ist **KI-Automation (80 %), DSGVO-konforme Anonymisierung und ROI-Dashboard**.

**Kernentscheidungen v3:**

| Element | v2 | v3 |
|---------|----|----|
| Pläne | 4 (Free/Basis/Pro/Business) | 3 (Basis/Pro/Business) |
| Einstiegspreis | 0 € | **14,90 €/Monat** (Basis) |
| Trial | 30 Tage ohne KK (Basis/Pro), 14 Tage mit KK (Business) | **14 Tage ohne KK** für alle zahlenden Pläne |
| Kündigung | monatlich / jährlich | **monatlich 4 Wochen**, **jährlich 3 Monate zum Jahresende** |
| Intervall-Default | monatlich | **jährlich (20 % Rabatt)** |
| Zahlungsmethoden | Karte / SEPA / PayPal | **Karte / SEPA / PayPal** (keine Rechnung) |
| Upsell-Regeln | einfache Proration | **Upgrade sofort, Downgrade Periodenende, nach Kündigung Sperre + 30 Tage Aufbewahrung** |

---

## 2. Research-Grundlagen & Quellen

### 2.1 SaaS-Pricing-Psychologie 2025

| Erkenntnis | Quelle / Wert | Implikation für uns |
|------------|---------------|---------------------|
| **Charm Pricing** ($29 statt $30) verbessert Conversion um **3–4 %** (Meta-Studie über 18.000 Unternehmen, ProfitWell) | ProfitWell/SaaS-Pricing-Pages-Repo | Preise mit ,90-Endung (14,90 / 29,90 / 49,90) |
| **Preis-Ankerung**: 2-Tier vs. 1-Tier steigert ARPU um **+15 %** | ProfitWell-Metastudie | 3 Pläne mit hohem Business-Preis als Anker |
| **Decoy-Effekt**: 60–70 % der Zahler wählen die mittlere Stufe, wenn die untere zu limitiert und die obere zu teuer wirkt | SaaS-Pricing-Pages-Repo | Pro als „Beliebtester Plan“ positionieren |
| **Badge „Most Popular“/„Best Value“** erhöht Mittelstufe-Anteil signifikant | SaaS-Pricing-Playbook 2025 | Visuelles Hervorheben von Pro |
| **Jährlich als Default** mit **20 % Rabatt** (2 Monate geschenkt) ist Standard | Buildology 2025, ChartMogul 2025 | Toggle-Default = jährlich |

### 2.2 Freemium vs. Trial — Conversion-Statistiken

| Modell | Trial-Entry | Trial-to-paid (Median) | Trial-to-paid (Top) | Quelle |
|--------|-------------|------------------------|---------------------|--------|
| Freemium forever | ~9 % | 3–5 % | 15 %+ | SaaS-Pricing-Pages-Repo |
| No-CC Trial | ~8,5 % | **18,2 %** | 35–45 % / 60 %+ | SaaS-Pricing-Pages-Repo |
| CC-required Trial | ~2,5 % | **48,8 %** | — | SaaS-Pricing-Pages-Repo |
| 14-day Trial | — | 20–25 % | — | Tanstackship / SaaSfactor |
| 30-day Trial | — | 25–35 % | — | Tanstackship |
| Achievement-based Trial vs. kalenderbasiert | — | **+258 %** Conversion | — | trialmoments.com |

**Entscheidung:** Wir entfernen den Free-Plan und setzen auf **14 Tage No-CC-Trial**. Begründung:

1. Ohne Free-Plan brauchen wir maximalen Trial-Entry. No-CC hat **3,4× höheren Entry** als CC-required (8,5 % vs. 2,5 %).
2. Unser Produkt ist komplex (Belege, Mieter, Abrechnung, Tickets). 14 Tage sind knapp, aber mit **Achievement-basierten Onboarding-Meilensteinen** (z. B. „Erster Beleg gescannt → Smart Insight freigeschaltet“) erreichen wir höhere Conversion.
3. 30 Tage ohne KK wäre zu lange für ein Tool, dessen Wert sich schnell zeigt; 14 Tage erzeugen Dringlichkeit.
4. CC-required würde bei einem noch unbekannten deutschen Startup die Entry-Rate halbieren.

### 2.3 Monatlich vs. Jährlich vs. 2-Jährlich

| Intervall | Jährliche Retention | Churn | Cashflow-Effekt | Quelle |
|-----------|---------------------|-------|------------------|--------|
| Monatlich | ~41 % (ARPA < 25 $) | 8,5–12 %/Monat | schlecht | ChartMogul 2025, Baremetrics |
| Jährlich | **62 %** (ARPA < 25 $) | 3,1–7 %/Jahr | gut | ChartMogul 2025, Baremetrics |
| 2-Jährlich | **27,3 %** nach 4 Jahren aktiv (höchste Retention aller Intervalle) | sehr niedrig | sehr gut | Piano Benchmark März 2026 |

**Patrick Campbell (ProfitWell):** „The more annuals a business has, the lower their churn. Annual contracts typically have **30 % better retention** overall compared to monthlies.“ (Saastr Podcast #429)

**Entscheidung:**

- **Jährlich als Default** mit 20 % Rabatt.
- **Monatlich verfügbar** für Nutzer, die Flexibilität wollen (kein Rabatt).
- **2-Jährlich als experimentelles Intervall** mit 30 % Rabatt testen, sobald 500+ zahlende Kunden existieren. Nicht im MVP.

### 2.4 Kündigungsfristen & Churn

| Kündigungsmodell | Bewertung | Risiko/Nutzen |
|------------------|-----------|---------------|
| **Sofort-Kündigung** | Hohe Churn-Gefahr, bei Jahreszahlung rechtlich problematisch | ❌ Nicht empfohlen |
| **4 Wochen / 1 Monat zum Monatsende** | Marktstandard für monatliche SaaS-Abos | ✅ Standard für Basis/Pro monatlich |
| **3 Monate zum Jahresende** | B2B-Standard, gibt Planungssicherheit | ✅ Standard für Jahres-/Business-Abos |
| **Kündigung nur zum Periodenende** | Gängig, senkt Churn | ✅ Kombiniert mit Downgrade-Regel |

**Entscheidung:**

- Monatliche Abos: **4 Wochen Kündigungsfrist zum Monatsende**.
- Jährliche/Business-Abos: **3 Monate zum Jahresende**.
- Nach Kündigung: Account bleibt bis Periodenende aktiv, danach **gesperrt + 30 Tage Daten-Aufbewahrung**, dann DSGVO-konforme Löschung.

---

## 3. Neue Preisstruktur v3

### 3.1 Plan-Übersicht

| Plan | Preis/Monat | Preis/Jahr (20 % Rabatt) | Preis/2-Jahre (30 % Rabatt) | Wohnungen | Objekte | KI | Zielgruppe |
|------|------------|--------------------------|----------------------------|-----------|---------|----|------------|
| **Basis** | **14,90 €** | **142,56 €** (= 11,88 €/Mo) | **250,32 €** (= 10,43 €/Mo) | 5 | ∞ | Basis-KI (Beleg-Scan, Ticket-Kategorisierung, Antwort-Entwürfe) | Kleinvermieter mit 1–5 WE |
| **Pro** | **29,90 €** | **287,04 €** (= 23,92 €/Mo) | **502,32 €** (= 20,93 €/Mo) | 25 | ∞ | Volle KI (Smart Insights, Mahnungen, Mieterhöhung §558 BGB, eID, ROI mit Finanzierung) | Semi-professionelle Vermieter mit 6–25 WE |
| **Business** | **49,90 €** | **479,04 €** (= 39,92 €/Mo) | **837,12 €** (= 34,88 €/Mo) | ∞ | ∞ | Volle KI + Team (5 Nutzer inkl.), API, Custom Reports | Kleine Hausverwaltungen / 25+ WE |

> **Hinweis:** Alle Preise verstehen sich inkl. 19 % MwSt. für Endkunden in Deutschland. Netto-Preise für B2B-Verwaltungen auf Anfrage.

### 3.2 Preis-Begründung aus Konkurrenz-Analyse

| Konkurrent | Preis | Unsere Positionierung |
|------------|-------|----------------------|
| immocloud | 9,99–39,99 € netto | Wir liegen im Mittelfeld, bieten aber mehr KI |
| rentably | 0–9 € | Nicht vergleichbar — deren KI ist extern via MCP |
| hellohousing | 4,50–19,50 € | Pro 29,90 € ist Premium-Positionierung mit voller KI |
| objego | 0–12,70 € | Unser Basis 14,90 € deckt KI-Kosten + Marge |
| verwaltio | 24,90 €+ | Unser Pro 29,90 € ist direkt vergleichbar, aber mit mehr Wohnungen |
| hausify | 49 €+ | Business 49,90 € als Anker-Preis |

**Strategische Positionierung:**

- **Basis 14,90 €** ist knapp über hellohousing Starter (4,50 €) und objego Verwaltung (7,95 €), aber deutlich unter verwaltio (24,90 €). Der Preis signalisiert: „Mehr Wert als kostenlose Alternativen, aber noch erschwinglich.“
- **Pro 29,90 €** ist der **Sweet Spot** — 25 Wohnungen, volle KI, direkt konkurrenzfähig zu immocloud Manager (15,99–25,99 € netto) und verwaltio (24,90 €).
- **Business 49,90 €** dient als **Preisanker**. Durch den hohen Anker wirkt Pro 29,90 € wie ein „Schnäppchen“ (Decoy-Effekt).

### 3.3 Feature-Matrix v3

| Feature | Basis | Pro | Business |
|---------|-------|-----|----------|
| **Wohnungen** | 5 | 25 | ∞ |
| **Objekte** | ∞ | ∞ | ∞ |
| **Mieter** | ∞ | ∞ | ∞ |
| **Storage** | 5 GB | 25 GB | 100 GB |
| **Nutzer pro Account** | 1 | 1 | 5 (+5 €/weiterer) |
| Ticket Auto-Kategorisierung | ✅ | ✅ | ✅ |
| Beleg-Scan (OCR + KI) | ✅ | ✅ | ✅ |
| Antwort-Entwürfe Tickets | ✅ | ✅ | ✅ |
| Smart Insights | ❌ | ✅ | ✅ |
| KI-Mahnungen (Stufe 1–3) | ❌ | ✅ | ✅ |
| Mieterhöhung §558 BGB | ❌ | ✅ | ✅ |
| Kündigung / Abmahnung KI | ❌ | ✅ | ✅ |
| Umlagefähigkeitsprüfung | ❌ | ✅ | ✅ |
| Automatisches Mahnwesen | ❌ | ✅ | ✅ |
| Mieter-Bewerbung (Ausweis/Lohn/Schufa) | ❌ | ✅ | ✅ |
| eID-Verifikation | ❌ | 3/Monat inkl. | 10/Monat inkl. |
| ROI mit Finanzierung | ❌ | ✅ | ✅ |
| Custom Branding | ❌ | ✅ | ✅ |
| API-Zugang | ❌ | ❌ | ✅ |
| Team-Funktion / Rollen | ❌ | ❌ | ✅ |
| Priority-Support | 24h | 12h | 4h |

---

## 4. Abrechnungsintervalle — Bewertung

### 4.1 Monatlich

| Pro | Kontra |
|-----|--------|
| Niedriger Einstieg für Nutzer | 12× höhere Churn-Gefahr |
| Flexibel, vertraut für B2C | Schlechter Cashflow |
| Leichter Upsell-Test | 12 Zahlungs-Versuche pro Jahr = mehr involuntary churn |

**Empfehlung:** Angeboten, aber **nicht als Default**.

### 4.2 Jährlich (Default)

| Pro | Kontra |
|-----|--------|
| Churn sinkt um 30–75 % | Kunde muss mehr Geld auf einmal zahlen |
| Cashflow-Vorteil von bis zu 12 Monaten Umsatz im Voraus | Bei schlechtem Onboarding höherer Refund-Druck |
| 20 % Rabatt ist attraktiv, aber nicht zu aggressiv (ProfitWell: Rabatte > 20 % verdoppeln Churn) | — |

**Empfehlung:** **Default = jährlich**. UI zeigt zuerst „14,90 €/Monat, jährlich bezahlt“ und darunter „178,80 €/Jahr — 2 Monate geschenkt“.

### 4.3 2-Jährlich

| Pro | Kontra |
|-----|--------|
| Höchste Retention (Piano: 27,3 % nach 4 Jahren) | Sehr lange Bindung, Kunden zögern |
| Beste Cashflow | Refund-Risiko bei unzufriedenen Kunden |
| 30 % Rabatt ist starkes Argument | Geringe Konversionsrate |

**Empfehlung:** Ab 500+ zahlenden Kunden als **experimentelles Intervall** testen. Im MVP nicht anbieten.

### 4.4 Intervall-Vergleich anhand Pro-Plan

| Intervall | Zahlung sofort | Effektiver Preis/Monat | Jährlicher Umsatz | Churn-Risiko |
|-----------|---------------|------------------------|-------------------|--------------|
| Monatlich | 29,90 € | 29,90 € | 358,80 € | Hoch |
| Jährlich | 287,04 € | 23,92 € | 287,04 € | Mittel |
| 2-Jährlich | 502,32 € | 20,93 € | 251,16 €/Jahr | Niedrig |

> Der 2-Jährlich-Plan bringt zwar weniger jährlichen Umsatz, aber deutlich mehr Lifetime-Value durch niedrigeren Churn.

---

## 5. Free Trial — Entscheidung

### 5.1 Option A: 14 Tage mit Kreditkarte (Netflix-Style)

| Pro | Kontra |
|-----|--------|
| 48,8 % mediane Trial-to-paid Conversion (2× besser als No-CC) | Trial-Entry sinkt um ~70 % (2,5 % vs. 8,5 %) |
| Qualifizierte Leads | Höhere Reibung, besonders für deutsche Nutzer |
| Geringer Trial-Missbrauch | Weniger Datenpunkte und Feedback |

### 5.2 Option B: 30 Tage ohne Kreditkarte

| Pro | Kontra |
|-----|--------|
| Höchster Trial-Entry (8,5 %) | Konversion niedriger (18,2 % Median) |
| Nutzer erleben vollständigen Wert | Trial-Missbrauch möglich |
| Passend zu komplexem Produkt | Längere Zeit bis Umsatz |

### 5.3 Option C: 14 Tage ohne Kreditkarte (Empfohlen)

| Pro | Kontra |
|-----|--------|
| Hoher Entry (8,5 %) | Niedrigere Conversion als CC-required |
| Dringlichkeit durch kurze Frist | 14 Tage knapp für volles Onboarding |
| Geringe Reibung | — |

**Empfohlene Lösung:** **14 Tage ohne Kreditkarte** für alle zahlenden Pläne (Basis/Pro/Business). Zusätzlich:

- **Achievement-basierte Trial-Momente**: Wenn Nutzer z. B. 3 Belege gescannt haben, wird ein „Pro-Feature-Preview" freigeschaltet (z. B. KI-Mahnung einmalig testen).
- **Trial-Reminder**: Tag 3 (Quick-Win), Tag 7 (Hälfte), Tag 12 (2 Tage vor Ablauf), Tag 14 (Ablauf + Downgrade-Info).
- **Kein dauerhafter Free-Plan nach Ablauf**: Nach 14 Tagen ohne Zahlung → Account gesperrt, 30 Tage Daten-Aufbewahrung, dann Löschung.

---

## 6. Kündigungsfristen & Account-Sperre

### 6.1 Empfohlene Kündigungsfristen

| Plan / Intervall | Kündigungsfrist | Wirksamkeit |
|------------------|-----------------|-------------|
| Basis/Pro monatlich | 4 Wochen zum Monatsende | Marktstandard, rechtlich unbedenklich |
| Basis/Pro jährlich | 3 Monate zum Jahresende | B2B-Standard, Planungssicherheit |
| Business | 3 Monate zum Jahresende | Gewerblich/Kommerziell angemessen |

### 6.2 Verhalten nach Kündigung

| Phase | Aktion | Dauer |
|-------|--------|-------|
| **Aktiv bis Periodenende** | Nutzer hat vollen Zugriff | Bis zum Ablaufdatum |
| **Sperrung nach Periodenende** | Login nicht mehr möglich, Daten gesperrt | Ab Periodenende |
| **Aufbewahrung** | Daten werden nicht gelöscht, aber Account ist gesperrt | **30 Tage** |
| **Löschung** | DSGVO-konforme Löschung nach Aufbewahrungsfristen | Nach 30 Tagen |

**Kommunikation:**

- E-Mail bei Kündigung: „Ihr Abo endet am [Datum]. Sie haben bis dahin weiterhin Zugriff. Danach wird Ihr Account für 30 Tage gesperrt, damit Sie Ihre Daten exportieren können. Nach 30 Tagen löschen wir Ihre Daten DSGVO-konform.“
- Innerhalb der 30 Tage: Nutzer kann Abo jederzeit reaktivieren (kein Datenverlust).

### 6.3 Vergleich Kündigungsmodelle

| Modell | Churn-Effekt | Rechtliche Risiken | Empfehlung |
|--------|--------------|-------------------|------------|
| Sofort kündbar | Sehr hoher Churn | Gering | ❌ Nur für monatlich in Startup-Phase testen |
| 4 Wochen | Standard | Gering | ✅ Monatlich |
| 3 Monate zum Jahresende | Niedrigster Churn | Standard B2B | ✅ Jährlich / Business |
| Keine Kündigung möglich (starre Bindung) | Geringster Churn, aber schlechte Reviews / Rechtsrisiken | Hoch (AGB-Recht) | ❌ Nicht empfohlen |

---

## 7. Upsell-Regeln

### 7.1 Grundprinzipien

| Regel | Umsetzung |
|-------|-----------|
| **Kein Upgrade-Trial** | Wenn ein Nutzer auf Pro/Business upgraden will, zahlt er sofort. Keine 7-Tage-Testversion für höhere Pläne. |
| **Upgrade sofort mit Proration** | Upgrade ist sofort wirksam. Stripe berechnet die Restlaufzeit anteilig (Proration). |
| **Downgrade zum Periodenende** | Downgrade wird erst am Ende der aktuellen Periode wirksam. Keine Rückerstattung für bereits bezahlte Perioden. |
| **Keine sofortige Leistungseinschränkung bei Downgrade** | Solange die aktuelle Periode läuft, bleiben alle Features aktiv. |
| **Nach Kündigung: Account gesperrt + 30 Tage Aufbewahrung** | Kein automatischer Free-Plan mehr. Account wird gesperrt, Daten 30 Tage aufbewahrt. |

### 7.2 Upgrade-Beispiel Basis → Pro (monatlich)

- Nutzer zahlt 14,90 €/Monat, aktuelle Periode läuft noch 10 Tage.
- Upgrade auf Pro (29,90 €/Monat).
- Stripe berechnet: 10 Tage Basis zu viel gezahlt = ~4,97 € Gutschrift.
- Neue Pro-Gebühr für restliche 20 Tage = ~19,93 €.
- Sofortige Differenzbelastung = ~14,96 €.
- Ab nächster Periode: 29,90 €/Monat.

### 7.3 Downgrade-Beispiel Pro → Basis (jährlich)

- Nutzer hat Pro für 287,04 €/Jahr bezahlt, noch 6 Monate läuft.
- Downgrade wird gewünscht.
- Keine Rückerstattung.
- Downgrade wirksam in 6 Monaten: automatischer Wechsel auf Basis (142,56 €/Jahr).
- Bis dahin: alle Pro-Features verfügbar.

### 7.4 Upsell-Trigger im Produkt

| Trigger | Hinweis | Zielplan |
|---------|---------|----------|
| 6. Wohnung anlegen | „Im Basis-Plan sind 5 Wohnungen inkludiert. Upgrade auf Pro für 25 Wohnungen." | Pro |
| KI-Mahnung öffnen | „KI-Mahnungen sind ab Pro verfügbar." | Pro |
| 4. eID-Verifikation | „Im Pro-Plan sind 3 eIDs/Monat inkludiert. Weitere für 2 €/Stück oder Upgrade auf Business." | Business |
| Team-Mitglied einladen | „Mehrere Nutzer sind ab Business verfügbar." | Business |
| ROI-Dashboard öffnen | „ROI mit Finanzierung ist ab Pro verfügbar." | Pro |

---

## 8. Zahlungsmethoden-Bewertung

### 8.1 Akzeptierte Methoden

| Methode | Gebühr | Bewertung |
|---------|--------|-----------|
| **Kreditkarte** | **1,5 % + 0,25 €** (Standard-EEA-Karten) | Standard, hohe Conversion, Apple Pay / Google Pay inkludiert |
| **SEPA-Lastschrift / Banktransfer** | **0,5 %** | Günstigste Methode, DACH-wichtig, ideal für wiederkehrende Zahlungen |
| **PayPal** | **2–3 % + 0,35 €** | Bekannt, Vertrauen, aber teuer; optional anbieten |
| **Rechnung** | ❌ Nicht angeboten | Hoher manueller Aufwand, Zahlungsausfall-Risiko, schlechter Cashflow |

> **Quelle Stripe Deutschland (2025):** Standard-EEA-Karten 1,5 % + 0,25 €, SEPA Bank Transfer 0,5 % (capped 5 €), PayPal über Stripe 0,2 % + 0,10 € + PayPal-Gebühren. Die vom Nutzer genannten PayPal-Gebühren (2–3 % + 0,35 €) decken die realen PayPal-Kosten ab.

### 8.2 Gebühren-Impact auf Marge pro Plan

| Plan | Brutto | Kreditkarte (1,5 % + 0,25 €) | Netto | Marge nach Karte* |
|------|--------|------------------------------|-------|-------------------|
| Basis | 14,90 € | 0,47 € | 14,43 € | 96,85 % |
| Pro | 29,90 € | 0,70 € | 29,20 € | 97,66 % |
| Business | 49,90 € | 1,00 € | 48,90 € | 98,00 % |

| Plan | Brutto | SEPA (0,5 %) | Netto | Marge nach SEPA* |
|------|--------|----------------|-------|------------------|
| Basis | 14,90 € | 0,07 € | 14,83 € | 99,53 % |
| Pro | 29,90 € | 0,15 € | 29,75 € | 99,50 % |
| Business | 49,90 € | 0,25 € | 49,65 € | 99,50 % |

\* Marge = Netto / Brutto. Ohne Berücksichtigung von KI/Hosting-Kosten.

### 8.3 Empfehlung zur Zahlungsmethode

- **Default-Reihenfolge im Checkout:** Apple Pay / Google Pay → Kreditkarte → SEPA → PayPal.
- **SEPA pushen** für Jahreszahlungen (geringste Gebühren).
- **PayPal optional** anbieten, aber mit Hinweis, dass Karte/SEPA schneller sind.
- **Keine Rechnung** — das blockiert Cashflow und erfordert Mahnwesen für Kundenmahung.

---

## 9. BWL-Bewertung — MRR, CLV, Churn, Cashflow, Break-even, CAC, LTV, Upsell

### 9.1 Annahmen für die Modellrechnung

| Parameter | Wert | Begründung |
|-----------|------|-------------|
| Durchschnittlicher ARPU | **25,00 €/Monat** | Gewichtetes Mittel aus Plan-Mix (50 % Basis, 40 % Pro, 10 % Business) |
| Jährlich-Anteil | **60 %** | Ziel nach 12 Monaten (Start: 30 %) |
| Monatlich-Anteil | **40 %** | — |
| Monatliche Churn-Rate | **5 %** | SMB-SaaS-Durchschnitt (Baremetrics: 3–5 % ideal) |
| Jährliche Churn-Rate | **25 %** | Entspricht ~2,3 % monatlich |
| Brutto-Marge | **85 %** | Nach KI/Hosting/Stripe-Kosten |
| CAC | **75 €** | Ziel für deutschen Markt (Content/Ads/Partnerschaften) |
| Fixkosten/Monat | **24 €** | MVP-Proxmox-Hosting, Resend-E-Mail, MaxMind etc. |

### 9.2 MRR & ARR

| Szenario | Kunden | MRR | ARR |
|----------|--------|-----|-----|
| Break-even | 2 | 50 € | 600 € |
| Ziel Monat 6 | 50 | 1.250 € | 15.000 € |
| Ziel Monat 12 | 200 | 5.000 € | 60.000 € |
| Ziel Monat 24 | 500 | 12.500 € | 150.000 € |

### 9.3 Kunden-Lebensdauer (LT) & Churn

| Churn | Durchschnittliche Lebensdauer (Monate) | Formel |
|-------|----------------------------------------|--------|
| 5 %/Monat | **20 Monate** | LT = 1 / 0,05 |
| 2,3 %/Monat (jährlich) | **43 Monate** | LT = 1 / 0,023 |

### 9.4 Customer Lifetime Value (CLV / LTV)

Formel: **LTV = (ARPU × Brutto-Marge) / Monatlicher Churn**

| Churn-Szenario | Rechnung | LTV |
|----------------|----------|-----|
| Monatlich 5 % | (25 € × 0,85) / 0,05 | **425 €** |
| Jährlich (2,3 %/Mo) | (25 € × 0,85) / 0,023 | **913 €** |
| Mit Upsell (+20 % Expansion) | (30 € × 0,85) / 0,05 | **510 €** |

### 9.5 CAC & LTV:CAC Ratio

| Szenario | CAC | LTV | LTV:CAC | Payback-Period (Monate) |
|----------|-----|-----|---------|-------------------------|
| Monatlich 5 % Churn | 75 € | 425 € | **5,7 : 1** | 3,5 Monate |
| Jährlich 2,3 % Churn | 75 € | 913 € | **12,2 : 1** | 3,5 Monate |
| Mit Upsell | 75 € | 510 € | **6,8 : 1** | 2,9 Monate |

> **Benchmark:** Gesundes SaaS-Unit-Economics erfordert LTV:CAC ≥ 3:1. Unsere Zielwerte liegen deutlich darüber.

### 9.6 Break-even-Analyse

| Plan | Brutto/Monat | Variable Kosten/Monat (KI+Hosting+Zahlung) | Deckungsbeitrag/Monat | Kunden für Break-even (Fixkosten 24 €) |
|------|--------------|-------------------------------------------|------------------------|----------------------------------------|
| Basis | 14,90 € | ~1,50 € | 13,40 € | **1,8 Kunden** |
| Pro | 29,90 € | ~1,80 € | 28,10 € | **0,9 Kunden** |
| Business | 49,90 € | ~2,50 € | 47,40 € | **0,5 Kunden** |
| Gewichteter Mix | 25,00 € | ~1,70 € | 23,30 € | **1,0 Kunde** |

> **Fazit:** Bereits **1 zahlender Kunde** im gewichteten Mix deckt die Fixkosten. Das Modell ist extrem robust.

### 9.7 Cashflow-Effekt durch Jahreszahlung

| Szenario | Monatlicher Cashflow | Jährlicher Cashflow pro Kunde | Vorteil Jahreszahlung |
|----------|----------------------|-------------------------------|----------------------|
| 1 Kunde Pro monatlich | 29,90 €/Mo | 358,80 €/Jahr | — |
| 1 Kunde Pro jährlich | 287,04 € sofort | 287,04 €/Jahr | +~12 Monate Cashflow im Voraus |
| 100 Kunden Pro, 60 % jährlich | — | ~25.800 €/Jahr sofort | Deutlich bessere Planungssicherheit |

**Patrick Campbell (ProfitWell):** SaaS-Unternehmen mit überwiegend jährlichen Verträgen haben **30–50 % mehr Working Capital** als monatlich abrechnende Unternehmen.

### 9.8 Upsell-Pfad & Expansion-MRR

| Upsell | Anteil der Kunden | Zusätzlicher MRR | Impact |
|--------|-------------------|-------------------|--------|
| Basis → Pro | 25 % | +15,00 € | Hoch |
| Pro → Business | 10 % | +20,00 € | Mittel |
| Extra Wohnung (1 €/WE) | 15 % | +1–5 € | Niedrig, aber stabil |
| Extra eID (2 €/Stück) | 5 % | +2–10 € | Sehr niedrig |

**Net Revenue Retention (NRR) Ziel:** 110–115 % durch Upsell und geringen Churn.

### 9.9 Sensitivitätsanalyse Churn

| Monatlicher Churn | LTV | LTV:CAC (CAC=75 €) | ARR-Verlust bei 100 Kunden/Jahr |
|-------------------|-----|--------------------|--------------------------------|
| 3 % | 708 € | 9,4 : 1 | ~10.800 € |
| 5 % | 425 € | 5,7 : 1 | ~18.000 € |
| 8 % | 266 € | 3,5 : 1 | ~28.800 € |
| 10 % | 213 € | 2,8 : 1 | ~36.000 € |

> **Fazit:** Selbst bei 8 % monatlichem Churn (schlecht für SMB-SaaS) liegen wir noch über dem gesunden 3:1-LTV:CAC. Das Modell ist churn-resistent.

---

## 10. Vergleich v2 → v3 in Zahlen

| Kennzahl | v2 (mit Free) | v3 (ohne Free) | Delta |
|----------|---------------|----------------|-------|
| Einstiegspreis | 0 € | 14,90 € | +14,90 € |
| Durchschnittlicher ARPU | ~12 € (inkl. Free) | **25 €** | +108 % |
| Break-even-Kunden | 3 zahlende | **1 zahlender** | -67 % |
| Churn-Risiko durch Free-Plan | Hoch (Support-Kosten) | Niedrig | — |
| Trial-to-paid Entry | 30 Tage No-CC | 14 Tage No-CC | Fokus auf Urgency |
| Cashflow | Schwach (viele Free) | Stark (direkte Zahlung) | — |
| LTV (gewichtet) | ~180 € | **425 €** | +136 % |

---

## 11. Implementierungs-Empfehlungen

### 11.1 MVP-Umsetzung

1. **3 Pläne** sofort live: Basis/Pro/Business.
2. **Trial**: 14 Tage ohne KK für alle Pläne.
3. **Intervall**: Monatlich + Jährlich (Default = jährlich, 20 % Rabatt).
4. **Zahlungsmethoden**: Kreditkarte, SEPA, PayPal via Stripe.
5. **Upsell-Regeln**: Upgrade sofort mit Proration, Downgrade Periodenende, nach Kündigung Sperre + 30 Tage Aufbewahrung.
6. **Kündigungsfristen**: 4 Wochen zum Monatsende (monatlich), 3 Monate zum Jahresende (jährlich/Business).

### 11.2 A/B-Tests nach Launch

| Test | Ziel | Priorität |
|------|------|-----------|
| 14 Tage vs. 30 Tage Trial | Optimale Conversion | Hoch |
| 20 % vs. 25 % Jahresrabatt | Balance Conversion vs. Marge | Hoch |
| Pro als Default vs. Basis als Default | ARPU maximieren | Mittel |
| SEPA als Default vs. Karte als Default | Gebühren senken | Mittel |
| 2-Jährlich-Intervall testen | Churn senken | Niedrig (ab 500 Kunden) |

### 11.3 Risiken & Gegenmaßnahmen

| Risiko | Wahrscheinlichkeit | Gegenmaßnahme |
|--------|--------------------|---------------|
| Nutzer vermissen Free-Plan | Mittel | Starke 14-Tage-Trial + Onboarding-Quick-Wins |
| Hoher Churn durch Preiserhöhung | Mittel | 20 % Jahresrabatt als Anker, flexible monatliche Option |
| Konkurrenz (rentably/objego) unterbietet | Hoch | KI-USP kommunizieren, nicht auf Preis konkurrieren |
| Zahlungsausfälle bei Jahreszahlung | Niedrig | Stripe Smart Retries, Dunning-E-Mails |
| Rechtliche Kündigungsfristen | Niedrig | AGB durch Anwalt prüfen, 3-Monats-Frist für Jahresabo |

---

## 12. Quellenverzeichnis

1. **ProfitWell / Patrick Campbell:** Annual vs. Monthly Plans — learn.profitwell.com/resources/annual-plans
2. **Baremetrics:** Annual vs Monthly Pricing Retention — baremetrics.com/blog/annual-vs-monthly-pricing-better-retention
3. **ChartMogul:** 2025 SaaS Billing Report — chartmogul.com/reports/saas-billing-report/
4. **Piano Benchmark (März 2026):** Monthly vs. Annual Subscriptions — piano.io/resources/monthly-vs-annual-subscriptions
5. **RevenueCat:** State of Subscription Apps 2024/2025 — revenuecat.com/state-of-subscription-apps-2024
6. **SaaS Pricing Pages Repo / Gauthier:** Pricing psychology, decoy effect, trial benchmarks — github.com/bdebout/gauthier-quiz-funnel-expert
7. **SaaSfactor:** 2025 SaaS Pricing Playbook — saasfactor.co/blogs/the-2025-saas-pricing-playbook
8. **Tanstackship:** SaaS Pricing Psychology — tanstackship.com/blog/saas-pricing-psychology
9. **Buildology:** SaaS Pricing Benchmarks 2025 — buildology.ai/tools/saas-pricing-benchmarks/
10. **Stripe Germany Pricing:** stripe.com/en-de/pricing
11. **Churn.io:** State of Subscription Fatigue — churn.io/blog/state-of-subscription-fatigue-churn
12. **Saastr Podcast #429:** Patrick Campbell on Retention — saastr.com/saastr-podcast-429-with-profitwell-founder-ceo-patrick-campbell
13. **MietVerwaltung Competitor Deep-Dive 2026:** /root/mietverwaltung/competitor-deep-dive-2026.md
14. **MietVerwaltung Abo-Abschluss-Prozess-Konzept:** /root/mietverwaltung/Abo-Abschluss-Prozess-Konzept.md

---

## 13. Preispsychologie und BWL-Optimierung

> Dieser Abschnitt analysiert, warum der „Beliebteste Plan“ nicht der kundenfreundlichste, sondern der **für uns (BWL/VWL) profitabelste Plan** sein soll — und wie wir das verschleiern, ohne dass der Kunde es merkt.

---

### 13.1 BWL-Analyse der drei Pläne

#### 13.1.1 Marge pro Plan

| Plan | Brutto/Monat | Variable Kosten/Monat | Deckungsbeitrag/Monat | Marge % |
|------|--------------|------------------------|------------------------|---------|
| **Basis** | 14,90 € | 1,37 € | **13,53 €** | **90,8 %** |
| **Pro** | 29,90 € | 2,30 € | **27,60 €** | **92,3 %** |
| **Business** | 49,90 € | 3,70 € | **46,20 €** | **92,6 %** |

**Kostenaufschlüsselung (geschätzt):**

| Plan | Zahlungsgebühr (Karte 1,5 % + 0,25 €) | KI-Nutzung | Hosting/Storage/Support | Summe |
|------|----------------------------------------|------------|-------------------------|-------|
| Basis | 0,47 € | 0,40 € | 0,50 € | 1,37 € |
| Pro | 0,70 € | 0,90 € | 0,70 € | 2,30 € |
| Business | 1,00 € | 1,50 € | 1,20 € | 3,70 € |

**Ergebnis:** Business hat den höchsten absoluten Deckungsbeitrag (46,20 €), gefolgt von Pro (27,60 €) und Basis (13,53 €). Alle Pläne haben extrem hohe Margen (90 %+).

#### 13.1.2 Churn-Rate pro Plan

| Plan | Geschätzte monatliche Churn-Rate | Begründung |
|------|----------------------------------|------------|
| **Basis** | **7 %/Monat** | Preissensibel, kleine Vermieter, wenig eingebettete Daten, schneller Wechsel zu billigeren Alternativen |
| **Pro** | **4 %/Monat** | Optimaler Sweet Spot: genug Value (volle KI), aber noch erschwinglich, stärkere Bindung durch ROI-Dashboard |
| **Business** | **2 %/Monat** | Professionelle Nutzer, hoher Switching-Cost, tiefere Integration, mehr Nutzer/Prozesse |

**Quelle/Benchmark:** Baremetrics/ProfitWell geben 3–5 %/Monat als idealen Bereich für SMB-SaaS an. Basis liegt darüber, weil der Einstiegssegment preissensibler ist; Business darunter, weil B2B-Kunden länger bleiben.

#### 13.1.3 Customer Lifetime Value (CLV / LTV) pro Plan

Formel: **LTV = Deckungsbeitrag / Monatliche Churn-Rate**

| Plan | Deckungsbeitrag/Monat | Churn/Monat | LTV |
|------|------------------------|-------------|-----|
| **Basis** | 13,53 € | 7 % | **193 €** |
| **Pro** | 27,60 € | 4 % | **690 €** |
| **Business** | 46,20 € | 2 % | **2.310 €** |

**Ergebnis:** Business hat den höchsten LTV, gefolgt von Pro. Aber LTV allein ist nicht entscheidend — es zählt **LTV × Volumen × Conversion-Rate**.

#### 13.1.4 Einfachheit zu verkaufen (Conversion-Rate)

| Plan | Geschätzte Trial-to-paid Conversion | Begründung |
|------|-------------------------------------|------------|
| **Basis** | **25 %** | Niedrigster Einstieg, aber Kunden haben weniger „Skin in the Game“ und churnen schneller |
| **Pro** | **20 %** | Höherer Preis senkt Entry leicht, aber Conversion ist stabil, weil Value klar ist (volle KI) |
| **Business** | **8 %** | Höchster Preis, nur für größere Portfolios/Hausverwaltungen relevant, längerer Sales-Cycle |

**Wichtig:** Basis hat zwar die höchste Conversion, aber die Kunden sind weniger wertvoll (niedriger LTV, höherer Churn). Business-Kunden sind extrem wertvoll, aber es gibt weniger davon.

#### 13.1.5 Der profitabelste Plan — aus BWL-Sicht

| Plan | LTV | Absoluter Deckungsbeitrag | Churn | Conversion | Skalierbarkeit |
|------|-----|---------------------------|-------|------------|----------------|
| Basis | 193 € | 13,53 €/Mo | Hoch (7 %) | Hoch (25 %) | Hoch |
| **Pro** | **690 €** | 27,60 €/Mo | Mittel (4 %) | Mittel (20 %) | **Sehr hoch** |
| Business | 2.310 € | 46,20 €/Mo | Niedrig (2 %) | Niedrig (8 %) | Niedrig |

**BWL-Fazit:** 

- **Business** ist der profitabelste *Einzelkunde*.
- **Pro** ist der profitabelste *Plan auf Unternehmensebene*, weil er die beste Balance aus **hohem LTV (690 €), hohem Deckungsbeitrag (27,60 €), akzeptablem Churn (4 %) und guter Skalierbarkeit** hat.
- **Basis** ist wichtig als **Anker und Acquisition-Tool**, aber kein Profit-Motor.

**Der „Beliebteste Plan“ sollte daher Pro sein.**

---

### 13.2 Anchor-Decoy-Positionierung

#### 13.2.1 Die drei Rollen

| Rolle | Plan | Preis | Funktion im Kundenkopf | Funktion für uns |
|-------|------|-------|------------------------|------------------|
| **Anchor (Anker)** | Basis | 14,90 € | „Das ist der Einstieg — günstig, aber limitiert“ | Senkt die Preisschwelle, macht Pro wie kleinen Aufschlag |
| **Target (Ziel)** | Pro | 29,90 € | „Das wählen die meisten — volle KI, fairer Preis“ | **Höchste Kombination aus Marge, LTV und Volumen** |
| **Decoy (Ablenkung)** | Business | 49,90 € | „Das ist für Profis/Hausverwaltungen — mir reicht Pro“ | Macht Pro wie den „vernünftigen Mittelweg“ aussehen |

#### 13.2.2 Warum diese Positionierung funktioniert

1. **Anchor-Effekt (Basis 14,90 €):** Der Kunde sieht zuerst 14,90 €. Wenn er dann auf Pro 29,90 € schaut, empfindet er den Aufschlag als „nur doppelt so viel“ — obwohl er **5× mehr Wohnungen und die komplette KI** bekommt. Der Anker verankert die Preiswahrnehmung unten.

2. **Decoy-Effekt (Business 49,90 €):** Der hohe Business-Preis macht Pro 29,90 € psychologisch zum „sicheren Mittelweg“. Der Kunde denkt: „Ich bin nicht so groß wie eine Hausverwaltung, also brauche ich nicht Business. Aber Basis ist mir zu limitiert. Pro ist genau richtig.“

3. **Compromise-Effekt:** Studien zeigen, dass Konsumenten in einer 3-Tier-Struktur tendenziell die **mittlere Option** wählen, weil sie weder „billig/armselig“ noch „teuer/überdimensioniert“ wirken wollen. Pro ist dieser Kompromiss.

4. **Social Proof („Beliebtester Plan“):** Der Badge suggeriert, dass andere Kunden bereits die „richtige“ Entscheidung getroffen haben. Das reduziert Entscheidungsangst und lenkt zum Target-Plan.

#### 13.2.3 Preis-Abstände analysieren

| Abstand | Wert | Psychologische Wirkung |
|---------|------|------------------------|
| Basis → Pro | +15,00 € (+100 %) | Großer Sprung, aber durch Feature-Dichte gerechtfertigt |
| Pro → Business | +20,00 € (+67 %) | Moderater Sprung, signalisiert Premium ohne abschreckend |
| Basis → Business | +35,00 € (+235 %) | Extremer Sprung, stärkt die Positionierung von Pro als Mittelweg |

**Optimierung:** Der Abstand Basis → Pro ist bewusst groß, damit Pro wie ein „Upgrade wert“ wirkt. Der Abstand Pro → Business ist kleiner, damit Business nicht völlig unrealistisch wirkt, aber trotzdem als Decoy dient.

---

### 13.3 Wie wir verschleiern, dass Pro unser profitabelster Plan ist

#### 13.3.1 Sprache und Badge

| Technik | Beispiel | Warum es funktioniert |
|---------|----------|------------------------|
| **„Beliebtester Plan“** statt „Bester Plan“ | „Beliebtester Plan“ | Impliziert sozialen Beweis, nicht Manipulation |
| **„Bestes Preis-Leistungs-Verhältnis“** | „Best Value“-Badge | Klingt objektiv, basierend auf Features, nicht auf unserer Marge |
| **Feature-basierte Argumentation** | „25 Wohnungen + volle KI“ | Der Kunde rationalisiert die Wahl selbst |
| **Segment-Framing** | „Für Vermieter mit 6–25 Wohnungen" | Passt auf viele Kunden, fühlt sich zugeschnitten an |

#### 13.3.2 Visuelle Gestaltung

| Element | Umsetzung | Effekt |
|---------|-----------|--------|
| **Pro-Karte hervorheben** | Dunklerer Rahmen, leichte Vergrößerung, Schatten | Zieht den Blick sofort |
| **Badge oben** | „Beliebtester Plan“ in Navy-Blau | Signaler für „das wählen andere auch“ |
| **CTA anders formulieren** | Basis: „Starten“, Pro: „Jetzt loslegen“, Business: „Kontaktieren“ | Pro bekommt den aktivsten CTA |
| **Jährlicher Preis prominent** | „287,04 €/Jahr — 2 Monate geschenkt" | Verstärkt Wertwahrnehmung ohne Marge zu zerstören |

#### 13.3.3 Testimonials und Social Proof

- „Ich habe mit Basis angefangen, aber schnell auf Pro gewechselt — die KI-Mahnungen allein sparen mir Stunden pro Monat.“
- „Pro ist der Sweet Spot. Ich habe 12 Wohnungen und nutze fast alle KI-Features." 
- **Wichtig:** Kein Testimonial für Business, es sei denn von einer realen Hausverwaltung — sonst wirkt es künstlich.

#### 13.3.4 Was wir NIE sagen

- „Pro hat die höchste Marge."
- „Wir verdienen am meisten an Pro."
- „Business ist nur dazu da, Pro günstig aussehen zu lassen."
- „Basis ist ein Verlustgeschäft."

---

### 13.4 Preis-Endung: 14,90 vs. 15,00 vs. 12,90

#### 13.4.1 Psychologische Wirkung

| Endung | Wirkung | Für unseren Markt |
|--------|---------|-------------------|
| **14,90 €** | Charm Pricing, unter 15-€-Schwelle, Wert-Signal | ✅ Optimal für Prosumer/Kleinvermieter |
| **15,00 €** | Runder Preis, Signal für Qualität/B2B, aber verliert Charm-Effekt | ⚠️ Für Business-Plan denkbar, nicht für Basis/Pro |
| **12,90 €** | Billig-Signal, unter 13-€-Schwelle, aber möglicherweise zu "billig" | ❌ Vermindert wahrgenommenen Wert, schmälert Marge |

#### 13.4.2 BWL/VWL-Analyse der Endungen

| Endung | Preis | Geschätzte Nachfrage-Änderung | Geschätzter Umsatz-Impact |
|--------|-------|-------------------------------|--------------------------|
| 12,90 € | -13,4 % gegenüber 14,90 € | +5–10 % Conversion | -5–8 % Umsatz (Preiselastizität < 1) |
| 14,90 € | Basispreis | Basisline | Basisline |
| 15,00 € | +0,7 % gegenüber 14,90 € | -2–3 % Conversion | -1–2 % Umsatz |

**VWL-Logik:** Die Nachfrage nach Vermieter-Software ist **preisinlastisch** (|ε| < 1). Eine Preissenkung um 13,4 % steigert die Nachfrage nur um 5–10 % — der Umsatz sinkt also. Eine Preiserhöhung um 0,7 % (14,90 → 15,00) senkt die Nachfrage nur leicht, aber verliert den Charm-Effekt.

**Empfehlung:** **14,90 / 29,90 / 49,90** für alle Pläne. Die ,90-Endung ist der psychologische Standard im DACH-Markt und bewahrt die Wahrnehmung als „fairer Preis".

---

### 13.5 Good-Better-Best Pattern

#### 13.5.1 Die drei Stufen

| Stufe | Plan | Rolle | Preispsychologische Funktion |
|-------|------|-------|------------------------------|
| **Good** | Basis 14,90 € | Akzeptabler Einstieg | „Ich bekomme etwas für mein Geld" |
| **Better** | Pro 29,90 € | **Target-Plan** | „Das ist das beste Preis-Leistungs-Verhältnis" |
| **Best** | Business 49,90 € | Premium/Decoy | „Für Profis, ich brauche das noch nicht" |

#### 13.5.2 Warum „Better“ der Verkaufsfokus ist

Das Good-Better-Best-Pattern funktioniert, weil Kunden die **mittlere Stufe** als „vernünftigen Kompromiss" wahrnehmen. Wir nutzen das bewusst:

- **Good (Basis)** muss attraktiv genug sein, um nicht abzuschrecken, aber limitiert genug, um ein Upgrade-Begehren zu wecken.
- **Better (Pro)** muss das „volle Erlebnis" bieten — in unserem Fall: volle KI, 25 Wohnungen, ROI-Dashboard. Das ist der Plan, der unseren USP am besten verkauft.
- **Best (Business)** muss überzeugend genug wirken, um Pro als Mittelweg zu positionieren, aber nicht so attraktiv, dass viele Kunden tatsächlich kaufen.

**Kontrolle der Mix-Ziele:**

| Plan | Ziel-Anteil am Umsatz | Ziel-Anteil an Kunden |
|------|----------------------|----------------------|
| Basis | 20 % | 35 % |
| **Pro** | **60 %** | **50 %** |
| Business | 20 % | 15 % |

---

### 13.6 VWL- und Verhaltensoekonomische Aspekte

#### 13.6.1 Preiselastizität und Marktposition

| Aspekt | Analyse | Konsequenz |
|--------|---------|------------|
| **Preiselastizität** | Inelastisch (|ε| ≈ 0,5–0,8) für Pro/Business; etwas elastischer für Basis | Keine aggressive Preissenkung nötig; Value-Selling statt Preiskampf |
| **Monopolistische Konkurrenz** | Wir differenzieren durch KI, DSGVO-Anonymisierung, ROI-Dashboard → Produkt differenziert | Wir haben begrenzte Preissetzungsmacht, müssen aber nicht am Preis konkurrieren |
| **Marktgleichgewicht** | Unsere Preise liegen über objego/rentably, aber unter immoware24/verwaltio → Gleichgewicht im Mittelklasse-Segment | Positionierung als „Premium-Standard" für Kleinvermieter |
| **Grenzkosten ≈ 0** | SaaS-Margen 90 %+ | Jeder zusätzliche Kunde ist fast reiner Gewinn → Fokus auf Acquisition + Retention |

#### 13.6.2 Verhaltensoekonomische Hebel

| Effekt | Anwendung bei uns | Ziel |
|--------|-------------------|------|
| **Loss Aversion** | 14-Tage-Trial: Nutzer erlebt Pro-Features, Verlust beim Ablauf fühlt sich größer an als der Gewinn von 14,90 € | Conversion steigern |
| **Endowment Effect** | Nutzer legt Mieter, Objekte, Belege an → fühlt sich „Eigentümer" der Daten → höhere Bereitschaft zu zahlen | Churn senken |
| **Status Quo Bias** | Jährlich als Default, automatische Verlängerung, Downgrade erst Periodenende | Retention erhöhen |
| **Anchoring** | Basis 14,90 € als Anker, Business 49,90 € als Decoy | Pro 29,90 € als „natürliche Wahl" positionieren |
| **Social Proof** | „Beliebtester Plan"-Badge, Testimonials, Live-Statistik „X Vermieter nutzen Pro" | Entscheidungsangst reduzieren |
| **Scarcity/Exclusivity** | „Frühbucher-Rabatt für die ersten 100 Kunden" | Dringlichkeit erzeugen |

#### 13.6.3 Status Quo Bias und jährliche Verträge

Der Status-Quo-Bias ist einer der stärksten Hebel im Abo-Geschäft:

- **Jährlich als Default:** Der Kunde muss aktiv auf „monatlich" umschalten. Viele lassen es bei jährlich.
- **Automatische Verlängerung:** Der Kunde muss aktiv kündigen. Jede Reibung in diesem Prozess erhöht Retention.
- **Downgrade erst Periodenende:** Auch wenn der Kunde downgrade will, behält er die Features bis zum Ende der Periode — das reduziert den „sofortigen Verlust".

**Achtung:** Diese Mechanismen müssen rechtlich transparent sein (§ 307 BGB, AGB-Recht), aber psychologisch wirksam bleiben.

---

### 13.7 Fazit: Der „Beliebteste Plan" ist Pro — und das ist BWL-optimal

| Kriterium | Gewinner | Wert |
|-----------|----------|------|
| Höchste absolute Marge/Kunde | Business | 46,20 €/Mo |
| Bestes Verhältnis Marge × Volumen × Churn | **Pro** | 27,60 € × 20 % Conv. × 4 % Churn |
| Höchster LTV | Business | 2.310 € |
| Bestes Verhältnis LTV × Conversion | **Pro** | 690 € × 20 % |
| Niedrigster Churn | Business | 2 %/Mo |
| Höchste Conversion | Basis | 25 % |
| **BWL-optimaler „Beliebtester Plan“** | **Pro** | Beste Kombination aus Profitabilität und Skalierbarkeit |

**Positionierung:**

- **Basis = Anchor** (macht Pro günstig erscheinen)
- **Pro = Target** (unser profitabelster plan auf Unternehmensebene, mit „Beliebtester Plan"-Badge)
- **Business = Decoy** (macht Pro zum vernünftigen Mittelweg und fängt Premium-Kunden ab)

**Preis-Endung:** 14,90 / 29,90 / 49,90 (Charm Pricing, DACH-Standard).

**Pattern:** Good (Basis) — Better (Pro, markiert) — Best (Business).

---

## 14. Offene Punkte

1. **Jahresrabatt**: 20 % final oder A/B-Test mit 25 %?
2. **2-Jährlich**: Ab wie vielen Kunden testen?
3. **Business-Plan**: Brauchen wir ihn sofort im MVP oder erst nach 100 zahlenden Kunden?
4. **PayPal**: Wirklich anbieten oder zunächst nur Karte + SEPA?
5. **Trial-Länge**: 14 Tage starten und nach 100 Trials auf 30 Tage testen?
6. **Badge-Formulierung**: „Beliebtester Plan", „Bestes Preis-Leistungs-Verhältnis" oder „Most Popular"?
7. **Pro-Preis**: Sollten wir Pro auf 24,90 € testen, um näher an verwaltio zu sein, oder 29,90 € halten?
