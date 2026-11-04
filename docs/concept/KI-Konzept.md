# KI- & Automatisierungs-Konzept — MietVerwaltung SaaS

## 1. Architektur-Übersicht

### 3-Schicht-Modell

```
SCHICHT 1 — LOKAL (Proxmox Server, CPU, 0€ Kosten)
├── Tesseract OCR          → Belege, Ausweise, Verträge lesen
├── PyMuPDF                → PDF-Text extrahieren
├── WeasyPrint             → PDF generieren (Vorlagen + Variablen)
├── Template-Engine (Jinja2) → Dokumente aus Vorlagen erstellen
├── Anonymisierungs-Engine   → Personendaten ersetzen vor KI-Aufruf
├── Berechnungs-Engine       → ROI, Rendite, Abrechnung, Fristen (reine Mathematik)
├── Keyword-Classifier       → Einfache Klassifikationen ohne KI
└── Redis Cache              → KI-Antworten cachen, Rate-Limiting

         │ anonymisierte Daten
         ▼

SCHICHT 2 — OLLAMA CLOUD (API, Pay-per-use oder Abo)
├── GLM 5.2 (Hauptmodell)
│   → Ticket-Kategorisierung
│   → Antwort-Entwürfe
│   → Dokument-Klassifikation
│   → Daten-Extraktion aus Text
│   → Abrechnungstexte
│   → Mahnungen
│   → Tone-Anpassung
│
└── Kimi K2.6 (Komplex-Modell)
    → Smart Insights & Empfehlungen
    → Mieterhöhung § 558 BGB
    → Jahresbericht
    → Komplexe Rechtsfälle
    → Mieter-Bewerbungs-Zusammenfassung

         │ KI-Antwort (mit Platzhaltern)
         ▼

SCHICHT 3 — LOKAL (Proxmox Server)
├── Platzhalter-Resolver    → [MIETER_NAME] → "Herr Schmidt"
├── PDF-Generierung         → fertiges Dokument mit Briefkopf
├── Datenbank-Speicherung   → Ergebnis persistieren
├── E-Mail-Versand          → Postfix/SMTP
└── Audit-Log               → was wurde an KI gesendet (anonymisiert)
```

### Datenfluss-Prinzip

```
Personendaten ──→ NIE an KI ──→ bleiben lokal
Anonymisierte Daten ──→ an KI ──→ Antwort lokal anreichern
```

---

## 2. Modell-Zuweisung

### GLM 5.2 (Standard — 80% aller KI-Aufrufe)

| Aufgabe | Prompt-Typ | Input Tokens | Output Tokens | Aufrufhäufigkeit |
|---------|-----------|-------------|---------------|-----------------|
| Ticket-Kategorisierung | Klassifikation | ~100 | ~20 | Hoch (jedes Ticket) |
| Ticket-Priorität | Klassifikation | ~100 | ~10 | Hoch (jedes Ticket) |
| Antwort-Entwurf | Textgenerierung | ~300 | ~200 | Mittel (bei Bedarf) |
| Dokument-Typ erkennen | Klassifikation | ~150 | ~20 | Mittel (jeder Upload) |
| Vertragsdaten extrahieren | Extraktion | ~1000 | ~200 | Selten (neuer Mietvertrag) |
| Beleg-Daten extrahieren | Extraktion | ~500 | ~100 | Mittel (jeder Beleg) |
| Abrechnungstext | Textgenerierung | ~200 | ~150 | Selten (jährlich) |
| Mahnung formulieren | Textgenerierung | ~200 | ~300 | Selten |
| Tone-Anpassung | Textgenerierung | ~100 | ~150 | Selten |
| Lösungs-Vorschlag FAQ | Textgenerierung | ~200 | ~200 | Mittel |
| Ticket-Zusammenfassung | Zusammenfassung | ~500 | ~100 | Selten |
| Sprachübersetzung | Übersetzung | ~200 | ~200 | Selten |

### Kimi K2.6 (Komplex — 20% aller KI-Aufrufe)

| Aufgabe | Prompt-Typ | Input Tokens | Output Tokens | Aufrufhäufigkeit |
|---------|-----------|-------------|---------------|-----------------|
| Smart Insights | Analyse + Text | ~1000 | ~500 | Täglich (batched) |
| Mieterhöhung § 558 BGB | Rechtstext | ~500 | ~500 | Sehr selten |
| Jahresbericht | Zusammenfassung | ~2000 | ~1000 | Jährlich |
| Mieter-Bewerbung zusammenfassen | Analyse | ~500 | ~300 | Selten (neuer Mieter) |
| Kostenvergleich Regional | Analyse | ~300 | ~200 | Monatlich |
| Energie-Empfehlung | Analyse | ~200 | ~300 | Jährlich |

