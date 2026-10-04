from __future__ import annotations
import base64,hashlib,json,secrets,re
from datetime import datetime,timezone
from typing import Any
import httpx
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from ..config import LICENSE_SERVER_URL,LICENSE_STATE_PATH,LICENSE_PUBLIC_KEY_B64
from .machine import machine_id
FREE_BOOK_LIMIT=1
def _now():return datetime.now(timezone.utc).isoformat()
def _user_id():
 state={}
 try:
  if LICENSE_STATE_PATH.exists(): state=json.loads(LICENSE_STATE_PATH.read_text(encoding="utf-8"))
 except Exception: pass
 uid=str(state.get("user_id","")).strip().lower()
 if not re.fullmatch(r"usr_[0-9a-f]{32}",uid):
  uid="usr_"+secrets.token_hex(16)
  state["user_id"]=uid
  LICENSE_STATE_PATH.parent.mkdir(parents=True,exist_ok=True)
  LICENSE_STATE_PATH.write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding="utf-8")
 return uid
def _read_state():
 if not LICENSE_STATE_PATH.exists():return {"machine_id":machine_id(),"user_id":_user_id(),"books_created":0,"licensed":False}
 try:
  state=json.loads(LICENSE_STATE_PATH.read_text(encoding="utf-8"));state["machine_id"]=machine_id();state["user_id"]=state.get("user_id") or _user_id();return state
 except Exception:return {"machine_id":machine_id(),"books_created":0,"licensed":False}
def _write_state(state):LICENSE_STATE_PATH.parent.mkdir(parents=True,exist_ok=True);LICENSE_STATE_PATH.write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding="utf-8")
def _decode_license(token:str, expected_machine=None):
 p=token.split(".")
 if len(p)!=3 or p[0]!="KDP1":raise ValueError("Formato de licença inválido.")
 raw=base64.urlsafe_b64decode(p[1]+"="*(-len(p[1])%4));sig=base64.urlsafe_b64decode(p[2]+"="*(-len(p[2])%4))
 if not LICENSE_PUBLIC_KEY_B64:raise RuntimeError("Chave pública da licença não configurada.")
 Ed25519PublicKey.from_public_bytes(base64.b64decode(LICENSE_PUBLIC_KEY_B64)).verify(sig,raw)
 data=json.loads(raw.decode("utf-8"))
 if data.get("type")!="lifetime" or data.get("machine_id")!=(expected_machine or machine_id()):raise ValueError("Licença não pertence a esta máquina.")
 return data
def server_bootstrap(fingerprint_hash: str = ""):
 if not LICENSE_SERVER_URL: return {}
 try:
  r=httpx.post(f"{LICENSE_SERVER_URL}/v1/client/bootstrap",json={"machine_id":machine_id(),"fingerprint_hash":fingerprint_hash,"user_id":_user_id()},timeout=10)
  r.raise_for_status()
  return r.json()
 except httpx.HTTPError:
  return {}

def status():
 state=_read_state()
 bootstrap=server_bootstrap()
 if bootstrap:
  if bootstrap.get("user_id"):
   state["user_id"]=str(bootstrap["user_id"]).strip().lower()
  if bootstrap.get("machine_id"):
   state["machine_id"]=str(bootstrap["machine_id"]).strip().lower()
  lic=bootstrap.get("license") or {}
  if "licensed" in lic:
   state["licensed"]=bool(lic.get("licensed"))
  state["bootstrap_at"]=_now()
  _write_state(state)
 uid=str(state.get("user_id") or _user_id()).strip().lower()
 return {"licensed":bool(state.get("licensed")),"user_id":uid,"books_created":int(state.get("books_created",0)),"free_books_remaining":0 if state.get("licensed") else max(0,FREE_BOOK_LIMIT-int(state.get("books_created",0))),"license_server_configured":bool(LICENSE_SERVER_URL),"machine_id":machine_id()}
def web_identity(user_id):
 uid=str(user_id or "").strip().lower()
 if not re.fullmatch(r"usr_[0-9a-f]{32}",uid): raise ValueError("ID de usuário inválido.")
 return hashlib.sha256(("kdp-web:"+uid).encode("utf-8")).hexdigest()

def web_license_status(user_id):
 uid=str(user_id or "").strip().lower(); mid=web_identity(uid)
 if not LICENSE_SERVER_URL: return {"licensed":False,"user_id":uid,"machine_id":mid,"license_server_configured":False}
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/client/bootstrap",json={"machine_id":mid,"fingerprint_hash":"","user_id":uid},timeout=10)
 r.raise_for_status(); d=r.json(); lic=d.get("license") or {}
 return {"licensed":bool(lic.get("licensed")),"user_id":str(d.get("user_id") or uid),"machine_id":str(d.get("machine_id") or mid),"free_books_remaining":int(lic.get("free_books_remaining",0)),"license_server_configured":True}

