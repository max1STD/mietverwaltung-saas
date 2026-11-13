# Pre-Build Architektur-Review: Server & Infrastructure

**Projekt:** MietVerwaltung SaaS — MVP Closed Beta auf Proxmox LXC  
**Gelesene Quellen:** `/root/mietverwaltung/Server-Konzept-v2.md` (656 Zeilen), `/root/mietverwaltung/server-architecture-diagram.html`  
**Server-Realität:** Proxmox LXC, 4 GB RAM, 2 vCPU, 4,2 GB freier Disk, PostgreSQL 17 nativ vorhanden, Node 24 via fnm, Python 3.13, **kein Docker installiert**, Cloudflared 2026.11.0 nativ vorhanden.  
**Ziel:** Konzept auf native (nicht-containerisierte) Ausführung prüfen und Risiken/Gaps dokumentieren.

---

## 1. Zusammenfassung

`Server-Konzept-v2.md` und das Architektur-Diagramm sind für eine **Docker/Docker-Compose-basierte** Infrastruktur geschrieben — sowohl für den MVP Closed Beta auf Proxmox als auch für das Go-Live auf Hetzner. Auf dem vorhandenen Proxmox-LXC ist Docker jedoch nicht installiert und wird aus Ressourcen- und Wartungsgründen auch nicht empfohlen. Der MVP muss daher **vollständig auf native systemd-Services umgestellt** werden.

Der Stack (FastAPI + Vue-Dev-Server + PostgreSQL + Redis + Cloudflared) läuft grundsätzlich auf 4 GB RAM / 2 vCPU für einen Closed Beta mit wenigen Testern, hat aber keine großen Reserven. Sicherheits- und Backup-Konzept müssen an native Services angepasst werden, da Docker-spezifische Isolationsmechanismen (Namespaces, read-only Rootfs, `cap_drop`, Docker Secrets) wegfallen.

**Empfohlene Vorgehensweise:** MVP als „native systemd-Stack“ bauen, Go-Live-Konzept separat für Hetzner/Docker belassen, aber beide Varianten im Repository dokumentieren.

---

## 2. Bewertungsmatrix

| # | Thema | Schwere | Kurzbeschreibung |
|---|-------|---------|------------------|
| 1 | Docker-Abhängigkeit | **CRITICAL** | Gesamtes Server-Konzept baut auf Docker Compose auf; Docker ist nicht installiert und nicht geplant. |
| 2 | Ressourcen RAM/CPU | **WARNING** | 4 GB / 2 vCPU reichen für Dev/Closed Beta, aber bei OCR/PDF/KI-Spitzenlast knapp. |
| 3 | Reverse Proxy nginx | **INFO** | Für den MVP optional; empfohlen sobald mehr als ein Service öffentlich erreichbar sein soll. |
| 4 | Cloudflared | **INFO** | Läuft nativ als Binary (Version 2026.11.0), Docker-Container ist überflüssig. |
| 5 | Deployment ohne Docker | **CRITICAL** | Bestehende GitHub Action `deploy-beta.yml` ruft `docker compose` auf; muss auf `git pull + systemd restart` umgeschrieben werden. |
| 6 | Sicherheit nativ vs. Docker | **WARNING** | Fehlende Container-Isolation muss durch systemd-Hardening, Firewall und 127.0.0.1-Bindings kompensiert werden. |
| 7 | Disk Space | **CRITICAL** | Nur 4,2 GB frei; Python-/Node-Deps, OCR/PDF-Libraries und KI-Modelle werden den Platz knapp machen. |
| 8 | Backup-Strategie | **WARNING** | Docker-Cron-Container entfällt; Backup muss als systemd-Timer oder Cronjob realisiert werden. |

---

## 3. Detail-Analyse

### 3.1 Notwendige Konzeptänderungen für Native (kein Docker)

**Schwere:** CRITICAL

**Befund:**

