# Google SaaS-Design-Recherche für MietVerwaltung

**Kontext:** MietVerwaltung SaaS (FastAPI + Vue.js)  
**Ziel:** Google-offizielle Empfehlungen für SaaS UX/UI, Material Design, Performance, Architektur und Patterns zusammenfassen und auf unsere Anwendung übertragen.

---

## 1. Google Material Design 3 (Material You) — aktuelle Prinzipien für Web-Apps

### Was Google empfiehlt

Material Design 3 ist Googles aktuelles, adaptives Design-System aus Richtlinien, Komponenten und Open-Source-Code.[1] Material You (M3) erweitert dies um drei Grundprinzipien:[2]

- **Personal for every style:** Personalisierung über dynamische Farbpaletten, abgeleitet von einem persönlichen Signal (z. B. Wallpaper). Das kann auf jede App – nicht nur Google-Apps – in Echtzeit angewendet werden.
- **Alive & Adaptive for every screen:** Das UI reagiert auf Bildschirmgrößen, Gerätetypen, Eingabemodalitäten und Kontext. Bewegung hilft, Raum zu verstehen, Marke zu transportieren und Vertrauen zu schaffen.
- **Accessible for every need:** Barrierefreiheit ist Kernwert. Steuerung von Kontrast, Größe und Linienbreite soll universell für Menschen mit dauerhaften oder situativen Einschränkungen funktionieren.

M3 gliedert sich in Foundations: Accessibility, Content Design, Customizing, Design Tokens, Interaction (States, Gestures, Inputs), Layout (Breakpoints, Grids, Spacing) und Usability.[1] Design Tokens speichern Stilwerte wie Farben und Schriften, damit dieselben Werte in Design, Code, Tools und Plattformen genutzt werden können.[1]

### Anwendbarkeit auf MietVerwaltung

- FastAPI + Vue.js passt gut zu Material Web, der offiziellen Web-Komponentenbibliothek von Google.[1]
- Eine Property-Management-SaaS hat viele wiederkehrende UI-Muster (Listen, Formulare, Dashboards, Dialoge) – hier bietet Material 3 fertige, barrierefreie Komponenten.
- „Personal for every style“ ist für B2B-SaaS weniger relevant als dynamische Wallpaper-Farben, aber das Prinzip der konsistenten Design-Tokens und Brand-Anpassbarkeit ist direkt übertragbar.

### Patterns, die wir übernehmen sollten

1. **Design-Token-System** für Farben, Typografie, Abstände und Radien in Figma und CSS/SCSS etablieren.
2. **Material Web (MDC-Web) oder Vuetify 3 mit Material 3** als Komponentenbasis nutzen.
3. **Adaptive Layouts** mit Breakpoints für Desktop (Büro), Tablet (Vor-Ort) und Mobile (unterwegs).
4. **Motion & Feedback** gezielt einsetzen: z. B. sanfte Übergänge bei Seitenwechseln, Ripple-Feedback auf Buttons.
5. **Barrierefreiheit by default** in jeder Komponente (Kontrast, Fokus-States, ARIA-Semantik) – Accessibility ist ein Kernwert von Material Design.[3]

---

## 2. Google's HEART Framework

### Was Google empfiehlt

HEART ist Googles Framework für nutzerzentrierte Metriken auf großer Skala, entwickelt von Kerry Rodden, Hilary Hutchinson und Xin Fu (CHI 2010).[7] Es umfasst fünf Kategorien:[7]

| Kategorie | Beschreibung | Beispiel-Metriken |
|-----------|--------------|-------------------|
| **Happiness** | Einstellung, subjektiv | Zufriedenheit, visuelle Attraktivität, NPS, wahrgenommene Einfachheit |
| **Engagement** | Intensität der Nutzung | Visits pro Woche, erledigte Vorgänge pro Tag, Tiefe der Interaktion |
| **Adoption** | Neue Nutzer gewinnen | Accounts in 7 Tagen, Abschluss des ersten Mieter-Anlegens |
| **Retention** | Bestehende Nutzer halten | % Nutzer, die nach 90 Tagen noch aktiv sind |
| **Task Success** | Effektivität & Effizienz | Task-Completion-Rate, Zeit pro Aufgabe, Fehlerrate |

