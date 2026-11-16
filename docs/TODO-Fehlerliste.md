# Offene Punkte / Fehlerliste — Mietverwaltung-SaaS

**Letzte Aktualisierung:** 16. November 2026  
**Verantwortlich:** Hermes Agent / Max Karthoff

Diese Datei dient als zentrale Fehler- und Todo-Liste für UX-Fixes, Bugs und kleine Verbesserungen, die während der Entwicklung auftauchen.

---

## UX / Frontend

| # | Thema | Status | Beschreibung | Wo |
|---|-------|--------|--------------|-----|
| 1 | Lösch-Bestätigung | ✅ Erledigt | Native `window.confirm` durch zentriertes `AppModal` im App-Design ersetzen. | `frontend/src/views/objekte/ObjekteListView.vue` |
| 2 | Cache invalidieren | ✅ Erledigt | index.html no-cache, Assets 1y via Vite-Fingerprint. Nginx-Config als Symlink. → GitHub #51 | `infra/nginx/mietverwaltung.conf` |
| 3 | Favicon fehlt | ✅ Erledigt | `/favicon.svg` hinzugefügt, liefert 200. → GitHub #52 | `frontend/public/favicon.svg`, `frontend/index.html` |
| 4 | Mobile Layouts prüfen | 🔲 Offen | Einige Tabellen/Formulare auf kleinen Bildschirmen noch nicht optimiert. | Alle `*View.vue` |
| 5 | Klickbare KPI-/Detail-Verknüpfungen | ✅ Erledigt | Dashboard-KPIs verlinken auf Listenansichten. → GitHub #47 | `frontend/src/views/dashboard/DashboardView.vue`, `frontend/src/components/dashboard/KPICard.vue` |
| 9 | Ticket: Dateianhänge | 🔄 In Arbeit | UI vorbereitet; echter Upload-Endpunkt folgt mit DMS-Integration. → GitHub #48 | `frontend/src/views/tickets/TicketFormView.vue`, `backend/app/routes/tickets.py` |
| 10 | Ticket: Mieter-Autofill | ✅ Erledigt | Bei Einheit-Auswahl wird Mieter automatisch gesetzt. → GitHub #48 | `frontend/src/views/tickets/TicketFormView.vue`, `backend/app/routes/_helpers.py` |
| 11 | Wohneinheit-Stammdaten erweitern | 🔲 Offen | Flächen, Ausstattung, Räume, Zustand, Energieklasse etc. → GitHub #50 | `backend/app/models/einheit.py`, `frontend/src/views/einheiten/` |
| 12 | Objekt-Stammdaten erweitern | 🔲 Offen | Flächen, Energieausweis, Heizung, Denkmalschutz, Status etc. → GitHub #49 | `backend/app/models/objekt.py`, `frontend/src/views/objekte/` |
| 13 | Kaufmännische Betragsformatierung | ✅ Erledigt | Beträge als „699.000,00 €“ anzeigen. | `frontend/src/components/ui/AppCurrencyInput.vue` |
| 7 | Einheit-Detail-View | 🔲 Offen | Es gibt bisher keine separate Detailansicht für Wohneinheiten. → GitHub #50 | `frontend/src/views/einheiten/` |
| 14 | Mietvertrag-Liste Objekt/Einheit | ✅ Erledigt | Spalten zeigen jetzt Einheit-Name und Objekt-Name. → GitHub #46 | `frontend/src/views/mietvertraege/MietvertraegeListView.vue`, `backend/app/routes/_helpers.py` |

---

## Backend / API

| # | Thema | Status | Beschreibung | Wo |
|---|-------|--------|--------------|-----|
| 7 | Paperless-ngx Integration | 🔄 In Arbeit | `dokumente`-Tabelle, User-Spalten und Alembic-Migration angelegt. Nächster Schritt: Client-Service, Upload-Endpunkte, Frontend-Dokumenten-Reiter. | `backend/app/models/dokument.py`, `backend/app/routes/dokumente.py` |
| 8 | Session-/Cookie-Handling | ✅ Erledigt | Access 24h / Refresh 30 Tage, remember_me Default true, X-Forwarded-Proto für Cloudflare-HTTPS, Promise-basierte Refresh-Queue. → GitHub #45 | `backend/app/services/jwt.py`, `backend/app/routes/auth.py`, `frontend/src/api/client.ts` |
| 9 | Nginx Fehlerseiten | 🔲 Offen | Bei 500/502 zeigt Nginx seine Standard-Fehlerseite. | `infra/nginx/mietverwaltung.conf` |
| 9 | Deployment-Automatisierung | 🔲 Offen | Backend/Frontend/Cloudflare manuell starten. Systemd-Units oder Docker-Compose für stabileren Neustart. | `infra/systemd/` |
| 10 | Tests nach Paperless-Änderungen | 🔲 Offen | Sicherstellen, dass `pytest tests` und `pnpm build` weiterhin grün bleiben. | `backend/tests/`, `frontend/package.json` |

---

## Infrastruktur / Deployment

| # | Thema | Status | Beschreibung | Wo |
|---|-------|--------|--------------|-----|
| 11 | Nginx-Berechtigungen | ✅ Erledigt | `www-data` konnte nicht auf `/root/.../frontend/dist` zugreifen. Rechte auf `root:www-data` mit `755` gesetzt. | `infra/nginx/mietverwaltung.conf`, Server |
| 12 | Statischer Frontend-Server | ✅ Erledigt | `python3 -m http.server` konnte POST-Requests nicht ans Backend weiterleiten. Durch Nginx-Reverse-Proxy ersetzt. | `infra/nginx/mietverwaltung.conf` |
| 11 | Cloudflare-Tunnel-URL | 🔲 Offen | URL ändert sich bei jedem Neustart. Für produktiven Betrieb eigenen Tunnel/Domain einrichten. | `cloudflared` |
| 12 | Log-Rotation | 🔲 Offen | `/tmp/backend.log` und `/tmp/cloudflare.log` wachsen unbegrenzt. Logrotate oder stdout zu Journald. | Server |

---

## Nächste große Arbeitspakete

1. **Paperless-ngx DMS-Integration** (aktuell in Arbeit)
   - Backend-Client-Service
   - Upload/Download/Vorschau-Endpunkte
   - Frontend-Reiter in Objekt/Einheit/Mieter/Mietvertrag

2. **Domain-Core stabilisieren**
   - E2E-Tests Objekt/Einheit/Mieter/Mietvertrag
   - Bankverbindungen + Kostenkategorien verifizieren

3. **Dashboard erweitern**
   - KPIs prüfen
   - Mobile Optimierung

---

## Anleitung: Einen neuen Punkt hinzufügen

1. Kürzeste passende Kategorie wählen.
2. Nächste freie Nummer vergeben.
3. Status setzen: `🔲 Offen`, `🔄 In Arbeit`, `✅ Erledigt`.
4. In Commit-Message referenzieren: z. B. `fix(ux): #1 Lösch-Bestätigung als AppModal`.

---

*Ende der Liste.*