`Server-Konzept-v2.md` beschreibt den MVP als „ein LXC, ein Docker-Compose-Stack“ mit fünf Services (`cloudflared`, `nginx`, `backend`, `db`, `redis`, `cron`) und Go-Live als „getrennte Docker-Compose-Dateien auf Hetzner“. Das Architektur-Diagramm visualisiert ebenfalls eine Docker-inspirierte Verteilung auf mehrere Hetzner-Server.

Auf dem Proxmox-LXC ist Docker nicht installiert (`which docker` liefert `None`) und die Ressourcen (4 GB / 2 vCPU / 4 GB Disk) sind für Docker-Overhead (Daemon, Images, Layer, Volumes) nicht großzügig bemessen.

**Empfohlene Änderungen:**

1. **Service-Orchestrierung:** `docker-compose.yml` ersetzen durch systemd-Unit-Dateien:
   - `mietverwaltung-backend.service`
   - `mietverwaltung-frontend.service` (nur Dev, später entfällt sie zugunsten von nginx + statischem Build)
   - `mietverwaltung-redis.service`
   - `cloudflared.service`
   - `mietverwaltung-backup.timer` + `.service`
2. **Secret-Management:** Docker Secrets (`/run/secrets/…`) ersetzen durch:
   - Eine `.env`-Datei mit `chmod 600` im Service-Root, **oder**
   - `sops` + `age` für verschlüsselte Secrets im Repository, entschlüsselt bei Deploy.
3. **Netzwerk:** Docker-internes Netzwerk (`mvp-net`, DNS-Namen `backend`, `db`, `redis`) ersetzen durch `127.0.0.1`-Bindings auf unterschiedlichen Ports:
   - FastAPI: `0.0.0.0:8000` (hinter nginx) bzw. `127.0.0.1:8000` (nur lokal)
   - Redis: `127.0.0.1:6379`
   - PostgreSQL: `127.0.0.1:5432` (bereits nativ vorhanden)
   - Vite Dev-Server: `127.0.0.1:5173`
4. **Storage:** Docker-Volumes (`/srv/mietverwaltung/…`) bleiben als normale Host-Verzeichnisse; nur Berechtigungen müssen gepflegt werden.
5. **Healthchecks:** `docker compose` Healthchecks ersetzen durch systemd `ExecStartPost`-Health-Skripte oder einfache `curl`-Prüfungen im Deploy-Skript.
6. **Cron-Backup:** `cron`-Service aus Docker Compose ersetzen durch systemd-Timer oder einen Cronjob, der direkt `pg_dump` aufruft.
7. **Doku:** Im Repository eine neue Datei `deploy/native-mvp.md` anlegen, die die systemd-Units, Installationsschritte und das native Deployment beschreibt.

---

### 3.2 Ressourcen-Schätzung: 4 GB RAM / 2 vCPU

**Schwere:** WARNING

**Befund:**

Aktuell stehen 4 GB RAM zur Verfügung, davon ca. 2,7 GB frei (laut `/proc/meminfo`). Der geplante Stack belegt im Ruhezustand schätzungsweise 1,5–2,2 GB RAM:

| Komponente | Ruhe-RAM | Spitzenlast | Bemerkung |
|------------|----------|-------------|-----------|
| PostgreSQL 17 | 250–512 MB | 1 GB+ | Abhängig von `shared_buffers`, aktueller DB-Größe und gleichzeitigen Connections |
| Redis 7 | 64–128 MB | 256 MB | Empfohlen: `maxmemory 256mb`, `allkeys-lru` |
| FastAPI (uvicorn) | 150–300 MB | 600 MB–1,2 GB | OCR/PDF/WeasyPrint/Presidio laden viele Bibliotheken; pro Worker 1 GB realistisch |
| Vite Dev-Server | 200–400 MB | 600 MB | Nur für Dev/Review nötig, später entfällt er |
| Cloudflared | 50–100 MB | 150 MB | Quick-Tunnel oder Named Tunnel |
| nginx | 20–50 MB | 100 MB | Optional für MVP |
| OS + Prozesse | 500–800 MB | — | Grundlast des LXC |
| **Gesamt Ruhe** | **~1,4–2,3 GB** | | |
| **Gesamt Peak (1 User, OCR/PDF)** | **2,5–3,5 GB** | | |