### Keyword-Classifier (Lokal, 0€ — Vorschaltung vor KI)

Viele Klassifikationen können **ohne KI** durch Keyword-Matching gelöst werden.
KI wird nur bei Mehrdeutigkeit aufgerufen:

| Eingabe | Keyword-Match | KI nötig? |
|---------|--------------|-----------|
| "Heizung bleibt kalt" | heizung, warm, kalt, thermostat → heizung | ❌ Keyword reicht |
| "Wasser tropft aus Decke" | wasser, tropf, feucht, leck → wasser | ❌ Keyword reicht |
| "Lampe geht nicht" | lampe, licht, strom, elektrik → elektrik | ❌ Keyword reicht |
| "Mold in bathroom" | Schimmel, mold, feuchtigkeit → schimmel | ❌ Keyword reicht |
| "Es ist komisch im Bad" | — kein klares Keyword | ✅ KI zur Klassifikation |

**Einsparung: ~60% der Ticket-Kategorisierungen ohne KI lösbar.**

---

## 3. Automatisierungs-Matrix

### Event-basierte Automatisierungen

| Trigger | Automatische Aktion | KI? | Mensch bestätigt? |
|---------|--------------------|----|-------------------|
| Neuer Mieter registriert | Willkommens-E-Mail + Dokumenten-Aufforderung | Nein | ❌全自动 |
| Mieter lädt Ausweis hoch | OCR → Daten extrahieren → Bild löschen → Vermerk | Tesseract (lokal) | ❌全自动 |
| Mieter lädt Lohnabrechnung hoch | OCR → Netto extrahieren → Mietbelastungsquote | Tesseract + GLM | ❌全自动 |
| Mieter lädt Schufa hoch | OCR → Score + Einträge strukturieren | Tesseract + GLM | ❌全自动 |
| Mieter erstellt Ticket | Keyword-Klassifikation → (falls nötig) KI-Kategorie + Priorität | Keyword/GLM | ❌全自动 |
| Ticket erstellt | E-Mail an Vermieter | Nein | ❌全自动 |
| Ticket erstellt | Lösungs-Vorschlag an Mieter (bei einfachen Problemen) | GLM | ❌全自动 |
| Ticket erstellt | Antwort-Entwurf für Vermieter generieren | GLM | ✅ Vermieter prüft |
| Vermieter sendet Ticket-Antwort | E-Mail an Mieter + Status ändern | Nein | ❌全自动 |
| Ticket-Status → erledigt | Mieter benachrichtigen → nach 7 Tagen schließen | Nein | ❌全自动 |
| Dokument hochgeladen | Typ erkennen → zuordnen | Keyword/GLM | ❌全自动 |
| Beleg fotografiert | OCR → Betrag + Kategorie + Umlagefähigkeit | Tesseract + GLM | ✅ Vermieter prüft |
| Kosten eingetragen | Umlagefähigkeit prüfen + Plausibilität | GLM | ❌全自动 (Warnung) |
| Monatserster | Mietzahlung erwartet → Status prüfen | Nein | ❌全自动 |
| Tag 3: Miete fehlt | Freundliche Erinnerung an Mieter | GLM (Text) | ✅ Vermieter prüft |
| Tag 7: Miete fehlt | Mahnung Stufe 1 generieren | GLM (Text) | ✅ Vermieter prüft |
| Tag 14: Miete fehlt | Mahnung Stufe 2 + Mahngebühr | GLM (Text) | ✅ Vermieter prüft |
| Tag 21: Miete fehlt | Warnung an Vermieter (Kündigung?) | Nein + GLM | ❌全自动 (Warnung) |
| Abrechnungszeitraum startet | Alle Kosten sammeln + sortieren | Nein | ❌全自动 |
| Abrechnung: Vollständigkeit | Fehlende Positionen melden | GLM | ❌全自动 (Warnung) |
| Abrechnung: Plausibilität | Ungewöhnliche Kosten markieren | GLM | ❌全自动 (Warnung) |
| Abrechnung erstellt | Erklärungstext generieren | GLM | ❌全自动 |
| Abrechnung erstellt | PDF mit Briefkopf generieren | WeasyPrint (lokal) | ❌全自动 |
| Vermieter klickt "Versenden" | E-Mail an Mieter mit PDF | Nein | ✅ Vermieter bestätigt |
| Mietvertrag endet in 6 Monaten | Erinnerung an Vermieter | Nein | ❌全自动 |
| Mietvertrag endet in 3 Monaten | Übergabeprotokoll-Vorlage generieren | Template (lokal) | ❌全自动 |
| Mietvertrag endet in 1 Monat | Erinnerung an Mieter (Termin) | Nein | ❌全自动 |
| Mietvertrag endet in 2 Wochen | Checkliste für Vermieter | Nein | ❌全自动 |
| Auszug durchgeführt | Kaution-Abrechnung erstellen | Template + Math | ✅ Vermieter prüft |
| Auszug + 30 Tage | Mieter-Zugang deaktivieren | Nein | ❌全自动 |

