# MietVerwaltung SaaS — Arbeitsplan Paket 5 (Stand 20.11.2026)

## Ziel
Nachdem Pakete 1–4 (Domain-Core, Öffentliche IDs, Dokumente, Stripe-Billing) abgeschlossen sind, wird die Anwendung production-reifer gemacht, bevor neue Geschäftslogik-Module folgen.

## Arbeitspaket 5: Production-Polish & Infrastruktur

**Scope:** Mobile UX, stabiler Betrieb, sauberes Deployment, Monitoring-Grundlagen.

### 5.1 Mobile Layouts
- [ ] Tabellen in Listen-Views für kleine Screens umbrechen/scrollen/kollabieren
- [ ] Formulare im Mobile-Viewport prüfen (Abstände, Input-Größen, Buttons)
- [ ] Sidebar/Navigation auf Touch optimieren (größere Hit-Areas, kollabieren)
- [ ] Login/Register-Formular auf kleinen Screens testen
- [ ] Frontend-Build grün halten

### 5.2 Nginx-Fehlerseiten
- [ ] Eigene 500/502/503-Fehlerseiten im `frontend/dist/`- oder `infra/nginx/`-Ordner
- [ ] `nginx.conf` anpassen: `error_page 500 502 503 504 /50x.html;`
- [ ] Seite im App-Design (Navy #0D3B70, kurze Meldung, Link zurück)
- [ ] Test via `curl -I` mit gestopptem Backend

### 5.3 Log-Rotation
- [ ] `/tmp/*.log` (uvicorn, cloudflared, nginx) rotieren lassen
- [ ] `logrotate`-Konfiguration in `infra/logrotate/mietverwaltung`
- [ ] Log-Pfade konsolidieren (z. B. `/var/log/mietverwaltung/`)
- [ ] Test: Logs werden täglich/wöchentlich rotiert und nach 30 Tagen gelöscht

### 5.4 Cloudflare-Tunnel stabilisieren
- [ ] Cloudflare-Zugangsdaten / Token prüfen
- [ ] Persistenter named tunnel (`cloudflared tunnel create mietverwaltung`) anlegen
- [ ] Konfiguration `infra/cloudflared/config.yml`
- [ ] Tunnel-URL wird nicht mehr bei jedem Neustart neu vergeben
- [ ] Dokumentation in `docs/ops/tunnel.md`

### 5.5 Deployment-Automatisierung
- [ ] systemd-Unit für Backend (`mietverwaltung-backend.service`)
- [ ] systemd-Unit für Nginx-Proxy/Frontend (`mietverwaltung-nginx.service`)
- [ ] systemd-Unit für Cloudflare-Tunnel (`mietverwaltung-tunnel.service`)
- [ ] Start-/Stop-/Restart-Skript oder Makefile-Target
- [ ] `.github/workflows/deploy-prod.yml` anpassen (kein Docker, native systemd-Deployment)
- [ ] Rolling-Restart ohne Downtime prüfen

### 5.6 Produktions-Readiness-Check
- [ ] `.env` Keys auf Server prüfen (Stripe, Resend, DB, JWT, Encryption)
- [ ] `/health` liefert auch DB/Redis-Status
- [ ] Sicherheits-Header-Review (CORS, CSP, HSTS)
- [ ] Smoke-Test nach Deployment

## Abgrenzung (kommen später)
- Keine neuen Geschäftslogik-Module (Mahnwesen, KI, Admin-Center)
- Keine Paperless-ngx-Docker-Integration
- Keine Stripe-Live-Schaltung (nur Vorbereitung)

## Akzeptanzkriterien
- Frontend-Build grün
- Backend-Testsuite bleibt 221/221 grün
- `make deploy` oder ähnliches startet/neu startet alle Services
- Logs wachsen nicht unbegrenzt
- Mobile Ansicht ist nutzbar für Login, Dashboard, Listen, Formulare
- Nginx zeigt eigene Fehlerseiten statt Standardseiten

## Reihenfolge
1. Mobile Layouts (schnellster sichtbarer Impact)
2. Nginx-Fehlerseiten
3. Log-Rotation
4. Cloudflare-Tunnel stabilisieren
5. systemd-Units + Deployment-Automatisierung
6. Produktions-Readiness-Check

## Kommunikation
- Nach jedem Unterpunkt kurze Statusmeldung + Commit
- Blocker oder Änderungen sofort melden
- User kann jederzeit Priorität ändern oder Paket überspringen
