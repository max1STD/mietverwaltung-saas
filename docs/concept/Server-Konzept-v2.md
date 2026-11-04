# Server-Konzept v2 — MietVerwaltung SaaS

> **Gültig ab:** 2026-11-02  
> **Ersetzt:** `/root/mietverwaltung/Server-Konzept.md`  
> **Dokument-Typ:** Architektur-Grundlage mit klarer Trennung  
>   - **MVP Closed Beta:** Proxmox, 0 €, maximal 10 bekannte Tester, nicht kommerziell  
>   - **Go-Live:** Hetzner, DSGVO-konform, kommerziell, öffentlich

---

## 0. Zwei Modi: MVP vs. Go-Live

| Aspekt | **MVP Closed Beta** | **Go-Live (kommerziell)** |
|--------|---------------------|---------------------------|
| Ziel | Interner Test mit max. 10 Personen | Öffentliche SaaS für zahlende Kunden |
| Hosting | Proxmox (eigen), ein LXC | Hetzner Cloud, getrennte Server |
| Kosten | **0 €** | ~30–35 €/Mo (Start) |
| Öffentlichkeit | Cloudflared-Tunnel-URL (keine Domain nötig) | Eigene Domain, öffentlich |
| Kommerziell | Nein | Ja |
| DSGVO-Pflichten | Entfallen wegen Nicht-Kommerzialität* | Vollständig (VVT, AVV, Einwilligung, etc.) |
| Server-Trennung | Nein — alles in einem LXC | Ja — Frontend/Backend getrennt |
| Backup | Lokal auf Proxmox | WAL-G + Hetzner Storage Box |
| E-Mail | Resend Free Tier | Amazon SES / Brevo |
| Monitoring | Basis-Logs | UptimeRobot + Sentry + Loki |
| GeoIP / Rate-Limit | Nicht zwingend | Ja |

\* Sobald personenbezogene Daten verarbeitet werden, gelten grundsätzlich Datenschutz-Grundsätze. Im dokumentierten Closed-Beta-Modus ohne geschäftsmäßige Verarbeitung werden die meisten kommerziellen Pflichten (AVV, Impressum, AGB) nicht ausgelöst. Beim Übergang zum Go-Live müssen diese vollständig nachgeholt werden.

---

## 1. MVP Closed Beta — Ein LXC, ein Docker-Compose-Stack

### 1.1 Zielsetzung

- Schnellster Weg, um 10 bekannte Tester an Bord zu bekommen.
- Keine öffentliche Domain nötig; Cloudflared-Tunnel-URL reicht.
- Keine Extra-Kosten.
- Trennung von Frontend/Backend ist **nicht** nötig — kommt erst beim Go-Live.

### 1.2 Proxmox LXC

| Eigenschaft | Wert |
|------------|------|
| Container-Typ | Unprivilegierter LXC |
| OS | Ubuntu 24.04 LTS |
| Ressourcen | 4 vCPU, 6–8 GB RAM, 40–60 GB Storage |
| Netzwerk | NAT/Bridge mit Internet-Zugang |
| Öffentliche IP | Nicht zwingend (Cloudflared Tunnel) |
| Software | Docker, Docker Compose, Cloudflared |

### 1.3 Netzwerk-Architektur MVP

```
Internet
    │
    ▼
┌─────────────────────────────────────┐
│  Cloudflare Edge                    │
│  (HTTPS, beliebige Tunnel-URL)      │
└─────────────┬───────────────────────┘
              │  Cloudflared Tunnel
              │  (ausgehend, im LXC)
              ▼
┌───────────────────────────────────────────────────────────┐
│                Proxmox LXC (MVP)                           │
│                                                            │
│   ┌─────────────┐      ┌──────────┐      ┌──────────┐   │
│   │ cloudflared │─────▶│  nginx   │─────▶│ FastAPI  │   │
│   └─────────────┘      │   :80    │      │  :8000   │   │
│                        └────┬─────┘      └────┬─────┘   │
│                             │                 │         │
│                        ┌────┴─────┐      ┌────┴─────┐   │
│                        │  Redis   │      │ Postgres │   │
│                        │  :6379   │      │  :5432   │   │
│                        └──────────┘      └──────────┘   │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

### 1.4 Docker Compose MVP (`docker-compose.yml`)

```yaml
name: mietverwaltung-mvp

