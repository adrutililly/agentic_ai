# llm_client.py
import os, json, logging
from typing import Optional, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from auth import get_access_token, KEYS

log = logging.getLogger("app")
load_dotenv()

BASE_URL = os.getenv(f"{KEYS.upper()}_BASE_URL", os.getenv("LLM_GATEWAY_BASE_URL") or os.getenv("LLM_GATEWAY_URL"))
GATEWAY_KEY = os.getenv(f"{KEYS.upper()}_GATEWAY_KEY", os.getenv("LLM_GATEWAY_KEY"))
EXTRA_HEADERS = os.getenv("LLM_EXTRA_HEADERS")  # JSON, e.g. {"Ocp-Apim-Subscription-Key":"..."}
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
DEFAULT_SYSTEM = os.getenv("LLM_SYSTEM") or (
    "You are a helpful, tool-using agent. Prefer web_search/wiki for factual queries. "
    "Be concise and include dates for time-sensitive info."
)

if not BASE_URL:
    raise RuntimeError("Missing LLM gateway base URL (…_BASE_URL or LLM_GATEWAY_URL)")

def _headers() -> Dict[str, str]:
    h: Dict[str, str] = {}
    token = get_access_token()
    h["Authorization"] = f"Bearer {token}"
    if GATEWAY_KEY:
        # APIM header (change name if your gateway expects a different one)
        h["X-LLM-Gateway-Key"] = GATEWAY_KEY
    if EXTRA_HEADERS:
        try:
            h.update(json.loads(EXTRA_HEADERS))
        except Exception:
            log.warning("LLM_EXTRA_HEADERS is not valid JSON; ignoring.")
    return h

def get_llm(system_instructions: Optional[str] = None,
            model: Optional[str] = None,
            temperature: float = 0.2) -> ChatOpenAI:
    base = BASE_URL.rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    llm = ChatOpenAI(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        openai_api_key="DUMMY",   # OpenAI SDK requires a non-empty key; real auth is via headers
        openai_api_base=base,
        default_headers=_headers(),
    )
    llm._system_message = SystemMessage(content=system_instructions or DEFAULT_SYSTEM)
    return llm
