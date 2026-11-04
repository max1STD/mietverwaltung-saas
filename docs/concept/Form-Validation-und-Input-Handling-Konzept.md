# Konzept: Form-Validation, Input-Handling, Browser-Autofill & Passwort-Regeln

**Projekt:** MietVerwaltung SaaS für private Kleinvermieter in DACH  
**Tech-Stack:** FastAPI + Vue.js 3 + PostgreSQL 17  
**Status:** Konzept (Pre-Build) — zur Abstimmung mit dem Product Owner.  
**Verwandte Dokumente:**
- [Adress-Autovervollstaendigung-Konzept.md](./Adress-Autovervollstaendigung-Konzept.md)
- [Server-Konzept-v2.md](./Server-Konzept-v2.md)
- [db-schema-v2.sql](./db-schema-v2.sql)

---

## Inhaltsverzeichnis

0. [Formular-Übersicht (alle Formulare)](#0-formular-übersicht-alle-formulare)
1. [Browser-Autofill / Autofill-Unterstützung](#1-browser-autofill--autofill-unterstützung)
2. [E-Mail-Validierung](#2-e-mail-validierung)
3. [Telefonnummer-Validierung](#3-telefonnummer-validierung)
4. [Namens-Validierung](#4-namens-validierung)
5. [Passwort-Regeln](#5-passwort-regeln)
6. [PLZ-Validierung](#6-plz-validierung)
7. [IBAN-Validierung](#7-iban-validierung)
8. [Datums-Validierung](#8-datums-validierung)
9. [Allgemeine Input-Regeln](#9-allgemeine-input-regeln)
10. [Validierungs-Architektur](#10-validierungs-architektur)
11. [Konkrete Code-Beispiele](#11-konkrete-code-beispiele)
12. [Fehlermeldungen](#12-fehlermeldungen)
13. [Formular-Spezifikationen](#13-formular-spezifikationen)

---

## 0. Formular-Übersicht (alle Formulare)

Diese Tabelle listet **alle Formulare** der MietVerwaltung mit den wichtigsten Regeln pro Feld. Details, Code-Beispiele und HTML-Markup befinden sich in [Abschnitt 13](#13-formular-spezifikationen).

| Formular | Felder (Pflicht) | Wichtigste Validierung | Autocomplete | Fehlermeldung (Auszug) |
|----------|------------------|------------------------|--------------|------------------------|
| **1. Registrierung** | Vorname, Nachname, E-Mail, Passwort, Passwort wiederholen, Datenschutz-Checkbox | Name 2–50 Zeichen; E-Mail RFC; Passwort 8–128, 4 Kategorien; Checkbox muss aktiv sein | `given-name`, `family-name`, `email`, `new-password` | „Bitte stimme den Datenschutzhinweisen zu.“ |
| **2. Login** | E-Mail, Passwort | E-Mail-Format; Passwort nicht leer | `email`, `current-password` | „Bitte gib eine gültige E-Mail-Adresse ein.“ |
| **3. Passwort-Reset** | E-Mail | E-Mail-Format | `email` | „Bitte gib eine gültige E-Mail-Adresse ein.“ |
| **4. 2FA-Setup** | 6-stelliger Code | 6 Ziffern | `one-time-code` | „Der Code ist ungültig oder abgelaufen.“ |
| **5. Passwort ändern** | Aktuelles Passwort, Neues Passwort, Wiederholung | Aktuelles Passwort korrekt; neue Regeln + keine persönlichen Daten | `current-password`, `new-password` | „Das aktuelle Passwort ist falsch.“ |
| **6. Vermieter-Profil** | Vorname, Nachname, E-Mail, Adresse, PLZ, Ort | Name/E-Mail/Telefon wie Auth; Adresse via AddressAutocomplete; IBAN DACH + Checksum | `given-name`, `family-name`, `email`, `tel`, `address-line1`, `postal-code`, `address-level2`, `iban` | „Bitte gib eine gültige IBAN ein.“ |
| **7. Objekt anlegen** | Name, Adresse, PLZ, Ort, Typ | Name 1–200 Zeichen; Baujahr 1500–heute; Kaufpreis ≥0; Finanzierungszahlen ≥0 | `organization`, `address-line1`, `postal-code`, `address-level2`, `country` | „Bitte gib eine gültige Adresse ein.“ |
| **8. Einheit anlegen** | Bezeichnung, qm, Kaltmiete | qm >0; Zimmer ganze Zahl >0; Kaltmiete >0; NK-Vorschuss ≥0; Energieklasse A+–H; Verfügbar_ab max. 5 Jahre Zukunft | `off` (interne Bezeichnung) | „Fläche muss größer als 0 sein.“ |
| **9. Mieter anlegen** | Vorname, Nachname, E-Mail | Geburtsdatum 1900–heute, ≥18 Jahre; Status-Enum; Telefon optional DACH | `given-name`, `family-name`, `email`, `tel`, `bday` | „Mieter muss mindestens 18 Jahre alt sein.“ |
| **10. Mietvertrag anlegen** | Mietbeginn, Kaltmiete | Mietbeginn max. 30 Tage Zukunft; Mietende > Mietbeginn; Kaltmiete >0; NK-Vorschuss ≥0; Kaution ≥0 | `off` | „Mietende muss nach dem Mietbeginn liegen.“ |
| **11. Bewerbung** | Vorname, Nachname, E-Mail, Telefon, Adresse | Einkommen ≥0; Schufa-Score 0–100; Adresse validiert | `given-name`, `family-name`, `email`, `tel`, `street-address`, `postal-code` | „Schufa-Score muss zwischen 0 und 100 liegen.“ |
| **12. Kosten erfassen** | Kategorie, Betrag, Datum | Betrag >0; Datum nicht in Zukunft; Umlageschlüssel-Enum; DATEV-Felder optional | `off` | „Betrag muss größer als 0 sein.“ |
| **13. Beleg-Scan** | Bild/PDF | Magic Bytes; max 10 MB; extrahierter Betrag >0; Datum nicht Zukunft | `off` | „Bitte lade ein gültiges Belegbild hoch (PDF/JPG/PNG, max. 10 MB).“ |
| **14. Abrechnung erstellen** | Einheit, Jahr, Zeitraum | Jahr 4-stellig; Zeitraum_von < Zeitraum_bis; max. 12 Monate | `off` | „Abrechnungszeitraum ungültig.“ |
| **15. Ticket erstellen** | Titel, Beschreibung, Kategorie, Priorität | Titel 3–200; Beschreibung ≥10; Kategorie-Enum; Priorität-Enum | `off` | „Beschreibung muss mindestens 10 Zeichen lang sein.“ |
| **16. Ticket-Kommentar** | Inhalt | Inhalt ≥1 Zeichen; HTML-Tags verweigert; is_internal boolean | `off` | „Bitte gib einen Kommentar ein.“ |
| **17. Dokument-Upload** | Datei, Typ | PDF/JPG/PNG; max 10 MB; Magic-Bytes; Dateiname 1–255 Zeichen; Typ-Enum | `off` | „Ungültiger Dateityp. Erlaubt: PDF, JPG, PNG.“ |
| **18. Bankverbindung anlegen** | IBAN, Kontoinhaber | IBAN DACH + Checksum; Kontoinhaber Name-Validierung; BIC optional | `iban`, `name` (Kontoinhaber) | „Bitte gib eine gültige IBAN ein.“ |
| **19. Kostenkategorie anlegen** | Name, BetrKV-Key, Umlagefähig, Schlüssel | Name 1–100; BetrKV-Key Enum; Verteilungsschlüssel Enum | `off` | „Ungültiger Betriebskostenverordnungs-Schlüssel.“ |
| **20. Handwerker anlegen** | Name/Firma, Gewerk, E-Mail, Telefon | Name/Firma 1–200; E-Mail/Telefon wie Auth; Bewertung 1–5 | `organization`, `email`, `tel` | „Bewertung muss zwischen 1 und 5 liegen.“ |
| **21. SLA konfigurieren** | Name, Antwortzeit, Lösungszeit | Name 1–100; Zeiten >0; JSON-Format Geschäftszeiten validiert | `off` | „Antwortzeit muss größer als 0 sein.“ |
| **22. Ticket-Trigger** | Name, Typ, Condition, Perform | Condition/Perform validiert gegen JSON-Schema; Trigger-Typ Enum | `off` | „Condition muss gültiges JSON sein.“ |
| **23. Frist anlegen** | Entity, Entity-ID, Deadline, Beschreibung | Entity-Enum; Deadline nicht in Vergangenheit; Beschreibung ≥3 | `off` | „Deadline darf nicht in der Vergangenheit liegen.“ |
| **24. Onboarding-Schritte** | Schritt-Name, is_done | Schritt-Name aus erlaubter Liste; is_done boolean | `off` | „Ungültiger Onboarding-Schritt.“ |

> **Legende Pflicht/Optional:** Pflichtfelder sind mit `NOT NULL` bzw. `required` definiert. Optionale Felder sind in den Detailtabellen mit „opt.“ gekennzeichnet.

---

## 1. Browser-Autofill / Autofill-Unterstützung

### Ziel
Safari, Chrome und Firefox sollen Adressen, Kontaktdaten, Login-Daten und Zahlungsinformationen automatisch ausfüllen können. Autofill funktioniert nur, wenn HTML-Struktur und `autocomplete`-Attribute korrekt gesetzt sind. Die Regeln gelten für **alle Formulare** der App, nicht nur für Auth-Formulare.

### DSGVO-Hinweis
Browser-Autofill passiert **ausschließlich client-seitig** im Browser des Nutzers. Es werden keine Daten an unseren Server gesendet, bevor der Nutzer absichtlich auf „Speichern“ oder „Absenden“ klickt. Im Datenschutzhinweis notieren wir: „Die automatische Vervollständigung Ihres Browsers ist eine Funktion Ihres Endgeräts; wir erhalten diese Daten erst beim Absenden des Formulars.“

### Grundregeln für erkanntes Autofill

1. Jedes `<input>` hat ein korrektes `autocomplete`-Attribut.
2. Jedes Eingabefeld hat eine `<label for="id">`, die auf die `id` des Inputs zeigt.
3. Keine versteckten/umbenannten Felder, um Autofill zu „tricksen“ (führt zu Inkonsistenzen).
4. Name-Attribute sind stabil und semantisch (z. B. `email`, nicht `f_1`).
5. Formulare werden mit `<form>` (nicht nur `<div>`) umgeben, damit Browser das Formular als Speicherobjekt erkennen.
6. Für reine App-Interna (z. B. Ticket-Kategorie, Energieklasse, Kostenkategorie) verwenden wir `autocomplete="off"`, damit der Browser keine irrelevanten Vorschläge macht.

### Standard-Attribute

| Feld | `autocomplete` | Hinweis |
|------|----------------|---------|
| Vorname | `given-name` | |
| Nachname | `family-name` | |
| Firmenname | `organization` | optional |
| E-Mail | `email` | `type="email"` |
| Telefon | `tel` | `type="tel"` |
| Mobiltelefon | `tel-mobile` | optional |
| Straße | `street-address` | oder `address-line1` |
| Hausnummer | `address-line2` | wenn separat |
| PLZ | `postal-code` | |
| Ort | `address-level2` | |
| Bundesland/Kanton | `address-level1` | |
| Land | `country` | `country-code` für Alpha-2 |
| Aktuelles Passwort | `current-password` | |
| Neues Passwort | `new-password` | |
| Einmal-Code (2FA) | `one-time-code` | |
| Geburtstag | `bday` | `type="date"` |
| IBAN | `iban` | |
| BIC | `bic` | |
| Kontoinhaber | `name` | |

### Autocomplete-Mapping für die wichtigsten Formulare

#### 1. Registrierung (Vermieter)

```html
<form method="POST" action="/api/auth/register" autocomplete="on">
  <label for="regVorname">Vorname</label>
  <input id="regVorname" name="vorname" type="text" autocomplete="given-name" required />

  <label for="regNachname">Nachname</label>
  <input id="regNachname" name="nachname" type="text" autocomplete="family-name" required />

  <label for="regEmail">E-Mail</label>
  <input id="regEmail" name="email" type="email" autocomplete="email" required />

  <label for="regPhone">Telefon</label>
  <input id="regPhone" name="phone" type="tel" autocomplete="tel" />

  <label for="regPassword">Passwort</label>
  <input id="regPassword" name="password" type="password" autocomplete="new-password" required />

  <label for="regPasswordConfirm">Passwort wiederholen</label>
  <input id="regPasswordConfirm" name="password_confirm" type="password" autocomplete="new-password" required />

  <label>
    <input type="checkbox" name="datenschutz" required />
    Ich stimme den Datenschutzhinweisen zu.
  </label>
</form>
```

#### 2. Login

```html
<form method="POST" action="/api/auth/login" autocomplete="on">
  <label for="loginEmail">E-Mail</label>
  <input id="loginEmail" name="email" type="email" autocomplete="email" required />

  <label for="loginPassword">Passwort</label>
  <input id="loginPassword" name="password" type="password" autocomplete="current-password" required />
</form>
```

#### 3. Mieter anlegen

```html
<form autocomplete="on">
  <label for="mieterVorname">Vorname</label>
  <input id="mieterVorname" name="vorname" type="text" autocomplete="given-name" required />

  <label for="mieterNachname">Nachname</label>
  <input id="mieterNachname" name="nachname" type="text" autocomplete="family-name" required />

  <label for="mieterEmail">E-Mail</label>
  <input id="mieterEmail" name="email" type="email" autocomplete="email" required />

  <label for="mieterPhone">Telefon</label>
  <input id="mieterPhone" name="phone" type="tel" autocomplete="tel" />

  <label for="mieterGeburtstag">Geburtsdatum</label>
  <input id="mieterGeburtstag" name="geburtsdatum" type="date" autocomplete="bday" />
</form>
```

#### 4. Objekt anlegen (Adresse)

Verwendet die [AddressAutocomplete-Komponente](./Adress-Autovervollstaendigung-Konzept.md). Die Felder müssen trotzdem separate `autocomplete`-Attribute tragen, damit der Browser die Adresse erkennt:

```html
<form autocomplete="on">
  <label for="objektName">Objektname</label>
  <input id="objektName" name="name" type="text" autocomplete="organization" />

  <label for="objektStrasse">Straße</label>
  <input id="objektStrasse" name="strasse" type="text" autocomplete="address-line1" required />

  <label for="objektHausnummer">Hausnummer</label>
  <input id="objektHausnummer" name="hausnummer" type="text" autocomplete="address-line2" required />

  <label for="objektPlz">PLZ</label>
  <input id="objektPlz" name="plz" type="text" autocomplete="postal-code" required />

  <label for="objektOrt">Ort</label>
  <input id="objektOrt" name="ort" type="text" autocomplete="address-level2" required />

  <label for="objektLand">Land</label>
  <select id="objektLand" name="land" autocomplete="country">
    <option value="DE">Deutschland</option>
    <option value="AT">Österreich</option>
    <option value="CH">Schweiz</option>
  </select>
</form>
```

#### 5. Bewerbung

```html
<form autocomplete="on">
  <label for="bewVorname">Vorname</label>
  <input id="bewVorname" name="vorname" type="text" autocomplete="given-name" required />

  <label for="bewNachname">Nachname</label>
  <input id="bewNachname" name="nachname" type="text" autocomplete="family-name" required />

  <label for="bewEmail">E-Mail</label>
  <input id="bewEmail" name="email" type="email" autocomplete="email" required />

  <label for="bewPhone">Telefon</label>
  <input id="bewPhone" name="phone" type="tel" autocomplete="tel" required />

  <label for="bewStrasse">Straße</label>
  <input id="bewStrasse" name="strasse" type="text" autocomplete="street-address" required />

  <label for="bewPlz">PLZ</label>
  <input id="bewPlz" name="plz" type="text" autocomplete="postal-code" required />

  <label for="bewOrt">Ort</label>
  <input id="bewOrt" name="ort" type="text" autocomplete="address-level2" required />

  <label for="bewEinkommen">Netto-Einkommen (€)</label>
  <input id="bewEinkommen" name="netto_einkommen" type="number" inputmode="decimal" />
</form>
```

#### 6. Profil bearbeiten

```html
<form autocomplete="on">
  <label for="profilVorname">Vorname</label>
  <input id="profilVorname" name="vorname" type="text" autocomplete="given-name" required />

  <label for="profilNachname">Nachname</label>
  <input id="profilNachname" name="nachname" type="text" autocomplete="family-name" required />

  <label for="profilEmail">E-Mail</label>
  <input id="profilEmail" name="email" type="email" autocomplete="email" required />

  <label for="profilPhone">Telefon</label>
  <input id="profilPhone" name="phone" type="tel" autocomplete="tel" />
</form>
```

#### 7. Passwort-Reset

```html
<form method="POST" action="/api/auth/password-reset-request" autocomplete="on">
  <label for="resetEmail">E-Mail</label>
  <input id="resetEmail" name="email" type="email" autocomplete="email" required />
</form>
```

#### 8. 2FA-Setup

```html
<form autocomplete="off">
  <label for="totpCode">Authenticator-Code</label>
  <input id="totpCode" name="code" type="text" inputmode="numeric" autocomplete="one-time-code" required />
</form>
```

> **Hinweis:** Bei 2FA-Einmal-Codes verwenden wir `autocomplete="one-time-code"`. Safari und Chrome können so SMS- oder Mail-Codes automatisch einfügen.

---

## 2. E-Mail-Validierung

### Anforderungen
- Format-Check nach vereinfachtem RFC 5322.
- Optionaler MX-Record-Check bei Registrierung (Backend).
- E-Mail ist personenbezogenes Datum (DSGVO).
- Eindeutigkeit in DB: `users.email UNIQUE` ist bereits definiert.
- Fehlermeldungen auf Deutsch.

### Regex (Frontend HTML5 + JS)

```html
<input
  type="email"
  name="email"
  autocomplete="email"
  pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
  maxlength="255"
  required
/>
```

Für JavaScript-Validierung:

```typescript
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

export function isValidEmail(email: string): boolean {
  return EMAIL_REGEX.test(email.trim().toLowerCase());
}
```

### Regex (Backend Python / FastAPI)

```python
import re
from pydantic import BaseModel, field_validator, EmailStr

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

class UserRegisterRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Bitte gib eine gültige E-Mail-Adresse ein.")
        v = v.strip().lower()
        if len(v) > 255:
            raise ValueError("Die E-Mail-Adresse ist zu lang (max. 255 Zeichen).")
        if not EMAIL_RE.match(v):
            raise ValueError("Bitte gib eine gültige E-Mail-Adresse ein.")
        return v
```

> **Hinweis:** Pydantics `EmailStr` prüft bereits RFC-konform. Das zusätzliche Regex dient dazu, ausschließlich die in DACH üblichen Zeichen zuzulassen und Fehlermeldungen zuverlässig auf Deutsch zurückzugeben.

### Optional: MX-Record-Check

```python
import dns.resolver

async def has_mx_record(domain: str) -> bool:
    try:
        answers = await dns.resolver.resolve(domain, "MX", lifetime=5)
        return len(answers) > 0
    except Exception:
        return False
```

Nur bei Registrierung verwenden; nie als harten Blocker ( temporäre DNS-Probleme würden sonst Registrierungen verhindern). Stattdessen Warnung anzeigen und Log-Eintrag schreiben.

### Gültig vs. ungültig

| Eingabe | Ergebnis | Bemerkung |
|---------|----------|-----------|
| `max@mustermann.de` | ✅ gültig | |
| `max.mustermann@immobilien.at` | ✅ gültig | |
| `max+test@mietverwaltung.ch` | ✅ gültig | Plus-Adressen erlauben |
| `Max@Mustermann.DE` | ✅ gültig | wird zu `max@mustermann.de` normalisiert |
| `max@mustermann` | ❌ ungültig | fehlende TLD |
| `max@.de` | ❌ ungültig | fehlender Domain-Teil |
| `mustermann.de` | ❌ ungültig | fehlendes @ |
| `max@ mustermann .de` | ❌ ungültig | Leerzeichen entfernt/verweigert |

### DSGVO
- E-Mail wird als personenbezogenes Datum behandelt.
- Speicherung nur nach Einwilligung (Checkbox bei Registrierung).
- Löschfristen: so lange Account aktiv, danach gesperrt bis Löschung nach steuerlichen Aufbewahrungsfristen.

---

## 3. Telefonnummer-Validierung

### Anforderungen
- DACH-Formate: DE (`+49`), AT (`+43`), CH (`+41`).
- Akzeptiert: `+49 123 456789`, `0123 456789`, `0049 123 456789`.
- Normalisierung vor DB-Speicherung (E.164, z. B. `+49123456789`).
- Backend: `phonenumbers` (Google libphonenumber).
- Frontend: `type="tel"` mit Format-Hinweis.
- Mindestens 6, maximal 20 Ziffern.

### Frontend (Vue.js / HTML)

```html
<label for="phone">Telefonnummer</label>
<input
  id="phone"
  type="tel"
  name="phone"
  autocomplete="tel"
  inputmode="tel"
  placeholder="+49 123 456789"
  maxlength="30"
/>
<p class="hint">Beispiel: +49 123 456789, 0123 456789 oder 0049 123 456789</p>
```

### Backend (Python)

```python
import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat
from pydantic import BaseModel, field_validator

VALID_COUNTRY_HINTS = {"DE", "AT", "CH"}

class PhoneNumber(str):
    """Pydantic-Custom-Type für E.164-Telefonnummern."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if not isinstance(v, str):
            raise TypeError("Telefonnummer muss ein Text sein.")
        v = v.strip()
        if not v:
            return ""

        parsed = None
        for region in VALID_COUNTRY_HINTS:
            try:
                parsed = phonenumbers.parse(v, region)
                if phonenumbers.is_valid_number(parsed):
                    break
            except NumberParseException:
                continue
        else:
            raise ValueError("Bitte gib eine gültige Telefonnummer ein (DE, AT oder CH).")

        national = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
        digits_only = "".join(c for c in national if c.isdigit())
        if len(digits_only) < 6 or len(digits_only) > 20:
            raise ValueError("Telefonnummer muss zwischen 6 und 20 Ziffern haben.")

        return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)

class MieterCreate(BaseModel):
    vorname: str
    nachname: str
    phone: PhoneNumber
```

### Normalisierung

| Eingabe | Normalisiert | Land |
|---------|--------------|------|
| `+49 123 456789` | `+49123456789` | DE |
| `0123 456789` | `+49123456789` | DE |
| `0049 123 456789` | `+49123456789` | DE |
| `+43 664 1234567` | `+436641234567` | AT |
| `+41 44 123 45 67` | `+41441234567` | CH |

### Fehlermeldungen
- „Bitte gib eine gültige Telefonnummer ein (DE, AT oder CH).“
- „Telefonnummer muss zwischen 6 und 20 Ziffern haben.“

---

## 4. Namens-Validierung

### Anforderungen
- Vorname: 2–50 Zeichen.
- Nachname: 2–50 Zeichen.
- Erlaubt: Buchstaben inkl. Umlaute (`äöüß`), Akzente (`éàñ`), Bindestrich, Leerzeichen für Doppelnamen.
- Keine Zahlen, keine weiteren Sonderzeichen.
- Unicode-Unterstützung (über Unicode-Properties).

### Frontend (JavaScript / TypeScript)

```typescript
const NAME_REGEX = /^(?!.*[- ]{2})[\p{L}\p{M}\- ]{2,50}$/u;

export function isValidName(name: string): boolean {
  return NAME_REGEX.test(name.trim());
}
```

- `\p{L}` = alle Buchstaben.
- `\p{M}` = diakritische Zeichen (Akzente, Umlaut-Marker).
- `(?!.*[- ]{2})` = keine doppelten Bindestriche oder Leerzeichen.

### Backend (Python)

```python
import re
import unicodedata
from pydantic import BaseModel, field_validator

# Modernes Python 3.7+ erlaubt \p{...} nur über das regex-Modul.
# Wir nutzen stattdessen eine Kombination aus Unicode-Kategorien.

NAME_RE = re.compile(r"^(?!.*[- ]{2})[\p{L}\p{M}\- ]{2,50}$", re.UNICODE)
```

Falls wir das Modul `regex` nicht einbinden wollen, verwenden wir eine Python-Funktion:

```python
def is_valid_name(value: str) -> str:
    value = unicodedata.normalize("NFC", value.strip())
    if not (2 <= len(value) <= 50):
        raise ValueError("Name muss zwischen 2 und 50 Zeichen lang sein.")

    for i, char in enumerate(value):
        cat = unicodedata.category(char)
        if char in ("-", " "):
            if i > 0 and value[i - 1] in ("-", " "):
                raise ValueError("Name darf keine doppelten Leerzeichen oder Bindestriche enthalten.")
            continue
        if cat not in {
            "Lu", "Ll", "Lt", "Lm", "Lo",  # Buchstaben
            "Mn", "Mc", "Me",              # diakritische Marker
        }:
            raise ValueError("Name darf nur Buchstaben, Bindestrich und Leerzeichen enthalten.")
    return value

class UserBase(BaseModel):
    vorname: str
    nachname: str

    @field_validator("vorname", "nachname", mode="before")
    @classmethod
    def validate_name(cls, v):
        return is_valid_name(v)
```

### Beispiele

| Eingabe | Ergebnis |
|---------|----------|
| `Max` | ✅ |
| `Müller` | ✅ |
| `Anna-Lena` | ✅ |
| `Maria José` | ✅ |
| `François` | ✅ |
| `Max123` | ❌ |
| `Max@Müller` | ❌ |
| `M--ller` | ❌ |
| `A` | ❌ (zu kurz) |

---

## 5. Passwort-Regeln

### Anforderungen
- Mindestlänge: 8 Zeichen.
- Mindestens 1 Großbuchstabe, 1 Kleinbuchstabe, 1 Ziffer, 1 Sonderzeichen.
- Keine führenden/trailing Spaces (trim).
- Passwort darf weder E-Mail noch Vorname/Nachname enthalten.
- Passwort-Stärke-Anzeige im Frontend (schwach / mittel / stark).
- Backend: Argon2id Hashing (bereits konzipiert).
- Passwort-Reset: Token-basiert, 15 Min gültig.
- Passwort ändern: aktuelles Passwort erforderlich.
- Fehlermeldungen auf Deutsch.

### Regex (Frontend)

```typescript
const PASSWORD_MIN_LENGTH = 8;

export function validatePasswordRules(password: string): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  if (password.length < PASSWORD_MIN_LENGTH) errors.push("Mindestens 8 Zeichen.");
  if (!/[A-Z]/.test(password)) errors.push("Mindestens ein Großbuchstabe.");
  if (!/[a-z]/.test(password)) errors.push("Mindestens ein Kleinbuchstabe.");
  if (!/[0-9]/.test(password)) errors.push("Mindestens eine Ziffer.");
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) errors.push("Mindestens ein Sonderzeichen.");
  if (password !== password.trim()) errors.push("Keine Leerzeichen am Anfang oder Ende.");
  return { ok: errors.length === 0, errors };
}
```

### Pydantic-Validator (Backend)

```python
import re
from pydantic import BaseModel, field_validator, EmailStr

PASSWORD_RULES = {
    "min_length": 8,
    "max_length": 128,
}

class PasswordCreate(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        v_stripped = v.strip()
        if v != v_stripped:
            raise ValueError("Passwort darf keine Leerzeichen am Anfang oder Ende haben.")
        if not (PASSWORD_RULES["min_length"] <= len(v) <= PASSWORD_RULES["max_length"]):
            raise ValueError("Passwort muss zwischen 8 und 128 Zeichen lang sein.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Passwort muss mindestens einen Großbuchstaben enthalten.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Passwort muss mindestens einen Kleinbuchstaben enthalten.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Passwort muss mindestens eine Ziffer enthalten.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Passwort muss mindestens ein Sonderzeichen enthalten.")
        return v

class UserRegister(BaseModel):
    email: EmailStr
    vorname: str
    nachname: str
    password: str

    @field_validator("password")
    @classmethod
    def password_not_personal(cls, v: str, info) -> str:
        values = info.data
        lower = v.lower()
        for key in ("email", "vorname", "nachname"):
            val = values.get(key)
            if val and val.lower() in lower:
                raise ValueError("Passwort darf keine persönlichen Daten wie E-Mail oder Namen enthalten.")
        return v
```

### Argon2id Hashing

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, plain)
        return True
    except Exception:
        return False
```

### Passwort-Reset & Passwort ändern

**Reset-Token:**

```python
from secrets import token_urlsafe
from datetime import datetime, timedelta

RESET_TOKEN_TTL_MINUTES = 15

class PasswordResetToken(BaseModel):
    token_hash: str
    user_id: UUID
    expires_at: datetime

# Erzeugung
token_plain = token_urlsafe(32)
token_hash = hashlib.sha256(token_plain.encode()).hexdigest()
expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
```

- Token wird per E-Mail als Link gesendet (`/reset-password?token=...`).
- Nur der Hash liegt in der DB; der plain Token wird nie gespeichert.
- 15 Min Gültigkeit, danach löschen.

**Passwort ändern:**

```python
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
```

- Endpunkt verifiziert `current_password` gegen Argon2id-Hash.
- Bei Erfolg wird neuer Hash gesetzt und alle anderen Sessions widerrufen (optional).

### Conventional Commits

Änderungen an Validierung und Passwort-Log werden mit Conventional Commits dokumentiert:

```text
feat(validation): add inline password strength meter
fix(auth): reject passwords containing email or name
feat(security): enforce Argon2id password hashing
refactor(validation): extract reusable useValidation composable
docs(validation): document password reset token flow
```

---

## 6. PLZ-Validierung

### Anforderungen
- DE: genau 5 Ziffern.
- AT: genau 4 Ziffern.
- CH: genau 4 Ziffern.
- Frontend: `pattern` + Längen-Check je nach Land.
- Backend: Validierung je nach `land_code`.
- Verknüpfung mit Adress-Autovervollständigung (PLZ → Ort) siehe [Adress-Autovervollstaendigung-Konzept.md](./Adress-Autovervollstaendigung-Konzept.md).

### Frontend

```html
<label for="plz">PLZ</label>
<input
  id="plz"
  name="plz"
  type="text"
  inputmode="numeric"
  autocomplete="postal-code"
  maxlength="5"
  pattern="\d{5}"
  title="Bitte gib eine gültige deutsche PLZ mit 5 Ziffern ein."
  required
/>
```

Für dynamisches Land:

```typescript
const PLZ_PATTERNS: Record<string, { pattern: string; length: number; hint: string }> = {
  DE: { pattern: "^\\d{5}$", length: 5, hint: "5 Ziffern, z. B. 21635" },
  AT: { pattern: "^\\d{4}$", length: 4, hint: "4 Ziffern, z. B. 1010" },
  CH: { pattern: "^\\d{4}$", length: 4, hint: "4 Ziffern, z. B. 8001" },
};

export function isValidPlz(plz: string, country: "DE" | "AT" | "CH"): boolean {
  const rule = PLZ_PATTERNS[country];
  return new RegExp(rule.pattern).test(plz.trim());
}
```

### Backend

```python
import re
from pydantic import BaseModel, field_validator

PLZ_RULES = {
    "DE": r"^\d{5}$",
    "AT": r"^\d{4}$",
    "CH": r"^\d{4}$",
}

class AdresseBase(BaseModel):
    land: str
    plz: str

    @field_validator("plz")
    @classmethod
    def validate_plz(cls, v: str, info) -> str:
        v = v.strip()
        land = info.data.get("land")
        pattern = PLZ_RULES.get(land)
        if not pattern:
            raise ValueError("Land nicht unterstützt.")
        if not re.match(pattern, v):
            raise ValueError(f"PLZ für {land} ungültig.")
        return v
```

### Adress-Autovervollständigung

- Bei PLZ-Eingabe wird automatisch `GET /api/addresses/plz/{plz}` aufgerufen.
- Ort wird vorausgefüllt, sofern eindeutig.
- Bei mehreren Orten pro PLZ (selten) wird Dropdown angezeigt.

---

## 7. IBAN-Validierung

### Anforderungen
- Format-Check je Land: DE 22 Zeichen, AT 20 Zeichen, CH 21 Zeichen.
- IBAN-Checksum (Modulo 97).
- Backend: `python-stdnum` Library.
- Frontend: Formatierung mit Leerzeichen alle 4 Zeichen.
- Normalisierung vor DB-Speicherung (ohne Leerzeichen).
- Verschlüsselung: AES-256-GCM (bereits konzipiert).

### Frontend-Formatierung

```typescript
export function formatIban(value: string): string {
  const cleaned = value.replace(/\s/g, "").toUpperCase();
  return cleaned.match(/.{1,4}/g)?.join(" ") || "";
}

export function parseIban(value: string): string {
  return value.replace(/\s/g, "").toUpperCase();
}
```

```html
<input
  :value="formattedIban"
  @input="formattedIban = formatIban($event.target.value)"
  type="text"
  inputmode="text"
  autocomplete="iban"
  maxlength="35"
  placeholder="DE89 3704 0044 0532 0130 00"
/>
```

### Backend

```python
from stdnum import iban as iban_validator
from stdnum.exceptions import InvalidChecksum, InvalidFormat, InvalidLength
from pydantic import BaseModel, field_validator

class BankverbindungCreate(BaseModel):
    iban: str
    bic: str | None = None

    @field_validator("iban")
    @classmethod
    def validate_iban(cls, v: str) -> str:
        v = v.replace(" ", "").replace("-", "").upper()
        try:
            iban_validator.validate(v)
        except (InvalidFormat, InvalidLength, InvalidChecksum) as e:
            raise ValueError("Bitte gib eine gültige IBAN ein.") from e
        return v
```

### Speicherung

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

AES_KEY = os.environ["AES_IBAN_KEY"].encode()  # 32 Bytes

def encrypt_iban(plain_iban: str) -> str:
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plain_iban.encode(), None)
    return f"{nonce.hex()}:{ct.hex()}"

def decrypt_iban(token: str) -> str:
    nonce_hex, ct_hex = token.split(":")
    aesgcm = AESGCM(AES_KEY)
    return aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(ct_hex), None).decode()
```

### Beispiele

| Eingabe | Ergebnis |
|---------|----------|
| `DE89 3704 0044 0532 0130 00` | ✅ gültig |
| `AT61 1904 3002 3457 3201` | ✅ gültig |
| `CH93 0076 2011 6238 5295 7` | ✅ gültig |
| `DE89 3704 0044 0532 0130 01` | ❌ ungültig (Checksum falsch) |
| `DE89 3704` | ❌ ungültig (zu kurz) |

---

## 8. Datums-Validierung

### Anforderungen
- Mietbeginn: nicht in der Zukunft oder maximal 30 Tage in der Zukunft (konfigurierbar).
- Mietende: nach Mietbeginn, falls gesetzt.
- Geburtsdatum: zwischen 1900-01-01 und heute, Mindestalter 18.
- Kaufdatum: nicht in der Zukunft.
- Frontend: Date-Picker mit `min`/`max`.
- Backend: Pydantic-Validatoren.

### Frontend (Date-Picker)

```html
<label for="mietbeginn">Mietbeginn</label>
<input
  id="mietbeginn"
  type="date"
  name="mietbeginn"
  :max="maxMietbeginn"
  required
/>

<label for="geburtsdatum">Geburtsdatum</label>
<input
  id="geburtsdatum"
  type="date"
  name="geburtsdatum"
  :min="'1900-01-01'"
  :max="maxGeburtsdatum"
  required
/>
```

```typescript
import { computed } from "vue";

const today = new Date().toISOString().split("T")[0];

const maxMietbeginn = computed(() => {
  const d = new Date();
  d.setDate(d.getDate() + 30);
  return d.toISOString().split("T")[0];
});

const maxGeburtsdatum = computed(() => {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 18);
  return d.toISOString().split("T")[0];
});
```

### Backend

```python
from datetime import date, timedelta
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

class MietvertragCreate(BaseModel):
    mietbeginn: date
    mietende: Optional[date] = None

    @field_validator("mietbeginn")
    @classmethod
    def mietbeginn_max_future(cls, v: date) -> date:
        if v > date.today() + timedelta(days=30):
            raise ValueError("Mietbeginn darf maximal 30 Tage in der Zukunft liegen.")
        return v

    @model_validator(mode="after")
    def check_dates(self):
        if self.mietende and self.mietende <= self.mietbeginn:
            raise ValueError("Mietende muss nach dem Mietbeginn liegen.")
        return self

class MieterPerson(BaseModel):
    geburtsdatum: date

    @field_validator("geburtsdatum")
    @classmethod
    def validate_age(cls, v: date) -> date:
        if v < date(1900, 1, 1):
            raise ValueError("Geburtsdatum darf nicht vor 1900 liegen.")
        if v > date.today():
            raise ValueError("Geburtsdatum darf nicht in der Zukunft liegen.")
        age = date.today().year - v.year - ((date.today().month, date.today().day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Mieter muss mindestens 18 Jahre alt sein.")
        return v

class ObjektFinanz(BaseModel):
    kaufdatum: Optional[date] = None

    @field_validator("kaufdatum")
    @classmethod
    def kaufdatum_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Kaufdatum darf nicht in der Zukunft liegen.")
        return v
```

---

## 9. Allgemeine Input-Regeln

### 9.1 Trim
Jeder String-Input wird vor Validierung und Speicherung getrimmt:

```python
from pydantic import field_validator

class TrimmedString(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if not isinstance(v, str):
            raise TypeError("String erwartet.")
        return v.strip()
```

### 9.2 Max-Längen
Max-Längen orientieren sich am DB-Schema:

| Feld | DB-Typ | Max-Länge |
|------|--------|-----------|
| E-Mail | `VARCHAR(255)` | 255 |
| Vorname/Nachname | `VARCHAR(100)` | 50 (Validierung) / 100 (DB Puffer) |
| Telefon | `VARCHAR(30)` | 30 |
| PLZ | `VARCHAR(10)` | 10 |
| Ort | `VARCHAR(100)` | 100 |
| Straße | `VARCHAR(200)` | 200 |
| IBAN | encrypted `TEXT` | 34 (normiert) |
| Passwort | — | 128 |

### 9.3 XSS-Schutz
Keine HTML-Tags in String-Inputs erlaubt. Wir **verweigern**, nicht nur entfernen:

```python
import re
from pydantic import field_validator

HTML_TAG_RE = re.compile(r"<[^\u003e]+>")

def no_html(value: str) -> str:
    if HTML_TAG_RE.search(value):
        raise ValueError("HTML-Tags sind in diesem Feld nicht erlaubt.")
    return value

class CleanText(BaseModel):
    bemerkung: str

    @field_validator("bemerkung")
    @classmethod
    def no_tags(cls, v: str) -> str:
        return no_html(v)
```

Für Rich-Text-Felder (z. B. Ticket-Kommentare) später: DOMPurify im Frontend + Bleach im Backend mit strikter Whitelist.

### 9.4 SQL-Injection
- Verwendung von SQLAlchemy 2.0 Core / ORM mit Parameter-Binding.
- Keine String-Concatenation in Queries.
- Bereits durch DB-Schema und ORM-Strategie sichergestellt.

### 9.5 Unicode-Normalisierung
Alle Text-Inputs werden vor Speicherung nach NFC normalisiert, damit Umlaute und Akzente konsistent gespeichert werden:

```python
import unicodedata
from pydantic import field_validator

class UnicodeBase(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def normalize_unicode(cls, v):
        if isinstance(v, str):
            return unicodedata.normalize("NFC", v)
        return v
```

### 9.6 Debounce für Typeahead/Autocomplete
- 300 ms Debounce für Echtzeit-Suchfelder (z. B. Mieter-Suche, Straßen-Typeahead).
- 150 ms Debounce für reine Adress-Straßen-Suche (bereits im Adress-Konzept definiert).

```typescript
import { useDebounceFn } from "@vueuse/core";

const debouncedSearch = useDebounceFn(async (query: string) => {
  results.value = await api.get("/api/search", { params: { q: query } });
}, 300);
```

---

## 10. Validierungs-Architektur

### Prinzip
1. **Frontend** = erste Verteidigungslinie: sofortiges Feedback, aber nicht vertrauenswürdig.
2. **Backend** = zweite Verteidigungslinie: Pydantic-Modelle validieren alles erneut.
3. **Datenbank** = dritte Verteidigungslinie: Constraints (CHECK, UNIQUE, NOT NULL).

### Frontend: Validierungszeitpunkte
- `onInput`: leichte visuelle Hinweise (z. B. Passwort-Stärke).
- `onBlur`: Feld-Validierung auslösen und Fehler anzeigen.
- `onSubmit`: Gesamtes Formular validieren; bei Fehlern Scroll-To-First-Error.

### Backend: Fehlerformat
Einheitliches JSON-Format:

```json
{
  "detail": {
    "email": ["Diese E-Mail-Adresse wird bereits verwendet."],
    "password": ["Passwort muss mindestens 8 Zeichen lang sein."]
  }
}
```

### FastAPI Exception Handler

```python
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = err.get("loc", [])
        field = loc[-1] if loc else "form"
        errors.setdefault(field, []).append(err.get("msg", "Ungültige Eingabe."))
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": errors})
```

### Inline-Fehleranzeige (Vue.js)

```vue
<div class="form-group">
  <label :for="id">E-Mail</label>
  <input
    :id="id"
    v-model="value"
    :aria-invalid="hasError"
    :aria-describedby="hasError ? errorId : undefined"
    @blur="validate"
  />
  <p v-if="hasError" :id="errorId" class="error">{{ errorMessage }}</p>
</div>
```

### Barrierefreiheit
- `aria-invalid="true"` bei Fehlern.
- `aria-describedby` verweist auf Fehlermeldung.
- `aria-live="polite"` am Fehlercontainer für Screenreader.
- Fokus-Management: erstes fehlerhaftes Feld erhält Fokus nach Submit.

---

## 11. Konkrete Code-Beispiele

### 11.1 Vue.js 3 Input-Komponente mit Validation (composable `useValidation`)

```typescript
// frontend/src/composables/useValidation.ts
import { ref, computed, type Ref } from "vue";

export function useValidation<T extends string>(
  value: Ref<string>,
  rules: Array<(v: string) => string | true>
) {
  const touched = ref(false);
  const errors = computed(() => {
    if (!touched.value && !value.value) return [];
    return rules
      .map((rule) => rule(value.value))
      .filter((result): result is string => result !== true);
  });

  const validate = () => {
    touched.value = true;
    return errors.value.length === 0;
  };

  const onBlur = () => validate();

  return {
    touched,
    errors,
    validate,
    onBlur,
    hasError: computed(() => errors.value.length > 0),
  };
}
```

```vue
<!-- frontend/src/components/BaseInput.vue -->
<template>
  <div class="form-group">
    <label :for="inputId">{{ label }}</label>
    <input
      :id="inputId"
      :type="type"
      :value="modelValue"
      :autocomplete="autocomplete"
      :aria-invalid="hasError"
      :aria-describedby="hasError ? errorId : undefined"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="validate"
    />
    <p v-if="hasError" :id="errorId" class="error-message" role="alert">
      {{ errors[0] }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, useId } from "vue";
import { useValidation } from "@/composables/useValidation";

const props = defineProps<{
  modelValue: string;
  label: string;
  type?: string;
  autocomplete?: string;
  rules: Array<(v: string) => string | true>;
}>();

defineEmits<{
  (e: "update:modelValue", value: string): void;
}>();

const inputId = useId();
const errorId = computed(() => `${inputId}-error`);

const value = computed({
  get: () => props.modelValue,
  set: (v) => {}, // wird über Event gehandhabt
});

const { errors, hasError, validate, onBlur } = useValidation(
  computed(() => props.modelValue),
  props.rules
);
</script>
```

### 11.2 FastAPI Pydantic-Modelle mit Validatoren

```python
# backend/app/schemas/auth.py
from datetime import date
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.validation.common import is_valid_name, normalize_text, no_html

class UserRegister(BaseModel):
    email: EmailStr
    vorname: str
    nachname: str
    password: str
    password_confirm: str

    @field_validator("vorname", "nachname", mode="before")
    @classmethod
    def validate_names(cls, v: str) -> str:
        return is_valid_name(normalize_text(v))

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return normalize_text(v).lower()

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Die Passwörter stimmen nicht überein.")
        return self
```

### 11.3 HTML autocomplete Attribute Beispiel für jedes Formular

Siehe [Abschnitt 1](#1-browser-autofill--autofill-unterstützung) und die detaillierten Formular-Spezifikationen in [Abschnitt 13](#13-formular-spezifikationen). Dort sind alle 24 Formulare mit HTML-Markup, Pflichtfeldern und Autocomplete-Werten abgedeckt.

### 11.4 Passwort-Stärke-Komponente

```vue
<!-- frontend/src/components/PasswordStrength.vue -->
<template>
  <div class="password-strength">
    <div class="bars">
      <span v-for="i in 4" :key="i" :class="['bar', { filled: i <= score }]"></span>
    </div>
    <span class="label">{{ label }}</span>
    <ul v-if="errors.length" class="errors">
      <li v-for="err in errors" :key="err">{{ err }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ password: string }>();

const { score, errors } = computed(() => {
  const p = props.password;
  let s = 0;
  const errs: string[] = [];

  if (p.length >= 8) s++;
  else errs.push("Mindestens 8 Zeichen.");
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) s++;
  else errs.push("Groß- und Kleinbuchstaben.");
  if (/[0-9]/.test(p)) s++;
  else errs.push("Mindestens eine Ziffer.");
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(p)) s++;
  else errs.push("Mindestens ein Sonderzeichen.");

  return { score: s, errors: errs };
}).value;

const label = computed(() => {
  if (props.password.length === 0) return "";
  if (score <= 1) return "Schwach";
  if (score === 2) return "Mittel";
  if (score === 3) return "Gut";
  return "Stark";
});
</script>

<style scoped>
.bars { display: flex; gap: 4px; margin-bottom: 6px; }
.bar { width: 24px; height: 4px; border-radius: 2px; background: #e5e5e5; }
.bar.filled:nth-child(1) { background: #ff3b30; }
.bar.filled:nth-child(2) { background: #ff9500; }
.bar.filled:nth-child(3) { background: #ffcc00; }
.bar.filled:nth-child(4) { background: #34c759; }
.label { font-size: 12px; font-weight: 500; }
.errors { font-size: 12px; color: #ff3b30; margin-top: 4px; }
</style>
```

### 11.5 IBAN-Formatierungs-Komponente

```vue
<!-- frontend/src/components/IbanInput.vue -->
<template>
  <div class="form-group">
    <label :for="id">IBAN</label>
    <input
      :id="id"
      :value="displayValue"
      type="text"
      autocomplete="iban"
      maxlength="35"
      @input="onInput"
      @blur="validate"
    />
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, useId } from "vue";

const model = defineModel<string>();
const id = useId();
const error = ref("");

const displayValue = computed(() =>
  (model.value || "").replace(/\s/g, "").toUpperCase().match(/.{1,4}/g)?.join(" ") || ""
);

const onInput = (e: Event) => {
  const raw = (e.target as HTMLInputElement).value;
  const cleaned = raw.replace(/[^A-Za-z0-9]/g, "").toUpperCase().slice(0, 34);
  model.value = cleaned;
};

const validate = () => {
  const v = (model.value || "").replace(/\s/g, "");
  const de = /^DE\d{20}$/;
  const at = /^AT\d{18}$/;
  const ch = /^CH\d{19}$/;
  if (!de.test(v) && !at.test(v) && !ch.test(v)) {
    error.value = "Bitte gib eine gültige IBAN ein.";
  } else {
    error.value = "";
  }
};
</script>
```

### 11.6 Telefonnummer-Normalisierung

```typescript
// frontend/src/utils/phone.ts
export function formatPhoneDisplay(value: string): string {
  // Nur für Lesbarkeit: nach +49/0049/0 Leerzeichen setzen
  const v = value.trim();
  if (v.startsWith("+49")) return v.replace(/^\+49\s?/, "+49 ");
  if (v.startsWith("0049")) return v.replace(/^0049\s?/, "+49 ");
  if (v.startsWith("0") && v.length > 3) return v.replace(/^0\s?/, "+49 ");
  return v;
}
```

```python
# backend/app/validation/phone.py
import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException

NORMALIZED_REGIONS = ("DE", "AT", "CH")

def normalize_phone(value: str) -> str:
    value = value.strip()
    if not value:
        return ""

    parsed = None
    for region in NORMALIZED_REGIONS:
        try:
            parsed = phonenumbers.parse(value, region)
            if phonenumbers.is_valid_number(parsed):
                break
        except NumberParseException:
            continue

    if not parsed:
        raise ValueError("Bitte gib eine gültige Telefonnummer ein (DE, AT oder CH).")

    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
```

---

## 12. Fehlermeldungen

### Gestaltungsprinzipien
- Auf Deutsch.
- Nutzerfreundlich, nicht technisch.
- Einheitlicher Stil: „Bitte gib eine gültige E-Mail-Adresse ein.“
- Konkret: was ist falsch, nicht nur „ungültig“.
- Keine Interna (Stacktraces, Feld-IDs) preisgeben.

### Vollständige Liste

| Feld / Regel | Fehlermeldung |
|--------------|---------------|
| E-Mail Format | „Bitte gib eine gültige E-Mail-Adresse ein.“ |
| E-Mail zu lang | „Die E-Mail-Adresse ist zu lang (max. 255 Zeichen).“ |
| E-Mail vergeben | „Diese E-Mail-Adresse wird bereits verwendet.“ |
| Telefon ungültig | „Bitte gib eine gültige Telefonnummer ein (DE, AT oder CH).“ |
| Telefon zu kurz/lang | „Telefonnummer muss zwischen 6 und 20 Ziffern haben.“ |
| Vorname/Nachname zu kurz | „Name muss mindestens 2 Zeichen lang sein.“ |
| Vorname/Nachname zu lang | „Name darf maximal 50 Zeichen lang sein.“ |
| Vorname/Nachname ungültige Zeichen | „Name darf nur Buchstaben, Bindestrich und Leerzeichen enthalten.“ |
| Vorname/Nachname doppelte Leerzeichen/Bindestriche | „Name darf keine doppelten Leerzeichen oder Bindestriche enthalten.“ |
| Passwort zu kurz | „Passwort muss mindestens 8 Zeichen lang sein.“ |
| Passwort zu lang | „Passwort darf maximal 128 Zeichen lang sein.“ |
| Passwort Großbuchstabe | „Passwort muss mindestens einen Großbuchstaben enthalten.“ |
| Passwort Kleinbuchstabe | „Passwort muss mindestens einen Kleinbuchstaben enthalten.“ |
| Passwort Ziffer | „Passwort muss mindestens eine Ziffer enthalten.“ |
| Passwort Sonderzeichen | „Passwort muss mindestens ein Sonderzeichen enthalten.“ |
| Passwort Leerzeichen | „Passwort darf keine Leerzeichen am Anfang oder Ende haben.“ |
| Passwort persönlich | „Passwort darf keine persönlichen Daten wie E-Mail oder Namen enthalten.“ |
| Passwort nicht identisch | „Die Passwörter stimmen nicht überein.“ |
| Aktuelles Passwort falsch | „Das aktuelle Passwort ist falsch.“ |
| Reset-Token ungültig | „Der Link ist ungültig oder abgelaufen. Bitte fordere einen neuen an.“ |
| PLZ DE | „Bitte gib eine gültige deutsche PLZ mit 5 Ziffern ein.“ |
| PLZ AT | „Bitte gib eine gültige österreichische PLZ mit 4 Ziffern ein.“ |
| PLZ CH | „Bitte gib eine gültige schweizerische PLZ mit 4 Ziffern ein.“ |
| IBAN | „Bitte gib eine gültige IBAN ein.“ |
| Mietbeginn Zukunft | „Mietbeginn darf maximal 30 Tage in der Zukunft liegen.“ |
| Mietende vor Beginn | „Mietende muss nach dem Mietbeginn liegen.“ |
| Geburtsdatum zu früh | „Geburtsdatum darf nicht vor 1900 liegen.“ |
| Geburtsdatum Zukunft | „Geburtsdatum darf nicht in der Zukunft liegen.“ |
| Geburtsdatum zu jung | „Mieter muss mindestens 18 Jahre alt sein.“ |
| Kaufdatum Zukunft | „Kaufdatum darf nicht in der Zukunft liegen.“ |
| HTML-Tags | „HTML-Tags sind in diesem Feld nicht erlaubt.“ |
| Pflichtfeld | „Dieses Feld ist ein Pflichtfeld.“ |
| Max-Länge | „Dieses Feld darf maximal {n} Zeichen enthalten.“ |
| Min-Länge | „Dieses Feld muss mindestens {n} Zeichen enthalten.“ |
| E-Mail 2FA-Code | „Der Code ist ungültig oder abgelaufen. Bitte fordere einen neuen an.“ |
| TOTP-Code | „Der Authenticator-Code ist ungültig. Bitte versuche es erneut.“ |
| Betrag | „Betrag muss größer als 0 sein.“ |
| Datum Zukunft | „Datum darf nicht in der Zukunft liegen.“ |
| Schufa-Score | „Schufa-Score muss zwischen 0 und 100 liegen.“ |
| Dateityp | „Ungültiger Dateityp. Erlaubt: PDF, JPG, PNG.“ |
| Dateigröße | „Datei zu groß (max. 10 MB)." |
| Ticket-Titel | „Titel muss zwischen 3 und 200 Zeichen lang sein.“ |
| Ticket-Beschreibung | „Beschreibung muss mindestens 10 Zeichen lang sein.“ |
| Bewertung | „Bewertung muss zwischen 1 und 5 liegen.“ |
| SLA-Zeit | „Zeit muss größer als 0 sein.“ |

---

## 13. Formular-Spezifikationen

Für jedes Formular in der App sind nachfolgend die Felder, Pflicht/Optional-Regeln, Validierungsregeln, Autocomplete-Attribute und Fehlermeldungen dokumentiert. Alle Regeln werden **im Frontend (Vue.js 3)** und **im Backend (FastAPI / Pydantic)** geprüft.

---

### 13.1 Auth-Formulare

#### 13.1.1 Registrierung (Vermieter)

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Vorname | ✅ | 2–50 Zeichen, Unicode-Name | `given-name` | „Name muss zwischen 2 und 50 Zeichen lang sein.“ |
| Nachname | ✅ | 2–50 Zeichen, Unicode-Name | `family-name` | „Name muss zwischen 2 und 50 Zeichen lang sein.“ |
| E-Mail | ✅ | RFC-Format, max 255, unique | `email` | „Bitte gib eine gültige E-Mail-Adresse ein.“ |
| Telefon | ❌ | DACH, 6–20 Ziffern, E.164 | `tel` | „Bitte gib eine gültige Telefonnummer ein.“ |
| Passwort | ✅ | 8–128, 4 Kategorien, keine Spaces | `new-password` | „Passwort muss mindestens 8 Zeichen lang sein.“ |
| Passwort wiederholen | ✅ | Identisch mit Passwort | `new-password` | „Die Passwörter stimmen nicht überein.“ |
| Datenschutz-Checkbox | ✅ | Muss `true` sein | `off` | „Bitte stimme den Datenschutzhinweisen zu.“ |

**Backend:**

```python
class UserRegister(BaseModel):
    email: EmailStr
    vorname: str
    nachname: str
    phone: PhoneNumber | None = None
    password: str
    password_confirm: str
    datenschutz: bool

    @field_validator("datenschutz")
    @classmethod
    def consent_required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Bitte stimme den Datenschutzhinweisen zu.")
        return v
```

#### 13.1.2 Login

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| E-Mail | ✅ | RFC-Format | `email` | „Bitte gib eine gültige E-Mail-Adresse ein.“ |
| Passwort | ✅ | Nicht leer | `current-password` | „Bitte gib dein Passwort ein.“ |

**Backend:**

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

#### 13.1.3 Passwort-Reset

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| E-Mail | ✅ | RFC-Format | `email` | „Bitte gib eine gültige E-Mail-Adresse ein.“ |

#### 13.1.4 2FA-Setup

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Code | ✅ | Genau 6 Ziffern | `one-time-code` | „Der Code ist ungültig oder abgelaufen.“ |

```python
class TwoFactorVerify(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def six_digits(cls, v: str) -> str:
        if not re.fullmatch(r"\d{6}", v.strip()):
            raise ValueError("Bitte gib den 6-stelligen Code ein.")
        return v
```

#### 13.1.5 Passwort ändern

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Aktuelles Passwort | ✅ | Nicht leer | `current-password` | „Bitte gib dein aktuelles Passwort ein.“ |
| Neues Passwort | ✅ | 8–128, 4 Kategorien | `new-password` | „Passwort muss mindestens 8 Zeichen lang sein.“ |
| Passwort wiederholen | ✅ | Identisch | `new-password` | „Die Passwörter stimmen nicht überein.“ |

**Backend:**

```python
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str
```

---

### 13.2 Vermieter-Profil

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Firma | ❌ | 0–200 Zeichen, keine HTML | `organization` | „Firmenname zu lang (max. 200 Zeichen).“ |
| Vorname | ✅ | 2–50 Zeichen, Unicode | `given-name` | Name-Regeln |
| Nachname | ✅ | 2–50 Zeichen, Unicode | `family-name` | Name-Regeln |
| E-Mail | ✅ | RFC, unique, max 255 | `email` | E-Mail-Regeln |
| Telefon | ❌ | DACH, E.164 | `tel` | Telefon-Regeln |
| Straße | ✅ | 1–200 Zeichen | `address-line1` | „Bitte gib eine Straße ein.“ |
| Hausnummer | ✅ | 1–20 Zeichen | `address-line2` | „Bitte gib eine Hausnummer ein.“ |
| PLZ | ✅ | Land-abhängig 4/5 Ziffern | `postal-code` | PLZ-Regeln |
| Ort | ✅ | 1–100 Zeichen | `address-level2` | „Bitte gib einen Ort ein.“ |
| Land | ✅ | `DE`/`AT`/`CH` | `country` | „Land nicht unterstützt.“ |
| IBAN | ❌ | DACH + Checksum | `iban` | „Bitte gib eine gültige IBAN ein.“ |
| BIC | ❌ | 8–11 Zeichen | `bic` | „BIC ungültig.“ |
| Steuernummer | ❌ | Verschlüsselt, max 20 | `off` | „Steuernummer zu lang.“ |

**Backend:**

```python
class VermieterProfileUpdate(BaseModel):
    firma: str | None = None
    vorname: str
    nachname: str
    email: EmailStr
    phone: PhoneNumber | None = None
    strasse: str
    hausnummer: str
    plz: str
    ort: str
    land: Literal["DE", "AT", "CH"]
    iban: str | None = None
    bic: str | None = None
    steuernr: str | None = None
```

---

### 13.3 Objekt anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Name | ✅ | 1–200 Zeichen | `organization` | „Objektname erforderlich.“ |
| Straße | ✅ | 1–200 Zeichen | `address-line1` | Adresse-Regeln |
| Hausnummer | ✅ | 1–20 Zeichen | `address-line2` | Adresse-Regeln |
| PLZ | ✅ | 4/5 Ziffern | `postal-code` | PLZ-Regeln |
| Ort | ✅ | 1–100 Zeichen | `address-level2` | Adresse-Regeln |
| Land | ✅ | `DE`/`AT`/`CH` | `country` | Land-Regeln |
| Typ | ✅ | Enum: EFH, MFH, DHH, Wohnanlage, Geschaeft | `off` | „Bitte wähle einen Objekttyp.“ |
| Baujahr | ❌ | 1500–heute | `off` | „Baujahr muss zwischen 1500 und heute liegen.“ |
| Gesamtfläche (qm) | ❌ | Dezimal >0 | `off` | „Gesamtfläche muss größer als 0 sein.“ |
| Kaufpreis | ❌ | ≥0 | `off` | „Kaufpreis darf nicht negativ sein.“ |
| Kaufdatum | ❌ | Nicht Zukunft | `off` | „Kaufdatum darf nicht in der Zukunft liegen.“ |
| Eigenkapital | ❌ | ≥0 | `off` | „Eigenkapital darf nicht negativ sein.“ |
| Darlehensbetrag | ❌ | ≥0 | `off` | „Darlehensbetrag darf nicht negativ sein.“ |
| Zinssatz | ❌ | 0–25% | `off` | „Zinssatz muss zwischen 0 und 25 % liegen.“ |
| Tilgungssatz | ❌ | 0–25% | `off` | „Tilgungssatz muss zwischen 0 und 25 % liegen.“ |
| Zinsbindung bis | ❌ | Datum | `off` | „Zinsbindungsdatum ungültig.“ |
| Sondertilgung | ❌ | Boolean | `off` | — |

**Backend:**

```python
class ObjektCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    strasse: str = Field(..., min_length=1, max_length=200)
    hausnummer: str = Field(..., min_length=1, max_length=20)
    plz: str
    ort: str = Field(..., min_length=1, max_length=100)
    land: Literal["DE", "AT", "CH"]
    typ: Literal["EFH", "MFH", "DHH", "Wohnanlage", "Geschaeft"]
    baujahr: int | None = Field(None, ge=1500, le=lambda: date.today().year)
    gesamtflaeche_qm: Decimal | None = Field(None, gt=0)
    kaufpreis: Decimal | None = Field(None, ge=0)
    kaufdatum: date | None = None
    eigenkapital: Decimal | None = Field(None, ge=0)
    darlehensbetrag: Decimal | None = Field(None, ge=0)
    zinssatz: Decimal | None = Field(None, ge=0, le=25)
    tilgungssatz: Decimal | None = Field(None, ge=0, le=25)
    zinsbindung_bis: date | None = None
    sondertilgung: bool = False
```

---

### 13.4 Einheit anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Bezeichnung | ✅ | 1–100 Zeichen | `off` | „Bitte gib eine Bezeichnung ein.“ |
| Fläche (qm) | ✅ | Dezimal >0 | `off` | „Fläche muss größer als 0 sein.“ |
| Zimmer | ❌ | Ganze Zahl >0 | `off` | „Zimmeranzahl muss größer als 0 sein.“ |
| Stockwerk | ❌ | 1–20 Zeichen | `off` | „Stockwerk zu lang.“ |
| Kaltmiete | ✅ | Decimal >0 | `off` | „Kaltmiete muss größer als 0 sein.“ |
| NK-Vorschuss | ❌ | Decimal ≥0 | `off` | „NK-Vorschuss darf nicht negativ sein.“ |
| Verfügbar ab | ❌ | Datum, max 5 Jahre Zukunft | `off` | „Verfügbarkeitsdatum zu weit in der Zukunft.“ |
| Energieklasse | ❌ | Enum A+, A, B, C, D, E, F, G, H | `off` | „Ungültige Energieklasse.“ |
| Ausstattung-Features | ❌ | Array erlaubter Werte | `off` | „Ungültige Ausstattung.“ |
| Aktuell vermietet | ❌ | Boolean | `off` | — |

**Backend:**

```python
class EinheitCreate(BaseModel):
    bezeichnung: str = Field(..., min_length=1, max_length=100)
    flaeche_qm: Decimal = Field(..., gt=0)
    zimmer: int | None = Field(None, gt=0)
    etage: str | None = Field(None, max_length=20)
    kaltmiete: Decimal = Field(..., gt=0)
    nk_vorschuss: Decimal | None = Field(None, ge=0)
    verfuegbar_ab: date | None = None
    energieklasse: Literal["A+", "A", "B", "C", "D", "E", "F", "G", "H"] | None = None
    ausstattung: list[str] = []
    aktuell_vermietet: bool = False
```

---

### 13.5 Mieter anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Vorname | ✅ | 2–50, Unicode | `given-name` | Name-Regeln |
| Nachname | ✅ | 2–50, Unicode | `family-name` | Name-Regeln |
| E-Mail | ✅ | RFC, unique | `email` | E-Mail-Regeln |
| Telefon | ❌ | DACH | `tel` | Telefon-Regeln |
| Geburtsdatum | ❌ | 1900–heute, ≥18 | `bday` | „Mieter muss mindestens 18 Jahre alt sein.“ |
| Status | ✅ | Enum: aktiv, inaktiv, bewerber | `off` | „Ungültiger Status.“ |
| Seit (Datum) | ❌ | ≤ heute | `off` | „Seit-Datum darf nicht in der Zukunft liegen.“ |

**DSGVO:** Geburtsdatum wird AES-256-GCM verschlüsselt gespeichert.

---

### 13.6 Mietvertrag anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Mieter | ✅ | Gültige UUID, Tenant-Isolation | `off` | „Bitte wähle einen Mieter.“ |
| Einheit | ✅ | Gültige UUID | `off` | „Bitte wähle eine Einheit.“ |
| Mietbeginn | ✅ | ≤ heute + 30 Tage | `off` | „Mietbeginn darf maximal 30 Tage in der Zukunft liegen.“ |
| Mietende | ❌ | > Mietbeginn | `off` | „Mietende muss nach dem Mietbeginn liegen.“ |
| Kaltmiete | ✅ | >0 | `off` | „Kaltmiete muss größer als 0 sein.“ |
| NK-Vorschuss | ❌ | ≥0 | `off` | „NK-Vorschuss darf nicht negativ sein.“ |
| Kaution | ❌ | ≥0 | `off` | „Kaution darf nicht negativ sein.“ |
| Status | ✅ | Enum: aktiv, gekündigt, beendet | `off` | „Ungültiger Vertragsstatus.“ |

---

### 13.7 Bewerbung

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Vorname | ✅ | 2–50, Unicode | `given-name` | Name-Regeln |
| Nachname | ✅ | 2–50, Unicode | `family-name` | Name-Regeln |
| E-Mail | ✅ | RFC | `email` | E-Mail-Regeln |
| Telefon | ✅ | DACH | `tel` | Telefon-Regeln |
| Wohnsitz | ✅ | Adresse validiert | `street-address`, `postal-code`, `address-level2` | Adresse-Regeln |
| Monatliches Einkommen | ❌ | ≥0 | `off` | „Einkommen darf nicht negativ sein.“ |
| Schufa-Score | ❌ | 0–100 | `off` | „Schufa-Score muss zwischen 0 und 100 liegen.“ |
| Dokumente | ❌ | PDF/JPG/PNG, max 10 MB | `off` | Datei-Regeln |

---

### 13.8 Kosten erfassen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Kategorie | ✅ | Gültige UUID/Enum | `off` | „Bitte wähle eine Kostenkategorie.“ |
| Betrag | ✅ | >0 | `off` | „Betrag muss größer als 0 sein.“ |
| Datum | ✅ | ≤ heute | `off` | „Kostendatum darf nicht in der Zukunft liegen.“ |
| Umlagefähig | ✅ | Boolean | `off` | — |
| Umlageschlüssel | ❌ | Enum: nach_qm, nach_personen, nach_verbrauch | `off` | „Ungültiger Umlageschlüssel.“ |
| Beleg (Datei) | ❌ | PDF/JPG/PNG, max 10 MB | `off` | Datei-Regeln |
| DATEV-Konto | ❌ | 1–50 Zeichen | `off` | „DATEV-Konto zu lang.“ |
| DATEV-Buchungstext | ❌ | 1–255 Zeichen | `off` | „Buchungstext zu lang.“ |

---

### 13.9 Beleg-Scan

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Belegbild/PDF | ✅ | Magic Bytes; PDF/JPG/PNG; max 10 MB | `off` | „Bitte lade ein gültiges Belegbild hoch (PDF/JPG/PNG, max. 10 MB).“ |
| Extrahierter Betrag | ✅ (KI) | >0 | `off` | „Betrag muss größer als 0 sein.“ |
| Extrahiertes Datum | ✅ (KI) | ≤ heute | `off` | „Datum darf nicht in der Zukunft liegen.“ |
| Kategorie (KI) | ✅ (KI) | Enum/UUID validiert | `off` | „Bitte wähle eine gültige Kategorie.“ |
| Umlagefähigkeit | ❌ | Boolean (KI-Vorschlag) | `off` | — |

**Backend:**

```python
class ReceiptUpload(BaseModel):
    betrag: Decimal = Field(..., gt=0)
    datum: date
    kategorie_id: UUID
    umlagefaehig: bool | None = None
```

---

### 13.10 Abrechnung erstellen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Einheit | ✅ | Gültige UUID | `off` | „Bitte wähle eine Einheit.“ |
| Jahr | ✅ | 4-stellig, 1900–2100 | `off` | „Bitte gib ein gültiges Jahr ein.“ |
| Zeitraum von | ✅ | Datum | `off` | „Abrechnungsbeginn erforderlich.“ |
| Zeitraum bis | ✅ | > Zeitraum von, max 12 Monate | `off` | „Abrechnungszeitraum ungültig.“ |
| Status | ✅ | Enum: entwurf, fertig, versendet | `off` | „Ungültiger Status.“ |

---

### 13.11 Ticket erstellen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Titel | ✅ | 3–200 Zeichen, keine HTML | `off` | „Titel muss zwischen 3 und 200 Zeichen lang sein.“ |
| Beschreibung | ✅ | ≥10 Zeichen, keine HTML | `off` | „Beschreibung muss mindestens 10 Zeichen lang sein.“ |
| Kategorie | ✅ | Enum: heizung, wasser, elektrik, schimmel, sonstiges | `off` | „Bitte wähle eine Kategorie.“ |
| Priorität | ✅ | Enum: dringend, normal, niedrig | `off` | „Bitte wähle eine Priorität.“ |
| Einheit | ❌ | Gültige UUID | `off` | „Ungültige Einheit.“ |

**Backend:**

```python
class TicketCreate(BaseModel):
    titel: str = Field(..., min_length=3, max_length=200)
    beschreibung: str = Field(..., min_length=10)
    kategorie: Literal["heizung", "wasser", "elektrik", "schimmel", "sonstiges"]
    prioritaet: Literal["dringend", "normal", "niedrig"]
    einheit_id: UUID | None = None
```

---

### 13.12 Ticket-Kommentar

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Inhalt | ✅ | ≥1 Zeichen, HTML verweigert | `off` | „Bitte gib einen Kommentar ein.“ |
| Ist KI-Entwurf | ❌ | Boolean | `off` | — |
| Intern | ❌ | Boolean | `off` | — |

```python
class TicketCommentCreate(BaseModel):
    inhalt: str = Field(..., min_length=1)
    is_ki_entwurf: bool = False
    is_internal: bool = False

    @field_validator("inhalt")
    @classmethod
    def no_tags(cls, v: str) -> str:
        return no_html(v)
```

---

### 13.13 Dokument-Upload

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Datei | ✅ | Magic Bytes; PDF/JPG/PNG; max 10 MB | `off` | „Ungültiger Dateityp. Erlaubt: PDF, JPG, PNG.“ |
| Dateiname | ✅ | 1–255 Zeichen, keine HTML | `off` | „Dateiname zu lang.“ |
| Typ | ✅ | Enum: vertrag, abrechnung, beleg, sonstiges | `off` | „Bitte wähle einen Dokumententyp.“ |
| Sichtbarkeit | ✅ | Enum: vermieter, mieter, beide, handwerker | `off` | „Ungültige Sichtbarkeit.“ |

**Backend (Magic Bytes):**

```python
ALLOWED_MAGIC = {
    b"%PDF": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
}

MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_document(file: UploadFile) -> None:
    header = file.file.read(8)
    file.file.seek(0)
    if len(header) < 4 or not any(header.startswith(m) for m in ALLOWED_MAGIC):
        raise ValueError("Ungültiger Dateityp. Erlaubt: PDF, JPG, PNG.")
    if file.size > MAX_FILE_SIZE:
        raise ValueError("Datei zu groß (max. 10 MB).")
```

---

### 13.14 Bankverbindung anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| IBAN | ✅ | DACH + Checksum | `iban` | „Bitte gib eine gültige IBAN ein.“ |
| BIC | ❌ | 8–11 Zeichen | `bic` | „BIC ungültig.“ |
| Kontoinhaber | ✅ | 2–50 Zeichen, Unicode-Name | `name` | Name-Regeln |
| Bankname | ❌ | 1–100 Zeichen | `organization` | „Bankname zu lang.“ |
| Standard | ❌ | Boolean | `off` | — |

---

### 13.15 Kostenkategorie anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Name | ✅ | 1–100 Zeichen | `off` | „Bitte gib einen Namen ein.“ |
| BetrKV-Key | ❌ | Enum der gültigen Betriebskostenverordnungs-Schlüssel | `off` | „Ungültiger BetrKV-Schlüssel.“ |
| Umlagefähig | ✅ | Boolean | `off` | — |
| Verteilungsschlüssel | ✅ | Enum: nach_qm, nach_personen, nach_verbrauch | `off` | „Ungültiger Verteilungsschlüssel.“ |

---

### 13.16 Handwerker anlegen (Roadmap)

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Name/Firma | ✅ | 1–200 Zeichen | `organization` | „Bitte gib einen Namen ein.“ |
| Gewerk | ❌ | 1–100 Zeichen | `off` | „Gewerk zu lang.“ |
| E-Mail | ❌ | RFC | `email` | E-Mail-Regeln |
| Telefon | ❌ | DACH | `tel` | Telefon-Regeln |
| Bewertung | ❌ | 1–5 | `off` | „Bewertung muss zwischen 1 und 5 liegen.“ |

---

### 13.17 SLA konfigurieren

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Name | ✅ | 1–100 Zeichen | `off` | „Bitte gib einen Namen ein.“ |
| Antwortzeit (h) | ✅ | Ganze Zahl >0 | `off` | „Antwortzeit muss größer als 0 sein.“ |
| Lösungszeit (h) | ✅ | Ganze Zahl >0 | `off` | „Lösungszeit muss größer als 0 sein.“ |
| Geschäftszeiten | ✅ | JSON-Schema validiert | `off` | „Ungültiges Format für Geschäftszeiten.“ |

---

### 13.18 Ticket-Trigger

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Name | ✅ | 1–100 Zeichen | `off` | „Bitte gib einen Namen ein.“ |
| Trigger-Typ | ✅ | Enum: event, scheduler, manual | `off` | „Ungültiger Trigger-Typ.“ |
| Condition | ✅ | JSON-Schema | `off` | „Condition muss gültiges JSON sein.“ |
| Perform | ✅ | JSON-Schema | `off` | „Perform muss gültiges JSON sein.“ |

```python
class TicketTriggerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    trigger_typ: Literal["event", "scheduler", "manual"]
    condition: dict
    perform: dict
```

---

### 13.19 Frist anlegen

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Entity | ✅ | Enum: mietvertrag, ticket, abrechnung, dokument | `off` | „Ungültige Entity.“ |
| Entity-ID | ✅ | Gültige UUID | `off` | „Ungültige Entity-ID.“ |
| Deadline | ✅ | ≥ heute | `off` | „Deadline darf nicht in der Vergangenheit liegen.“ |
| Beschreibung | ✅ | 3–500 Zeichen | `off` | „Beschreibung muss zwischen 3 und 500 Zeichen lang sein.“ |
| Warn-Level | ✅ | Enum: niedrig, mittel, hoch | `off` | „Ungültiges Warn-Level.“ |

---

### 13.20 Onboarding-Schritte

| Feld | Pflicht | Validierung | Autocomplete | Fehlermeldung |
|------|---------|-------------|--------------|----------------|
| Schritt-Name | ✅ | Enum erlaubter Schritte | `off` | „Ungültiger Onboarding-Schritt.“ |
| Abgeschlossen | ✅ | Boolean | `off` | — |

```python
class OnboardingStepUpdate(BaseModel):
    schritt_name: Literal[
        "profil_vollstaendig",
        "erstes_objekt",
        "erste_einheit",
        "erster_mieter",
        "bankverbindung",
    ]
    is_done: bool
```

---

## Zusammenfassung der Entscheidungen

| Bereich | Entscheidung |
|---------|--------------|
| Autofill | Korrekte `autocomplete`-Attribute + semantische Labels für alle 24 Formulare. |
| E-Mail | Pydantic `EmailStr` + zusätzliches Regex; optionaler MX-Check. |
| Telefon | `phonenumbers` Library; Speicherung als E.164; Frontend `type="tel"`. |
| Namen | Unicode-Property-basierte Validierung; 2–50 Zeichen; Bindestrich/Leerzeichen. |
| Passwort | 8–128 Zeichen, 4 Kategorien, Argon2id, Reset-Token 15 Min, keine persönlichen Daten. |
| PLZ | DE 5 Ziffern, AT/CH 4 Ziffern; Land-abhängige Validierung. |
| IBAN | `python-stdnum`; Frontend-Formatierung; Speicherung normalisiert + AES-256-GCM. |
| Datum | Pydantic-Validatoren; Date-Picker mit `min`/`max`. |
| Input-Regeln | trim, max-length, no-HTML, NFC-Normalisierung, debounce 300 ms. |
| Architektur | Frontend onBlur/onSubmit + Backend Pydantic + DB-Constraints; JSON `{field: [messages]}`. |
| Barrierefreiheit | `aria-invalid`, `aria-describedby`, Fokus-Management. |

---

**Nächste Schritte:**
1. Abstimmung mit PO zu optionalen Checks (MX-Record, Passwort-Stärke-Bibliothek).
2. Übernahme in Build-Plan unter Phase „Auth & Validation“.
3. Definition zentraler Fehlertext-Schlüssel für i18n (auch wenn MVP nur Deutsch ist).
4. Erstellung der Pydantic-Schema-Dateien pro Formular im Backend.
5. Erstellung zentraler Validation-Composables im Frontend.