Google betont, dass nicht immer alle fünf Kategorien sinnvoll sind. Im Enterprise-Kontext kann Engagement weniger relevant sein; dann liegt der Fokus auf Happiness und Task Success.[7]

HEART wird mit dem **Goals-Signals-Metrics-Prozess** operationalisiert:[7]

1. **Goals:** Produkt-/Feature-Ziele aus Nutzerperspektive definieren.
2. **Signals:** Verhaltens- oder attitudinale Indikatoren finden, die Erfolg/Misserfolg anzeigen.
3. **Metrics:** Spezifische, dashboard-taugliche Kennzahlen ableiten, idealerweise als Ratio, Prozentsatz oder Durchschnitt pro Nutzer (nicht rohe Counts).

### Anwendbarkeit auf MietVerwaltung

- MietVerwaltung ist ein Enterprise-/B2B-SaaS: Nutzer haben klare Aufgaben (Mietvertrag anlegen, Mieter verwalten, Zahlung erfassen, Mahnung erstellen).
- Task Success ist daher die zentrale Kategorie.
- Adoption/Retention messen, wie gut Vermieter von der Onboarding-Phase in die produktive Nutzung übergehen.
- Happiness hilft, Zufriedenheit mit UI-Klarheit und Arbeitsfluss zu erfassen.

### Patterns, die wir übernehmen sollten

1. **Event-basiertes Tracking** für Key Tasks (z. B. erster Mietvertrag, erste Mahnung, erste Übersichtsansicht).
2. **Task-Completion-Funnels** für wiederkehrende Workflows (Mietvertrag anlegen → Mieter zuordnen → Miete hinterlegen).
3. **In-Product-Survey** (z. B. CES nach erstem Workflow) für Happiness.
4. **Cohort-Retention** (7/30/90 Tage) nach erstem erfolgreichem Task, nicht nur nach Login.
5. **Dashboard** für Product/UX-Team mit HEART-Metriken, segmentiert nach Nutzerrolle (Vermieter vs. Hausverwaltung).

---

## 3. Google's PULSE Framework

### Was Google empfiehlt

PULSE steht für **Page views, Uptime, Latency, Seven-day active users, Earnings**. Es beschreibt die gängigen großskaligen Metriken für Geschäfts- und Technikgesundheit, die viele Organisationen bereits tracken.[7]

Google kritisiert PULSE als ergänzend, aber unzureichend für UX-Entscheidungen:[7]

- Seitenaufrufe und 7-Tage-aktive Nutzer sind indirekt und mehrdeutig (mehr Klicks können auch Verwirrung bedeuten).
- Uptime und Latency sind technische Gesundheitsmetriken, keine UX-Metriken.
- PULSE unterscheidet nicht zwischen neuen und zurückkehrenden Nutzern.
- Kurzfristige Einnahmen können langfristig schlechte UX verbergen.

PULSE wird daher als **Ergänzung zu HEART** gesehen, nicht als Ersatz.[7]

### Anwendbarkeit auf MietVerwaltung

- PULSE-Metriken (Uptime, Latency, Earnings, MAU/WAU) werden im Betrieb ohnehin gemessen.
- Für Design-Entscheidungen sollten wir sie mit HEART kombinieren, um nicht nur „läuft das System“, sondern „kann der Nutzer seine Aufgabe erfüllen“ zu beantworten.

### Patterns, die wir übernehmen sollten

1. **PULSE + HEART zusammenführen** in einem Monitoring-Dashboard.
2. **Bei A/B-Tests immer HEART-Metriken** (Task Success, Happiness) neben Conversion/Earnings betrachten.
3. **Seven-day-active durch Adoption + Retention ersetzen/ergänzen**, um Neukunden von Stammkunden zu trennen.

---

## 4. Google's Design Sprint Methodologie

### Was Google empfiehlt

Der Google Design Sprint ist ein zeitlich begrenzter Prozess, um kritische Geschäftsfragen durch Design, Prototyping und Testen mit echten Nutzern zu beantworten.[8] Das offizielle Google-Kit definiert sechs Phasen:[8]

1. **Understand** – Nutzer, Bedürfnisse, Kontext und Wettbewerb verstehen.
2. **Define** – Problemstellung und Sprint-Ziel definieren.
3. **Sketch** – Lösungen visualisieren und Ideen sammeln.
4. **Decide** – Die beste Idee auswählen.
5. **Prototype** – Prototyp bauen, der Usability vor Design-Polish priorisiert.
6. **Validate** – Mit echten Nutzern testen.

