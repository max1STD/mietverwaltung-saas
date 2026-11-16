# Deployment-Guide: Mietverwaltung-SaaS

**Datum:** 16. November 2026  
**Autor:** Hermes Agent  
**Scope:** Lokales Deployment-Setup mit Nginx, Backend, Frontend und Cloudflare-Tunnel.

---

## 1. Übersicht

Der Produktiv-Stack besteht aus drei Komponenten:

```
[Nutzer] → [Cloudflare-Tunnel] → [Nginx :5173] → [Frontend dist/ oder Backend :8000]
```

| Komponente | Port | Aufgabe |
|------------|------|---------|
| FastAPI-Backend | 8000 | API, Auth, Business-Logik |
| Nginx | 5173 | Statisches Frontend + API-Proxy |
| Cloudflared | – | Öffentlicher Tunnel auf Nginx |

---

## 2. Voraussetzungen

- PostgreSQL läuft auf `127.0.0.1:5432`.
- Redis läuft auf `127.0.0.1:6379`.
- `.env` im Projekt-Root ist mit Datenbank, JWT und ggf. Stripe-Keys befüllt.
- Nginx ist installiert.
- Node.js/npm ist für den Frontend-Build verfügbar.
- Cloudflared ist installiert.

---

## 3. Einmalige Einrichtung

### 3.1 Nginx-Konfiguration aktivieren

```bash
sudo cp infra/nginx/mietverwaltung.conf /etc/nginx/sites-enabled/mietverwaltung.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo nginx -s reload
```

### 3.2 Datenbank-Migrationen

```bash
cd backend
.venv/bin/python -m alembic upgrade head
```

---

## 4. Start des Stacks

### 4.1 Backend

```bash
cd /root/mietverwaltung-saas/backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4.2 Frontend-Build

```bash
cd /root/mietverwaltung-saas/frontend
npm run build
```

Das Ergebnis liegt in `frontend/dist/`.

### 4.3 Cloudflare-Tunnel

```bash
cloudflared tunnel --url http://127.0.0.1:5173
```

Die öffentliche URL wird in der Ausgabe angezeigt.

---

## 5. Wichtige Endpunkte

| URL | Zweck |
|-----|-------|
| `https://<tunnel>/` | Frontend |
| `https://<tunnel>/api/v1/...` | API |
| `https://<tunnel>/health` | Health-Check |
| `https://<tunnel>/docs` | Swagger-Doku |

---

## 6. Fehlerszenarien

### Login schlägt fehl / „Anmeldung fehlgeschlagen“

**Ursache:** Frontend wurde nur mit `python3 -m http.server` gestartet. Statischer Server kann POST-Requests nicht an das Backend weiterleiten.

**Lösung:** Immer Nginx verwenden oder `pnpm dev` / `npx vite` für Entwicklung nutzen, damit der `/api`-Proxy greift.

### 404 für Frontend-Routen nach Reload

**Ursache:** SPA-Fallback fehlt.

**Lösung:** Nginx-Konfiguration enthält `try_files $uri $uri/ /index.html;`.

### 500 beim Aufruf von /health

**Ursache:** `/health` wird vom Frontend-SPA-Fallback abgefangen.

**Lösung:** Nginx-Regel für `/health` muss direkt ans Backend proxen.

---

## 7. Automatisierung (optional)

Für stabilen Betrieb empfohlen:

- Systemd-Units für Backend und Cloudflared.
- Watchdog oder Health-Check, der Backend bei Ausfall neustartet.
- Log-Rotation für `/tmp/backend.log` und `/tmp/cloudflare.log`.

---

## 8. Aktuelle URLs

Letzte bestätigte Live-URL: `https://levels-taxi-survey-town.trycloudflare.com`

Cloudflare-Tunnel-URLs ändern sich bei jedem Neustart des Tunnels.

---

*Ende des Guides.*
