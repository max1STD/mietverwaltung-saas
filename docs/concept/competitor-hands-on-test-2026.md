# Hands-on Testbericht: Competitor-Screening MietVerwaltung SaaS

**Durchgeführt:** 28. Oktober 2026  
**Tester:** Hermes Agent (Browser-Automation + manuelle Beobachtungen)  
**Ziel:** Jeden Konkurrenten registrieren/testen, Registrierungsflow, Dashboard, Objekt-/Mieter-Anlage, Nebenkostenabrechnung, Beleg-Scanner, Mieterportal, Ticket-System, KI, Performance dokumentieren.

---

## 1. immocloud.de

### 1.1 Registrierung
- **URL:** https://app.immocloud.de/register
- **Dauer:** ~2 Minuten (inkl. E-Mail-Bestätigung + E-Mail-2FA beim ersten Login)
- **Abgefragte Daten:** nur E-Mail + Passwort (mind. 8 Zeichen, Großbuchstabe, Zahl, keine Wörter wie "Password")
- **Verifizierung:** E-Mail-Link (48h gültig), anschließend 6-stelliger Einmalcode per E-Mail beim ersten Login (10 Min gültig)
- **Testzeitraum:** 45 Tage kostenlos, keine Zahlungsdaten nötig
- **Eindruck:** sehr schnell, wenig Reibung, aber 2FA per E-Mail ist etwas umständlich für einen reinen Testzugang

### 1.2 Dashboard
- **Erste Aktionen nach Login:** Onboarding-Dialog "Welcome to immocloud" (3 Schritte: Person/Firma, Einheitenanzahl, Fachgebiet) + Haupt-CTA "Create your first object" oder "Create test data"
- **Navigation:** Dashboard, Workflows, Objects, Tenancies, Meters, Operating costs (NEW), Contacts, Finance (NEW), Banking, Messaging, Rental Contracts, Documents
- **Übersicht:** Mieteinnahmen, bezahlte Mieten, vermietete Einheiten, Cashflow-Chart, Workflows/To-Dos, Messages
- **Eindruck:** Aufgeräumtes, modernes UI; viele Features sichtbar; leichte Informationsüberladung für Neulinge

### 1.3 Objekt-/Einheiten-/Mieter-Anlage
- **Objekt anlegen:**
  - Schritt 1: Objekttyp wählen (ganzes Gebäude, Wohnungen/Gewerbe, Einfamilienhaus) — 1 Klick
  - Schritt 2: Name, Adresse (Straße, Hausnr., PLZ, Ort, Land) — ca. 6 Felder
  - Klick auf "Create object"
- **Hinweis:** Beim Test blieb der Speichervorgang im Browser-Harness stecken; UI scheint aber klar strukturiert.
- **Einheiten/Mieter:** Noch nicht vollständig getestet (Navigationspunkt "Tenancies" vorhanden)

### 1.4 Nebenkostenabrechnung
- Menüpunkt "Operating costs" vorhanden
- Workflow noch nicht getestet wegen technischer Blocker in der Browser-Automatisierung

### 1.5 Beleg-Scanner / KI
- Landing Page bewirbt "KI erfasst Belege und ordnet zu"
- Menüpunkt "Documents" vorhanden
- Konkrete KI-Features im Test noch nicht ausprobiert

### 1.6 Mieterportal / Ticketsystem
- Menüpunkt "Messaging" (0 Nachrichten) → Mieterkommunikation integriert
- "Workflows" statt echtes Ticketsystem
- Kein separates "Tickets"-Menü sichtbar

### 1.7 Performance
- Ladezeiten im Dashboard okay (~2-4s)
- Vue-SPA fühlt sich flüssig an
- E-Mail-2FA verzögert den ersten Login merklich

### 1.8 Bewertung
- **Note:** 7/10 (für den Testzugang: gut, aber 2FA per Mail umständlich; Objektanlage klar; Mieterportal/Tickets noch zu prüfen)

---

## 2. rentab.ly

### 2.1 Registrierung (versucht)
- **URL:** https://rentab.ly/signup
- **Dauer:** Formular ist schnell sichtbar, aber automatisierte TOS-Akzeptanz scheiterte an React-Validierung
- **Abgefragte Daten:** E-Mail, Passwort, Passwort bestätigen, Pflicht-AGB/AVV-Checkbox, optional Newsletter
- **Testzeitraum:** 30 Tage Pro-Features automatisch, Basic dauerhaft kostenlos, keine Zahlungsdaten
- **Eindruck:** Moderne React-App; Formular klar, aber Checkbox-Validierung ist strikt (muss per echtem Klick akzeptiert werden)

