from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import httpx

from ..config import LICENSE_SERVER_URL, LICENSE_STATE_PATH
from .machine import machine_id

FREE_BOOK_LIMIT = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_state() -> dict[str, Any]:
    if not LICENSE_STATE_PATH.exists():
        return {"machine_id": machine_id(), "books_created": 0, "licensed": False}
    try:
        state = json.loads(LICENSE_STATE_PATH.read_text(encoding="utf-8"))
        state["machine_id"] = machine_id()
        return state
    except Exception:
        return {"machine_id": machine_id(), "books_created": 0, "licensed": False}


def _write_state(state: dict[str, Any]) -> None:
    LICENSE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LICENSE_STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def status() -> dict[str, Any]:
    state = _read_state()
    current_machine = machine_id()
    return {
        "licensed": bool(state.get("licensed")),
        "books_created": int(state.get("books_created", 0)),
        "free_books_remaining": (
            0 if state.get("licensed")
            else max(0, FREE_BOOK_LIMIT - int(state.get("books_created", 0)))
        ),
        "license_server_configured": bool(LICENSE_SERVER_URL),
        "machine_id": current_machine,
    }


def assert_can_create_book(project_id: str | None = None) -> None:
    state = _read_state()

    if state.get("licensed"):
        return

    if int(state.get("books_created", 0)) >= FREE_BOOK_LIMIT:
        raise PermissionError(
            "O período gratuito de 1 livro já foi utilizado. "
            "Ative a licença vitalícia para continuar."
        )

    # Production mode: the official server is authoritative for the one-book trial.
    # Local/offline development remains usable when no server URL is configured.
    if LICENSE_SERVER_URL and project_id:
        try:
            response = httpx.post(
                f"{LICENSE_SERVER_URL}/v1/trial/consume",
                json={"machine_id": machine_id(), "project_id": project_id},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("allowed"):
                raise PermissionError(
                    data.get(
                        "reason",
                        "O período gratuito já foi utilizado. Ative a licença vitalícia para continuar.",
                    )
                )
        except PermissionError:
            raise
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Não foi possível validar o período gratuito no servidor oficial."
            ) from exc


def register_book_created() -> None:
    state = _read_state()
    state["machine_id"] = machine_id()
    state["books_created"] = int(state.get("books_created", 0)) + 1
    state["last_book_created_at"] = _now()
    _write_state(state)


def activate_with_license(license_token: str) -> dict[str, Any]:
    if not LICENSE_SERVER_URL:
        raise RuntimeError("Servidor de licenças não configurado.")

    response = httpx.post(
        f"{LICENSE_SERVER_URL}/v1/license/activate",
        json={"machine_id": machine_id(), "license_token": license_token},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("valid"):
        raise ValueError(data.get("message", "Licença inválida."))

    state = _read_state()
    state.update({"machine_id": machine_id(), "licensed": True, "license": data})
    _write_state(state)
    return data


def verify_payment_and_issue_license(
    tx_id: str, asset: str, machine: str | None = None
) -> dict[str, Any]:
    """Ask the official server to verify a BSC payment and issue a signed license."""
    if not LICENSE_SERVER_URL:
        raise RuntimeError("Servidor de licenças não configurado.")

    response = httpx.post(
        f"{LICENSE_SERVER_URL}/v1/payment/verify-and-issue",
        json={
            "machine_id": machine or machine_id(),
            "tx_id": tx_id.strip(),
            "asset": asset.upper().strip(),
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("valid"):
        raise ValueError(data.get("message", "Pagamento não validado."))
    return data
