# Server-Konzept — MietVerwaltung SaaS

## 1. Übersicht: Zwei Umgebungen

```
ENTWICKLUNG (lokal)                    PRODUKTION (Hetzner)
┌──────────────────────┐              ┌──────────────────────┐
│  Proxmox VM/LXC      │              │  Hetzner Cloud CX32   │
│  4 vCPU, 8GB RAM     │    Deploy    │  4 vCPU, 8GB RAM      │
│  50GB SSD            │ ──────────→  │  80GB SSD             │
│  Docker Compose      │              │  Docker Compose       │
│  .test Domain        │              │  mietverwaltung.de    │
│  Keine echten Kunden │              │  Echte Kunden         │
└──────────────────────┘              └──────────────────────┘
         │                                     │
         │           Ollama Cloud API           │
         └─────────────┬───────────────────────┘
                       ▼
              ┌──────────────────┐
              │  Ollama Cloud    │
              │  GLM 5.2         │
              │  Kimi K2.6       │
              └──────────────────┘
```

---

## 2. Produktionsserver — Hetzner Cloud

### Server- Spezifikation

| Eigenschaft | Wert |
|------------|------|
| Provider | Hetzner Cloud (Deutschland) |
| Standort | Falkenstein (FSN1) oder Frankfurt (FRA) |
| Server-Typ | CX32 (Start) → CX42 (bei Wachstum) |
| CPU | 4 vCPU (Intel) |
| RAM | 8 GB (CX32) / 16 GB (CX42) |
| SSD | 80 GB / 160 GB |
| Bandbreite | 20 TB Traffic/Monat |
| IPv4 | 1× inklusive |
| Preis | ~15€/Monat (CX32) |

### Hetzner-spezifische DSGVO-Maßnahmen

| Maßnahme | Status |
|----------|--------|
| Server in Deutschland | ✅ FSN1/FRA |
| AVV mit Hetzner | ✅ Hetzner bietet AVV an |
| Keine EU-Datenübermittlung | ✅ |
| ISO 27001 zertifiziert | ✅ Hetzner |
| Backup in EU | ✅ Hetzner Storage Box (DE) |

---

## 3. Software-Stack auf dem Server

### Betriebssystem & Basis

| Komponente | Version | Zweck |
|------------|---------|-------|
| OS | Ubuntu 24.04 LTS | Stabil, lange Support-Dauer |
| Docker | 27.x | Container-Orchestrierung |
| Docker Compose | v2 | Multi-Container-Setup |
| CloudPanel | aktuell | Domain, SSL, Reverse Proxy |
| UFW | — | Firewall |

### Docker Services (docker-compose.yml)

```
┌─────────────────────────────────────────────────────────┐
│                 Docker Network (mietverwaltung)          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Frontend  │  │ Backend  │  │Database  │  │  Redis  │ │
│  │ (Vue.js)  │  │(FastAPI) │  │(Postgres)│  │ (Cache) │ │
│  │ :8080     │  │ :8000    │  │ :5432    │  │ :6379   │ │
│  │ nginx     │  │ Python   │  │ PG 17    │  │         │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                      │                                   │
│              ┌──────────────┐    ┌──────────────┐       │
│              │  OCR Service │    │ PDF Service  │       │
│              │ (Tesseract)  │    │ (WeasyPrint) │       │
│              │ integriert   │    │ integriert   │       │
│              │ im Backend   │    │ im Backend   │       │
│              └──────────────┘    └──────────────┘       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Postfix (Mail)                       │   │
│  │              :25 / :587                           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Service-Details

| Service | Container | Port (intern) | Port (extern) | Ressourcen |
|---------|-----------|--------------|--------------|-----------|
| Frontend (Vue.js) | nginx:alpine | 8080 | — (über CloudPanel) | 128MB RAM |
| Backend (FastAPI) | python:3.13-slim | 8000 | — (intern) | 512MB RAM |
| PostgreSQL 17 | postgres:17 | 5432 | — (intern) | 1GB RAM |
| Redis 7 | redis:7-alpine | 6379 | — (intern) | 128MB RAM |
| Postfix | postfix:latest | 25 | — (intern) | 64MB RAM |
| **Gesamt** | — | — | — | **~1,8GB RAM** |

**Verbleibend für OS + CloudPanel + Puffer: ~6,2GB RAM → ausreichend.**

---

## 4. Netzwerk-Architektur

### Port-Layout

```
INTERNET (nur über CloudPanel/nginx)
    │
    ├── :443 (HTTPS) ──────→ CloudPanel nginx ──→ Frontend (:8080)
    │                                         └──→ Backend API (:8000/api)
    │
    ├── :80 (HTTP) ────────→ Redirect → :443 (HTTPS only)
    │
    └── :22 (SSH) ─────────→ Nur von deinen IPs (UFW)

