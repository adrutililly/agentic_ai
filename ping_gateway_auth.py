import os, json, requests
from dotenv import load_dotenv
load_dotenv()

KEYS = (os.getenv("KEYS") or "dev").lower()

base = os.getenv(f"{KEYS.upper()}_BASE_URL") or os.getenv("LLM_GATEWAY_BASE_URL") or os.getenv("LLM_GATEWAY_URL")
if not base:
    raise SystemExit("Missing *_BASE_URL or LLM_GATEWAY_URL in .env")
base = base.rstrip("/")
if not base.endswith("/v1"):
    base += "/v1"

# Get AAD bearer via your auth.py
from auth import get_access_token
token = get_access_token()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

# Gateway/APIM key header (you used X-LLM-Gateway-Key)
gk = os.getenv(f"{KEYS.upper()}_GATEWAY_KEY") or os.getenv("LLM_GATEWAY_KEY")
if gk:
    headers["X-LLM-Gateway-Key"] = gk

# Optional extra APIM header if your platform requires it
extra = os.getenv("LLM_EXTRA_HEADERS")
if extra:
    try:
        headers.update(json.loads(extra))
    except Exception:
        print("⚠️ LLM_EXTRA_HEADERS not valid JSON; ignoring.")

def show(resp):
    print(resp.status_code, resp.reason)
    print((resp.text or "")[:600], "\n")

print("Base =", base)
print("POST /chat/completions")
model = os.getenv("LLM_MODEL", "gpt-4o")
payload = {"model": model, "messages": [{"role": "user", "content": "Say OK."}]}
show(requests.post(f"{base}/chat/completions", headers=headers, json=payload, timeout=30))