**CPU:** 2 vCPU reichen für sequenzielle Requests und einzelne OCR/PDF-Jobs. Sobald mehrere gleichzeitige Anfragen oder schwere KI-/OCR-Jobs laufen, wird die CPU zum Engpass. Tesseract, WeasyPrint und spaCy/Presidio sind CPU-intensiv und teilweise single-threaded.

**Empfohlene Maßnahmen:**

- PostgreSQL `shared_buffers` auf **256 MB** begrenzen (statt 1 GB), `effective_cache_size` auf 1–1,5 GB.
- Redis mit `--maxmemory 256mb --maxmemory-policy allkeys-lru` starten.
- FastAPI mit **1 Worker** (`--workers 1`) betreiben; für Closed Beta ausreichend, später hochskalieren.
- Vite Dev-Server nur bei Bedarf starten (User-Review), ansonsten statischen Build über nginx servieren.
- Schwere OCR/PDF-Jobs asynchron in einen Hintergrundprozess auslagern (z. B. Celery/ARQ oder eigener systemd-Service), damit der API-Worker nicht blockiert.
- Swap abschalten oder auf 1–2 GB begrenzen; bei 4 GB RAM verlangsamt unbegrenzter Swap die App spürbar.
- Monitoring mit `vmstat`, `htop`, Prometheus-Node-Exporter-Light oder einfach `systemctl status` einrichten.

---

### 3.3 Ist nginx im Native-Setup noch nötig?

**Schwere:** INFO

**Befund:**

Im Docker-Konzept leitet nginx den Traffic an `backend:8000` und liefert statische Frontend-Dateien aus. Im aktuellen LXC ist nginx **nicht installiert** (`which nginx` liefert keine Ausgabe). Für einen reinen Dev/Closed-Beta-Betrieb ist nginx **technisch nicht zwingend**:

- Cloudflared kann direkt auf FastAPI (`http://127.0.0.1:8000`) oder den Vite Dev-Server (`http://127.0.0.1:5173`) zeigen.
- Der Vite Dev-Server ist selbst ein HTTP-Server mit HMR (Hot Module Replacement).

**Empfehlung:**

- **Für kurze Demos/Tests:** Cloudflared Quick Tunnel direkt auf Vite (`5173`) oder FastAPI (`8000`) routen. Einfach, aber nicht produktionsnah.
- **Für den eigentlichen Closed Beta:** nginx **doch installieren** und folgende Aufgaben übernehmen lassen:
  - Statisches Frontend-Build (`frontend/dist`) ausliefern
  - `/api/` an FastAPI weiterleiten
  - HTTPS-Terminierung über Cloudflared (der Tunnel endet bei nginx)
  - `client_max_body_size` für Uploads (z. B. 25 MB)
  - Gzip, Caching-Header, Sicherheits-Header (HSTS, X-Frame-Options)
  - Einfaches Rate-Limiting (`limit_req_zone`)
- Die vorhandene `deploy/nginx/nginx.conf` referenziert Docker-Hostnamen (`backend:8000`, `frontend:80`). Sie muss für Native auf `127.0.0.1:8000` bzw. den statischen Build-Pfad angepasst werden.

---

### 3.4 Cloudflared Tunnel ohne Docker

**Schwere:** INFO

**Befund:**

Cloudflared ist bereits als natives Binary vorhanden:

```text
/usr/local/bin/cloudflared
cloudflared version 2026.11.0 (built 2026-11-12-12:17 UTC)
```