INTERN (Docker Network — nicht von außen erreichbar)
    ├── :8000  Backend API
    ├── :5432  PostgreSQL
    ├── :6379  Redis
    └── :25    Postfix (Mail)
```

### Firewall (UFW)

```
# Eingehend
:22    ALLOW   <deine-IPs>           # SSH nur von deinen IPs
:80    ALLOW   Anywhere              # HTTP → HTTPS redirect
:443   ALLOW   Anywhere              # HTTPS (Hauptzugang)

# Alles andere: DENY (default)

# IP-Blocking DACH (später via GeoIP)
# Nicht-DACH-IPs → 403 (in nginx konfiguriert)
```

### CloudPanel Konfiguration

```
Domain: mietverwaltung.de
  ├── SSL: Let's Encrypt (auto-renew)
  ├── nginx Site:
  │   ├── / → Frontend (Vue.js, statisch)
  │   ├── /api → Backend (FastAPI, :8000)
  │   ├── Security Headers (HSTS, CSP, X-Frame-Options)
  │   ├── Gzip Kompression
  │   └── Rate Limiting (API: 100 req/min)
  └── PHP: nicht benötigt (Python-Backend)
```

### nginx Reverse Proxy Konfiguration

```nginx
server {
    listen 443 ssl http2;
    server_name mietverwaltung.de;

    # SSL
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    add_header Referrer-Policy "strict-origin" always;

    # Frontend (statische Dateien)
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate Limiting
        limit_req zone=api burst=20 nodelay;

        # Upload Size (für Dokumente)
        client_max_body_size 25M;
    }

    # Health Check
    location /api/health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# HTTP → HTTPS Redirect
server {
    listen 80;
    server_name mietverwaltung.de;
    return 301 https://$server_name$request_uri;
}
```

---

## 5. Datenbank-Architektur

### PostgreSQL Konfiguration

```ini
# postgresql.conf (optimiert für 8GB Server)

# Memory
shared_buffers = 512MB          # 25% von dediziertem RAM
effective_cache_size = 2GB      # 50% von RAM
work_mem = 16MB
maintenance_work_mem = 128MB

# Connections
max_connections = 50            # reicht für SaaS mit <100 Vermietern

# Security
ssl = on
password_encryption = scram-sha-256
listen_addresses = 'localhost'  # nur intern

# Row Level Security (DSGVO Datenisolation)
# In jeder Tabelle mit vermieter_id:
# CREATE POLICY vermieter_isolation ON einheiten
#   USING (vermieter_id = current_setting('app.vermieter_id')::uuid);
```

### Verschlüsselung

```sql
-- pgcrypto für Feld-Verschlüsselung
CREATE EXTENSION pgcrypto;

-- Sensible Felder verschlüsseln
-- IBAN: AES-256-GCM
-- Steuernummer: AES-256-GCM
-- Geburtsdatum: AES-256-GCM

-- Beispiel:
INSERT INTO vermieter_profile (iban)
VALUES (pgp_sym_encrypt('DE89370400440532013000', encryption_key));
```

### Backup-Strategie

```
TÄGLICH (automatisch, 02:00 Uhr):
  ├── pg_dump → komprimiert → verschlüsselt
  ├── Upload zu Hetzner Storage Box
  ├── Retention: 7 Tage (daily)
  └── Audit-Log-Eintrag

WÖCHENTLICH (Sonntag, 03:00 Uhr):
  ├── Full backup (Datenbank + Datei-Uploads)
  ├── Upload zu Hetzner Storage Box
  └── Retention: 4 Wochen (weekly)

MONATLICH (1. des Monats, 04:00 Uhr):
  ├── Full backup
  ├── Retention: 12 Monate (monthly)
  └── Verifizierung: Restore-Test