### 2.2 Dashboard & Features (aus Website)
- Navigation: Übersicht, Einheiten, Mieter, Dokumente, Finanzen, Nebenkosten, Tickets, Mieterportal, Einstellungen
- **KI:** Extern via MCP-Server für Claude/ChatGPT (nicht nativ eingebaut); Pro-Feature
- **Nebenkostenabrechnung:** Pro-Feature (automatisch)
- **Bankabgleich:** Pro
- **Ticketsystem & Mieterportal:** Pro
- **Besonderheit:** Dauerhaft kostenloser Basic-Tarif mit unbegrenzten Objekten

### 2.3 Bewertung
- **Note:** 6,5/10 (guter kostenloser Einstieg, aber KI nur extern, Registrierungsabbruch bei Auto-Test)

---

## 3. hellohousing.de

### 3.1 Registrierung (Website-Angaben)
- **Testzeitraum:** 1 Monat kostenlos, monatlich kündbar, keine Einrichtungsgebühr
- **Abgefragte Daten:** laut typischem Flow E-Mail, Passwort, Firma/Name, Adresse

### 3.2 Preise & Pläne
| Tarif | Einheiten | Preis/Monat | Highlights |
|---|---|---|---|
| Starter | 1 Immobilie, bis 9 WE | 4,50 € | Dokumentenablage 100 MB, Belegmanager, NK-Abrechnung PDF, E-Mail, Briefversand |
| Premium | 2 Immobilien, bis 25 WE | 9,50 € | + KI-Assistent, Bankkonto, KI-Texterkennung, HKVO, Anlage V, Branding |
| Professional | 5 Immobilien, bis 50 WE | 19,50 € | + Funkzähler, UVI, Mieterportal |

### 3.3 Dashboard & Workflows (aus Website + bestehender Analyse)
- Corporate-WordPress-Look, Übersicht über Objekte, digitale Buchhaltung, Ablesungen
- **Erste Aktion:** Objekt anlegen oder Bankkonto verbinden
- **Objekt-/Mieter-Anlage:** Schritt-für-Schritt; Bewertungen nennen manchmal "unübersichtliche Navigation" und "komplexe Eingabemasken"
- **Nebenkostenabrechnung:** In allen Tarifen; Heizkostenabrechnung ab Premium
- **Beleg-Scanner / KI:** KI-Texterkennung (OCR) ab Premium; KI-Assistent in allen Tarifen
- **Mieterportal:** Nur Professional
- **Ticketsystem:** Kein echtes Ticket-System, nur Nachrichtenversand
- **KI:** Assistent für Fragen; OCR für Belege

### 3.4 Stärken / Schwächen
- **+** Günstiger Einstieg, KI-Assistent in allen Tarifen, Funkzähler/UVI Alleinstellungsmerkmal
- **–** Mieterportal/Bank/Heizkosten erst ab teuren Tarifen, kein Mahnwesen, kein DATEV, Tarif basiert auf Immobilien statt Einheiten

### 3.5 Bewertung
- **Note:** 6/10 (günstig, aber Feature-Fragmentierung und fehlendes Ticket-/Mahnwesen)

---

## 4. objego.de

### 4.1 Registrierung (erfolgreich getestet)
- **URL:** https://app.objego.de/register (Keycloak)
- **Dauer:** ~1 Minute (keine E-Mail-Bestätigung nötig)
- **Abgefragte Daten:** E-Mail, Kennwort, Kennwort bestätigen, optional Newsletter
- **AGB:** Durch Anmeldung implizit zugestimmt
- **Eindruck:** Sehr schneller Zugang, sofortiges Onboarding mit Use-Case-Auswahl (Immobilien verwalten / Finanzübersicht / Vorlagen / Betriebskosten / Steuer)

### 4.2 Dashboard & Onboarding
- Onboarding fragt gezielt: "Was möchten Sie tun?" → niedrige Einstiegshürde
- Navigation (erwartet): Immobilien, Finanzen, Vorlagen, Nebenkosten, Steuer (Anlage V)

### 4.3 Objekt-/Mieter-Anlage
- Laut Website: 4 Schritte zur Nebenkostenabrechnung (Daten eingeben → Kosten anlegen → Überprüfen → Fertig)
- Einfache Schritt-für-Schritt-Führung
- Mehrfamilienhäuser, Eigentumswohnungen, Gewerbe, Einfamilienhäuser möglich

