# Pre-Build Architecture Review: Security & DSGVO — MietVerwaltung SaaS

> **Geprüfte Dokumente:**
> - `/root/mietverwaltung/Abo-Abschluss-Prozess-Konzept.md`
> - `/root/mietverwaltung/Website-und-Lead-Generierung-Konzept.md`
> - `/root/mietverwaltung/Form-Validation-und-Input-Handling-Konzept.md`
> - `/root/mietverwaltung/DB-Management-und-Deployment-Sicherheit.md`
> - `/root/.hermes/skills/software-development/mietverwaltung-saas/SKILL.md` + `references/ki-architecture.md`
>
> **Status:** Konzept-Review vor Build  
> **Schweregrade:** `Kritisch` / `Hoch` / `Mittel` / `Niedrig`

---

## Executive Summary

Die Konzepte decken die wichtigsten Sicherheits- und DSGVO-Grundlagen ab (2FA, JWT, Argon2id, AES-256-GCM, Stripe-Webhook-Sicherheit, RLS, Soft-Delete, Audit-Logs, öffentliche Rate-Limiting). Es fehlen jedoch vor Build kritische Detail-Definitionen, insbesondere bei der **Rate-Limiting-Abdeckung für Auth-Endpunkte**, der **DSGVO-Betroffenenrechte-Implementierung (Art. 15/17/20/21)**, der **Schlüsselverwaltung für Feldverschlüsselung**, der **CSP-/Cookie-Sicherheit** und dem **MaxMind-GeoIP-Blocking**. Diese Lücken sollten vor Code-Start geschlossen werden, um teure nachträgliche Änderungen zu vermeiden.

---

## 1. Authentifizierung & Session-Management

### Was vorhanden ist

- **2FA-Pflicht** mit TOTP + E-Mail-Code-Fallback (`users.totp_secret`, `email_code`, `backup_codes` im DB-Schema v4; `Admin-Center-Konzept.md`; Skill).
- **JWT 15 Min Access + 7 Tage Refresh** in HTTP-only Secure Cookies (Skill, `Server-Konzept-v2.md`).
- **`user_sessions`**-Tabelle für Geräte-Logout, IP, User-Agent, Ablauf, Widerruf (DB-Schema v4).
- **Argon2id** Passwort-Hashing (`Form-Validation-und-Input-Handling-Konzept.md`, Skill).
- Rollen (`vermieter`, `mieter`, `admin`) und server-seitige Rollenprüfung (Skill).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 1.1 | **Keine Rate-Limiting-Definition für Login / Registrierung / Passwort-Reset** | **Kritisch** | In den gelesenen Konzepten ist Rate-Limiting nur für öffentliche Marketing-Endpunkte (`/api/public/*`) und Checkout (`3 Versuche/IP/Stunde`) definiert. Brute-Force-Angriffe auf `/api/auth/login`, `/api/auth/register`, `/api/auth/password-reset` werden nicht abgedeckt. |
| 1.2 | **Account-Lockout-Policy fehlt Details** | Hoch | `users.failed_login_count` und `users.locked_until` existieren im Schema, aber es gibt keine dokumentierte Schwelle (z. B. 5 Fehlversuche), Sperrdauer (z. B. 15 Min) oder Entsperr-Prozess (Admin, E-Mail, automatisch). |
| 1.3 | **Refresh-Token-Rotation nicht explizit** | Mittel | 7-Tage-Refresh-Tokens werden in `user_sessions` gespeichert; es ist nicht dokumentiert, ob bei jedem Access-Token-Refresh ein neues Refresh-Token ausgestellt und das alte ungültig gemacht wird (Best Practice gegen Replay). |
| 1.4 | **Session-Widerruf / „Alle Geräte abmelden" nicht spezifiziert** | Mittel | `revoked_at` existiert, aber der Ablauf-Flow (Login, Passwortänderung, Admin-Sperre, 2FA-Deaktivierung) wird nicht detailliert. |
| 1.5 | **Backup-Codes-Logik fehlt** | Mittel | `backup_codes JSONB` ist im Schema, aber keine Dokumentation zur Erzeugung, Validierung, Einmalverwendung und Benachrichtigung. |
| 1.6 | **2FA-Enforcement-Flow unklar** | Mittel | Im Onboarding-Konzept ist 2FA Teil des Registrierungs-Flows; für Mieter wird E-Mail-Code bevorzugt. Es fehlt aber ein dokumentierter Zustandsautomat, der verhindert, dass Nutzer ohne abgeschlossene 2VA geschützte Endpunkte nutzen. |