### Zeitgesteuerte Automatisierungen (Cron-Jobs)

| Frequenz | Uhrzeit | Aktion | KI? |
|----------|---------|--------|-----|
| **Täglich** | 06:00 | Smart Insights generieren (Kimi K2.6) | ✅ KI |
| **Täglich** | 06:00 | Fristen-Check (Mietende, Kündigung, Abrechnung) | Nein |
| **Täglich** | 06:00 | Mietzahlungs-Check (welche überfällig?) | Nein |
| **Täglich** | 08:00 | Mahn-Workflow ausführen (Tag 3/7/14/21) | GLM (Text) |
| **Wöchentlich** | Mo 07:00 | Kosten-Plausibilitäts-Check | ✅ KI |
| **Wöchentlich** | Mo 07:00 | Offene Tickets-Übersicht an Vermieter | Nein |
| **Monatlich** | 1. des Monats | Mieteinnahmen-Report | Nein |
| **Monatlich** | 1. des Monats | Kostenvergleich regional (falls Daten verfügbar) | ✅ KI |
| **Jährlich** | 01.01. | Abrechnungs-Vorbereitung (Kosten sammeln) | Nein |
| **Jährlich** | 01.01. | Vollständigkeits-Check Abrechnung | ✅ KI |
| **Jährlich** | 31.12. | Jahresbericht generieren | ✅ KI (Kimi) |

### Automatisierungs-Grad

```
100% automatisch (kein Mensch nötig):
├── OCR-Datenextraktion (Ausweis, Lohnabrechnung, Belege)
├── Ticket-Kategorisierung + Priorität
├── Dokument-Klassifikation
├── Fristen-Monitoring
├── Mietzahlungs-Tracking
├── Smart Insights (täglich)
├── E-Mail-Benachrichtigungen
├── Platzhalter-Einsetzung
├── PDF-Generierung
├── Template-Dokumente (Wohnungsgeber etc.)
└── Berechnungen (ROI, Rendite, Abrechnung)

80% automatisch (Mensch prüft, 1 Klick):
├── KI-Antwort auf Ticket → Vermieter prüft → sendet
├── Beleg-Scan → Vermieter bestätigt Kosten-Eintrag
├── Mahnung → Vermieter prüft → sendet
├── Abrechnung → Vermieter prüft → sendet
└── Mieterhöhung → Vermieter prüft → sendet

50% automatisch (Mensch entscheidet):
├── Mieter-Bewerbung → Vermieter entscheidet Annehmen/Ablehnen
├── Kündigung → Vermieter entscheidet
└── Mietpreis-Anpassung → Vermieter entscheidet
```

---

## 4. Anonymisierungs-Protokoll

### Was anonymisiert wird (vor KI-Aufruf)

| Datentyp | Original | Anonymisiert |
|----------|----------|-------------|
| Personenname | Thomas Schmidt | [MIETER_NAME] |
| Adresse | Hauptstraße 5, 21635 Jork | [OBJEKT_ADRESSE] |
| E-Mail | t.schmidt@email.de | [MIETER_EMAIL] |
| Telefon | 0151 1234567 | [MIETER_TELEFON] |
| IBAN | DE89 3704 0044... | [IBAN] |
| Steuernummer | 43/123/45678 | [STEUERNR] |
| Geburtsdatum | 15.04.1985 | [GEBURTSDATUM] |
| Schufa-Score | 96% | [SCHUFA_SCORE] (nur Zahl bleibt) |
| Arbeitgeber | VW Werk Wolfsburg | [ARBEITGEBER] |
| Nettoeinkommen | 3.200€ | [NETTO_EINKOMMEN] (nur Zahl bleibt) |