services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run --token ${CLOUDFLARED_TUNNEL_TOKEN}
    environment:
      TUNNEL_TOKEN: ${CLOUDFLARED_TUNNEL_TOKEN}
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    networks:
      - mvp-net
    restart: unless-stopped

  nginx:
    image: nginx:stable-alpine
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    volumes:
      - /srv/mietverwaltung/frontend/dist:/usr/share/nginx/html:ro
      - ./ops/nginx/mvp-nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /var/log/nginx:/var/log/nginx
    tmpfs:
      - /var/cache/nginx:noexec,nosuid,size=64m
      - /run:noexec,nosuid,size=32m
    networks:
      - mvp-net
    restart: unless-stopped
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: ops/phase1/Dockerfile.backend
    image: mietverwaltung/backend:${GIT_TAG:-latest}
    user: "1000:1000"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://mietuser@mietverwaltung-db:5432/mietverwaltung
      DB_PASSWORD_FILE: /run/secrets/db_password
      DB_HOST: mietverwaltung-db
      REDIS_URL: redis://mietverwaltung-redis:6379/0
      REDIS_PASSWORD_FILE: /run/secrets/redis_password
      SECRET_KEY_FILE: /run/secrets/app_secret
      ENCRYPTION_KEY_FILE: /run/secrets/encryption_key
      OLLAMA_API_KEY_FILE: /run/secrets/ollama_api_key
    secrets:
      - db_password
      - redis_password
      - app_secret
      - encryption_key
      - ollama_api_key
    tmpfs:
      - /tmp:noexec,nosuid,size=512m
    volumes:
      - /srv/mietverwaltung/uploads:/app/uploads
      - /srv/mietverwaltung/exports:/app/exports
      - /srv/mietverwaltung/logs:/app/logs
    networks:
      - mvp-net
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:17
    user: "1000:1000"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    environment:
      POSTGRES_USER_FILE: /run/secrets/db_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: mietverwaltung
      PGDATA: /var/lib/postgresql/data/pgdata
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256 --auth-local=scram-sha-256"
    secrets:
      - db_user
      - db_password
    volumes:
      - /srv/mietverwaltung/postgres-data:/var/lib/postgresql/data
      - /srv/mietverwaltung/logs/postgres:/app/logs
      - ./db/init:/docker-entrypoint-initdb.d:ro
    networks:
      - mvp-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $(cat /run/secrets/db_user) -d mietverwaltung"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    user: "1000:1000"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    command: >
      redis-server
      --requirepass $(cat /run/secrets/redis_password)
      --appendonly yes
      --appendfsync everysec
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
    secrets:
      - redis_password
    volumes:
      - /srv/mietverwaltung/redis-data:/data
    networks:
      - mvp-net
    healthcheck:
      test: ["CMD-SHELL", "redis-cli --raw --no-auth-warning -a $(cat /run/secrets/redis_password) ping | grep PONG"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  cron:
    build:
      context: .
      dockerfile: ops/phase1/Dockerfile.backend
    image: mietverwaltung/backend:${GIT_TAG:-latest}
    user: "1000:1000"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    entrypoint: ["/bin/sh"]
    command: ["-c", "crond -f -l 2"]
    env_file: .env
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
      DB_HOST: mietverwaltung-db
    secrets:
      - db_password
      - db_user
    volumes:
      - /srv/mietverwaltung/backups:/app/backups
      - ./ops/scripts/mvp-backup.sh:/usr/local/bin/miet-backup:ro
      - ./ops/crontab:/etc/cron.d/mietverwaltung:ro
    networks:
      - mvp-net
    depends_on:
      - db
    restart: unless-stopped

secrets:
  db_user:
    file: ./ops/secrets/db_user.txt
  db_password:
    file: ./ops/secrets/db_password.txt
  redis_password:
    file: ./ops/secrets/redis_password.txt
  app_secret:
    file: ./ops/secrets/app_secret.txt
  encryption_key:
    file: ./ops/secrets/encryption_key.txt
  ollama_api_key:
    file: ./ops/secrets/ollama_api_key.txt

networks:
  mvp-net:
    driver: bridge
```

### 1.5 MVP nginx Konfiguration (`ops/nginx/mvp-nginx.conf`)

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 25M;
    }

    location /api/health {
        proxy_pass http://backend:8000/health;
        access_log off;
    }

    location ~ /\. {
        deny all;
    }
}
```

### 1.6 MVP .env (`/.env`)

```env
APP_ENV=production
APP_NAME=MietVerwaltung MVP
APP_URL=https://mietverwaltung-xxx.trycloudflare.com
API_URL=https://mietverwaltung-xxx.trycloudflare.com
LOG_LEVEL=INFO

# Cloudflared Tunnel
CLOUDFLARED_TUNNEL_TOKEN=your-token-here

# E-Mail (Resend Free Tier)
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_...
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_FROM=noreply@mietverwaltung.de
SMTP_FROM_NAME=MietVerwaltung

# Ollama Cloud
OLLAMA_BASE_URL=https://ollama.com/v1
OLLAMA_MODEL_STANDARD=glm5.2
OLLAMA_MODEL_COMPLEX=kimi-k2.6

# Lokale Pfade
BACKUP_DIR=/srv/mietverwaltung/backups
UPLOAD_DIR=/srv/mietverwaltung/uploads
```

### 1.7 MVP Sicherheit

Im Closed-Beta-Modus wird bewusst **minimalistisch** gehandhabt:

- SSH-Key-Login auf dem Proxmox-Host und im LXC.
- Docker-Container laufen non-root mit `cap_drop: ALL`.
- Keine öffentlichen Ports außer dem Cloudflared-Tunnel (ausgehend).
- Kein GeoIP-Blocking, kein Fail2Ban, kein Rate-Limiting — zwingend erst beim Go-Live.

> Hinweis: Sobald die Anwendung öffentlich und kommerziell wird, müssen alle Go-Live-Sicherheitsmaßnahmen (Abschnitt 4) nachgerüstet werden.

### 1.8 MVP Backup

- Tägliches `pg_dump` per Cron in `/srv/mietverwaltung/backups`.
- Uploads werden regelmäßig auf Proxmox-Host-EBene gesnapshottet.
- Keine externe Storage Box nötig.

```bash
#!/bin/bash
# ops/scripts/mvp-backup.sh
timestamp=$(date +%Y-%m-%d_%H-%M-%S)
pg_dump -h mietverwaltung-db -U mietuser -Fc mietverwaltung > /app/backups/db_${timestamp}.dump
find /app/backups -name 'db_*.dump' -mtime +7 -delete
```

---

## 2. Go-Live / Kommerzielle Phase — Hetzner

### 2.1 Auslöser

Go-Live ist erreicht, sobald:
- echte, zahlende Kunden bedient werden,
- die Anwendung öffentlich erreichbar ist,
- personenbezogene Daten im geschäftsmäßigen Kontext verarbeitet werden.

### 2.2 Phase 1 — Go-Live (2 Server)

| Server | Typ | Kosten/Monat | Rolle |
|--------|-----|---------------|-------|
| Frontend-Server | CX22 | ~4,50 € | nginx + Vue.js, SSL, öffentlich |
| Backend-Server | CX32 | ~15,09 € | FastAPI + PostgreSQL + Redis, nur private IP |
| Storage Box | 100 GB | ~4,15 € | Verschlüsselte Backups |
| Domain | — | ~5,00 € | Eigene Domain |
| **Fixkosten gesamt** | | **~28,74 €** | |

### 2.3 Phase 2 — Wachstum (3 Server)

- Frontend CX22
- Backend-App CX32
- Dedizierter DB-Server CX32 (oder CX42)

### 2.4 Phase 3 — Scale

- CDN + Load Balancer
- Mehrere App-Server
- Hetzner Managed PostgreSQL

### 2.5 Go-Live Docker Compose

- `docker-compose.frontend-hetzner.yml`
- `docker-compose.backend.yml`

Siehe Dateien im Repository-Root. Die Konfiguration entspricht der vorherigen Version dieses Konzepts mit Hetzner Private Network.

---

## 3. Migration MVP → Go-Live

1. **Daten exportieren**
   - PostgreSQL-Dump aus MVP.
   - Uploads kopieren.
2. **Hetzner aufbauen**
   - CX22 + CX32, Private Network, Firewalls.
3. **Domain + DNS einrichten**
   - Cloudflare kann weiterhin genutzt werden (dann ohne Tunnel).
4. **Compose-Dateien wechseln**
   - Von `docker-compose.yml` (MVP) auf `docker-compose.frontend-hetzner.yml` + `docker-compose.backend.yml`.
5. **Sicherheit nachrüsten**
   - GeoIP, Fail2Ban, Rate-Limiting, Sentry, UptimeRobot, Loki.
6. **DSGVO-Dokumente erstellen**
   - VVT, AVV, Datenschutzerklärung, Einwilligung, AGB, Impressum.

---

## 4. Go-Live Sicherheit

### 4.1 Netzwerk

- Frontend-Server: nur :443/:80 öffentlich.
- Backend-Server: nur Frontend-Server auf Port 8000 erlaubt.
- Hetzner Cloud Network `10.0.0.0/16`.

### 4.2 SSH / Firewall

- SSH nur Key-Auth, Admin-IP.
- UFW + Hetzner Cloud Firewall.
- Fail2Ban.

### 4.3 GeoIP-Blocking

- Nur DACH-IPs (DE/AT/CH) erlaubt.

### 4.4 Docker-Sicherheit

```yaml
user: "1000:1000"
read_only: true
cap_drop:
  - ALL
security_opt:
  - no-new-privileges:true
```

### 4.5 Application Security

- Argon2id, JWT 15 Min + Refresh 7 Tage, 2FA-Pflicht.
- Server-seitige Rollenprüfung, Rate-Limiting.
- AES-256-GCM-Feldverschlüsselung, Audit-Log.

---

## 5. Datenbank (Go-Live)

### 5.1 PostgreSQL 17

- Identische Version wie im MVP.
- `scram-sha-256`, RLS, `pgcrypto`.

### 5.2 Backup-Strategie mit PITR (WAL-G)

| Ebene | Werkzeug | Frequenz | Retention |
|-------|----------|----------|-----------|
| WAL-Archivierung | WAL-G `wal-push` | Kontinuierlich | Bis zum ältesten Full-Backup |
| Delta-Backup | WAL-G `backup-push` | Täglich | 7 Tage |
| Full-Backup | WAL-G `backup-push --full` | Wöchentlich | 4 Wochen |
| Logisches Backup | `pg_dump` | Monatlich | 12 Monate |

**Remote-Speicher:** Hetzner Storage Box per SSH.

### 5.3 PITR Restore

```bash
docker compose stop db
docker compose run --rm -u postgres db \
  sh -c 'rm -rf "${PGDATA:?}"/* && wal-g backup-fetch "${PGDATA}" LATEST'

docker compose run --rm -u postgres db \
  sh -c 'cat > "${PGDATA}/recovery.signal" <>EOF
restore_command = '\''wal-g wal-fetch %f %p'\''
recovery_target_time = '\''2026-11-02 14:00:00+01'\''
recovery_target_action = promote
EOF'

docker compose up -d db
```

---

## 6. E-Mail

### 6.1 MVP: Resend Free Tier

- 3.000 E-Mails/Monat kostenlos.
- Einfache API.
- Ausreichend für 10 Tester.

### 6.2 Go-Live: Amazon SES / Brevo

| Anbieter | EU-Hosting | Preis | Empfehlung |
|----------|------------|-------|------------|
| Amazon SES | ✅ eu-central-1 | $0,10/1.000 | Skalierbar |
| Brevo | ✅ EU | 9.000/Monat Free | DSGVO-freundlich |
| Resend | EU-Sending, Storage US | 3.000 Free, $20/50k | MVP |

---

## 7. Datei-Storage

### 7.1 Verzeichnisstruktur

```
/srv/mietverwaltung/uploads/
├── objekte/{objekt_id}/
├── einheiten/{einheit_id}/
├── mieter/{mieter_id}/
├── belege/{objekt_id}/
└── dokumente_generiert/{dokument_id}.pdf
```

### 7.2 Storage-Limits (Go-Live)

| Plan | Inklusiv-Storage |
|------|------------------|
| Free | 500 MB |
| Basis | 2 GB |
| Pro | 10 GB |
| Business | 50 GB |

---

## 8. Secret Management

### 8.1 MVP

- Einfache Docker Secrets aus lokalen Textdateien.
- `.env` ohne echte Secrets (nur Nicht-Sensitive).

### 8.2 Go-Live

- **SOPS + age** für verschlüsselte Secret-Speicherung.
- **Docker Secrets** zur Laufzeit.

---

## 9. Monitoring

| Phase | Tool |
|-------|------|
| **MVP** | Docker-Logs, gelegentlicher `curl /api/health` |
| **Go-Live** | UptimeRobot, Sentry EU, Prometheus/Grafana, Loki + Grafana Alloy |

---

## 10. Dev- und Staging-Umgebung

### 10.1 Dev

- PostgreSQL 17 in Docker (gleiche Version wie Prod/MVP).
- Redis in Docker.
- MailHog als SMTP-Catcher.
- Hot-Reload für FastAPI + Vue.js.

> `docker-compose.dev.yml`

### 10.2 Staging (ab Go-Live)

- Eigener Docker-Stack auf Backend-Server.
- Eigene DB, eigener Port (8001).
- Subdomain `staging.app.mietverwaltung.de`.

> `docker-compose.staging.yml`

---

## 11. Kostenübersicht

| Phase | Hosting | E-Mail | Backup | Domain | Monitoring | **Gesamt/Monat** |
|-------|---------|--------|--------|--------|------------|------------------|
| **MVP Closed Beta** | 0 € | 0 € (Resend Free) | 0 € (lokal) | 0 € | 0 € | **0 €** |
| **Go-Live Phase 1** | ~19 € (CX22+CX32) | ~1 € | ~4 € | ~5 € | ~0–26 € | **~30–35 €** |
| **Go-Live Phase 2** | ~30 € | ~2 € | ~4 € | ~5 € | ~26 € | **~65–70 €** |
| **Scale** | ~50 €+ | ~5 € | ~5 € | ~5 € | ~50 € | **~100 €+** |

### Break-even Go-Live

| Plan | Preis | Marge (nach ~0,30 € Kosten) | Break-even |
|------|-------|----------------------------|-------------|
| Basis | 14,90 € | ~14,60 € | 2 Vermieter |
| Pro | 29,90 € | ~29,60 € | 1 Vermieter |
| Business | 49,90 € | ~49,60 € | 1 Vermieter |

---

## 12. Go-Live Checkliste

- [ ] Kommerzielle Entscheidung getroffen.
- [ ] DSGVO-Dokumente erstellt (VVT, AVV, Datenschutzerklärung, Einwilligung, AGB, Impressum).
- [ ] Hetzner-Server in DE bestellt, Private Network konfiguriert.
- [ ] Domain + DNS eingerichtet.
- [ ] SSL-Zertifikat (Let's Encrypt / Cloudflare) vorhanden.
- [ ] Frontend/Backend getrennt deployt.
- [ ] Backend-Firewall: nur Frontend auf :8000 erlaubt.
- [ ] Secrets mit SOPS+age verschlüsselt.
- [ ] WAL-G-Backup + Restore getestet.
- [ ] Amazon SES/Brevo Domain verifiziert.
- [ ] UptimeRobot + Sentry + Loki aktiv.
- [ ] GeoIP-Blocking, Rate-Limiting, Fail2Ban aktiviert.
- [ ] Audit-Log und 2FA im Backend aktiv.

---

## 13. Dateien im Repository

```
/root/mietverwaltung/
├── Server-Konzept-v2.md
├── docker-compose.yml                 # MVP Closed Beta (ein LXC)
├── docker-compose.dev.yml
├── docker-compose.frontend-hetzner.yml  # Go-Live Frontend
├── docker-compose.backend.yml         # Go-Live Backend
├── docker-compose.staging.yml
├── .env.example                       # MVP
├── .env.development.example
├── email-templates/
├── ops/
│   ├── nginx/
│   │   ├── mvp-nginx.conf
│   │   ├── frontend-server-hetzner.conf
│   │   └── frontend-server-proxmox.conf
│   ├── scripts/
│   │   ├── mvp-backup.sh
│   │   ├── backup.sh
│   │   ├── restore.sh
│   │   └── init-secrets.sh
│   └── secrets/        # Platzhalter, SOPS-verschlüsselt im Go-Live
```

---

## 14. Build-Plan-Hinweis

- **Phase 0–5:** MVP auf Proxmox entwickeln und mit 10 Testern validieren.
- **Phase 6+:** Entscheidung Go-Live → Migration auf Hetzner, DSGVO-Konformität, Trennung Frontend/Backend.

---

## 15. Referenzen

- `Abo-Modell.md`
- `KI-Konzept.md`
- `.hermes/plans/2026-10-28_db-schema-v3.md`
- `ops/DEPLOYMENT.md`