### Empfohlene Maßnahmen vor Build

1. Dokumentiere **globale Auth-Rate-Limits**: Login/Register/Passwort-Reset (z. B. 5 Versuche/IP/15 Min, steigende Sperrzeit).
2. Definiere **Account-Lockout**: Schwelle, Sperrdauer, Entsperr-Kanal, Logging.
3. Verpflichte **Refresh-Token-Rotation** + Widerruf bei sicherheitsrelevanten Ereignissen.
4. Spezifiziere Backup-Code-Generierung, -Speicherung (gehasht), -Verbrauch und Warnung bei niedrigem Bestand.
5. Implementiere einen **2FA-State-Machine-Check** (`2fa_verified`-Flag im JWT-Scope), der vor App-Zugriff geprüft wird.

---

## 2. Datenverschlüsselung (AES-256-GCM)

### Was vorhanden ist

- **Feldverschlüsselung** für `bankverbindungen.iban_enc` und `mieter.birth_date_enc` mit AES-256-GCM (DB-Schema v4, Skill).
- `pgcrypto`-Extension in PostgreSQL wird genannt.
- Docker Secret `ENCRYPTION_KEY_FILE` bzw. `DB_ENCRYPTION_KEY` in `Server-Konzept-v2.md` und CI-Workflow.
- SOPS + age für Go-Live Secret-Management (`Server-Konzept-v2.md`).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 2.1 | **Keine dokumentierte Schlüsselableitung / -ladung zum Startzeitpunkt** | **Hoch** | Es ist nicht beschrieben, wie die Anwendung den Roh-Schlüssel aus `ENCRYPTION_KEY_FILE` lädt, ob er base64-decodiert wird, wie die 32 Byte für AES-256 validiert werden und wie der GCM-Nonce pro Feld gespeichert wird. |
| 2.2 | **Fehlendes Format für verschlüsselte Spalten** | Mittel | Es fehlt die Spezifikation, wie Ciphertext + Tag + Nonce im `BYTEA` abgelegt werden (z. B. `nonce(12) || ciphertext || tag(16)`). Ohne festes Format ist ein späterer Wechsel/Backup-Wiedereinspielen fehleranfällig. |
| 2.3 | **Kein Key-Rotation-Konzept** | Mittel | Es gibt keine Strategie für die Rotation des Datenverschlüsselungs-Schlüssels bei Verdacht auf Kompromittierung oder periodisch (z. B. jährlich). |
| 2.4 | **Keine Trennung Master-Key / DEK** | Niedrig | Aktuell scheint ein einzelner Schlüssel für alle Daten genutzt zu werden. Für höhere Sicherheit sollte über ein Key-Envelope-Schema (Master-Key verschlüsselt pro-Tenant-DEKs) nachgedacht werden. |
| 2.5 | **CI-Test-Schlüssel wird hartkodiert** | Mittel | `migration-test.yml` setzt `DB_ENCRYPTION_KEY=dGVzdC1rZXktZm9yLWNpLXRoYXQtaXMtMzItYnl0ZXM=`. Das ist für CI akzeptabel, muss aber dokumentiert und von Produktions-Schlüsseln strikt getrennt sein. |

### Empfohlene Maßnahmen vor Build

1. Dokumentiere **AES-256-GCM-Implementierung** inkl. Nonce-Generierung (zufällig, 96 Bit), Tag-Länge, Speicherformat im `BYTEA`.
2. Definiere **Schlüssel-Ladeprozess** beim App-Start: Pfad, Berechtigungen (0400), Längenvalidierung, Fallback-Verhalten.
3. Füge ein **Key-Rotation-Runbook** hinzu (neuer Schlüssel, Re-Encryption-Routine, alte Backups sicher löschen).
4. Trenne Test- und Produktions-Schlüssel; dokumentiere, wie SOPS+age den Produktionsschlüssel verschlüsselt ablegt.

---

## 3. KI-Anonymisierung (Presidio)

### Was vorhanden ist