BACKUP-SCRIPT (automatisiert):
  1. pg_dump --format=custom --compress=9
  2. gpg --symmetric --cipher-algo AES256 (verschlüsseln)
  3. rsync → storage-box.hetzner.com
  4. Alert bei Fehler (E-Mail an Admin)
```

---

## 6. Datei-Storage (Dokumenten-Uploads)

### Architektur

```
Upload-Verzeichnis:
/opt/mietverwaltung/uploads/
├── objekte/
│   └── {objekt_id}/
│       └── mietvertrag_2026.pdf
├── mieter/
│   └── {mieter_id}/
│       ├── lohnabrechnung_01.pdf
│       ├── lohnabrechnung_02.pdf
│       └── schufa_auskunft.pdf
├── belege/
│   └── {objekt_id}/
│       └── muellabfuhr_2026.pdf
└── dokumente_generiert/
    └── {mieter_id}/
        └── wohnungsgeberbestaetigung.pdf

VERSCHLÜSSELUNG:
  Alle Dateien AES-256 verschlüsselt at-rest
  Entschlüsselung nur zur Laufzeit im Backend

LÖSCHUNG:
  - Ausweis-Bilder: sofort nach OCR
  - Lohnabrechnungen: nach 30 Tagen oder Entscheidung
  - Schufa: nach Entscheidung
  - Generierte Dokumente: bleiben (gehören zum Mietverhältnis)
  - Aufbewahrungsfrist: Mietvertragsdaten 10J (§147 AO)
```

### Upload-Validierung

```python
ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
VIRUS_SCAN = True  # ClamAV (optional, später)

def validate_upload(file):
    # Type check
    if file.content_type not in ALLOWED_TYPES:
        raise ValidationError("Nur PDF, JPG, PNG erlaubt")
    # Size check
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("Max 10 MB pro Datei")
    # Magic bytes check (echter Dateityp, nicht nur Header)
    if not check_magic_bytes(file):
        raise ValidationError("Datei beschädigt oder gefälscht")
```

---

## 7. E-Mail-System

### Postfix Konfiguration

```ini
# main.cf
myhostname = mail.mietverwaltung.de
mydomain = mietverwaltung.de
inet_interfaces = all
inet_protocols = ipv4

# TLS
smtpd_tls_cert_file = /path/to/cert.pem
smtpd_tls_key_file = /path/to/key.pem
smtpd_use_tls = yes
smtpd_tls_auth_only = yes

# Sicherheit
smtpd_recipient_restrictions =
    permit_mynetworks,
    reject_unauth_destination

# DKIM/SPF/DMARC (gegen Spam-Markierung)
# DNS-Einträge:
#   TXT  mietverwaltung.de  "v=spf1 mx a -all"
#   TXT  _dmarc.mietverwaltung.de  "v=DMARC1; p=quarantine; adkim=s; aspf=s"
```

### E-Mail-Typen

| E-Mail | Auslöser | Von | An | Template |
|--------|---------|-----|-----|---------|
| Willkommen (Vermieter) | Registrierung | system | vermieter | HTML |
| Willkommen (Mieter) | Vermieter erstellt Login | system | mieter | HTML |
| Neues Ticket | Mieter erstellt Ticket | system | vermieter | HTML |
| Ticket-Antwort | Vermieter antwortet | system | mieter | HTML |
| Ticket-Status geändert | Status-Wechsel | system | mieter | HTML |
| 2FA-Code | Login ohne TOTP | system | user | Plain |
| Mahnung Stufe 1/2/3 | Cron-Job | system | mieter | PDF-Anhang |
| Abrechnung | Vermieter versendet | system | mieter | PDF-Anhang |
| Dokument generiert | Vermieter generiert | system | mieter | PDF-Anhang |
| Passwort-Reset | User anfordert | system | user | HTML |
| Frist-Warnung | Cron-Job | system | vermieter | HTML |

---

## 8. Security-Konzept (Server-Ebene)

### SSL/TLS

```
Let's Encrypt Zertifikat (über CloudPanel)
  ├── Auto-Renewal (alle 60 Tage)
  ├── TLS 1.2 + 1.3 nur (1.0/1.1 deaktiviert)
  ├── HSTS Header (max-age=31536000)
  └── OCSP Stapling aktiviert