Sprints können 1–5 Tage dauern; 3–4 Tage werden empfohlen, um alle Phasen sinnvoll durchlaufen zu können.[8]

### Anwendbarkeit auf MietVerwaltung

- Design Sprints eignen sich für große Feature-Entscheidungen (z. B. „Wie sieht das ideale Mieter-Onboarding aus?“ oder „Wie optimieren wir die Mahnungs-Erstellung?“).
- Sie sparen 4–6 Wochen Entwicklungszeit, weil das Team sich vor dem Build auf ein getestetes Konzept einigt.[8]

### Patterns, die wir übernehmen sollten

1. **Sprint vor großen Features** (z. B. Neugestaltung Dashboard, Onboarding, Dokumentenverwaltung).
2. **Prototypen mit echten Vermieter-Nutzern testen**, nicht nur interne Stakeholder.
3. **Sketch-Phase für mehrere Lösungsvarianten**, dann strukturiert entscheiden.
4. **Sprint-Team interdisziplinär** besetzen: Produkt, UX, Entwicklung (FastAPI/Vue), Content, Vertrieb/Customer Success.

---

## 5. Google Web.dev — SaaS Performance & UX Guidelines

### Was Google empfiehlt

web.dev ist Googles zentrale Plattform für Web-Performance und UX-Qualität. Die zentrale Aussage: „Optimizing for quality of user experience is key to the long-term success of any site on the web.“[9] Wichtige Leitlinien:[10][11]

- **Core Web Vitals** messen und optimieren (siehe Kapitel 6).
- **Offline/instabile Verbindungen berücksichtigen:** Status kommunizieren, Tasks queuen, Hintergrund-Sync ermöglichen, Low-Bandwidth-Optionen anbieten.[10]
- **Inclusive Design:** Klare Sprache, Standard-Icons mit Textlabeln, sinnvolle Bilder und Farbcodierung.[10]
- **Performance-Budgets** setzen und durchsetzen, damit das Team auch nach Launch schnell bleibt.[11]
- **Lighthouse & PageSpeed Insights** nutzen, um Performance, Accessibility, Best Practices, SEO und PWA zu prüfen.[11]
- **Ressourcen-Inventur:** Jeden Asset auf seinen Performance-Impact prüfen; Code Splitting statt monolithischem JavaScript-Bundle.[11]

### Anwendbarkeit auf MietVerwaltung

- Mietverwalter arbeiten oft mobil vor Ort (schlechtes Netz) oder im Büro mit vielen Tabs. Performance und Offline-Resilienz sind kritisch.
- Formular-lastige SaaS profitiert besonders von schnellem LCP, niedrigem INP und stabilem CLS.
- Eine PWA-Architektur ermöglicht Teildaten lokal zu cachen (z. B. Mieterliste, Mietverträge).

### Patterns, die wir übernehmen sollten

1. **Lighthouse CI** in den Build-Prozess integrieren (Performance-Budgets automatisch prüfen).
2. **Service Worker / PWA** für Offline-Lesen von Mieter- und Vertragsdaten.
3. **Skelett-Screens und Progress-Indikatoren** für Datenzugriffe, besonders auf mobilen Netzen.
4. **Knappe, klare UI-Texte** ohne Fachjargon; Icons immer mit Labels kombinieren.
5. **web-vitals JS-Library** einbinden und reale Nutzermetriken an Analytics senden.[9]

---

## 6. Google's Core Web Vitals — LCP, INP, CLS für SaaS

### Was Google empfiehlt

Core Web Vitals sind die Teilmenge der Web Vitals, die für alle Webseiten gelten und in allen Google-Tools sichtbar werden.[9] Die aktuellen drei Metriken:[9]

| Metrik | Was sie misst | Guter Wert (75. Perzentil) |
|--------|---------------|----------------------------|
| **LCP** (Largest Contentful Paint) | Lade-Performance | ≤ 2,5 s |
| **INP** (Interaction to Next Paint) | Interaktivität/Reaktionsfähigkeit | ≤ 200 ms |
| **CLS** (Cumulative Layout Shift) | Visuelle Stabilität | ≤ 0,1 |