- Prinzip: Personendaten verlassen den Server nicht; Platzhalter vor KI-Aufruf, lokales Auflösen danach (Skill, `KI-Konzept.md`, `references/ki-architecture.md`).
- **Presidio + spaCy `de_core_news_lg`** als bevorzugte Lösung genannt (Skill).
- Fallback auf regelbasierte Templates, wenn Ollama Cloud ausfällt (Skill).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 3.1 | **Kein Presidio-Setup / spaCy-Modell-Download dokumentiert** | **Hoch** | In `references/ki-architecture.md` wird stattdessen nur ein **Regex-basierter** `anonymize()`-Code gezeigt. Es fehlt die `requirements.txt`-Zeile, der Download-Befehl (`python -m spacy download de_core_news_lg`), die Presidio-Initialisierung und die Custom-Entity-Recognizer für IBAN/Steuernummer/Geburtsdatum. |
| 3.2 | **Kein Fallback bei Presidio-Fehler definiert** | **Hoch** | Wenn Presidio abstürzt, das Modell fehlt oder NER ungenau ist, gibt es keine dokumentierte Fallback-Kaskade (z. B. Presidio → Regex + Validierung → manuelle Review-Pflicht → Abbruch). |
| 3.3 | **Keine Anonymisierungs-Validierung / Confidence-Threshold** | Mittel | Es fehlt ein QA-Schritt, der prüft, ob nach Anonymisierung noch PII im Prompt enthalten ist (z. B. zweiter Presidio-Scan des anonymisierten Prompts). |
| 3.4 | **AVV mit Ollama Cloud nicht detailliert** | Mittel | Der Skill erwähnt, dass eine AVV nötig ist, auch bei Pseudonymisierung. Es fehlt der konkrete Vertragspunkt, Datenschutzeinstellungen und ein Verarbeitungsverzeichnis-Eintrag. |
| 3.5 | **KI-Call-Logs enthalten möglicherweise Prompts** | Mittel | `ai_stored_results.result` speichert JSONB-Ergebnisse; es muss sichergestellt sein, dass dort nur anonymisierte/keine PII enthalten sind. |

### Empfohlene Maßnahmen vor Build

1. Ersetze oder ergänze den Regex-Code durch eine **Presidio-basierte Anonymisierungs-Engine** mit `de_core_news_lg` + Custom-Recognizern für IBAN, Steuernummer, Geburtsdatum, Adressen.
2. Dokumentiere **Modell-Installation** in `backend/requirements.txt` und Deployment-Skript (`python -m spacy download ...`).
3. Definiere **Fallback-Kaskade**: Presidio → Presidio+Regex → reiner Regex-Blocker → Abbruch mit menschlicher Review-Pflicht.
4. Implementiere einen **Anonymisierungs-Validator** (zweiter Scan des anonymisierten Prompts) und Logging jedes KI-Aufrufs mit `anonymized=True/False`.
5. Erstelle AVV-Eintrag für Ollama Cloud im VVT.

---

## 4. Payment-Sicherheit (Stripe)

### Was vorhanden ist