Es funktioniert ohne Docker. Der MVP-Stack kann Cloudflared entweder als:

1. **Quick Tunnel** (`cloudflared tunnel --url http://localhost:PORT`) für temporäre Demos, oder
2. **Named Tunnel** mit einem persistenten Token (`cloudflared tunnel run --token $TOKEN`) für den dauerhaften Closed Beta.

**Empfohlene Maßnahmen:**

- Für den Closed Beta einen Named Tunnel einrichten und als systemd-Service (`cloudflared.service`) laufen lassen.
- Keinen Docker-Container für Cloudflared verwenden.
- Die `.env`-Variable `CLOUDFLARED_TUNNEL_TOKEN` bleibt gültig; nur der Startmechanismus ändert sich.
- `trycloudflare.com`-Quick-Tunnel-URLs sind temporär und ändern sich bei jedem Neustart — nicht für den dauerhaften Beta-Betrieb verwenden.

---

### 3.5 Deployment ohne Docker (GitHub Actions → systemd)

**Schwere:** CRITICAL

**Befund:**

Die bestehende Datei `.github/workflows/deploy-beta.yml` ist für Docker geschrieben:

```yaml
cd /opt/mietverwaltung
git pull origin main
docker compose build
docker compose up -d
docker compose exec backend alembic upgrade head
curl -sf http://localhost:8000/health || exit 1
```

Drei Probleme:

1. Docker-Befehle funktionieren auf dem LXC nicht.
2. Der Pfad `/opt/mietverwaltung` existiert nicht; das Repository liegt unter `/root/mietverwaltung-saas`.
3. Es fehlen Schritte für native Python-Abhängigkeiten, Node-Build und systemd-Restart.

**Empfohlene neue Deploy-Pipeline:**

```yaml
# .github/workflows/deploy-beta.yml (native)
script: |
  set -euo pipefail
  cd /root/mietverwaltung-saas

  # Backup vor Deploy
  /root/mietverwaltung-saas/deploy/scripts/backup-db.sh

  # Source aktualisieren
  git fetch origin
  git checkout main
  git pull origin main

  # Backend-Abhängigkeiten in Venv
  source /root/mietverwaltung-saas/backend/.venv/bin/activate
  pip install -r backend/requirements.txt

  # Datenbank-Migrationen
  alembic -c backend/alembic.ini upgrade head

  # Frontend bauen
  cd /root/mietverwaltung-saas/frontend
  fnm use 24
  npm ci
  npm run build

  # Services neu starten
  sudo systemctl restart mietverwaltung-backend
  sudo systemctl restart mietverwaltung-nginx

  # Health-Check
  sleep 3
  curl -sf http://127.0.0.1:8000/api/health || exit 1
```

**Wichtige ergänzende Maßnahmen:**

- Ein dediziertes Deploy-User erstellen (nicht root), das nur die nötigen `systemctl`/`git`-Rechte hat.
- Python-Virtual-Environment (`/root/mietverwaltung-saas/backend/.venv`) zwingend verwenden, um System-Python nicht zu verändern.
- Node-Version vor Build setzen: `fnm use 24` (gemäß User-Angabe).
- Pre-Deploy-DB-Backup (`pg_dump`) als Rollback-Grundlage.
- Blue/Green-Rollout ist auf einem Single-Server nicht trivial; stattdessen:
  - git-Tag-basiertes Rollback (`git checkout <previous-tag>` + Restart)
  - DB-Migrationen immer backward-kompatibel halten, damit ein Code-Rollback funktioniert
- GitHub Environment `beta` mit Approval-Schritt beibehalten.
- SSH-Key als GitHub Secret hinterlegen; `PROXMOX_HOST`, `PROXMOX_USER`, `PROXMOX_SSH_KEY` passen, aber Pfad und Befehle müssen geändert werden.

---

### 3.6 Sicherheit: Native vs. Docker

**Schwere:** WARNING

**Befund:**