```

### SSH-Härtung

```bash
# /etc/ssh/sshd_config
Port 22                          # oder abweichend
PermitRootLogin prohibit-password # Key-only für root
PasswordAuthentication no        # Keine Passwort-Logins
PubkeyAuthentication yes         # Nur SSH-Keys
MaxAuthTries 3
AllowUsers root deploy           # Nur spezifische User
```

### Fail2Ban (Brute-Force-Schutz)

```ini
[sshd]
enabled = true
maxretry = 3
bantime = 3600
findtime = 600

[nginx-limit-req]
enabled = true
maxretry = 10
bantime = 7200
```

### GeoIP-Blocking (DACH-Restriktion)

```nginx
# nginx config
geoip2 /etc/nginx/geoip/GeoLite2-Country.mmdb {
    $geoip2_data_country_code country iso_code;
}

map $geoip2_data_country_code $allowed_country {
    default no;
    DE yes;    # Deutschland
    AT yes;    # Österreich
    CH yes;    # Schweiz
}

server {
    if ($allowed_country = no) {
        return 403;
    }
}
```

### Docker-Sicherheit

```yaml
# docker-compose.yml Sicherheits-Prinzipien:
services:
  backend:
    user: "1000:1000"              # Nicht als root
    read_only: true                # Read-only filesystem
    cap_drop: [ALL]                # Alle Capabilities entfernen
    security_opt:
      - no-new-privileges:true
    networks:
      - internal                   # Nur internes Netzwerk

  postgres:
    user: "999:999"
    networks:
      - internal                   # NIEMALS extern erreichbar

networks:
  internal:
    internal: true                 # Kein Internet-Zugang
```

---

## 9. Monitoring & Health Checks

### Health Check Endpoints

```python
# Backend (FastAPI)
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "database": check_db(),
        "redis": check_redis(),
        "ai": check_ollama(),
        "timestamp": datetime.utcnow()
    }

@app.get("/health/ai")
async def ai_health():
    try:
        response = ollama_cloud.generate("OK", max_tokens=5)
        return {"ai": "online", "model": "glm-5.2"}
    except:
        return {"ai": "offline", "fallback": "active"}
```

### Monitoring (einfach, ohne extra Tools)

```
CRON-JOB (alle 5 Minuten):
  ├── curl http://localhost:8000/health
  ├── Wenn "error" → E-Mail an Admin
  ├── Disk-Usage > 80% → Warnung
  ├── RAM-Usage > 85% → Warnung
  └── DB-Connections > 40 → Warnung

CRON-JOB (stündlich):
  ├── KI-Verfügbarkeit prüfen
  ├── Backup-Status prüfen
  └── SSL-Zertifikat-Ablauf prüfen
```

### Log-Management

```
Docker Logs:
  ├── json-file driver
  ├── max-size: 10m
  ├── max-file: 3
  └── Rotation automatisch

App-Logs (Backend):
  ├── /var/log/mietverwaltung/app.log
  ├── Rotation: täglich, 30 Tage behalten
  ├── Format: JSON (strukturiert)
  └── Keine Personendaten in Logs!

Audit-Logs (DSGVO):
  ├── Separate Tabelle in PostgreSQL
  ├── Auth-Events, Datenzugriff, Exporte, Löschungen
  ├── Retention: 12 Monate
  └── Zugriff nur für Admin
```

---

## 10. Deployment-Pipeline

### Entwicklung → Produktion

```
1. LOKAL (Proxmox VM)
   ├── Code schreiben
   ├── Docker Compose starten
   ├── Tests ausführen
   └── Features testen

2. GIT (GitHub/Gitea)
   ├── git commit
   ├── git push origin main
   └── CI/CD (optional später)

3. PRODUKTION (Hetzner)
   ├── SSH → Server
   ├── git pull origin main
   ├── docker compose build
   ├── docker compose up -d
   ├── Migration ausführen (alembic upgrade head)
   ├── Health Check prüfen
   └── Fertig
```

### docker-compose.yml Struktur

```yaml
version: '3.8'