- **PCI-DSS SAQ-A** via Stripe Elements / Stripe Checkout; keine Kartendaten auf eigenem Server (`Abo-Abschluss-Prozess-Konzept.md`).
- Stripe-Signatur-Verifikation mit `stripe.Webhook.construct_event` und **Raw-Body** (`Abo-Abschluss-Prozess-Konzept.md`).
- **Idempotenz** über `stripe_webhook_events.stripe_event_id UNIQUE` (`Abo-Abschluss-Prozess-Konzept.md`).
- `payment_method_id`, `stripe_customer_id`, `stripe_subscription_id` werden lokal gespeichert; IBAN bei SEPA nur bei Stripe.
- Webhook wird innerhalb 3 Sekunden mit 200 OK beantwortet, schwere Arbeit in Background-Queue.

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 4.1 | **Race-Condition bei Idempotenz + Background-Task** | Hoch | Das Event wird als verarbeitet markiert, **bevor** der Background-Task `process_stripe_event` läuft. Wenn dieser fehlschlägt, ist das Event als „verarbeitet" markiert, ohne dass die DB aktualisiert wurde. Es fehlt ein „processing"-Status und ein Retry-Mechanismus. |
| 4.2 | **IP-Whitelist für Stripe wird nicht automatisch aktualisiert** | Mittel | Es wird eine statische Stripe-IP-Whitelist genannt, aber kein Mechanismus dokumentiert, der die Liste regelmäßig von Stripe abruft und aktualisiert (`https://stripe.com/docs/ips`). |
| 4.3 | **CSRF-Schutz für Checkout-Endpunkte fragil** | Mittel | Für `/subscribe` wird ein CSRF-Token im Header erwartet. Es fehlt aber die Dokumentation, wie das Token generiert, an das Frontend übergeben und serverseitig validiert wird (z. B. Double-Submit-Cookie vs. Session-Token). |
| 4.4 | **Fehlende Plan-Preis-Integrity im Trial-Endpunkt** | Mittel | Der `/trial`-Endpunkt nimmt `plan` als String entgegen und validiert gegen `PLAN_LIMITS`, aber der Preis/Status wird nicht gegen Stripe-Preise (`PRICE_MAP`) oder lokale Berechtigungen geprüft. |
| 4.5 | **Webhook-Timeout-Retry-Konzept unvollständig** | Mittel | Stripe retries 3×, danach Dead-Letter-Queue. Es fehlt aber die konkrete DLQ-Implementierung und Admin-Benachrichtigung im gelesenen Code. |
| 4.6 | **Keine Idempotenz-Key-Handling für App-Requests** | Niedrig | Für idempotente App-Aufrufe (z. B. „Subscribe") fehlt ein Client-generierter `Idempotency-Key`, der doppelte Klicks verhindert. |

### Empfohlene Maßnahmen vor Build

1. Speichere Webhook-Events mit Status **`received` → `processing` → `processed` / `failed`**; führe Background-Task nur für `received`-Events aus.
2. Implementiere **Retry-Queue** für fehlgeschlagene Webhooks mit exponentiellem Backoff + Admin-Alert.
3. Automatisiere **Stripe-IP-Whitelist-Update** per Cron oder Fetch beim Start.
4. Dokumentiere CSRF-Token-Strategie für alle mutierenden App-Endpunkte (Double-Submit-Cookie empfohlen).
5. Füge `Idempotency-Key`-Header für Checkout- und Planwechsel-Endpunkte hinzu.

---

## 5. DSGVO — Betroffenenrechte (Art. 15/17/20/21)

### Was vorhanden ist

- **`einwilligungen`**-Tabelle mit versionierter, zweckgebundener Einwilligung und `withdrawn_at` (DB-Schema v4).
- **`audit_logs`**-Tabelle mit `user_id`, `vermieter_id`, `action`, `risk_level`, `details`, `ip_address` (DB-Schema v4).
- **Soft-Delete** und Aufbewahrungsfristen für alle personenbezogenen Tabellen (DB-Schema v4).
- Skill erweitert DSGVO um Art. 16 (Berichtigung), 18 (Einschränkung), 20 (Übertragbarkeit), 21 (Widerspruch).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 5.1 | **Keine konkreten Endpunkte/UI für Betroffenenrechte** | **Kritisch** | Es gibt in den gelesenen Konzepten keine API-Spezifikation oder UI-Mockups für Auskunft (Art. 15), Löschung (Art. 17), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21). Diese Rechte müssen vor Go-Live verfügbar sein. |
| 5.2 | **Kein Datenexport-Format / -Umfang definiert** | **Hoch** | Für Art. 20 muss ein maschinenlesbarer Export (JSON/CSV/PDF) aller personenbezogenen Daten eines Nutzers definiert werden, inkl. Einwilligungen, Audit-Logs, Zahlungsdaten, hochgeladener Dokumente. |
| 5.3 | **Lösch-Workflow vs. Aufbewahrungsfristen unklar** | **Hoch** | Soft-Delete existiert, aber es fehlt der Prozess: Wer löscht? Admin oder User? Welche Daten werden sofort anonymisiert (z. B. E-Mail), welche nach 10 Jahren hart gelöscht? Wie wird der Nutzer benachrichtigt? |
| 5.4 | **Keine Berichtigungs- und Einschränkungs-Logik** | Mittel | Art. 16 (Berichtigung) und Art. 18 (Einschränkung) sind zwar im Skill genannt, aber nicht im DB-Schema oder in Endpunkten abgebildet. |
| 5.5 | **Kein Widerspruchs-Register** | Mittel | Art. 21-Widersprüche (z. B. gegen Marketing-E-Mails) müssen zentral erfasst und für alle Kommunikationskanäle ausgewertet werden. |