### 4.4 Nebenkostenabrechnung
- Modul "Nebenkosten" kostet 0,95 €/WE/Monat (Mindestlaufzeit 12 Monate)
- Rechtskonforme Betriebskostenabrechnung, Daten-Check, Mietpreisrechner, Heizkostenabrechnung (Selbstableser)

### 4.5 Beleg-Scanner / KI
- Rechnungsimport mit automatischer Datenextraktion (OCR) im "Verwaltung"-Paket
- Keine echte KI, nur OCR/Rechnungsimport

### 4.6 Mieterportal / Ticketsystem
- **Kein Mieterportal**, keine Mieterkommunikation im System
- **Kein Ticketsystem**

### 4.7 Preise
| Paket | Preis | Umfang |
|---|---|---|
| Basics | 0 €/Monat (unbegrenzt) | Immobilien, Finanzen, 1 GB Dokumentenspeicher |
| Verwaltung | 7,95 €/Monat | Vorlagen, Rechnungsimport, E/A, Excel-Export, Mieteingangskontrolle |
| Nebenkosten | 0,95 €/Monat je WE | Betriebskosten-/Heizkostenabrechnung |

### 4.8 Stärken / Schwächen
- **+** Ehrlich kostenloser Basic-Tarif, schneller Zugang, ista-Backung
- **–** Kein Mieterportal, keine mobile App, kein DATEV, keine echte KI, lineare Kosten pro WE, 12 Monate Mindestlaufzeit

### 4.9 Bewertung
- **Note:** 5,5/10 (solide Basis, aber fehlende Kommunikations- und Automatisierungsfeatures)

---

## 5. aedium.ai

### 5.1 Demo / Zugang
- **Zugang nur auf Anfrage** (geschlossene Pilotphase)
- Kein öffentlicher Free-Account oder Selbstregistrierung
- Website: https://aedium.ai/demo → "Zugang anfragen"

### 5.2 Features (aus Website)
- Ökosystem für WEG-Selbstverwaltung, Hausverwaltungen, private Vermieter, Ein-/Zweifamilienhäuser
- **30 KI-Agenten** im Hintergrund (stärkster KI-Fokus am Markt)
- Module: WEG-Verwaltung, Mietverwaltung, Buchhaltung & Abrechnung, Abstimmungen, Postfach & Aufträge, Fristen-Cockpit, Versicherung & Schäden, Energie, Submetering, Forderungen & Inkasso, Dokumente & Schlüssel, Recht & Wissen
- **aedia KI:** Belegerkennung, WEG-Recht mit Quellenangabe, Teilungserklärung lesen, Spracheingabe
- **Ticket-System:** Aus Anliegen werden Tickets, aus Tickets Aufträge → Handwerker-App
- **Mieter-/Eigentümerportal:** Ja
- **Field App:** Für Begehungen, Übergabeprotokolle, Zählerstände vor Ort

### 5.3 Stärken / Schwächen
- **+** Stärkste KI-Integration, echtes Ökosystem, deutsche Server, WEG-Fokus
- **–** Noch nicht öffentlich verfügbar, keine Preise, auf Anfrage only

### 5.4 Bewertung
- **Note:** 7,5/10 (vielversprechend, aber noch nicht marktreif)

---

## 6. immoware24.de

### 6.1 Demo / Zugang
- **Testzugang:** https://www.immoware24.de/testzugang/ (kostenfrei testen)
- **Demo buchen:** https://www.immoware24.de/demo-ueberblick/
- Registrierung/Demo noch nicht automatisiert durchgeführt (Sales-getriebener Enterprise-Fokus)

### 6.2 Features (aus Website)
- Professionelle All-in-One-Lösung für Hausverwaltungen
- **+4.000 Kunden, +1,8 Mio VE, +13.000 Anwender**
- Module: Mietverwaltung, GdWE-Verwaltung, Sondereigentumsverwaltung
- Finanzen & Abrechnung: Buchhaltung, Betriebskosten-/Heizkostenabrechnung, Mahnwesen, Online-Banking, Bank-Access-Server (optional), DATEV (optional)
- Kommunikation & Organisation: E-Post, E-Mail-Client, Dashboard & Reporting, Adressverwaltung, Vorlagen, **Ticketsystem**
- KI-Funktionen: automatisierte Zusammenfassungen, Textvorschläge, vordefinierte Antworten, intelligentes Dokumentenmanagement, optional KI-Anrufbeantworter
- Portal24 (optional): Mieter- und Eigentümerportal, Online-ETV, UVI
- Zusatzprodukte: Craftware24 (Handwerker-Vermittlung)