### Was NICHT anonymisiert wird (unkritisch für KI)

| Datentyp | Warum unkritisch |
|----------|-----------------|
| Kaltmiete (Zahl) | Finanzieller Wert, keine Person |
| Wohnfläche (Zahl) | Objektmerkmal |
| Heizkosten (Zahl) | Betriebskosten |
| Ticket-Kategorie | Klassifikation |
| Baujahr (Zahl) | Objektmerkmal |
| Kündigungsfrist (Datum) | Rechtsfrist |
| Müllabfuhr-Kosten (Zahl) | Betriebskosten |

### Anonymisierungs-Engine (technisch)

```python
ANONYMIZATION_RULES = {
    # Regex-Pattern → Platzhalter
    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b': '[MIETER_NAME]',  # Vorname Nachname
    r'\b\d{5} [A-Z][a-z]+\b': '[PLZ_ORT]',  # PLZ Ort
    r'[A-Z][a-z]+straße \d+': '[STRASSE_HAUSNR]',  # Straße Hausnr
    r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+': '[EMAIL]',  # E-Mail
    r'\d{3,4}[\s/]?\d{6,8}': '[TELEFON]',  # Telefon
    r'DE\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}': '[IBAN]',  # IBAN
    r'\d{2}\.\d{2}\.\d{4}': '[DATUM]',  # Datum (generisch)
}

def anonymize(text, context=None):
    """
    Ersetzt alle personenbezogenen Daten durch Platzhalter.
    Behält eine Mapping-Tabelle für die Rück-Übersetzung.
    """
    mapping = {}
    for pattern, placeholder in ANONYMIZATION_RULES.items():
        matches = re.findall(pattern, text)
        for i, match in enumerate(matches):
            key = f"{placeholder}_{i}" if i > 0 else placeholder
            mapping[key] = match
            text = text.replace(match, key, 1)
    return text, mapping

def deanonymize(text, mapping):
    """Setzt Platzhalter wieder durch echte Werte ein."""
    for placeholder, original in mapping.items():
        text = text.replace(placeholder, original)
    return text
```

### Beispiel-Flow: Mahnung generieren

```python
# 1. Daten sammeln (lokal)
daten = {
    "mieter_name": "Thomas Schmidt",
    "mieter_adresse": "Hauptstraße 5, 21635 Jork",
    "miete": 850,
    "rueckstand": 1700,
    "frist_tage": 14,
    "mahngebuehr": 15,
    "datum": "20.10.2026",
    "ort": "Stade"
}

# 2. Prompt mit Anonymisierung (lokal)
prompt = f"""
Schreibe eine Mahnung Stufe 2 an [MIETER_NAME] in [MIETER_ORT].
Rückstand: {daten['rueckstand']}€ (2 Monate à {daten['miete']}€).
Frist: {daten['frist_tage']} Tage ab Zustellung.
Mahngebühr: {daten['mahngebuehr']}€.
Gesamtforderung: {daten['rueckstand'] + daten['mahngebuehr']}€.
Rechtliche Grundlage: § 573 BGB, § 569 BGB.
Ton: formell, bestimmt, aber nicht aggressiv.
"""

# 3. An Ollama Cloud senden (nur anonymisiert!)
response = ollama_cloud.generate(
    model="glm-5.2",
    prompt=prompt
)
# KI sieht: "[MIETER_NAME] in [MIETER_ORT]"
# KI sieht NICHT: "Thomas Schmidt", "Jork"

# 4. Platzhalter auflösen (lokal)
final_text = response.replace("[MIETER_NAME]", daten["mieter_name"])
final_text = final_text.replace("[MIETER_ORT]", daten["ort"])

# 5. PDF generieren (lokal)
pdf = weasyprint.render(template + final_text)

# 6. Speichern + Audit-Log
save_pdf(pdf)
audit_log("mahnung_generated", ticket_id, "anonymized_prompt_sent_to_ai")
```

---

## 5. Kostenmodell — Ollama Cloud

### Szenario 1: Pay-per-Use (pro Token)

Geschätzte Aufrufe pro Vermieter pro Monat:

| Aufgabe | Aufrufe/Monat | Input Tokens | Output Tokens | Token/Monat |
|---------|--------------|-------------|---------------|-------------|
| Ticket-Kategorisierung (Keyword-Vorschaltung, 40% KI) | 4 | 100 | 20 | 480 |
| Ticket-Priorität | 4 | 100 | 10 | 440 |
| Antwort-Entwurf | 3 | 300 | 200 | 1.500 |
| Beleg-Scan (Datenextraktion) | 5 | 500 | 100 | 3.000 |
| Dokument-Klassifikation | 3 | 150 | 20 | 510 |
| Mahnung (falls überfällig) | 1 | 200 | 300 | 500 |
| Lösungs-Vorschlag FAQ | 2 | 200 | 200 | 800 |
| Smart Insights (täglich, batched) | 30 | 1.000 | 500 | 45.000 |
| Sonstiges | 5 | 200 | 200 | 2.000 |
| **GLM 5.2 Gesamt** | **~57** | — | — | **~54.230** |

| Aufgabe | Aufrufe/Monat | Input Tokens | Output Tokens | Token/Monat |
|---------|--------------|-------------|---------------|-------------|
| Mieter-Bewerbung | 0,5 | 500 | 300 | 400 |
| Kostenvergleich | 1 | 300 | 200 | 500 |
| Jahresbericht (anteilig) | 0,1 | 2.000 | 1.000 | 300 |
| **Kimi K2.6 Gesamt** | **~1,6** | — | — | **~1.200** |

**Geschätzte Kosten pro Vermieter/Monat:**

| Modell | Token/Monat | Preis/1K Token | Kosten/Monat |
|--------|------------|---------------|-------------|
| GLM 5.2 | ~54.000 | $0,002 (geschätzt) | ~$0,11 |
| GLM 5.2 | ~54.000 | $0,01 (worst case) | ~$0,54 |
| Kimi K2.6 | ~1.200 | $0,005 | ~$0,01 |
| **Gesamt (günstig)** | — | — | **~$0,12 (~0,11€)** |
| **Gesamt (teuer)** | — | — | **~$0,55 (~0,50€)** |

### Szenario 2: Abo (Pauschale)

Falls Ollama Cloud ein Abo anbietet (z.B. $20/Monat für unbegrenzte Aufrufe):

| Vermieter-Anzahl | Kosten bei Abo | Kosten bei Pay-per-Use |
|-----------------|----------------|----------------------|
| 10 | $20 | $1,20 - $6,00 |
| 50 | $20 | $6,00 - $30,00 |
| 100 | $20 | $12,00 - $60,00 |
| 500 | $20 | $60,00 - $300,00 |

**Break-even:**
- Bei ~$0,12/Vermieter → Abo lohnt ab ~167 Vermietern
- Bei ~$0,50/Vermieter → Abo lohnt ab ~40 Vermietern

### Empfehlung

```
Phase 1 (Start, < 50 Vermieter):  Pay-per-Use (günstiger)
Phase 2 (50+ Vermieter):          Abo prüfen (wenn verfügbar)
Phase 3 (500+ Vermieter):         Abo oder eigenes Modell auf Proxmox (GPU)
```

### Optimierung: Was die Kosten drückt

1. **Keyword-Classifier Vorschaltung** → ~60% der Klassifikationen ohne KI
2. **Smart Insights cachen** → nur neu generieren wenn Daten sich ändern (nicht täglich)
3. **Antwort-Entwürfe on-demand** → nur generieren wenn Vermieter draufklickt
4. **Batch-Verarbeitung** → mehrere Tickets/Belege in einem KI-Aufruf
5. **Kurze Prompts** → Token-effiziente Prompt-Engineering
6. **Redis-Cache** → gleiche Frage nicht zweimal an KI senden

**Mit Optimierung: Kosten pro Vermieter/Monat ~0,05-0,15€**

---

## 6. Fallback-Strategie (KI nicht verfügbar)

### 3-Stufen-Fallback

```
Stufe 1: Ollama Cloud (GLM 5.2 / Kimi K2.6)
    │  ── nicht verfügbar (Timeout, 500er)
    ▼
Stufe 2: Fallback-Provider (Aleph Alpha / Mistral AI — EU)
    │  ── auch nicht verfügbar
    ▼
Stufe 3: Lokaler Fallback (Regelbasiert / Templates)
```