### Empfohlene Maßnahmen vor Build

1. Erstelle **DSGVO-Self-Service-Endpunkte**:
   - `GET /api/v1/me/data-export` (JSON-ZIP, maschinenlesbar)
   - `DELETE /api/v1/me/account` (Soft-Delete + Anonymisierungs-Job)
   - `POST /api/v1/me/objection` (Widerspruch Marketing)
   - `PUT /api/v1/me` (Berichtigung)
2. Definiere **Lösch-Kaskade** mit Aufbewahrungsfristen-Matrix (Schema v4 hat bereits Fristen; diese müssen in einen Lösch-Cron überführt werden).
3. Implementiere **Widerspruchs-Flags** in `users`/`einwilligungen` und werte sie vor jedem Marketing-Mail-Versand aus.
4. Dokumentiere **Fristen für Auskunftsanfragen** (1 Monat, Verlängerung +2 Monate).

---

## 6. Rate-Limiting

### Was vorhanden ist

- **Öffentliche Endpunkte**:
  - `/api/public/stats`: 60 req/min/IP (`Website-und-Lead-Generierung-Konzept.md`).
  - `/api/public/leads`: 3 Submissions/IP/Tag (`Website-und-Lead-Generierung-Konzept.md`).
  - `/api/public/demo/start`: max. 5 gleichzeitige Sessions/IP/10 Min (`Website-und-Lead-Generierung-Konzept.md`).
- **Checkout**: 3 Versuche/IP/Stunde (`Abo-Abschluss-Prozess-Konzept.md`).
- **Adress-Typeahead**: 30 req/min/User (`Adress-Autovervollstaendigung-Konzept.md`).
- **Massen-Import**: Max. 20 WE/Tag ohne manuelle Prüfung (`Markt-und-Preisanalyse-v2.md`).
- nginx `limit_req` als erste Verteidigungslinie (`Website-und-Lead-Generierung-Konzept.md`).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 6.1 | **Login / Register / Passwort-Reset haben kein Rate-Limiting** | **Kritisch** | Diese Endpunkte sind das Hauptangriffsziel für Brute-Force und Credential-Stuffing. Weder im `Server-Konzept-v2.md` noch in `Form-Validation-...` noch im Skill sind Limits definiert. |
| 6.2 | **Kein Rate-Limiting für authentifizierte Endpunkte** | Hoch | Objekt-/Mieter-/Ticket-/Kosten-Endpunkte (`/api/v1/*`) haben keine Nutzer- oder IP-basierten Limits. Ein Angreifer mit gültigem Token könnte Daten auslesen oder massiv schreiben. |
| 6.3 | **Keine globale Middleware-Dokumentation** | Mittel | `public_rate_limit.py` ist ein dekorierter Ansatz. Es fehlt eine zentrale Middleware, die Auth-Endpunkte und sensible Endpunkte standardmäßig schützt. |
| 6.4 | **Rate-Limit-Header fehlen** | Niedrig | Nur `X-RateLimit-Limit` wird für `/stats` erwähnt. `X-RateLimit-Remaining` und `Retry-After` fehlen. |

### Empfohlene Maßnahmen vor Build

1. Definiere **Auth-Rate-Limits**:
   - Login: 5 Versuche/IP/15 Min + Account-Lockout nach 10 Versuchen/Tag.
   - Registrierung: 3 Accounts/IP/Tag + Captcha nach 2 Versuchen.
   - Passwort-Reset: 3 Anfragen/E-Mail/Tag.
2. Implementiere **globale Rate-Limit-Middleware** für alle `/api/v1/*`-Endpunkte (z. B. 100 req/min/User, 1000 req/min/IP).
3. Füge **Rate-Limit-Response-Header** (`X-RateLimit-Limit`, `Remaining`, `Retry-After`) hinzu.
4. Schütze Massenoperationen (Bulk-Upload, -Import, -Delete) mit strikten Limits und Admin-Benachrichtigung.

---

## 7. CSRF / CSP / Security Headers

### Was vorhanden ist

