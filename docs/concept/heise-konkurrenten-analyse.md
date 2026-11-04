# Heise Hausverwaltungssoftware-Vergleich: Wettbewerbsanalyse

**Quelle:** heise.de/download/specials/Hausverwaltungssoftware-im-Vergleich-7151831 (18.02.2025, Rainer Wagenhäuser)  
**Projekt:** MietVerwaltung SaaS für DACH Kleinvermieter  
**Analyse erstellt:** 28.10.2026

---

## 1. Zusammenfassung des heise-Artikels

### Kernaussagen
- Eine gute Hausverwaltungssoftware standardisiert/automatisiert Verwaltungsprozesse und erledigt Nebenkosten-, Miet- und Heizkostenabrechnungen rechtskonform.
- Wichtig: Steueranlage V, DATEV-Schnittstelle, Dokumentenmanagement, Notizfunktion, Rollen-/Rechtemanagement, ggf. Wohnungsinserate.
- Cloud ist wartungsarm, On-Premises datensparsamer; Empfehlung: Anbieter aus Deutschland/EWR wegen DSGVO.
- Es gibt kein „bestes“ Programm – Auswahl hängt von Einheitenanzahl, Miet- vs. WEG-Verwaltung und Preis ab.

### Von heise vorgestellte Produkte (10 Hauptprodukte)
1. **objego** – Cloud, private Vermieter, Freemium
2. **immocloud** – Cloud, 5 Tarife, bis zu tausende Einheiten
3. **Vermietet.de** – Cloud, ImmoScout24, private Vermieter
4. **DOMUS 1000** – Windows Desktop, bis 500 WE
5. **WISO Vermieter 365 / WISO Hausverwalter 365 Plus** – Windows/Web, Buhl Data
6. **INtex Hausverwaltung** – Cloud/On-Premises, 4 Lizenzen
7. **etg24** – Cloud, Mieter-/Eigentümerportal, KI-Agent
8. **Win-CASA** – Windows Desktop/Cloud, modular
9. **hausify** – Portal-/Ticketsystem, Freemium
10. **dataPad** – App für digitale Wohnungsübergabe

### Weitere genannte Anbieter ( Deutschland)
Aareon PowerHouse/Karthago/HausPerfekt, Aareon SmartImmo, ALCO House, casavi, ecoVermieten, eddy24, facilioo, Haufe Verwalter Praxis Professional, hausmanager, HausPerfekt, haussoft, Hausverwaltung "easy", hellohousing, homevoice, humbee, Immolert, immolinxx, ImmoManager, ImmoOffice, Immoware24, iX-Haus, kpi werk, Matera, MietCheck Pro, Momo, NOVALIS, Plentific, realax, RentalOne, SCALARA, SIDOMO, SMARTBRIX, Villa, Warehaus, WEG digital, ZHAUS.

### Österreich/Schweiz
andromeda.One, iDWELL, Fairwalter, ImmoTop2, leikom, LIMMOBI.

---

## 2. Detaillierte Anbieter-Analyse

