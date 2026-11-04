# Contributing — MietVerwaltung SaaS

## Commits

Wir nutzen **Conventional Commits**:

```
feat(scope): description      # Neues Feature
fix(scope): description       # Bugfix
refactor(scope): description  # Refactoring ohne Funktionsänderung
docs(scope): description      # Dokumentation
test(scope): description      # Tests
chore(scope): description     # Build, Dependencies, Config
ci(scope): description        # CI/CD
perf(scope): description      # Performance
```

**Scopes:** `backend`, `frontend`, `db`, `ai`, `deploy`, `docs`, `shared`

## Branching

- **Trunk-Based Development** — kurze Feature-Branches, häufig merge in `main`
- Branch-Name: `<type>/<short-description>` (z.B. `feat/mieter-crud`)
- Kein direkter Push auf `main` — PR mit mindestens 1 Review erforderlich
- CI muss grün sein vor Merge

## Code-Qualität

- **Backend:** ruff (lint), mypy (types), pytest (tests), bandit (security)
- **Frontend:** eslint, vitest
- Kein Code ohne Tests in `main`
- API-Schemas (Pydantic) sind Single Source of Truth — TypeScript-Typen werden generiert

## Sicherheit

- **Niemals Secrets, Passwörter, API-Keys im Code committen**
- `.env`-Dateien sind gitignored
- GitHub Secrets für CI/CD
- DSGVO-konforme Verarbeitung bei allen Personendaten
- KI-Anfragen werden vor Versand anonymisiert (Presidio)

## KI-Builder (Hermes Agent)

- Generierter Code muss denselben Qualitätsstandards entsprechen
- Jeder KI-generierte PR muss von einem Menschen reviewt werden
- KI darf keine Secrets generieren oder hardcodieren