- nginx setzt `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block` (`Website-und-Lead-Generierung-Konzept.md`).
- CSRF-Token-Header (`X-CSRF-Token`) wird für `/subscribe` erwähnt (`Abo-Abschluss-Prozess-Konzept.md`).
- CORS: Nur eigene Domain, kein `*` (`Website-und-Lead-Generierung-Konzept.md`).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 7.1 | **Kein Content-Security-Policy (CSP) Header** | **Hoch** | CSP ist der wirksamste Schutz gegen XSS und Data-Injection. Sie wird in keinem der gelesenen Konzepte definiert. |
| 7.2 | **CSRF-Strategie unvollständig** | **Hoch** | `verify_csrf_token` wird erwähnt, aber nicht, wie das Token generiert, gespeichert, an das Frontend übergeben und bei state-changing Requests validiert wird. Login/Register/Passwort-Reset werden nicht explizit geschützt. |
| 7.3 | **Fehlende SameSite-/Secure-/HttpOnly-Cookie-Policy** | Hoch | JWT/Refresh-Cookies müssen `HttpOnly`, `Secure`, `SameSite=Strict` und mit passendem `Path`/`Domain` gesetzt sein. Nicht dokumentiert. |
| 7.4 | **HSTS fehlt** | Mittel | `Strict-Transport-Security` Header wird in nginx-Konfigurationen nicht erwähnt. |
| 7.5 | **Referrer-Policy fehlt** | Niedrig | Keine `Referrer-Policy` definiert; bei Stripe/Payment-Redirects relevant. |
| 7.6 | **X-XSS-Protection ist veraltet** | Niedrig | Moderne Browser ignorieren `X-XSS-Protection`; CSP ist der aktuelle Standard. |

### Empfohlene Maßnahmen vor Build

1. Definiere eine **strikte CSP** für `app.mietverwaltung.de` und `www.mietverwaltung.de`:
   - `default-src 'self'`
   - `script-src 'self'` (+ Nonce für inline Skripte)
   - `style-src 'self' 'unsafe-inline'` (Tailwind erfordert oft inline Styles)
   - `img-src 'self' data: blob:`
   - `connect-src 'self' https://api.stripe.com https://ollama.com/v1 ...`
   - `frame-ancestors 'none'`, `base-uri 'self'`, `form-action 'self'`
2. Dokumentiere **CSRF-Token-Strategie**: Double-Submit-Cookie empfohlen, Validierung für alle `POST/PUT/PATCH/DELETE`-Endpunkte.
3. Setze Cookie-Flags `HttpOnly`, `Secure`, `SameSite=Strict`, `__Host-`-Prefix für Tokens.
4. Füge HSTS (`max-age=31536000; includeSubDomains; preload`) und `Referrer-Policy strict-origin-when-cross-origin` hinzu.

---

## 8. Audit-Logging

### Was vorhanden ist

- **`audit_logs`**-Tabelle mit `action`, `entity`, `entity_id`, `risk_level`, `details JSONB`, `ip_address` (DB-Schema v4).
- `subscription_events` und `stripe_webhook_events` für Payment/Subscription-Änderungen (`Abo-Abschluss-Prozess-Konzept.md`).
- Admin-Center-Log-Management mit Retention (Access 7 Tage, Audit 12 Monate, Security 90 Tage, KI/E-Mail 6 Monate; `Admin-Center-Konzept.md`).
- IP-Anonymisierung für Access-Logs (`anonymize_ip()` im Admin-Center).

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 8.1 | **Keine vollständige Liste sicherheitsrelevanter Aktionen** | Hoch | Es fehlt eine Matrix, welche Aktionen zwingend geloggt werden müssen: Login/Logout/Failed-Login, 2FA-Statusänderung, Passwort-Reset, Einwilligungsänderung, Datenexport, Löschung, Impersonate, Zahlungsstatusänderung, Plan-Limit-Überschreitung, IP-Block, Admin-Aktionen. |
| 8.2 | **Kein Schutz gegen Log-Manipulation** | Mittel | `audit_logs` ist eine normale PostgreSQL-Tabelle. Es fehlt ein append-only / tamper-evident Konzept (z. B. Hash-Kette, WORM-Speicher, externe Unveränderlichkeit). |
| 8.3 | **Mieter-Login-Aktivitäten unklar** | Mittel | `audit_logs` hat `vermieter_id`; für Mieter-Logins muss geklärt sein, ob `vermieter_id = users.vermieter_id` gesetzt wird und wie Mieter-Aktionen getrennt geloggt werden. |
| 8.4 | **Keine automatische Eskalation bei High-Risk-Events** | Mittel | `risk_level` existiert, aber es fehlt die Regel, wann ein Event einen Admin-Alert auslöst (z. B. 5 Failed-Logins, Impersonate, massiver Datenexport). |
| 8.5 | **Keine klare Trennung Access- vs. Audit-Logs** | Niedrig | Im Code-Beispiel wird `log_audit(...)` für Webhook-Empfang genutzt; Access-Logs und Audit-Logs sollten technisch getrennt werden. |