def activate_web_license(license_token,user_id):
 uid=str(user_id or "").strip().lower(); mid=web_identity(uid)
 if not LICENSE_SERVER_URL: raise RuntimeError("Servidor de licenças não configurado.")
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/license/activate",json={"machine_id":mid,"user_id":uid,"license_token":license_token},timeout=15)
 r.raise_for_status(); data=r.json()
 if not data.get("valid"): raise ValueError(data.get("reason","Licença inválida."))
 return data

def create_web_payment_intent(asset,user_id):
 uid=str(user_id or "").strip().lower(); mid=web_identity(uid)
 if not LICENSE_SERVER_URL: raise RuntimeError("Servidor de licenças não configurado.")
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/payment/create-intent",json={"machine_id":mid,"user_id":uid,"asset":asset.upper().strip()},timeout=30)
 r.raise_for_status(); data=r.json(); data.setdefault("user_id",uid); data.setdefault("machine_id",mid); return data

def verify_web_payment_and_issue_license(tx_id,asset,user_id,referral_code="",intent_id=None,intent_secret=None):
 uid=str(user_id or "").strip().lower(); mid=web_identity(uid)
 if not LICENSE_SERVER_URL: raise RuntimeError("Servidor de licenças não configurado.")
 if not intent_id or not intent_secret: raise RuntimeError("Crie um pedido de pagamento antes de enviar a transação.")
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/payment/verify-and-issue",json={"machine_id":mid,"user_id":uid,"intent_id":intent_id,"intent_secret":intent_secret,"tx_id":tx_id.strip(),"asset":asset.upper().strip(),"referral_code":referral_code.strip()},timeout=45)
 r.raise_for_status(); data=r.json()
 if not data.get("valid"): raise ValueError(data.get("reason","Pagamento não validado."))
 _decode_license(data["license_token"], expected_machine=mid)
 return data

def assert_can_create_book(project_id=None, trial_machine_id=None):
 # Desktop uses its physical machine. Web uses a deterministic machine ID derived
 # from the persistent browser User ID, so Render's own machine is never shared
 # between customers.
 if trial_machine_id:
  if not LICENSE_SERVER_URL or not project_id:
   raise RuntimeError("Não foi possível validar o período gratuito no servidor oficial.")
  try:
   r=httpx.post(f"{LICENSE_SERVER_URL}/v1/trial/consume",json={"machine_id":trial_machine_id,"project_id":project_id},timeout=10);r.raise_for_status();d=r.json()
   if not d.get("allowed"):raise PermissionError(d.get("reason","O período gratuito já foi utilizado."))
   return
  except PermissionError:raise
  except httpx.HTTPError as e:raise RuntimeError("Não foi possível validar o período gratuito no servidor oficial.") from e
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
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/license/activate",json={"machine_id":machine_id(),"user_id":_user_id(),"license_token":license_token},timeout=15);r.raise_for_status();server=r.json()
 if not server.get("valid"):raise ValueError(server.get("reason","Licença inválida."))
 state=_read_state();state.update({"machine_id":machine_id(),"licensed":True,"license":server});_write_state(state);return server
def create_payment_intent(asset,machine=None):
 if not LICENSE_SERVER_URL:raise RuntimeError("Servidor de licenças não configurado.")
 mid=machine or machine_id();uid=_user_id();asset=asset.upper().strip()
 last_error=None
 for attempt in range(3):
  try:
   r=httpx.post(f"{LICENSE_SERVER_URL}/v1/payment/create-intent",json={"machine_id":mid,"user_id":uid,"asset":asset},timeout=30)
   r.raise_for_status()
   return r.json()
  except httpx.HTTPError as e:
   last_error=e
   if attempt<2: time.sleep(2)
 raise RuntimeError("Servidor de licenças temporariamente indisponível. Tente novamente em alguns segundos.") from last_error

def verify_payment_and_issue_license(tx_id,asset,machine=None,referral_code="",intent_id=None,intent_secret=None):
 if not LICENSE_SERVER_URL:raise RuntimeError("Servidor de licenças não configurado.")
 mid=machine or machine_id();uid=_user_id();asset=asset.upper().strip()
 if not intent_id or not intent_secret:raise RuntimeError("Crie um pedido de pagamento antes de enviar a transação.")
 r=httpx.post(f"{LICENSE_SERVER_URL}/v1/payment/verify-and-issue",json={"machine_id":mid,"user_id":uid,"intent_id":intent_id,"intent_secret":intent_secret,"tx_id":tx_id.strip(),"asset":asset,"referral_code":referral_code.strip()},timeout=45);r.raise_for_status();data=r.json()
 if not data.get("valid"):raise ValueError(data.get("reason","Pagamento não validado."))
 _decode_license(data["license_token"])
 state=_read_state();state.update({"machine_id":machine_id(),"user_id":uid,"licensed":True,"license":data});_write_state(state)
 return data