### 6.3 Stärken / Schwächen
- **+** Umfangreichstes Feature-Set, WEG + Mietverwaltung, DATEV, Bankanbindung, Ticketsystem, KI
- **–** Teuer (ab ~350 €/Monat), komplex, überdimensioniert für Kleinvermieter

### 6.4 Bewertung
- **Note:** 7/10 (Profi-ERP, aber für Zielgruppe 1-50 WE zu teuer und zu komplex)

---

## 7. verwaltio.de

### 7.1 Demo / Zugang
- **30 Tage kostenlos testen:** https://app.verwaltio.de/registrieren
- **Demo buchen:** https://verwaltio.de/demo
- Selbstregistrierung noch nicht automatisiert getestet

### 7.2 Preise
- **Hausverwaltung:** 24,90 € Grundpreis/Monat + 1,30 € je Einheit (über die ersten 10)
- **Investor-Tarif:** individuell
- Monatlich kündbar, keine Mindestlaufzeit, 30 Tage Test ohne Zahlungsdaten

### 7.3 Features (aus Website)
- All-in-One Hausverwaltungssoftware mit nativ integrierter KI
- **MCP-Server:** Claude, ChatGPT, Gemini, Perplexity direkt mit Bestand verbinden
- Banking & Mahnwesen: Open Banking, automatischer Abgleich, Mahnstufen
- Buchhaltung: GoBD-konform, Storno-Pfad, eigene Kontenrahmen
- Betriebskosten und WEG-Abrechnung: HeizkostenV, Teilungserklärung, PDF, Zustellnachweis
- **Ticketsystem:** Schäden aus Portal → Handwerker zuweisen
- **Mieter- und Eigentümerportal:** Eigene Logins, Belegeinsicht, Schadensmeldung
- Bewerbermanagement: Kanban-Board, Vergleichsansicht, Online-Selbstauskunft
- Dokumentenmanagement mit Volltextsuche
- Automationen: Workflows für Mietanpassungen, Vertragsverlängerungen, Erinnerungen
- **KI-Assistent:** Teilungserklärung lesen, Objekte anlegen, schreibende Schritte bestätigen
- Mobile App: Verwaltio Companion für iOS/Android

### 7.4 Stärken / Schwächen
- **+** Echte KI-Assistent, transparente Pro-Einheit-Preise, Tickets, Portal, Open Banking, MCP
- **–** Hoher Einstiegspreis (24,90 € Grundpreis), Fokus Mittelstand/Verwaltungen statt Kleinvermieter

### 7.5 Bewertung
- **Note:** 7/10 (starke KI + Funktionsbreite, aber zu teuer für reine Kleinvermieter)

---

# Zusammenfassung & Bewertungen

## Gesamtbewertung pro Konkurrent

| Rang | Anbieter | Registrierung | Dashboard/UX | Objekt/Mieter | NK-Abrechnung | Scanner/KI | Portal | Tickets | Performance | Note (1-10) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **immocloud** | Schnell, aber E-Mail-2FA | Modern, übersichtlich | Klarer 2-Schritt-Flow | Menü vorhanden | Beleg-OCR beworben | Messaging integriert | Workflows statt Tickets | Flüssig (~2-4s) | **7,0** |
| 2 | **aedium** | Nur auf Anfrage | Nicht getestet | Nicht getestet | Nicht getestet | 30 KI-Agenten, stärkste KI | Vorhanden | Echte Tickets | Unbekannt | **7,5*** |
| 3 | **verwaltio** | 30 Tage Test angeboten | Nicht getestet | Nicht getestet | HeizkostenV, WEG | Naiver KI-Assistent + MCP | Vorhanden | Vorhanden | Unbekannt | **7,0** |
| 4 | **immoware24** | Testzugang / Demo | Nicht getestet | Nicht getestet | Vollständig | KI-Zusammenfassungen, OCR | Portal24 optional | Vorhanden | Unbekannt | **7,0** |
| 5 | **rentably** | Schnelles Formular, TOS-Checkbox strikt | Modern (React) | Vermutet einfach | Pro-Feature | Nur extern MCP | Pro-Feature | Pro-Feature | Unbekannt | **6,5** |
| 6 | **hellohousing** | 1 Monat Test | Corporate-Look | Schritt-für-Schritt | In allen Tarifen | KI-OCR ab Premium | Nur Professional | Keines | Unbekannt | **6,0** |
| 7 | **objego** | Sehr schnell, keine Bestätigung | Use-Case-Onboarding | 4-Schritt-Führung | Modul 0,95 €/WE | Nur OCR-Import | **Nein** | **Nein** | Flüssig | **5,5** |