services:
  # === FRONTEND ===
  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
    restart: always
    networks:
      - web

  # === BACKEND ===
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    volumes:
      - uploads:/app/uploads
    restart: always
    networks:
      - web
      - internal

  # === DATENBANK ===
  postgres:
    image: postgres:17-alpine
    env_file:
      - .env.production
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d
    restart: always
    networks:
      - internal    # NIEMALS extern

  # === CACHE ===
  redis:
    image: redis:7-alpine
    restart: always
    networks:
      - internal

  # === MAIL ===
  postfix:
    build: ./postfix
    restart: always
    networks:
      - internal
      - web

volumes:
  uploads:
  pgdata:

networks:
  web:           # Extern erreichbar (über CloudPanel)
  internal:      # Nur intern (DB, Redis)
    internal: true
```

### .env.production

```env
# Datenbank
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mietverwaltung
POSTGRES_USER=mietverwaltung
POSTGRES_PASSWORD=<strong-random-password>
DB_ENCRYPTION_KEY=<strong-random-key>

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=<strong-random-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# Ollama Cloud
OLLAMA_BASE_URL=https://ollama.com/v1
OLLAMA_API_KEY=<api-key>
OLLAMA_MODEL_PRIMARY=glm-5.2
OLLAMA_MODEL_COMPLEX=kimi-k2.6

# E-Mail
SMTP_HOST=mail.mietverwaltung.de
SMTP_PORT=587
SMTP_USER=noreply@mietverwaltung.de
SMTP_PASSWORD=<mail-password>

# App
APP_ENV=production
APP_URL=https://mietverwaltung.de
ALLOWED_COUNTRIES=DE,AT,CH

# DSGVO
DSGVO_RETENTION_CONTRACT_YEARS=10
DSGVO_RETENTION_BILLING_YEARS=6
```

---

## 11. Verzeichnis-Struktur (Projekt)

```
/mietverwaltung/
├── docker-compose.yml
├── docker-compose.dev.yml          # Development overrides
├── .env.production
├── .env.development
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                    # DB-Migrationen
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── main.py                 # FastAPI Entry Point
│   │   ├── config.py               # Settings
│   │   ├── database.py             # DB-Connection
│   │   ├── auth/                   # Auth + 2FA + JWT
│   │   ├── models/                 # SQLAlchemy Models
│   │   ├── routes/                 # API-Endpoints
│   │   │   ├── auth.py
│   │   │   ├── objekte.py
│   │   │   ├── mieter.py
│   │   │   ├── tickets.py
│   │   │   ├── kosten.py
│   │   │   ├── abrechnung.py
│   │   │   ├── dokumente.py
│   │   │   └── dashboard.py
│   │   ├── services/               # Business Logic
│   │   │   ├── ki/
│   │   │   │   ├── ollama.py       # Ollama Cloud API
│   │   │   │   ├── anonymizer.py   # Anonymisierungs-Engine
│   │   │   │   ├── classifier.py   # Keyword-Classifier
│   │   │   │   ├── ocr.py          # Tesseract OCR
│   │   │   │   └── prompts.py      # Prompt-Templates
│   │   │   ├── pdf.py              # WeasyPrint PDF-Generierung
│   │   │   ├── templates.py        # Jinja2 Template-Engine
│   │   │   ├── email.py            # E-Mail-Versand
│   │   │   ├── abrechnung.py       # Abrechnungs-Logik
│   │   │   ├── mahnung.py          # Mahn-Workflow
│   │   │   └── insights.py         # Smart Insights
│   │   ├── middleware/              # Security Middleware
│   │   │   ├── auth.py             # JWT-Validation
│   │   │   ├── roles.py            # RBAC
│   │   │   ├── rate_limit.py       # Rate Limiting
│   │   │   └── geoip.py            # DACH-Blocking
│   │   └── utils/
│   │       ├── crypto.py           # Verschlüsselung
│   │       ├── audit.py            # Audit-Log
│   │       └── validators.py       # Input-Validation
│   └── tests/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/                 # Vue Router
│   │   ├── stores/                 # Pinia State
│   │   ├── views/
│   │   │   ├── vermieter/          # Vermieter-Portal
│   │   │   ├── mieter/             # Mieter-Portal
│   │   │   └── auth/               # Login, Register, 2FA
│   │   ├── components/             # Wiederverwendbare UI
│   │   ├── assets/
│   │   └── styles/
│   └── public/
│       └── manifest.json           # PWA Manifest
│
├── db/
│   └── init/
│       └── 01-schema.sql           # Initial DB-Schema
│
├── postfix/
│   ├── Dockerfile
│   └── main.cf
│
├── nginx/
│   └── mietverwaltung.conf          # Reverse Proxy Config
│
└── scripts/
    ├── backup.sh                    # Backup-Script
    ├── restore.sh                   # Restore-Script
    ├── health-check.sh              # Health-Check
    └── deploy.sh                    # Deployment-Script
