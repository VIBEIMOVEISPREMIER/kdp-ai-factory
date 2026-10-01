"""Generic user-configurable image API providers."""
from __future__ import annotations
import json
from typing import Any
import httpx
from ..config import DATA_DIR

PATH = DATA_DIR / "image_providers.json"

def list_providers() -> list[dict[str, Any]]:
    if not PATH.exists():
        return []
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_providers(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return items

def upsert_provider(provider: dict[str, Any]) -> dict[str, Any]:
    items = list_providers()
    provider = dict(provider)
    provider.setdefault("id", provider.get("name", "custom").lower().replace(" ", "-"))
    items = [x for x in items if x.get("id") != provider["id"]]
    items.append(provider)
    save_providers(items)
    return provider

async def generate(provider: dict[str, Any], prompt: str) -> dict[str, Any]:
    base = provider.get("base_url", "").rstrip("/")
    endpoint = provider.get("endpoint", "/images/generations")
    url = f"{base}/{endpoint.lstrip('/')}"
    headers = dict(provider.get("headers") or {})
    if provider.get("api_key"):
        headers["Authorization"] = f"Bearer {provider['api_key']}"
    payload = dict(provider.get("extra_body") or {})
    payload["prompt"] = prompt
    if provider.get("model"):
        payload["model"] = provider["model"]
    async with httpx.AsyncClient(timeout=float(provider.get("timeout", 180))) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
