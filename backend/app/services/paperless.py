"""Paperless-ngx API-Client für das Dokumentenmanagement.

Der Client kommuniziert mit einer internen Paperless-ngx-Instanz.
Pro Vermieter wird ein eigener Paperless-Benutzer angelegt, damit Dokumente
logisch getrennt sind. Wenn Paperless deaktiviert ist (`PAPERLESS_ENABLED=false`),
werden alle Aufrufe zu No-Ops, und der lokale Speicher-Service übernimmt.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PaperlessConfigError(Exception):
    """Paperless ist nicht korrekt konfiguriert."""


class PaperlessAPIError(Exception):
    """Paperless API hat einen Fehler zurückgegeben."""


@dataclass
class PaperlessUser:
    id: int
    username: str
    token: str


class PaperlessClient:
    """Low-Level HTTP-Client für Paperless-ngx.

    Für Admin-Aktionen (User anlegen) wird `PAPERLESS_ADMIN_TOKEN` verwendet.
    Für Dokumenten-Uploads wird der pro-Vermieter-User-Token verwendet.
    """

    def __init__(self, base_url: str | None = None, admin_token: str | None = None, timeout: float = 30.0) -> None:
        self.base_url = (base_url or settings.PAPERLESS_URL).rstrip("/")
        self.admin_token = admin_token or settings.PAPERLESS_ADMIN_TOKEN
        self.timeout = timeout
        if settings.PAPERLESS_ENABLED and not self.base_url:
            raise PaperlessConfigError("PAPERLESS_URL fehlt")

    def _admin_headers(self) -> dict[str, str]:
        if not self.admin_token:
            raise PaperlessConfigError("PAPERLESS_ADMIN_TOKEN fehlt")
        return {
            "Authorization": f"Token {self.admin_token}",
            "Accept": "application/json",
        }

    def _user_headers(self, user_token: str) -> dict[str, str]:
        return {
            "Authorization": f"Token {user_token}",
            "Accept": "application/json",
        }

    async def get_or_create_user(
        self,
        vermieter_id: int,
        email: str,
        first_name: str = "",
        last_name: str = "",
    ) -> PaperlessUser:
        """Holt oder erstellt einen Paperless-Benutzer für einen Vermieter."""
        username = f"vermieter_{vermieter_id}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Prüfen, ob User bereits existiert
            r = await client.get(
                f"{self.base_url}/api/users/",
                headers=self._admin_headers(),
                params={"username": username},
            )
            r.raise_for_status()
            data = r.json()
            for user in data.get("results", []):
                if user.get("username") == username:
                    token = await self._get_or_create_token(client, user["id"])
                    return PaperlessUser(id=user["id"], username=username, token=token)

            # Neu anlegen
            payload: dict[str, Any] = {
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_superuser": False,
                "is_staff": False,
            }
            r = await client.post(
                f"{self.base_url}/api/users/",
                headers=self._admin_headers(),
                json=payload,
            )
            if r.status_code == 400 and "username" in r.text:
                # Race condition: Benutzer wurde gerade erstellt
                return await self.get_or_create_user(vermieter_id, email, first_name, last_name)
            r.raise_for_status()
            user = r.json()
            token = await self._get_or_create_token(client, user["id"])
            return PaperlessUser(id=user["id"], username=username, token=token)

    async def _get_or_create_token(self, client: httpx.AsyncClient, user_id: int) -> str:
        r = await client.get(
            f"{self.base_url}/api/tokens/",
            headers=self._admin_headers(),
        )
        r.raise_for_status()
        data = r.json()
        for token_obj in data.get("results", []):
            if token_obj.get("user") == user_id:
                return str(token_obj["key"])
        r = await client.post(
            f"{self.base_url}/api/tokens/",
            headers=self._admin_headers(),
            json={"user": user_id},
        )
        r.raise_for_status()
        return str(r.json()["key"])

    async def upload_document(
        self,
        user_token: str,
        file: BytesIO,
        filename: str,
        title: str,
        correspondent_id: int | None = None,
        document_type_id: int | None = None,
        tag_ids: list[int] | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """Lädt ein Dokument in Paperless hoch."""
        files: dict[str, Any] = {
            "document": (filename, file, "application/octet-stream"),
        }
        data: dict[str, Any] = {
            "title": title,
            "correspondent": correspondent_id or "",
            "document_type": document_type_id or "",
            "tags": tag_ids or [],
        }
        if created_at:
            data["created"] = created_at

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/documents/post_document/",
                headers=self._user_headers(user_token),
                data=data,
                files=files,
            )
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error("Paperless upload failed: %s %s", r.status_code, r.text)
                raise PaperlessAPIError(f"Paperless upload fehlgeschlagen: {r.status_code} {r.text}") from exc
            return r.json()

    async def get_document(self, user_token: str, document_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/documents/{document_id}/",
                headers=self._user_headers(user_token),
            )
            r.raise_for_status()
            return r.json()

    async def download_document(self, user_token: str, document_id: int) -> bytes:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/documents/{document_id}/download/",
                headers=self._user_headers(user_token),
            )
            r.raise_for_status()
            return r.content

    async def preview_document(self, user_token: str, document_id: int) -> bytes:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/documents/{document_id}/preview/",
                headers=self._user_headers(user_token),
            )
            r.raise_for_status()
            return r.content

    async def delete_document(self, user_token: str, document_id: int) -> None:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.delete(
                f"{self.base_url}/api/documents/{document_id}/",
                headers=self._user_headers(user_token),
            )
            r.raise_for_status()

    async def search_documents(
        self,
        user_token: str,
        query: str | None = None,
        correspondent_id: int | None = None,
        tag_ids: list[int] | None = None,
        page_size: int = 50,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page_size": page_size}
        if query:
            params["query"] = query
        if correspondent_id:
            params["correspondent__id"] = correspondent_id
        if tag_ids:
            params["tags__id__in"] = ",".join(str(t) for t in tag_ids)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/documents/",
                headers=self._user_headers(user_token),
                params=params,
            )
            r.raise_for_status()
            return r.json()

    async def get_or_create_correspondent(self, admin_token_override: str | None = None, name: str = "Vermieter") -> int:
        """Erstellt einen globalen Correspondenten für Vermieter-Dokumente."""
        token = admin_token_override or self.admin_token
        if not token:
            raise PaperlessConfigError("ADMIN-Token fehlt")
        headers = {"Authorization": f"Token {token}", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/correspondents/",
                headers=headers,
                params={"name__iexact": name},
            )
            r.raise_for_status()
            data = r.json()
            for c in data.get("results", []):
                if c.get("name", "").lower() == name.lower():
                    return int(c["id"])
            r = await client.post(
                f"{self.base_url}/api/correspondents/",
                headers=headers,
                json={"name": name, "matching_algorithm": "ANY"},
            )
            r.raise_for_status()
            return int(r.json()["id"])

    async def ensure_tags(self, tag_names: list[str]) -> list[int]:
        """Stellt sicher, dass die angegebenen Tags existieren, und gibt IDs zurück."""
        if not self.admin_token:
            raise PaperlessConfigError("ADMIN-Token fehlt")
        headers = self._admin_headers()
        tag_ids: list[int] = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for name in tag_names:
                r = await client.get(
                    f"{self.base_url}/api/tags/",
                    headers=headers,
                    params={"name__iexact": name},
                )
                r.raise_for_status()
                data = r.json()
                existing = next(
                    (t for t in data.get("results", []) if t.get("name", "").lower() == name.lower()),
                    None,
                )
                if existing:
                    tag_ids.append(int(existing["id"]))
                    continue
                r = await client.post(
                    f"{self.base_url}/api/tags/",
                    headers=headers,
                    json={"name": name, "match": "", "matching_algorithm": "NONE"},
                )
                r.raise_for_status()
                tag_ids.append(int(r.json()["id"]))
        return tag_ids