### Empfohlene Maßnahmen vor Build

1. Erstelle eine **Audit-Action-Matrix** mit Mindest-Logging für:
   - Authentifizierung (Login Success/Failed, Logout, 2FA Enable/Disable/Verify, Password Reset/Change)
   - Autorisierung (Role change, Impersonate start/end, Permission denied)
   - Daten (Export, Löschung, Berichtigung, Massenimport)
   - Zahlung (Subscription create/change/cancel, Webhook, Refund)
   - Sicherheit (Rate-Limit hit, IP block, GeoIP violation, CSP violation report)
2. Implementiere **High-Risk-Alerting** (E-Mail/Slack) bei definierten Schwellen.
3. Prüfe append-only-Strategie für `audit_logs` (z. B. INSERT-only-Policy, Hash-Kette, externes SIEM).
4. Stelle sicher, dass Mieter-Aktionen mit `vermieter_id` des zugehörigen Vermieters geloggt werden.

---

## 9. IP-Blocking (DACH-only via MaxMind GeoLite2)

### Was vorhanden ist

- **DACH-IP-Blocking** in Go-Life-Phase geplant: nur DE/AT/CH erlaubt (`Server-Konzept-v2.md`, Skill).
- `geoip_middleware.py`, `update-geoip.sh` und `geoip-blocking.md` in `Repo-Struktur-und-Change-Management.md` vorgesehen.
- Whitelist für Ausnahmen (VPN/Urlaub) im Skill erwähnt.

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 9.1 | **Keine konkrete MaxMind-Integration im gelesenen Code** | **Hoch** | Es gibt keinen Code oder keine Konfiguration, wie MaxMind GeoLite2 geladen, aktualisiert und in FastAPI/nginx ausgewertet wird. Nur Dateinamen in der Repo-Struktur. |
| 9.2 | **Keine GeoLite2-Lizenz-Key-Verwaltung** | Mittel | MaxMind erfordert einen License Key für Datenbank-Downloads. Es fehlt die Verwaltung in Secrets und der Update-Cron. |
| 9.3 | **Whitelist-/Bypass-Mechanismus unklar** | Mittel | VPN/Urlaub-Whitelist wird erwähnt, aber nicht, wie ein Nutzer sich freischaltet (Support-Ticket, E-Mail-Verifizierung, temporärer Token). |
| 9.4 | **Kein Fallback bei fehlender/veralteter GeoIP-DB** | Mittel | Wenn die MMDB-Datei fehlt, muss definiert sein, ob alle Requests blockiert oder erlaubt werden (Fail-open vs. Fail-closed). |
| 9.5 | **Keine IPv6-Berücksichtigung** | Niedrig | MaxMind unterstützt IPv6; die Middleware muss explizit damit umgehen. |

### Empfohlene Maßnahmen vor Build

1. Implementiere **`geoip_middleware.py`** mit `geoip2` / `maxminddb` für FastAPI.
2. Dokumentiere **Update-Prozess**: wöchentlicher Cron mit `License Key`, Download, Prüfsumme, Backup der alten MMDB.
3. Definiere **Whitelist-Verfahren** mit Audit-Log und temporärer Freischaltung.
4. Entscheide **Fail-Closed** bei fehlender/veralteter GeoIP-DB in Produktion, **Fail-Open** nur in Entwicklung.
5. Teste IPv6 und X-Forwarded-For/CF-Connecting-IP hinter nginx/Cloudflare.

---

## 10. Passwort-Policy

### Was vorhanden ist

- **Mindestlänge 8 Zeichen**, 1 Großbuchstabe, 1 Kleinbuchstabe, 1 Ziffer, 1 Sonderzeichen (`Form-Validation-und-Input-Handling-Konzept.md`).
- Passwort darf keine persönlichen Daten enthalten (E-Mail, Vor-/Nachname).
- Max. Länge 128 Zeichen; Trim-Regel.
- **Argon2id** Hashing mit `time_cost=3`, `memory_cost=65536`, `parallelism=4`, `salt_len=16`, `hash_len=32`.
- Passwort-Reset-Token: 15 Min Gültigkeit, gehasht in DB.
- Passwort ändern erfordert aktuelles Passwort.

