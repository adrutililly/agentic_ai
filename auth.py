# auth.py
import os, time, requests
from dotenv import load_dotenv

load_dotenv()  # ✅ ensure .env is loaded before we read env vars

# Decide env ONLY via .env (KEYS=dev|qa|prod); default to dev if missing.
KEYS = os.getenv("KEYS", "dev").lower()

TENANT_ID = os.getenv("TENANT_ID")
SCOPE     = os.getenv("AAD_SCOPE", "api://llm-gateway.lilly.com/.default")

CLIENT_ID     = os.getenv(f"{KEYS.upper()}_CLIENT_ID", os.getenv("CLIENT_ID"))
CLIENT_SECRET = os.getenv(f"{KEYS.upper()}_CLIENT_SECRET", os.getenv("CLIENT_SECRET"))

if not (TENANT_ID and CLIENT_ID and CLIENT_SECRET):
    raise RuntimeError(f"Missing TENANT_ID / CLIENT_ID / CLIENT_SECRET (env={KEYS})")

TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

_token, _exp = None, 0

def get_access_token() -> str:
    global _token, _exp
    now = time.time()
    if _token and now < _exp - 60:
        return _token

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
    }
    resp = requests.post(TOKEN_URL, data=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    _token = data["access_token"]
    _exp   = now + int(data.get("expires_in", 3600))
    return _token