Docker bietet standardmäßig:

- Prozess-/Netzwerk-Isolation pro Container
- `read_only: true`, `cap_drop: ALL`, `no-new-privileges`
- Docker Secrets im RAM (`/run/secrets`)
- Keine Notwendigkeit, Services an öffentliche Ports zu binden (nur exposed Ports erreichbar)

Bei nativem Betrieb entfällt diese Isolation. Services, die an `0.0.0.0` binden, sind potenziell von außen erreichbar, falls die Firewall/Cloudflared-Konfiguration fehlerhaft ist.

**Empfohlene Maßnahmen:**

| Docker-Feature | Native-Äquivalent |
|----------------|-----------------|
| Non-root-User (`user: 1000:1000`) | systemd `User=mietverwaltung`, `Group=mietverwaltung` |
| `read_only: true` | systemd `ProtectSystem=strict`, `ProtectHome=true` |
| `cap_drop: ALL` | systemd `CapabilityBoundingSet=`, `NoNewPrivileges=true` |
| Private tmpfs | systemd `PrivateTmp=true` |
| Docker Secrets | SOPS + age, oder `.env` mit `chmod 600` |
| Internes Netzwerk | Services an `127.0.0.1` binden; PostgreSQL `listen_addresses = 'localhost'` |
| Keine öffentlichen DB/Redis-Ports | UFW/iptables: nur 443/80/Tunnel erlauben; DB/Redis blockiert |

**Weitere Sicherheitsgaps im aktuellen Konzept:**

- **GeoIP / Rate-Limiting / Fail2Ban:** Im MVP-Konzept bewusst deaktiviert. Für einen Closed Beta mit bekannten Testern akzeptabel, aber muss vor Go-Live nachgerüstet werden.
- **PostgreSQL:** Bereits nativ installiert; prüfen, dass `listen_addresses` nicht auf `*` steht und kein externer Zugriff möglich ist.
- **Redis:** Noch nicht installiert. Bei Installation unbedingt `requirepass` setzen und an `127.0.0.1` binden.
- **Secret-Rotation:** Ohne Docker ist ein Re-Deploy bei Secret-Änderung notwendig; planen.
- **File-Uploads:** Upload-Verzeichnis `/srv/mietverwaltung/uploads` muss außerhalb des App-Code-Pfads liegen und unter eigenem Linux-User laufen.

**Empfehlung:** Eine `deploy/systemd-hardening.md` anlegen mit Vorlagen für alle systemd-Units und UFW-Regeln.

---

### 3.7 Disk Space: 4 GB frei — ausreichend für Dev?

**Schwere:** CRITICAL

**Befund:**

Aktuell sind nur 4,2 GB auf `/` frei (40 GB Gesamt, 89 % belegt). Große Verbraucher, die bereits auf dem System liegen:

| Pfad | Größe | Inhalt |
|------|-------|--------|
| `/root/.cache` | **4,0 GB** | camoufox (1,4 GB), uv (1,1 GB), ms-playwright (990 MB), pnpm (165 MB), huggingface (142 MB), electron (112 MB), node-gyp (65 MB), pip (18 MB), etc. |
| `/var/cache/apt/archives` | 620 MB | Heruntergeladene Debian-Pakete |
| `/root/.npm` | 284 MB | npm-Cache |
| `/var/lib/postgresql` | 95 MB | Bereits vorhandene Postgres-Daten |
| `/root/mietverwaltung/repos` | 135 MB | Klonierte Vergleichs-Repos |

Zusätzlich werden für den MVP-Stack anfallen:

| Posten | Geschätzter Platzbedarf |
|--------|--------------------------|
| Python-Virtual-Env (`backend/.venv`) | 500 MB–1,2 GB |
| spaCy-Modell `de_core_news_lg` | 500 MB–1 GB |
| Node-Modules (`frontend/node_modules`) | 300 MB–800 MB |
| System-Pakete (`tesseract-ocr`, `libweasyprint`, `build-essential`) | 200 MB–500 MB |
| Uploads / generierte PDFs / Logs | schnell wachsend |
| DB-Backups (`pg_dump`) | mindestens so groß wie die DB |