### Stufe 3 — Regelbasierte Fallbacks

| KI-Feature | Fallback (ohne KI) |
|-----------|-------------------|
| Ticket-Kategorisierung | Keyword-Classifier (hat ohnehin 60% abgedeckt) |
| Ticket-Priorität | Standard = "normal" (Vermieter kann ändern) |
| Antwort-Entwurf | Standard-Templates ("Vielen Dank für Ihre Meldung. Ich prüfe das und melde mich.") |
| Beleg-Scan | Manuelle Eingabe durch Vermieter |
| Smart Insights | Ausblenden + "KI-Analyse暂时不可用" |
| Mahnung | Standard-Vorlage ohne KI-Text |
| Abrechnungstext | Standard-Text ("Anbei erhalten Sie Ihre Nebenkostenabrechnung.") |
| Dokument-Klassifikation | Vermieter wählt Typ manuell |

**Prinzip: Die App funktioniert auch ohne KI — nur mit weniger Automatisierung.**

### Health-Check

```python
# Alle 5 Minuten: KI-Verfügbarkeit prüfen
async def ai_health_check():
    try:
        response = ollama_cloud.generate(
            model="glm-5.2",
            prompt="Antworte mit 'OK'",
            max_tokens=5
        )
        if response.strip() == "OK":
            ai_status = "online"
        else:
            ai_status = "degraded"
    except:
        ai_status = "offline"
        # Fallback aktivieren
        enable_rule_based_fallback()
```

---

## 7. Prompt-Engineering — Templates

### System-Prompt (für alle KI-Aufrufe gleich)

```
Du bist ein KI-Assistent für eine Mietverwaltungs-Software.
Du hilfst einem Vermieter in Deutschland bei der Verwaltung
seiner Immobilien. Alle personenbezogenen Daten wurden
anonymisiert (Platzhalter in [GROSSBUCHSTABEN]).

Regeln:
- Antworte präzise und auf Deutsch
- Verwende formelle Sprache (Sie-Form)
- Bei rechtlichen Themen: nenne den Paragrafen, aber füge hinzu
  "Bitte rechtlich prüfen lassen"
- Generiere nur den angeforderten Text, keine Erklärungen
- Verwende die Platzhalter exakt wie gegeben
```

### Task-spezifische Prompt-Templates

**Ticket-Kategorisierung:**
```
Kategorisiere folgendes Ticket in eine dieser Kategorien:
heizung, wasser, elektrik, schimmel, sonstiges

Ticket-Titel: {titel}
Ticket-Beschreibung: {beschreibung}

Antworte NUR mit der Kategorie, kein weiterer Text.
```

**Antwort-Entwurf:**
```
Erstelle einen Antwort-Entwurf für folgendes Ticket:

Ticket: {titel}
Beschreibung: {beschreibung}
Kategorie: {kategorie}
Priorität: {prioritaet}

Der Vermieter möchte freundlich, aber professionell antworten.
Erwähne, dass das Problem geprüft wird und nenne einen
realistischen Zeitrahmen für die Bearbeitung.

Verwende [MIETER_NAME] als Anrede.
```

**Mahnung:**
```
Schreibe eine {stufe} an [MIETER_NAME].

Daten:
- Rückstand: {rueckstand}€ ({monate} Monate à {miete}€)
- Bisherige Mahnung: {bisherige_mahnung}
- Frist: {frist} Tage
- Mahngebühr: {mahngebuehr}€
- Gesamtforderung: {gesamt}€
- Rechtliche Grundlage: § 573 BGB, § 569 BGB

Ton: {tonfall}
Format: formeller Brief mit Datum und Anrede.
```

**Smart Insights:**
```
Analysiere folgende Immobilienkennzahlen und generiere
3 konkrete Handlungsempfehlungen:

Objekt: [OBJEKT_NAME]
Bruttomietrendite: {rendite}%
Nettomietrendite: {nettorendite}%
Cashflow/Monat: {cashflow}€
DSCR: {dscr}
Offene Tickets: {tickets}
Kostenentwicklung: {kosten_trend}%
Miete vs. Mietspiegel: {mietspiegel_delta}%

Generiere genau 3 Insights im Format:
⚠️ / 💡 / 📈 [Kurzheadline]: [Beschreibung + Empfehlung]
```

---

## 8. Caching-Strategie