INP hat First Input Delay (FID) ersetzt, weil es die gesamte Interaktionsqualität während des Besuchs besser abbildet.[9] Google empfiehlt, diese Werte am **75. Perzentil** mobiler und desktop Nutzer zu messen.[9]

### Anwendbarkeit auf MietVerwaltung

- LCP: Dashboards und Listen schnell sichtbar machen, damit Nutzer sofort arbeiten können.
- INP: Formulare, Tabellen-Sortierungen, Filter und Dialoge müssen sofort reagieren.
- CLS: Kein Springen von Buttons/Formularen, wenn Daten nachgeladen werden.

### Patterns, die wir übernehmen sollten

1. **LCP-Optimierung:** Hero-Elemente (Dashboard-Header, erste Tabellenzeilen) priorisiert laden; Server-Side Rendering oder statisches Caching für initialen Content.
2. **INP-Optimierung:** Lange JavaScript-Operationen in Tasks aufteilen; Vue-Komponenten gezielt lazy-loaden.
3. **CLS-Optimierung:** Feste Platzhalter für asynchron geladene Inhalte; Bilder/Charts mit definierten Dimensionen.
4. **Monitoring:** PageSpeed Insights + Search Console Core Web Vitals Report + eigene RUM-Daten via web-vitals Library.[9]

---

## 7. Google Cloud's SaaS Architecture Best Practices

### Was Google empfiehlt

Google Cloud bietet zwei relevante Leitlinien für SaaS:

**a) Well-Architected Framework**[12]

Sechs Säulen: Operational Excellence, Security/Privacy/Compliance, Reliability, Cost Optimization, Performance Optimization, Sustainability. Kerngedanken:[12]

- **Design for change:** Kleine, regelmäßige Änderungen mit schnellem Feedback.
- **Document your architecture:** Dokumentation mit Use-Case-Kontext, Entscheidungsprotokoll und Change-Log.
- **Simplify and use managed services:** MVP-Start, keine Over-Engineering, wo möglich vollverwaltete Services nutzen.
- **Decouple your architecture:** Lose gekoppelte Komponenten ermöglichen unabhängige Upgrades, Sicherheitskontrollen, Zuverlässigkeitsziele und Kostensteuerung pro Subsystem.
- **Stateless architecture:** Erhöht Skalierbarkeit und Widerstandsfähigkeit bei Neustarts.

**b) SaaS Runtime / Multi-Tenancy**[13]

- **Ein Google-Cloud-Projekt pro Tenant** empfohlen, um IAM, Netzwerk, Kosten und Ressourcen klar zu trennen.
- **Producer-Project** für die SaaS-Konfiguration, **Tenant-Projects** für Kundenressourcen.
- **Automatisierter Tenant-Onboarding** mit Terraform (provisional unit kind).
- **Separate Actuation-Service-Accounts** pro Tenant.
- **APIs müssen im Tenant-Projekt aktiviert** sein.

### Anwendbarkeit auf MietVerwaltung

- MietVerwaltung ist eine Multi-Tenant-SaaS (mehrere Vermieter/Hausverwaltungen teilen eine Plattform, Daten müssen isoliert sein).
- Das Framework hilft, Security, Compliance (Datenschutz), Kosten pro Mandant und Performance gezielt zu adressieren.

### Patterns, die wir übernehmen sollten

1. **Tenant-Isolation** auf Daten- und Berechtigungsebene (ggf. später ein GCP-Projekt pro großer Kunde).
2. **Stateless FastAPI-Services** mit getrenntem Storage/Cache (Cloud SQL, Cloud Storage, Redis).
3. **API-First & decoupled:** Services (Mieter, Verträge, Zahlungen, Dokumente) klar voneinander trennen.
4. **Infrastructure as Code** für wiederholbares, auditierbares Deployment pro Umgebung/Kunde.
5. **Entscheidungsprotokoll (Architecture Decision Records)** führen, warum FastAPI/Vue/Tenant-Modell gewählt wurde.

---

## 8. Google Workspace UX Patterns — wie Google eigene Apps designt

### Was Google empfiehlt

Google Workspace-Add-ons sollen sich nahtlos in die Host-App einfügen und vertraute Controls und Verhaltensweisen nutzen.[14] Wichtige UX-Patterns:[14]

