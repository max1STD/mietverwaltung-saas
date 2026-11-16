# Mehrwert-Scoring: Paperless-ngx vs. Eigenbau-DMS

**Datum:** 16. November 2026  
**Autor:** Hermes Agent  
**Scope:** Objektive Bewertung, wie viel zusätzlichen Wert Paperless-ngx für das Mietverwaltung-SaaS gegenüber einer Eigenentwicklung bringt.

---

## 1. Bewertungsmethode

Jede Funktion wird auf einer Skala von **0–10** bewertet:

- **0–3:** Geringer oder kein Mehrwert, leicht selbst baubar.
- **4–6:** Moderater Mehrwert, Eigenbau ist noch vertretbar.
- **7–10:** Hoher Mehrwert, Eigenbau wäre deutlich aufwändiger oder technisch riskant.

Zusätzlich wird ein **Gewichtungsfaktor (1–3)** vergeben, je nach strategischer Bedeutung für das Produkt.

Die gewichtete Punktzahl errechnet sich als: `Punkt × Gewicht`.

---

## 2. Funktionsbewertung

| Funktion | Eigenbau-Aufwand | Paperless-Qualität | Mehrwert (0–10) | Gewicht (1–3) | Gewichteter Wert |
|----------|-------------------|--------------------|-----------------|---------------|------------------|
| **Datei-Upload + Speicherung** | Sehr gering | Standard | 2 | 3 | 6 |
| **Download + Streaming** | Sehr gering | Standard | 2 | 3 | 6 |
| **Liste/Filter nach Entität** | Gering | Standard | 3 | 3 | 9 |
| **PDF-Vorschau im Browser** | Gering | Gut | 5 | 2 | 10 |
| **Thumbnails für Dokumente** | Mittel | Gut | 6 | 2 | 12 |
| **OCR (gescannte PDFs/Bilder)** | Hoch | Sehr gut | 9 | 3 | 27 |
| **Volltextsuche über Inhalt** | Hoch | Sehr gut | 9 | 3 | 27 |
| **Such-Hit-Highlighting** | Sehr hoch | Gut | 8 | 2 | 16 |
| **Asynchrone Verarbeitung** | Mittel | Sehr gut | 7 | 2 | 14 |
| **Versionierung von Dokumenten** | Mittel | Gut | 7 | 2 | 14 |
| **Tags / Metadaten** | Gering | Gut | 5 | 2 | 10 |
| **Office-Dokumente → PDF** | Mittel | Gut (via Gotenberg/Tika) | 7 | 1 | 7 |
| **API-Stabilität + Community** | – | Sehr hoch | 8 | 2 | 16 |
| **Langfristige Wartung** | – | Sehr gut | 8 | 3 | 24 |
| **DSGVO-konformes Self-Hosting** | – | Gegeben | 7 | 3 | 21 |
| **Gesamt** | | | | | **219** |

Mögliche Maximalpunktzahl: `10 × 3 × 15 = 450`  
Erreichte gewichtete Punktzahl: **219 / 450 = 48,7 %**

---

## 3. Interpretation

Ein Wert von **48,7 %** bedeutet: Paperless-ngx bringt **einen moderaten bis hohen Mehrwert**, aber nicht in jeder Dimension. Der Hauptmehrwert liegt klar bei **OCR und Volltextsuche**. Ohne diese beiden Features wäre der Score deutlich niedriger und eine Eigenentwicklung wirtschaftlicher.

### Kernmehrwerte (hoch, sollten überwiegen)

| Funktion | Gewichteter Wert | Warum wichtig |
|----------|------------------|---------------|
| OCR | 27 | Vermieter scannen Verträge/Abrechnungen ein |
| Volltextsuche | 27 | Schnelles Auffinden von Klauseln, Beträgen, Adressen |
| Langfristige Wartung | 24 | Weniger Bugfixing, weniger Edge-Cases |
| DSGVO-konformes Hosting | 21 | Wettbewerbsvorteil bei deutschen Vermietern |
| API-Stabilität + Community | 16 | Weniger „Wissen in einem Kopf“ |

### Geringe Mehrwerte (eher Nice-to-have)