| KI-Aufruf | Cache-Dauer | Cache-Key |
|-----------|------------|-----------|
| Ticket-Kategorisierung | 30 Tage | hash(titel + beschreibung) |
| Dokument-Klassifikation | 30 Tage | hash(text_content) |
| Smart Insights | 24h (oder bei Datenänderung) | user_id + date |
| Antwort-Entwurf | Nicht cachen (jedes Ticket individuell) | — |
| Mahnung | Nicht cachen (individuell) | — |
| Abrechnungstext | 30 Tage | einheit_id + jahr |
| Kostenvergleich | 7 Tage | objekt_id + kategorie |

**Redis als Cache-Store. Cache-Hit-Rate Ziel: 30-40%**

---

## 9. Quality Assurance / Monitoring

### KI-Qualitäts-Metriken

| Metrik | Wie gemessen | Ziel |
|--------|-------------|------|
| Ticket-Kategorisierung: Korrekt | Vermieter ändert Kategorie? | <15% Korrekturen |
| Antwort-Entwurf: Übernommen | Vermieter sendet ohne Änderung? | >50% unverändert |
| Beleg-Scan: Korrekt | Vermieter korrigiert Eintrag? | <20% Korrekturen |
| Smart Insights: Relevant | Vermieter klickt darauf? | >20% Click-Rate |
| KI-Latenz | Zeit pro Aufruf | <5 Sekunden |
| KI-Verfügbarkeit | Health-Check | >99% |

### Feedback-Loop

```
KI generiert Vorschlag
    ↓
Vermieter übernimmt unverändert →  ✅ Positive signal → so lassen
Vermieter ändert Vorschlag    →  📝 Negative signal → Prompt optimieren
Vermieter löscht Vorschlag    →  ❌ Strong negative → Feature überdenken
```

### Audit-Log

Jeder KI-Aufruf wird protokolliert:

```json
{
  "timestamp": "2026-10-20T14:32:15Z",
  "user_id": "uuid",
  "task": "ticket_categorization",
  "model": "glm-5.2",
  "input_anonymized": true,
  "input_tokens": 120,
  "output_tokens": 15,
  "latency_ms": 1200,
  "cache_hit": false,
  "result_accepted": true
}
```

---

## 10. SaaS-Pricing-Impact

### Kostenstruktur pro Vermieter

| Kostenpunkt | Pro Vermieter/Monat |
|------------|-------------------|
| KI (Ollama Cloud, optimiert) | ~0,05-0,15€ |
| Hosting (Proxmox, anteilig) | ~0,50-1,00€ |
| E-Mail-Versand | ~0,01€ |
| Datenbank/Storage | ~0,10€ |
| **Gesamt** | **~0,70-1,30€** |

### Empfohlene SaaS-Preise

| Plan | Preis/Monat | Enthaltene KI | Zielgruppe |
|------|------------|---------------|-----------|
| **Free** | 0€ | 1 Objekt, 1 Mieter, keine KI | Testen |
| **Basis** | 9,90€ | 3 Objekte, Basis-KI (Tickets, Belege) | Kleinvermieter |
| **Pro** | 19,90€ | 10 Objekte, volle KI (alle Features) | Professionell |
| **Business** | 39,90€ | Unbegrenzt, alle KI, Priority Support | Hausverwaltungen |

**Break-even bei Pro-Plan: ~19€ Preis - ~1€ Kosten = ~18€ Marge/Vermieter**

---

## 11. Implementierungs-Reihenfolge

### Phase 1: Basis-KI (mit MVP)
1. Anonymisierungs-Engine
2. Ollama Cloud API-Integration (GLM 5.2)
3. Keyword-Classifier (lokal, vor KI)
4. Ticket-Kategorisierung + Priorität
5. Beleg-Scan (Tesseract + GLM)
6. Template-Dokumente (Wohnungsgeber etc.)
7. Antwort-Entwürfe für Tickets

### Phase 2: Erweiterte KI
8. Smart Insights (Kimi K2.6, täglich)
9. Mahnungs-Workflow (automatisiert)
10. Abrechnungstext-Generierung
11. Dokument-Klassifikation
12. Fallback-System (Aleph Alpha)

### Phase 3: Advanced KI
13. Mieterhöhung § 558 BGB generieren
14. Jahresbericht (Kimi K2.6)
15. Kostenvergleich regional
16. Energie-Empfehlungen
17. Caching & Optimierung
18. Quality-Monitoring Dashboard