- **Kurze, klare Texte:** Die meisten Aktionen sollen über Iconografie, Layout und kurze Labels verständlich sein.
- **Satzgroßschreibung (sentence case)** für Buttons, Labels und Card-Actions.
- **Buttons starten mit Verben**, maximal 3 Buttons in einer Reihe.
- **Fehlermeldungen nutzerfreundlich:** Klare Erklärung + Lösung statt technischer Jargon oder Exceptions.
- **Branding dezent:** Kurz, einfach, keine Google-Produktnamen oder -Icons verwenden.
- **Kontextabhängige Hilfe:** Wenn ein Bereich mehr Erklärung braucht als ein kurzes Label, separate Hilfeseite verlinken.

### Anwendbarkeit auf MietVerwaltung

- Auch MietVerwaltung ist eine produktive Arbeitsanwendung, in der Nutzer täglich viele kleine Aufgaben erledigen. Klarheit und Geschwindigkeit stehen vor Visueller Dramaturgie.
- Vermieter sind oft keine UX-Profis; daher sind vertraute Patterns und konsistente Labels wichtig.

### Patterns, die wir übernehmen sollten

1. **Sentence case** für alle UI-Texte in Deutsch (außer Eigennamen/Marken).
2. **Button-Labels immer als Verb-Phrase** („Mietvertrag anlegen“, „Mahnung erstellen“, „Mieter speichern“).
3. **Maximal 3 primäre Aktionen pro Card/Dialog**; sekundäre Aktionen in Menüs auslagern.
4. **Fehlermeldungen nach Schema:** Was ist passiert → Was bedeutet das → Was kann der Nutzer tun.
5. **Inline-Hilfe und Tooltips** für fachliche Begriffe (Nebenkostenabrechnung, Kautionskonto).

---

## 9. Google's Research on Onboarding Flows

### Was Google empfiehlt

Material Design definiert Onboarding als „warm welcome“ – die erste Erfahrung neuer Nutzer. Ziel: Nutzer begrüßen, den Nutzen vermitteln und zu Aktionen führen, die Engagement in der ersten Session und Retention in den ersten 7 Tagen erhöhen.[6]

Drei Onboarding-Modelle:[6]

| Modell | Wann nutzen | Beschreibung |
|--------|-------------|--------------|
| **Self-Select** | UI anpassbar, Setup-/Consent-Anforderungen | Kurze Auswahl, die das Erlebnis personalisiert |
| **Quickstart** | Bekannte UI, einfaches Setup | Nutzer landet direkt in der App; optionaler Hilfe-Button |
| **Top User Benefits** | Neues Produkt, neue Art des Nutzens, große UI-Änderungen | Kurzer Autoplay-Carousel mit bis zu 3 Kernnutzen |

Material empfiehlt:[6]

- Onboarding nur Erstnutzern zeigen, nicht zurückkehrenden Nutzern.
- Entscheidungen im Self-Select-Modell müssen **meaningful, noticeable, new information, short** sein.
- Nach Onboarding sollte der Nutzer auf einem Screen landen, auf dem er sofort handeln kann.
- Wenn der Nutzer gegen Ende der ersten Session unsicher wirkt, UI-Prompt mit Lernangebot anzeigen.

### Anwendbarkeit auf MietVerwaltung

- Der erste Erfolg in MietVerwaltung ist entscheidend: erster Mietvertrag angelegt, erster Mieter erfasst oder erste Miete verbucht.
- Ein zu langes Onboarding würde Fachnutzer abschrecken; Quickstart + kontextuelle Tipps ist wahrscheinlich der richtige Weg.

### Patterns, die wir übernehmen sollten

1. **Quickstart als Default:** Nutzer nach Login direkt aufs Dashboard leiten.
2. **Self-Select optional:** Branche/Vermieter-Typ während der ersten Einrichtung abfragen, um Vorlagen zu personalisieren.
3. **Kontextuelle Coach-Marks/Tooltips** anstatt eines langen Walkthroughs (z. B. „Hier legen Sie Ihren ersten Mietvertrag an“).
4. **First-Success-Tracking:** Messen, wie viele Nutzer in den ersten 24 h den ersten Task abschließen.
5. **Onboarding nur einmal** anzeigen; bei späteren Logins sofort zur Arbeitsoberfläche.

---

## 10. Google's Guidelines für Empty States, Error States, Loading States