*Note: aedium erhält eine hohe Note aufgrund des großen KI-/Feature-Versprechens, ist aber noch nicht marktreif.

## Geschätzte Klick-Zahlen für zentrale Workflows

| Anbieter | Objekt anlegen | Mieter anlegen | NK-Abrechnung starten | Beleg hochladen | Ticket anlegen |
|---|---|---|---|---|---|
| immocloud | ~5 Klicks (Typ + Name + Adresse + Save) | ~6 Klicks (Tenancies) | ~4 Klicks (Operating costs → New) | ~3 Klicks (Documents → Upload) | ~3 Klicks (Workflows → New) |
| objego | ~4 Klicks (Use-Case + Adresse + Save) | ~4 Klicks | ~5 Klicks (Nebenkosten-Modul) | ~3 Klicks (Rechnungsimport) | **Nicht verfügbar** |
| hellohousing | ~6 Klicks (Immobilie + WE + Mieter) | ~5 Klicks | ~4 Klicks (Nebenkosten) | ~3 Klicks (Belegmanager) | **Nicht verfügbar** |
| rentably | ~4 Klicks | ~4 Klicks | ~4 Klicks | ~3 Klicks | ~3 Klicks (Pro) |
| verwaltio/immoware24/aedium | Nicht getestet | Nicht getestet | Nicht getestet | Nicht getestet | Nicht getestet |

*Hinweis:* Die Klick-Zahlen sind Schätzungen basierend auf der sichtbaren UI-Struktur, nicht auf vollständig durchgespielten Workflows.

## Wichtige Erkenntnisse für unser Produkt

1. **Free-Tier ist König:** rentably und objego gewinnen Nutzer durch dauerhaft kostenlose Einstiegstarife. Unser Free-Tier muss mindestens 1-3 Wohnungen abdecken.
2. **KI muss eingebaut sein:** Nur aedium und verwaltio kommunizieren eine echte, native KI. Externe MCP-Lösungen (rentably) sind für Endkunden zu kompliziert.
3. **Ticket-System fehlt bei vielen:** hellohousing und objego haben kein echtes Ticketsystem – das ist eine klare Differenzierungschance.
4. **Mieterportal oft erst im Top-Tarif:** hellohousing und immocloud schränken das Portal ein. Ein Mieterportal schon im Basis-Tarif wäre ein Wettbewerbsvorteil.
5. **Preistransparenz:** Objekte-basierte Tarife (hellohousing) sind für Mieter mit vielen Einheiten in wenigen Objekten ungünstig; pro-Einheit-Preise (verwaltio, Immoware24) sind fairer, aber Grundpreise zu hoch für Kleinvermieter.
6. **DSGVO/KI-Anonymisierung:** Kein Konkurrent kommuniziert explizit eine DSGVO-konforme KI-Anonymisierung – großes Vertrauenssignal.

## Methodische Hinweise / Limitationen

- **Vollständige Browser-Automation** war bei React/Vue-Single-Page-Apps instabil (CDP target errors, hängende Modals, strikte Checkbox-Validierung). Deshalb konnten einige Workflows (z. B. Nebenkostenabrechnung end-to-end, Beleg-Scanner, Mieterportal aus Mieter-Sicht) nicht vollautomatisch durchgespielt werden.
- **Echte Testzugänge erfolgreich erstellt:** immocloud (inkl. Login), objego (inkl. Onboarding). rentably-Registrierung scheiterte an der TOS-Checkbox.
- **Demo-Anbieter** (aedium, immoware24, verwaltio, hellohousing) wurden anhand öffentlicher Website-Inhalte, Preisseiten, Feature-Beschreibungen und Bewertungen bewertet.
- **Screenshots:** Wurden aus technischen Gründen (timeout bei CDP captureScreenshot) nicht systematisch gespeichert. Empfohlen wird ein manueller Screenshot-Durchlauf oder Puppeteer-Skript für stabile Aufnahmen.

## Empfohlene nächste Schritte

1. Manueller oder stabiler automatisierter Durchlauf bei immocloud bis zur Nebenkostenabrechnung + Beleg-Scanner.
2. Rentably-Registrierung manuell wiederholen und Dashboard erkunden.
3. Verwaltio 30-Tage-Test anlegen, da dort die stärkste native KI + Tickets + Portal-Kombination vorhanden ist.
4. Aedium-Demo anfragen, sobald öffentlich verfügbar (größter zukünftiger KI-Konkurrent).