**Empfohlene Maßnahmen:**

1. **Cache-Bereinigung sofort:**
   ```bash
   apt-get clean
   pip cache purge
   npm cache clean --force
   rm -rf /var/cache/apt/archives/*
   ```
   Nicht benötigte Caches (`camoufox`, `ms-playwright`, `electron`, `huggingface`, `uv`) nur löschen, wenn sie für andere Projekte nicht mehr benötigt werden. Zuerst prüfen, welche Prozesse sie nutzen.
2. **`/root/mietverwaltung/repos`** auf Proxmox-Host verschieben oder nach Recherchephase löschen.
3. **Logrotate** sofort konfigurieren, damit Backend-/nginx-/PostgreSQL-Logs nicht unbegrenzt wachsen.
4. **Upload-Limit** pro Datei z. B. 10–25 MB setzen und alte generierte PDFs aufräumen.
5. **Backup-Rotation:** Maximal 3–7 lokale Backups behalten, ältere auf externen Speicher verschieben oder löschen.
6. **LXC-Disk erweitern:** Bei Proxmox ist das Root-Volume auf 40 GB begrenzt. Für produktiven Betrieb und längere Tests sollte es auf **mindestens 60–80 GB** vergrößert werden.

**Fazit:** 4 GB reichen für den ersten Dev-Start, aber nicht für eine Woche aktiven Betriebs mit Dependencies, Uploads und Backups.

---

### 3.8 Backup-Strategie ohne Docker

**Schwere:** WARNING

**Befund:**

`Server-Konzept-v2.md` sieht für den MVP ein Backup über einen `cron`-Docker-Container vor (`ops/scripts/mvp-backup.sh`), der täglich `pg_dump` ausführt. Ohne Docker muss dieses Cron-Job nativ laufen.

Für das Go-Live ist WAL-G mit PITR geplant — das ist natürlich auch ohne Docker möglich, aber aufwendiger zu konfigurieren (Binary installieren, PostgreSQL-Config `archive_command`, SSH-Schlüssel zur Storage Box).

**Empfohlene Backup-Lösung für den Native-MVP:**

1. **Tägliches logisches Backup** mit `pg_dump`:
   ```bash
   #!/bin/bash
   # /root/mietverwaltung-saas/deploy/scripts/backup-db.sh
   set -euo pipefail
   TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
   BACKUP_DIR="/srv/mietverwaltung/backups"
   mkdir -p "$BACKUP_DIR"
   pg_dump -Fc -U mietuser mietverwaltung > "$BACKUP_DIR/db_${TIMESTAMP}.dump"
   find "$BACKUP_DIR" -name 'db_*.dump' -mtime +7 -delete
   ```
2. **Upload-Backup**:
   - Täglich `rsync -a /srv/mietverwaltung/uploads/ /srv/mietverwaltung/backups/uploads/` oder auf Proxmox-Host ziehen.
3. **Automatisierung**:
   - systemd-Timer: `mietverwaltung-backup.timer` + `mietverwaltung-backup.service`, oder
   - Ein Eintrag in `/etc/cron.d/mietverwaltung`.
4. **Pre-Deploy-Backup:** Jeder Deploy muss **vor** Migration und Restart ein Backup anlegen (siehe 3.5).
5. **Restore-Test:** Einmal pro Woche ein Backup in eine leere Test-DB einspielen (`pg_restore`) und prüfen, ob die App damit startet.
6. **Go-Live-Vorbereitung:** WAL-G nativ installieren und PITR-Restore testen, bevor Hetzner-Infrastruktur produktiv wird.

---

## 4. Weitere Gaps gegenüber dem Konzept