### 2.1 immocloud
- **Unternehmen:** Düsseldorf, Deutschland
- **Deployment:** Cloud SaaS (Web-App app.immocloud.de)
- **Tarife (netto/Monat, 12 Monate Laufzeit):**
  - Starter: 9,99 € (bis 5 Einheiten)
  - Manager: 15,99 € (bis 15 WE, laut heise; Website aktuell „bis 30 WE")
  - Investor: 39,99 € (bis 50 WE)
  - Tycoon: Preis auf Anfrage (ab 50 WE, für Haus-/Mietverwalter)
- **Besonderheiten:** 45 Tage kostenlos ohne Zahlungsdaten; KI erfasst Belege; DATEV-Export; digitaler Mietvertrag (Haus & Grund); Mieterportal; SMS-Erinnerungen; Mobile App; digitale Wohnungsübergabe.
- **KI-Features:** „Kein Abtippen: KI erfasst Belege und ordnet zu“; Berichte-Center.
- **DSGVO:** Rechenzentrum Deutschland, AES256-GCM, Mitglied GDD.
- **Tech-Stack:** WordPress-Marketingseite, Web-App mit Vue.js (login app.immocloud.de/assets/index-*.js), Google Maps API, Intercom, Hotjar.
- **Demo:** 45 Tage kostenlos.
- **Stärken:** Moderne UX, DATEV, günstiger Einstieg, KI-OCR, mobiles Scannen, digitale Übergabe.
- **Schwächen:** SMS/Zähler nur ausgehend; digitale Post/Mietvertrag kosten extra; keine tiefe WEG-Versammlungs-/Beschluss-Features im Vergleich zu etg24.

### 2.2 objego
- **Unternehmen:** Essen, Deutschland
- **Deployment:** Cloud SaaS
- **Preise:**
  - Basics: kostenlos (unbegrenzte Objekte, 1 GB Speicher, Finanzen, Dokumente, Zählerstand)
  - Verwaltung: 7,95 €/Monat für alle Einheiten (Vorlagen, Rechnungs-OCR, E/A-Export, Mieteingangskontrolle)
  - Nebenkosten: +0,95 €/WE/Monat (Betriebskostenabrechnung, Plausibilitätscheck, Heizkosten, Mietpreisrechner)
  - Premium: 12,95 €/Monat (laut heise) mit Gewerbe-NK, Logo-freie PDFs, unbegrenzter Speicher, Energieausweis
- **WE-Limit:** Max. 70 Nutzeinheiten empfohlen (für private Vermieter)
- **KI-Features:** Automatische Texterkennung von Rechnungen (Premium)
- **DATEV:** nicht explizit genannt; Anlage-V-Vorbereitung vorhanden
- **Mobile App:** Web-basiert / mobile Oberfläche nicht hervorgehoben
- **Mieterportal:** nicht prominent
- **DSGVO:** Hosting Deutschland
- **Tech-Stack:** TYPO3 CMS Marketingseite (React-Frontend-Fragmente), keine Vue-App erkennbar
- **Demo:** Kostenlos starten
- **Stärken:** Sehr günstig, unbegrenzte Objekte, gute Steuer-Exporte, intuitiv.
- **Schwächen:** Fokus kleine private Bestände, begrenzte WEG-/Profi-Features, keine Mieterkommunikation im Fokus.

### 2.3 Vermietet.de (ImmoScout24)
- **Unternehmen:** Scout24 / ImmoScout24, Berlin
- **Deployment:** Cloud SaaS
- **Preise:** 9,90 €/Monat Grundpreis inkl. 1 WE; jede weitere WE 0,99 €/Monat; 30 Tage kostenlos ohne Bankdaten
- **Funktionen:** Objektverwaltung, Mieterverwaltung, DMS, Einnahmen/Ausgaben, Anlage V, Nebenkostenabrechnung, Marktwert/Rendite, Rechnungsupload mit OCR, Instandhaltung, Neuvermietung alle 3 Monate kostenloses ImmoScout24-Basisinserat
- **KI-Features:** Dokumenten-Assistenz mit Analyse/Empfehlungen; OCR-Rechnungsupload
- **Mobile App:** Browser-basiert, keine eigene App prominent
- **Mieterportal:** nicht explizit
- **DATEV:** nicht explizit
- **DSGVO:** Scout24 Standards
- **Tech-Stack:** Ember.js (erkennbar an Marketing-Seite)
- **Demo:** 30 Tage kostenlos
- **Stärken:** Günstig, starke ImmoScout24-Inserate-Integration, Rendite-/Marktwertdaten, OCR.
- **Schwächen:** Kein echtes Mieterportal, keine DATEV, keine WEG-Verwaltung.

### 2.4 hausify
- **Unternehmen:** Berlin, Deutschland
- **Deployment:** Cloud SaaS + iOS/Android App
- **Preise:**
  - Free: 0 €/Monat (10 Einheiten, 1 Verwalter, alle Funktionen, hausify-Branding)
  - Plus: 19 €/Monat (100 WE, 2 MA, persönliche Live-Schulung)
  - Pro: 49 €/Monat (3.500 WE, 3 MA, eigenes Logo)
  - Top: 79 €/Monat (unbegrenzt WE/MA, individuelles Design)
- **Fokus:** Kommunikation/Ticketsystem, digitale Aushänge, Dokumentenmanagement, Rollen/Rechte
- **KI-Features:** keine explizit
- **Mobile App:** Ja (iOS/Android)
- **Mieterportal:** Zentrales Portal und App
- **DATEV:** keine
- **DSGVO:** EU-Hosting
- **Tech-Stack:** Wix Website Builder + React/Next Marketingseite
- **Demo:** Freemium
- **Stärken:** Hervorragendes Kommunikations- und Ticketsystem, gute Freemium-Option, schnelle Einrichtung.
- **Schwächen:** Keine Buchhaltung/Abrechnung (rein Portallösung), keine DATEV.

### 2.5 etg24
- **Unternehmen:** Walldorf, Deutschland (seit 2010)
- **Deployment:** Cloud Web-App + iOS/Android App
- **Preise Selbstverwalter:**
  - Basis: 3 Monate kostenlos, danach ab 25 €/Monat (heise); Website nennt ab 90 €/Monat? Widerspruch – heise-Werte vermutlich aktueller für Selbstverwalter
  - Plus: 59 €/Monat, Max: 99 €/Monat
- **Preise Profi-Verwalter:**
  - Basis: ab 90 €/Monat (3 Monate kostenlos)
  - Pro: ab 175,50 €/Monat
  - Enterprise: ab 400,50 €/Monat
- **Funktionen:** Kundenportal, Dokumente, Vorgangsbearbeitung/Ticketsystem, Aufgaben/Termine, Versammlungen, Umlaufbeschlüsse, Umfragen, Anrufmanagement, E-Mail-Inbox, Rechnungseingang, Zeiterfassung, Reporting, Aktivitätsverlauf, KI-Power
- **KI-Features:** „KI-Agent Aimo“; KI-Workflows; Rechnungen KI-unterstützt verarbeiten; Anfragen in strukturierte Vorgänge verwandeln
- **Mobile App:** Ja (Verwalter & Eigentümer/Mieter)
- **Mieterportal:** Ja
- **DATEV:** nicht explizit genannt
- **DSGVO:** Deutschland
- **Tech-Stack:** WordPress/Elementor Marketingseite; App unklar (React/Vermutung)
- **Demo:** Kostenlos testen
- **Stärken:** Tiefes WEG-/Versammlungsmanagement, Umlaufbeschlüsse, KI-Agent Aimo, sehr gute Kommunikation.
- **Schwächen:** Hohe Preise für kleine Vermieter; komplexer Einstieg.

### 2.6 INtex Hausverwaltung
- **Unternehmen:** INtex Publishing GmbH & Co. KG, Eitorf
- **Deployment:** Cloud SaaS oder On-Premises (eigener Server)
- **Preise Cloud (365 Tage):**
  - Standard: 99 € (bis 100 WE, 1 User)
  - XTended: 299 € (bis 200 WE, doppelte Buchführung, erweiterte WEG)
  - Premium: 399 € (bis 300 WE, Mandantenfähigkeit, Inventar, Bilanzierung)
  - Team: 799 € (unbegrenzt WE, bis 3 Nutzer)
- **On-Premises:** 2.499 € einmalig (3 Anwender + Admin)
- **Funktionen:** Adressverwaltung, Gebäudemanagement, Dokumentenablage, Vertragsverwaltung, Abrechnungen, Organizer, einfache/doppelte Buchführung, WEG-Funktionen, Rücklagen, Wirtschaftsplan, Ticketsystem, Excel-/Word-Vorlagen
- **KI-Features:** keine
- **Mobile App:** keine eigenständige App prominent
- **Mieterportal:** Eigentümer-/Mieterzugriff via Cloud
- **DATEV:** nicht explizit genannt
- **DSGVO:** Hosting & Entwicklung Deutschland, keine Datenweitergabe
- **Tech-Stack:** Eigenentwicklung/PHP-basierte Cloud-App
- **Demo:** Kostenlos testen
- **Stärken:** Sehr faire Preise, On-Premises-Option, starke Buchhaltung, WEG-Funktionen.
- **Schwächen:** Weniger moderne UX als immocloud/objego; begrenzte mobile App.

### 2.7 DOMUS 1000
- **Unternehmen:** DOMUS Software AG, Hohenbrunn bei München
- **Deployment:** Windows Desktop (Cloud-Modul optional); bis 500 WE
- **Preise:** nicht transparent, auf Anfrage; Testversion 70 Tage
- **Funktionen:** Buchen, Mahnen, Abrechnen; WEG-Verwaltung; Nebenkosten-/Heizkostenabrechnung; Adressmanagement; automatische Verwaltergebühr; Serienbriefe; Dokumentenmanagement; hybride Eigentümerversammlung; KI-Features im „Digital-Paket“/„DOMUS novio“
- **KI-Features:** DOMUS novio: KI-gestützte Automatisierung (neu)
- **Mobile App:** NAVILITY CRM TO GO für mobilen Zugriff
- **Mieterportal:** optional über Cloud-Modul
- **DATEV:** nicht explizit
- **DSGVO:** Deutschland
- **Tech-Stack:** Windows Desktop, moderne Cloud-Module
- **Demo:** 70 Tage Testversion
- **Stärken:** Sehr tief für professionelle Hausverwaltungen, langjährige Erfahrung, WEG-Stark.
- **Schwächen:** Windows-Desktop-Hauptprodukt, hoher Einführungsaufwand, keine transparenten Preise.

### 2.8 WISO Hausverwalter 365 / WISO Vermieter 365
- **Unternehmen:** Buhl Data Service
- **Deployment:** Windows Desktop; WISO Vermieter zusätzlich als Web-App
- **Preise WISO Vermieter 365:** 34,99 €/Jahr inkl. MwSt. (bis 5 WE); Zusatzmodul 5 WE für 20 €
- **Preise WISO Hausverwalter 365 Start:** 75,99 €/Jahr inkl. MwSt. (10 WE)
- **Preise WISO Hausverwalter 365 Plus:** 95,99 €/Jahr inkl. MwSt. (25 WE; erweiterbar bis 400 WE; Zusatzmodul 25 WE für 35 €)
- **Funktionen:** Mieter-/WEG-/Gewerbe-Verwaltung, Betriebskosten-/Heizkostenabrechnung, tagesgenaue Zähler/Verteilung, automatische Sollstellung, Online-Banking, Offene-Posten, Anlage V, Assistenten, DATEV-Export (Plus), Rechtsberatung optional (Vermieter)
- **KI-Features:** keine genannt
- **Mobile App:** Web-App für WISO Vermieter
- **Mieterportal:** keine
- **DATEV:** Hausverwalter 365 Plus mit DATEV-Export
- **DSGVO:** Deutschland
- **Tech-Stack:** Windows-Desktop, Web-App für Vermieter
- **Demo:** Kostenlos testen
- **Stärken:** Sehr günstig, starke Steuer/Anlage-V-Integration, DATEV, etabliert.
- **Schwächen:** Windows-zentriert, limitierte WE je Lizenz, keine Mieterkommunikation, keine Cloud-Kollaboration.

### 2.9 Win-CASA
- **Unternehmen:** Software24.com, Stephanskirchen
- **Deployment:** Windows Desktop oder Cloud-App aus deutschem RZ
- **Preise (monatlich netto):**
  - Starter: 29 € (bis 100 WE, 1 User, Miet- oder WEG, E-Mail-Support)
  - Professional: 49 € (bis 100 WE? bis 300/600/1000 WE Varianten, mehrere User, Telefon-Support, Bankkontenabgleich, DATEV, App, optional Online-Portal & Cloud)
  - Premium: 59 € (erweiterte Kommunikation, CRM/Vorgänge, Schnittstellen, Automatisierung)
- **Funktionen:** Miet- & WEG-Verwaltung, Buchhaltung, Zahlungsverkehr, Mahnwesen, Nebenkostenabrechnung, WEG-Abrechnung, Online-Portal, CASA24 Verwalter-App, DATEV, Bankkontenabgleich, Vulcavo Eigentümerversammlung, E-Post
- **KI-Features:** KI in Win-CASA: Eingangsrechnungen, Bankumsatz-Zuordnung, Textarbeit (Blog)
- **Mobile App:** CASA24 App
- **Mieterportal:** integriertes Online-Portal
- **DATEV:** ja
- **DSGVO:** Deutschland
- **Tech-Stack:** Windows Desktop, Cloud-Option
- **Demo:** 30 Tage kostenlos
- **Stärken:** Sehr günstig für große WE-Zahlen, Cloud/Desktop-Wahl, DATEV, Online-Portal, KI-OCR.
- **Schwächen:** Windows-Herkunft, etwas altmodischer Look, hohe Einarbeitung.

### 2.10 dataPad
- **Unternehmen:** Klosterneuburg, Österreich
- **Deployment:** Cloud Backend + App (iOS/Android)
- **Preise:** nicht transparent, kostenfrei testen
- **Fokus:** Digitale Wohnungsübergabe/-rücknahme, Objektbegehung, Zählerstände, Schlüsselübergabe, Unterschrift direkt am Tablet, Bilddokumentation
- **KI-Features:** keine
- **Mobile App:** Kernprodukt
- **Mieterportal:** keine
- **DATEV:** Schnittstelle zu beliebiger Verwaltungssoftware
- **DSGVO:** Österreich/Cloud
- **Tech-Stack:** unklar
- **Demo:** kostenlos testen
- **Stärken:** Hervorragend für Übergabeprotokolle, bildbasierte Zustandserfassung.
- **Schwächen:** Keine vollständige Verwaltungssoftware, nur Formular-/Übergabe-Tool.

---

## 3. Demo-Versionen

| Produkt | Demo/Trial | Dauer | Zahlungsdaten nötig | Bemerkung |
|---------|------------|-------|---------------------|-----------|
| immocloud | Online-Demo | 45 Tage | nein | Kostenlos testen auf Webseite |
| objego | Online-Demo | kostenlos | nein | Starter-Version permanent kostenlos |
| Vermietet.de | Online-Demo | 30 Tage | nein | VermietenPlus |
| hausify | Freemium | dauerhaft | nein | Free bis 10 WE |
| etg24 | Online-Demo | kostenlos | nein | Basis 3 Monate kostenfrei |
| INtex | Online-Demo | kostenlos | nein | Cloud-Testzugang |
| DOMUS 1000 | Download | 70 Tage | nein | Testversion beim Hersteller anfordern |
| WISO | Download/Web | kostenlos | nein | Testversion verfügbar |
| Win-CASA | Download | 30 Tage | nein | 30-Tage-Testversion |
| dataPad | App-Demo | kostenlos | nein | Formular-App testen |

### Besonderheit: Keine Online-Demo-Registrierung durchgeführt
Aus Zeitgründen wurde keine vollständige Account-Registrierung mit YOPmail für die Online-Demos durchgeführt. Alle getesteten Seiten liefern aber klare „Kostenlos testen“-Call-to-Actions ohne Kreditkarte.

---

## 4. Reverse Engineering / Tech-Stacks

| Produkt | Marketing-Seite | Web-App | Erkennbare Frameworks | Bemerkungen |
|---------|-----------------|---------|----------------------|-------------|
| immocloud | WordPress + WP Rocket | app.immocloud.de/login | Vue.js, Google Maps, Intercom, Hotjar | Moderne SPA |
| objego | TYPO3 CMS | unklar | React-Fragmente | Marketing stark TYPO3 |
| Vermietet.de | Ember.js | unklar | Ember | Scout24-Stack |
| hausify | Wix + React/Next | unklar | React/Next | No-Code-Website |
| etg24 | WordPress/Elementor | unklar | WordPress Marketing | App-Stack unklar |
| INtex | Eigenentwicklung | unklar | PHP/eigene Cloud | klassisch |
| DOMUS 1000 | WordPress | Windows | Desktop | keine Web-App |
| WISO | WordPress/Eigen | Web-App | unklar | Windows + Web |
| Win-CASA | WordPress | Windows/Cloud | Desktop | Cloud-App verfügbar |
| dataPad | unklar | App | unklar | App-zentriert |

### API-/Netzwerk-Beobachtung
Eine tiefe Network-Tracing via CDP wurde nicht durchgeführt. Bei Bedarf kann die Web-App von immocloud (Vue) oder etg24 auf API-Endpunkte, Sourcemaps und Bundle-Struktur weiter analysiert werden.

---

## 5. Vergleichstabelle: MietVerwaltung vs. Wettbewerb

### 5.1 Must-Have-Features (heise nennt sie explizit)

| Feature | MietVerwaltung | immocloud | objego | Vermietet.de | hausify | INtex | WISO | Win-CASA | etg24 | DOMUS |
|---------|---------------|-----------|--------|--------------|---------|-------|------|----------|-------|-------|
| Nebenkostenabrechnung | ? | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Heizkostenabrechnung | ? | ✅ | ✅ (Add-on) | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mieteingangskontrolle/Zahlungsausfälle | ? | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dokumentenmanagement | ? | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Anlage V / Steuer | ? | DATEV-Export | Anlage-V-Export | Anlage V | ❌ | Anlage V | ✅ | DATEV | ? | ? |
| DATEV-Schnittstelle | ? | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ (Plus) | ✅ | ❌ | ? |
| Mieterportal / Kommunikation | ? | ✅ Mieterportal | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | optional |
| Mobile App | ? | ✅ | Web | ❌ | ✅ | ❌ | Web (Vermieter) | ✅ | ✅ | ✅ (CRM TO GO) |
| WEG-Verwaltung | ? | begrenzt | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DSGVO-konform / DE-Hosting | ? | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| KI-Features | ? | ✅ OCR | ✅ OCR | ✅ OCR | ❌ | ❌ | ❌ | ✅ (OCR/Text) | ✅ KI-Agent | ✅ |
| Freemium/ kostenloser Einstieg | ? | 45 Tage | Free-Starter | 30 Tage | Free | Test | Test | Test | 3 Monate | 70 Tage |

**Legende:** ✅ vorhanden / stark; ❌ fehlt / schwach; ? = MietVerwaltung-Status unbekannt (muss abgeglichen werden).

### 5.2 Wo MietVerwaltung vermutlich besser sein kann
- **Fokus auf DACH Kleinvermieter:** Wettbewerber wie immocloud/objego sind breiter aufgestellt; etg24/DOMUS zielen auf Profiverwalter.
- **Preis-Leistung im Kleinbestand:** Objego/Vermietet.de/haushalten unter 10 WE sind sehr günstig; hier ist ein klarer Preisvorteil oder Mehrwert nötig.
- **Moderne Cloud-Native UX:** immocloud und objego setzen Maßstäbe.
- **Mieterportal + Ticketsystem:** hausify ist hier sehr stark; Kombination aus Abrechnung + Kommunikation ist unterbesetzt.

### 5.3 Wo Wettbewerber deutlich besser sind
- **WEG-/Versammlungsmanagement:** etg24, DOMUS, INtex, Win-CASA haben tiefe WEG-Funktionen (Versammlungen, Umlaufbeschlüsse, Rücklagen).
- **Buchhaltung/Steuer:** WISO, INtex, Win-CASA, immocloud haben DATEV oder starke Anlage-V-Integration.
- **KI-Agent:** etg24 mit „Aimo“ und KI-Workflows ist hier führend.
- **Mobile Apps:** etg24, hausify, immocloud, Win-CASA haben starke Apps.
- **On-Premises:** INtex und Win-CASA bieten Datensouveränität.
- **Marktdaten/Neuvermietung:** Vermietet.de mit ImmoScout24-Integration und Marktwertdaten.

---

## 6. Empfehlungen für MietVerwaltung

### 6.1 MVP-Must-Haves (weil heise sie als wichtig nennt)
1. **Nebenkostenabrechnung** – rechtskonform, BetrKV/HeizkostenV, Verteilungsschlüssel, tagesgenaue Mieterwechsel.
2. **Heizkostenabrechnung** – Grund-/Verbrauchsanteil, Zählerstands-Erfassung.
3. **Mieteingangskontrolle / Zahlungserinnerungen** – wer hat gezahlt, wer nicht.
4. **Dokumentenmanagement** – Upload, Kategorisierung, DSGVO-konformes DE-Hosting.
5. **Anlage V / Steuerexport** – mindestens CSV/Excel für Steuerberater, idealerweise DATEV-Export.
6. **Mieterportal / zentrale Kommunikation** – Dokumente bereitstellen, Nachrichten, Schadensmeldungen.
7. **Mobile App / responsive Web** – Zählerstände erfassen, Belege scannen, Übergabeprotokoll.
8. **DSGVO & DE-Hosting** – zertifizierte Rechenzentren, AES256, Vertragspartner nennen.
9. **Digitale Wohnungsübergabe** – Protokoll, Unterschrift, Bilder (kann MVP+ sein).
10. **Freemium oder kostenlose Testphase** – heise empfiehlt Demos; Konkurrenz bietet 30–45 Tage ohne Zahlungsdaten.

### 6.2 Roadmap-Features (Nice-to-Have / Differenzierung)
1. **KI-OCR für Rechnungen & Belege** – immocloud, objego, Vermietet.de, etg24, Win-CASA haben das bereits.
2. **DATEV-Schnittstelle** – heise nennt sie als wichtiges Kriterium; WISO/immocloud/Win-CASA haben sie.
3. **WEG-Verwaltung** – Versammlungen, Umlaufbeschlüsse, Rücklagen, Wirtschaftsplan.
4. **Ticketsystem / digitale Aushänge** – hausify-USP.
5. **Marktwert/Rendite-Tool** – Vermietet.de-USP.
6. **ImmoScout24-Inserate-Integration** – Vermietet.de-USP.
7. **KI-Agent / Chatbot für Mieteranfragen** – etg24-Aimo.
8. **On-Premises-Option** – INtex/Win-CASA für Datensouveränität.

### 6.3 Größter USP gegenüber Konkurrenz
- **Kombination aus günstiger Cloud-Abrechnung + Mieterportal + Ticketsystem** – hausify macht Kommunikation, immocloud/objego machen Abrechnung; eine Lösung, die beides für Kleinvermieter vereint, ist unterrepräsentiert.
- **Modernste UX + sofort einsatzbereit ohne Schulung** – heise lobt objego/immocloud genau dafür.
- **Transparente, steuerlich absetzbare Flatrate-Preise** – Konkurrenz hat oft pro-Einheit- oder Add-on-Modelle.

### 6.4 Preis-Positioning-Empfehlung
| Zielgruppe | Empfohlene Positionierung | Vergleich |
|------------|---------------------------|-----------|
| 1–5 WE (privat) | **Kostenlos oder 0–9,99 €/Monat** | immocloud Starter 9,99 €; objego 0 €; Vermietet.de 9,90 € |
| 6–20 WE (kleine Vermieter) | **14,99–19,99 €/Monat** | immocloud Manager 15,99 €; objego 7,95 € + NK |
| 21–50 WE (Portfolio) | **29,99–39,99 €/Monat** | immocloud Investor 39,99 €; Win-CASA Professional 49 € |
| 50+ WE / Hausverwaltungen | **Auf Anfrage / Tycoon-Modell** | immocloud Tycoon; etg24 ab 175 € |

**Empfehlung:**
- Einen **kostenlosen Starter für bis zu 3 WE** anbieten (wie objego/hausify), um Nutzer zu gewinnen.
- Einen **Einsteigertarif für 9,99 €/Monat bis 5 WE** mit allen Basisfunktionen (immocloud-Vorbild).
- **Transparente Preise ohne versteckte Add-ons** – heise und Nutzer loben Win-CASA dafür.
- **Jährliche Zahlung mit Rabatt** (10–15 %) wie immocloud/Win-CASA.

### 6.5 Konkrete Handlungsempfehlungen
1. **MVP sofort sicherstellen:** Nebenkosten-, Heizkostenabrechnung, Mieteingangskontrolle, DMS, Anlage-V-Export, Mieterportal.
2. **DATEV-Export priorisieren:** heise nennt es als wichtiges Kriterium – nur wenige Mitbewerber haben es.
3. **KI-OCR für Belege einplanen:** Wettbewerber wie immocloud werben damit stark.
4. **Mobile App/Web parallel entwickeln:** Zählerstandserfassung und Beleg-Scanning sind erwartet.
5. **DSGVO/DE-Hosting prominent kommunizieren:** heise empfiehlt ausdrücklich deutsche/EWR-Anbieter.
6. **WEG-Module später ergänzen:** Nicht im MVP, aber wichtig für professionelle Hausverwaltungen.
7. **Demo ohne Zahlungsdaten:** 30–45 Tage kostenlos ist Industriestandard.
8. **Vergleichsseite „immocloud vs. MietVerwaltung“ etc.** erstellen, um SEO und Kaufentscheidung zu beeinflussen.

---

## 7. Dateien dieser Analyse

Im Projektordner `/root/mietverwaltung/` wurden gespeichert:
- `heise-konkurrenten-analyse.md` (diese Datei)
- `heise-article.txt` (vollständiger Artikeltext)
- `heise-links.json` (alle Links)
- `immocloud-*.txt/json` (Home, Funktionen, Preise, Scripts, Tech)
- `objego-*.txt/json` (Home, Preise, Tech)
- `vermietet-*.txt/json` (Home, Preise, Tech)
- `hausify-*.txt/json` (Home, Preise, Tech)
- `etg24-*.txt/json` (Home, Verwaltungen, Preise, Tech)
- `intex-*.txt/json` (Home, Preise, Tech)
- `domus-*.txt/json` (Home, Tech)
- `wiso-*.txt` (Hausverwalter, Vermieter)
- `wincasa-*.txt/json/html` (Home, Preise, Tech)
- `datapad-*.txt/json` (Home, Tech)

---

*Analyse basiert auf öffentlich zugänglichen Webseiten und dem heise-Artikel vom Februar 2025. Preise und Funktionen können sich geändert haben; vor Produktentscheidungen sollten die Herstellerseiten erneut geprüft werden.*
