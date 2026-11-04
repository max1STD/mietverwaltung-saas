# GitHub-Scout Checkliste: MietVerwaltung SaaS

Bewertungsskala pro Kriterium: **Ja / Teilweise / Nein**
Gewichtung: ⭐ (1) = nice-to-have, ⭐⭐⭐⭐⭐ (5) = kritisch für Nutzung/Übernahme

## Checkliste

| # | Kriterium | Frage | Gewichtung |
|---|-----------|-------|------------|
| 1 | **Kerndatenmodell** | Hat das Projekt ein Datenmodell für Objekte, Einheiten/Wohnungen und Mieter? | ⭐⭐⭐⭐⭐ |
| 2 | **Nebenkostenabrechnung** | Enthält es Logik zur Betriebs- und Nebenkostenabrechnung (BetrKV-konform)? | ⭐⭐⭐⭐⭐ |
| 3 | **DACH-Spezifisch** | Ist es für Deutschland/Österreich/Schweiz bzw. Mietrecht/BetrKV angepasst? | ⭐⭐⭐⭐ |
| 4 | **Lizenz** | (Nur relevant bei Code-Übernahme — wir holen nur Ideen, daher niedrige Gewichtung) | ⭐ |
| 5 | **Tech-Stack-Kompatibilität** | Passt der Stack zu uns (FastAPI/Vue.js/PostgreSQL/Redis/Python/Node)? | ⭐⭐⭐ |
| 6 | **Code-Qualität** | Gibt es Tests, Dokumentation, saubere Architektur, Type Hints? | ⭐⭐⭐ |
| 7 | **Aktiv gewartet** | Gab es Commits/Releases in den letzten 6 Monaten? | ⭐⭐⭐ |
| 8 | **KI-Integration** | Gibt es KI/LLM-Features oder offene Schnittstellen dafür? | ⭐⭐ |
| 9 | **OCR / Belegscanning** | Kann es Belege/Rechnungen einlesen und verarbeiten (OCR)? | ⭐⭐ |
| 10 | **Ticket-System / Kommunikation** | Gibt es ein Mieterportal, Ticketsystem oder Kommunikationsmodul? | ⭐⭐ |
| 11 | **eID / Verifikation** | Unterstützt es eID, Personalausweis-Prüfung oder Vertrauensdienste? | ⭐⭐ |
| 12 | **Mahnwesen / Zahlungsverfolgung** | Gibt es Mahnungen, Zahlungsverfolgung oder Fälligkeitsmanagement? | ⭐⭐ |
| 13 | **PDF-Export / Berichte** | Kann es Verträge, Abrechnungen, Berichte als PDF generieren? | ⭐⭐ |
| 14 | **DSGVO / Datenschutz** | Werden DSGVO-Aspekte berücksichtigt (Löschkonzept, Einwilligung, Auftragsverarbeitung)? | ⭐⭐⭐ |
| 15 | **Community / Reife** | Gibt es aktive Community, Issues, PRs, Releases, Readme mit Setup-Anleitung? | ⭐⭐ |

## Empfehlungsskala

| Empfehlung | Bedeutung |
|------------|-----------|
| **Übernehmen** | Hohe Relevanz, guter Code, passender Stack, kompatible Lizenz – lohnt sich für Integration/Fork. |
| **Studieren** | Interessante Ansätze, teilweise übernehmbar, aber nicht direkt nutzbar. Dient als Inspirationsquelle. |
| **Ignorieren** | Geringe Relevanz, inaktiv, falscher Stack, restriktive Lizenz oder zu spezialisiert. |

## Bewertungsnotation

In der Analyse wird jedes Repo mit den Kriterien bewertet:
- **Ja** = volle Erfüllung
- **Teilweise** = vorhanden, aber lückenhaft oder nicht DACH-konform
- **Nein** = nicht vorhanden oder nicht relevant

Zusätzlich wird ein Gesamtpunktestand vergeben (max. 44 Punkte bei ⭐=1, ⭐⭐=2 usw., falls Ja = volle Gewichtung, Teilweise = halbe Gewichtung, Nein = 0).