| Funktion | Gewichteter Wert | Bemerkung |
|----------|------------------|-----------|
| Datei-Upload | 6 | Trivial selbst baubar |
| Download/Streaming | 6 | Trivial selbst baubar |
| Liste/Filter | 9 | Einfach mit SQL |
| Tags/Metadaten | 10 | Wir haben eh eigenes Datenmodell |

---

## 4. Kosten-Nutzen-Betrachtung

### Geschätzte Entwicklungskosten

| Variante | Entwicklungszeit | Opportunitätskosten |
|----------|------------------|---------------------|
| **Eigenbau-DMS (ohne OCR/Suche)** | 1–2 Wochen | Gering |
| **Eigenbau-DMS (mit OCR + Postgres-Fulltext)** | 3–5 Wochen | Hoch |
| **Eigenbau-DMS (mit OCR + Meilisearch/Elasticsearch)** | 5–8 Wochen | Sehr hoch |
| **Paperless-Einbindung** | 1–1,5 Wochen | Moderat |

### Betriebskosten pro Vermieter/Monat (siehe Tenant-Trennung-Konzept)

| Variante | Mehrkosten/Vermieter |
|----------|----------------------|
| Eigenbau (Dateien auf Server, keine OCR) | ca. 0,10–0,50 € |
| Eigenbau (mit OCR + eigener Suchindex) | ca. 0,50–2,00 € |
| Paperless-ngx (Shared + pro-User) | ca. 0,50–3,00 € |

### Break-Even

Paperless-ngx lohnt sich dann, wenn:
- OCR und Volltextsuche echte Kundenanforderungen sind.
- Wir die 1–2 Wochen Entwicklungsersparnis gegenüber Eigenbau-OCR nutzen wollen.
- Wir nicht selbst 2–5 Jahre OCR-Edge-Cases sammeln wollen.

Paperless-ngx lohnt sich **nicht**, wenn:
- Kunden nur PDFs hochladen und downloaden wollen (kein OCR nötig).
- Der Betriebsaufwand (zusätzlicher Container) unerwünscht ist.
- Die Admin-Sichtbarkeit auf Dokumente juristisch nicht akzeptabel ist.

---

## 5. Szenario-Bewertung

### Szenario A: MVP mit einfachem Datei-Upload
- **Empfehlung:** Eigenbau.
- **Begründung:** Paperless-Mehrwert zu gering für zusätzlichen Container.

### Szenario B: MVP mit OCR + Suche als Wettbewerbsmerkmal
- **Empfehlung:** Paperless-ngx.
- **Begründung:** Hoher Mehrwert bei OCR/Suche, schnellere Time-to-Market.

### Szenario C: Enterprise-SaaS mit tausenden Vermietern
- **Empfehlung:** Paperless-ngx zunächst, später Eigenbau oder mandantenfähiges DMS.
- **Begründung:** Paperless reicht bis mittlerer Skalierung, langfristig braucht es echte Multi-Tenancy.

---

## 6. Fazit

Paperless-ngx hat einen **deutlichen, aber nicht überwältigenden Mehrwert**. Der entscheidende Faktor ist:

> **Brauchen wir OCR und Volltextsuche für Kunden-Dokumente?**

Falls ja: Paperless spart 2–4 Wochen Entwicklung und liefert bessere Qualität als ein schneller Eigenbau.  
Falls nein: Eine einfache Eigenlösung ist schlanker, günstiger und schneller im Betrieb.

**Empfehlung für unseren aktuellen Stand:**
Wir haben bereits PDF-Generierung (Mahnung, Wohnungsgeberbestätigung). Wenn wir Vermietern erlauben wollen, **gescannte Verträge, Abrechnungen und Korrespondenz abzulegen und zu durchsuchen**, ist Paperless-ngx der richtige Schritt. Für reine PDF-Ablage reicht ein Eigenbau.

---

## 7. Entscheidungshilfe

| Frage | Ja → | Nein → |
|-------|------|--------|
| Sollen gescannte Dokumente durchsuchbar sein? | Paperless | Eigenbau |
| Ist DSGVO-Self-Hosting wichtig? | Paperless | Beides |
| Ist schneller MVP-Launch wichtig? | Paperless | Eigenbau |
| Soll es absolut keinen Admin-Zugriff geben? | Eigenbau + Verschlüsselung | Paperless |
| Sind Betriebskosten pro Vermieter kritisch? | Eigenbau | Paperless |

---

*Ende des Scorings.*