### Gefundene Lücken

| # | Lücke | Schwere | Begründung |
|---|-------|---------|------------|
| 10.1 | **Mindestlänge 8 Zeichen für Finanz-SaaS knapp** | Mittel | BSI empfiehlt für Webanwendungen mit sensiblen Daten mindestens 12 Zeichen oder Passwort-Entropie-Messung. 8 Zeichen + Komplexitätsregeln ist NIST-konform, aber nicht „strong". |
| 10.2 | **Keine Prüfung gegen kompromittierte Passwörter** | Mittel | Es fehlt eine Abfrage gegen HIBP (Have I Been Pwned) oder eine eigene Blockliste häufiger Passwörter. |
| 10.3 | **Keine Passwort-Historie** | Niedrig | Es gibt keine Regel, dass das neue Passwort nicht eines der letzten N Passwörter sein darf. |
| 10.4 | **Keine explizite Account-Lockout-Kopplung** | Hoch | Obwohl `failed_login_count` existiert, ist nicht definiert, wie viele Fehlversuche bis zur Sperre erlaubt sind (siehe auch 1.2). |
| 10.5 | **Kein Passwort-Change-Notification** | Niedrig | Nach Passwortänderung/Reset sollte der Nutzer per E-Mail benachrichtigt werden. |

### Empfohlene Maßnahmen vor Build

1. Erhöhe Mindestlänge auf **12 Zeichen** oder führe eine Entropie-basierte Policy ein (z. B. zxcvbn, min. Score 3).
2. Prüfe neue Passwörter gegen **HIBP-API** (k-Anonymity) oder eigene Blockliste.
3. Speichere Passwort-Historie (gehasht) und verbiete Wiederverwendung der letzten 5 Passwörter.
4. Benachrichtige bei Passwort-Änderung, -Reset und Login von neuem Gerät/Standort.
5. Kopple Passwort-Policy eng mit Account-Lockout und 2FA-Fallback-Regeln.

---

## Gesamtbewertung

| Bereich | Status | Schweregrad höchste Lücke |
|---------|--------|---------------------------|
| 1. Authentifizierung | Teilweise abgedeckt | **Kritisch** (Auth-Rate-Limiting fehlt) |
| 2. Datenverschlüsselung | Konzept vorhanden, Details fehlen | **Hoch** (Key-Management) |
| 3. KI-Anonymisierung | Konzept vorhanden, Code/Setup fehlen | **Hoch** (Presidio-Setup + Fallback) |
| 4. Payment-Sicherheit | Stark, aber Race-Condition | **Hoch** (Webhook-Idempotenz) |
| 5. DSGVO Art. 15/17/20/21 | Nur Schema, keine Endpunkte/UI | **Kritisch** |
| 6. Rate-Limiting | Öffentliche Endpunkte gut, Auth/App fehlen | **Kritisch** |
| 7. CSRF/CSP | Grundidee vorhanden, CSP fehlt | **Hoch** |
| 8. Audit-Logging | Schema vorhanden, Matrix fehlt | **Hoch** |
| 9. IP-Blocking (MaxMind) | Nur Dateinamen geplant | **Hoch** |
| 10. Passwort-Policy | Solide, aber 8 Zeichen knapp | **Mittel** |

**Empfohlener nächster Schritt:** Vor dem Build müssen die als **Kritisch** und **Hoch** markierten Lücken in einem **Sicherheits- und DSGVO-Addendum** geschlossen werden. Empfohlene Reihenfolge:

1. Auth-Rate-Limiting + Account-Lockout
2. DSGVO-Betroffenenrechte-Endpunkte und -UI
3. CSP + CSRF + Cookie-Policy
4. Presidio-Setup + KI-Anonymisierungs-Fallback
5. MaxMind-GeoIP-Blocking + Update-Mechanismus
6. AES-Key-Management + Storage-Format
7. Stripe-Webhook-Idempotenz-Fix + Retry/DLQ
8. Audit-Action-Matrix + High-Risk-Alerting

---

*Review erstellt: 2026-11-13*  
*Autor: Hermes Agent (Security & DSGVO Review)*