```

---

## 12. Entwicklungs-VM (Proxmox)

### Proxmox LXC/VM Spezifikation

| Eigenschaft | Wert |
|------------|------|
| Typ | LXC Container (leichtgewichtiger als VM) |
| OS | Ubuntu 24.04 LTS |
| CPU | 2 Kerne |
| RAM | 4 GB |
| SSD | 30 GB |
| Netzwerk | Nur intern + Cloudflared Tunnel |
| Docker | Ja |
| Zugriff | SSH + Cloudflared Tunnel für Tests |

### Development vs. Production

| Aspekt | Development (Proxmox) | Production (Hetzner) |
|--------|----------------------|---------------------|
| Domain | *.trycloudflare.com | mietverwaltung.de |
| SSL | Cloudflared Tunnel | Let's Encrypt |
| DB | SQLite (einfacher) oder PostgreSQL | PostgreSQL |
| Mail | Mailhog (catch-all, nichts senden) | Postfix (echter Versand) |
| KI | Ollama Cloud (gleiche API) | Ollama Cloud |
| Daten | Testdaten/Beispieldaten | Echte Kundendaten |
| Debug | DEBUG=True, Hot-Reload | DEBUG=False, optimiert |
| Backups | Manuell | Automatisch täglich |

---

## 13. Kosten-Gesamtübersicht

### Fixkosten (Produktion)

| Posten | Kosten/Monat |
|--------|-------------|
| Hetzner CX32 | 15,09€ |
| Hetzner Storage Box 100GB | 4,15€ |
| Domain (mietverwaltung.de) | ~5,00€ |
| **Fixkosten gesamt** | **~24,24€** |

### Variable Kosten (pro Vermieter)

| Posten | Kosten/Monat |
|--------|-------------|
| KI (Ollama Cloud) | ~0,05-0,15€ |
| Storage (Dokumente) | ~0,05€ |
| E-Mail-Versand | ~0,01€ |
| **Pro Vermieter** | **~0,11-0,21€** |

### Break-even

| Plan | Preis | Ab wievielen Vermietern profitabel? |
|------|-------|-----------------------------------|
| Basis (9,90€) | 9,90€ - ~0,20€ = 9,70€ Marge | 3 Vermieter (24€ Fixkosten ÷ 9,70€) |
| Pro (19,90€) | 19,90€ - ~0,20€ = 19,70€ Marge | 2 Vermieter |
| Business (39,90€) | 39,90€ - ~0,30€ = 39,60€ Marge | 1 Vermieter |

**Ab 3 zahlenden Vermietern ist die SaaS profitabel.**

---

## 14. Wartung & Updates

### Regelmäßige Tasks

| Frequenz | Task | Automatisiert? |
|----------|------|---------------|
| Täglich 02:00 | Database Backup | ✅ Cron |
| Wöchentlich | Docker Image Updates prüfen | ✅ Cron (Watchtower) |
| Monatlich | Security Updates (apt) | ⚠️ Manuell + Test |
| Monatlich | Backup-Restore-Test | ⚠️ Manuell |
| Quartal | Dependency Updates (pip, npm) | ⚠️ Manuell + Test |
| Halbjährlich | SSL-Zertifikat-Prüfung | ✅ Auto-Renew |
| Jährlich | DSGVO-Audit | ⚠️ Manuell |

### Update-Prozess

```
1. Auf Development-VM: Updates installieren + testen
2. Bei Erfolg: git commit + push
3. Auf Hetzner: git pull
4. docker compose build
5. docker compose up -d (zero-downtime bei großem Traffic)
6. Health Check → wenn error: rollback (git checkout previous + rebuild)
```