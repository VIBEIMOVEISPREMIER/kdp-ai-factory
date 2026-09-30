from __future__ import annotations
import base64,json
from datetime import datetime,timezone
from typing import Any
import httpx
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from ..config import LICENSE_SERVER_URL,LICENSE_STATE_PATH,LICENSE_PUBLIC_KEY_B64
from .machine import machine_id
FREE_BOOK_LIMIT=1
def _now():return datetime.now(timezone.utc).isoformat()
def _read_state():
 if not LICENSE_STATE_PATH.exists():return {"machine_id":machine_id(),"books_created":0,"licensed":False}
 try:
  state=json.loads(LICENSE_STATE_PATH.read_text(encoding="utf-8"));state["machine_id"]=machine_id();return state
 except Exception:return {"machine_id":machine_id(),"books_created":0,"licensed":False}
def _write_state(state):LICENSE_STATE_PATH.parent.mkdir(parents=True,exist_ok=True);LICENSE_STATE_PATH.write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding="utf-8")
def _decode_license(token:str):
 p=token.split(".")
 if len(p)!=3 or p[0]!="KDP1":raise ValueError("Formato de licença inválido.")
 raw=base64.urlsafe_b64decode(p[1]+"="*(-len(p[1])%4));sig=base64.urlsafe_b64decode(p[2]+"="*(-len(p[2])%4))
 if not LICENSE_PUBLIC_KEY_B64:raise RuntimeError("Chave pública da licença não configurada.")
 Ed25519PublicKey.from_public_bytes(base64.b64decode(LICENSE_PUBLIC_KEY_B64)).verify(sig,raw)
 data=json.loads(raw.decode("utf-8"))
 if data.get("type")!="lifetime" or data.get("machine_id")!=machine_id():raise ValueError("Licença não pertence a esta máquina.")
 return data
def status():
 state=_read_state()
 return {"licensed":bool(state.get("licensed")),"books_created":int(state.get("books_created",0)),"free_books_remaining":0 if state.get("licensed") else max(0,FREE_BOOK_LIMIT-int(state.get("books_created",0))),"license_server_configured":bool(LICENSE_SERVER_URL),"machine_id":machine_id()}
def assert_can_create_book(project_id=None):
 state=_read_state()
 if state.get("licensed"):return
 if int(state.get("books_created",0))>=FREE_BOOK_LIMIT:raise PermissionError("O período gratuito de 1 livro já foi utilizado. Ative a licença vitalícia para continuar.")
 if LICENSE_SERVER_URL and project_id:
  try:
   r=httpx.post(f"{LICENSE_SERVER_URL}/v1/trial/consume",json={"machine_id":machine_id(),"project_id":project_id},timeout=10);r.raise_for_status();d=r.json()
   if not d.get("allowed"):raise PermissionError(d.get("reason","O período gratuito já foi utilizado."))
  except PermissionError:raise
  except httpx.HTTPError as e:raise RuntimeError("Não foi possível validar o período gratuito no servidor oficial.") from e
def register_book_created():
 state=_read_state();state["machine_id"]=machine_id();state["books_created"]=int(state.get("books_created",0))+1;state["last_book_created_at"]=_now();_write_state(state)
def activate_with_license(license_token):
 if not LICENSE_SERVER_URL:raise RuntimeError("Servidor de licenças não configurado.")
 data=_decode_license(license_token)
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/license/activate",json={"machine_id":machine_id(),"license_token":license_token},timeout=15);r.raise_for_status();server=r.json()
 if not server.get("valid"):raise ValueError(server.get("reason","Licença inválida."))
 state=_read_state();state.update({"machine_id":machine_id(),"licensed":True,"license":server});_write_state(state);return server
def verify_payment_and_issue_license(tx_id,asset,machine=None):
 if not LICENSE_SERVER_URL:raise RuntimeError("Servidor de licenças não configurado.")
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/payment/verify-and-issue",json={"machine_id":machine or machine_id(),"tx_id":tx_id.strip(),"asset":asset.upper().strip()},timeout=45);r.raise_for_status();data=r.json()
 if not data.get("valid"):raise ValueError(data.get("reason","Pagamento não validado."))
 _decode_license(data["license_token"])
 state=_read_state();state.update({"machine_id":machine_id(),"licensed":True,"license":data});_write_state(state)
 return data