### Was Google empfiehlt

Material Design behandelt diese States nicht als Nachgedanken, sondern als gleichberechtigte Patterns.[5]

**Empty States** treten auf, wenn Inhalt nicht angezeigt werden kann (leere Liste, keine Suchergebnisse). Eine gute Empty State zeigt:[5]

- ein neutrales, nicht-interaktives Bild,
- einen positiven, markenkonsistenten Tagline, der den Zweck vermittelt, ohne wie ein Call-to-Action zu wirken,
- Alternativen wie Starter-Inhalte, Bildungsinhalte oder „Best Match“-Vorschläge.

**Error States** (zusammen mit Confirmation & Acknowledgement):[4]

- Kommunizieren, was fehlgeschlagen ist.
- Klären, ob Daten gespeichert wurden oder nicht.
- Bieten Recovery (Retry, alternativer Pfad).
- Error-Messages als supporting Text unterhalb des betroffenen Feldes anzeigen.

**Loading States:**[4]

- Skelett-Screens für strukturierte Inhalte.
- Fortschrittsanzeige, wenn die Dauer messbar ist.
- Nicht-blockierende Indikatoren, wo möglich.
- Klare Labels für lange Operationen.

Google betont außerdem, dass Loading, Empty und Error unterschiedlich aussehen müssen, damit Nutzer nicht einen Spinner mit einer dauerhaft leeren Liste verwechseln.[4]

### Anwendbarkeit auf MietVerwaltung

- Leere Listen sind typisch: noch keine Mieter, keine Mietverträge, keine offenen Zahlungen.
- Fehler können fachlich kritisch sein (z. B. Mahnung konnte nicht erstellt werden, Zahlungsimport fehlgeschlagen).
- Ladezeiten treten bei Berichten, Imports und Dashboard-Daten auf.

### Patterns, die wir übernehmen sollten

1. **Empty-State-Komponente** mit Illustration, erklärendem Text und primärer Aktion („Ersten Mieter anlegen“).
2. **Starter-Inhalte/Vorlagen** anbieten: Beispiel-Mietvertrag, Beispiel-Mieter, damit Nutzer sofort erkunden können.
3. **Fehler-State-Template:** Was ist passiert → Warum → Wie beheben → Retry/Alternativpfad.
4. **Skelett-Screens** für Dashboard und Listen; Spinner nur für kurze, unbestimmte Operationen.
5. **Klare Trennung** zwischen Loading, Empty und Error: nie denselben visuellen Zustand für mehrere Bedeutungen verwenden.

---

## Zusammenfassung: Top-Prioritäten für MietVerwaltung

| Priorität | Maßnahme | Google-Quelle |
|-----------|----------|---------------|
| 1 | Material 3 Design-System + Design Tokens etablieren | [1][2] |
| 2 | HEART-Metriken mit Fokus Task Success + Retention einführen | [7] |
| 3 | Core Web Vitals (LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1) garantieren | [9][11] |
| 4 | Quickstart-Onboarding + First-Success-Tracking | [6] |
| 5 | Empty/Error/Loading-State-Patterns standardisieren | [4][5] |
| 6 | Decoupled, stateless FastAPI-Architektur mit Tenant-Isolation | [12][13] |
| 7 | UX-Texte nach Workspace-Patterns: kurz, klar, Verben-Buttons | [14] |
| 8 | Design Sprint vor großen Feature-Neugestaltungen | [8] |

---

## Sources

[1] https://m3.material.io/foundations  
[2] https://m3.material.io/blog/announcing-material-you  
[3] https://m3.material.io/foundations/overview/principles  
[4] https://m3.material.io/foundations/interaction/states/overview  
[5] https://m1.material.io/patterns/empty-states.html  
[6] https://www.mdui.org/en/design/1/growth-communications/onboarding.html  
[7] https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf  
[8] https://designsprintkit.withgoogle.com/methodology  
[9] https://web.dev/articles/vitals  
[10] https://web.dev/articles/offline-ux-design-guidelines  
[11] https://developers.google.com/solutions/content-driven/frontend/performance  
[12] https://docs.cloud.google.com/architecture/framework  
[13] https://docs.cloud.google.com/saas-runtime/docs/tenants  
[14] https://developers.google.com/workspace/add-ons/guides/workspace-style