| # | Befund | Schwere | Empfohlene Lösung |
|---|--------|---------|-------------------|
| A | `deploy/nginx/nginx.conf` nutzt Docker-Hostnamen (`backend:8000`, `frontend:80`) | WARNING | Auf `127.0.0.1:8000` und statisches `frontend/dist` umstellen. |
| B | `spacy de_core_news_lg` ist nicht in `requirements.txt`; Presidio braucht es für die DSGVO-Anonymisierung | WARNING | Download-Schritt in Deploy/Setup-Skript einbauen; zusätzlich 500 MB–1 GB Platz. |
| C | WeasyPrint/Tesseract benötigen System-Pakete (`libpango`, `tesseract-ocr-deu`, `libffi` etc.) | WARNING | `deploy/scripts/install-system-deps.sh` anlegen. |
| D | `Server-Konzept-v2.md` zeigt noch alte feste Pläne in der Break-even-Tabelle (Basis 14,90 €, Pro 29,90 €) | INFO | Tabelle auf WE-basiertes Pricing aktualisieren, da `Abo-Modell-v3.md` bereits WE-basiert ist. |
| E | Architektur-Diagramm zeigt Postfix als Mail-Server; Konzept v2 hat ihn für Go-Live durch Resend/Amazon SES ersetzt | INFO | Diagramm für MVP/Go-Live aktualisieren oder Hinweis ergänzen, dass Postfix nicht verwendet wird. |
| F | Keine zentrale Log-Rotation / Log-Management definiert | WARNING | `logrotate`-Konfiguration für `/var/log/mietverwaltung/*.log` anlegen. |

---

## 5. Empfohlene nächste Schritte (priorisiert)

1. **CRITICAL:** Entscheidung festhalten: MVP läuft nativ (systemd). Docker-Compose-Dateien im Repository als „Go-Live-Referenz“ markieren, aber nicht für Proxmox verwenden.
2. **CRITICAL:** Disk bereinigen: `apt-get clean`, Caches prüfen/löschen, LXC-Disk bei Proxmox auf 60–80 GB erweitern.
3. **CRITICAL:** `.github/workflows/deploy-beta.yml` auf native systemd-Deploy-Pipeline umschreiben.
4. **WARNING:** Native systemd-Units für Backend, Redis, nginx, Cloudflared und Backup-Timer erstellen + Hardening-Optionen setzen.
5. **WARNING:** `deploy/nginx/nginx.conf` auf `127.0.0.1:8000` und statisches `frontend/dist` anpassen.
6. **WARNING:** Systemabhängigkeiten für OCR/PDF installieren und in Setup-Skript dokumentieren.
7. **INFO:** `Server-Konzept-v2.md` und Architektur-Diagramm um einen neuen Abschnitt „Native MVP-Variante (Proxmox ohne Docker)“ ergänzen.
8. **INFO:** `README.md` und `ARCHITECTURE.md` im Repository aktualisieren, damit der native Stack nachvollziehbar ist.

---

## 6. Fazit

Der MVP ist auf dem vorhandenen Proxmox-LXC **ohne Docker betreibbar**, erfordert aber eine grundlegende Überarbeitung des Server-Konzepts und der Deploy-Pipeline. Die größten Risiken sind der **fehlende native Deployment-Plan**, die **knappe Disk-Größe** und die **fehlende Container-Isolation**, die durch systemd-Hardening und Firewall-Regeln kompensiert werden muss. RAM und CPU sind für einen Closed Beta mit wenigen Testern ausreichend, solange schwere OCR/PDF-Prozesse nicht parallel laufen. Backup und Cron müssen von Docker-Container auf systemd-Timer/Cronjob umgebaut werden.

Sobald Go-Live ansteht, sollte die Docker-basierte Hetzner-Architektur aus `Server-Konzept-v2.md` wieder aufgegriffen werden — dort passt Docker zu Ressourcen und Sicherheitsanforderungen.
