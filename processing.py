# processing.py
import ast
import math
import re
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from llm_client import get_llm

# -----------------------
# Utility: safe math eval
# -----------------------
_ALLOWED_NAMES = {
    k: getattr(math, k)
    for k in [
        "pi", "e", "tau", "inf", "nan", "sqrt", "log", "log10", "sin", "cos", "tan",
        "asin", "acos", "atan", "sinh", "cosh", "tanh", "exp", "floor", "ceil", "fabs",
    ]
}
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)
_ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)

def _eval_expr(expr: str) -> float:
    node = ast.parse(expr, mode="eval")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Num):
            return n.n
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and isinstance(n.op, _ALLOWED_BINOPS):
            l, r = _eval(n.left), _eval(n.right)
            if isinstance(n.op, ast.Add):  return l + r
            if isinstance(n.op, ast.Sub):  return l - r
            if isinstance(n.op, ast.Mult): return l * r
            if isinstance(n.op, ast.Div):  return l / r
            if isinstance(n.op, ast.Pow):  return l ** r
            if isinstance(n.op, ast.Mod):  return l % r
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, _ALLOWED_UNARYOPS):
            v = _eval(n.operand)
            return +v if isinstance(n.op, ast.UAdd) else -v
        if isinstance(n, ast.Name) and n.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[n.id]
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _ALLOWED_NAMES:
            fn = _ALLOWED_NAMES[n.func.id]
            args = [_eval(a) for a in n.args]
            return fn(*args)
        raise ValueError("Unsafe or unsupported expression.")
    return float(_eval(node))


# -----------------------
# Tools
# -----------------------
HTTP_TIMEOUT = 12.0
UA = "AgenticApp/1.0 (+https://example.internal)"

class WebSearchArgs(BaseModel):
    query: str = Field(..., description="Natural language query to search on the web.")

def _web_search(args: WebSearchArgs) -> Dict[str, Any]:
    url = "https://api.duckduckgo.com/"
    params = {"q": args.query, "format": "json", "no_html": 1, "t": "agentic-app"}
    with httpx.Client(timeout=HTTP_TIMEOUT, headers={"User-Agent": UA}) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    abstract = data.get("AbstractText") or data.get("Abstract") or ""
    heading = data.get("Heading") or ""
    related = []
    for item in data.get("RelatedTopics", [])[:8]:
        if isinstance(item, dict):
            if "Text" in item and "FirstURL" in item:
                related.append({"text": item["Text"], "url": item["FirstURL"]})
            elif "Topics" in item:
                for sub in item["Topics"][:5]:
                    if "Text" in sub and "FirstURL" in sub:
                        related.append({"text": sub["Text"], "url": sub["FirstURL"]})
    return {"heading": heading, "abstract": abstract, "related": related[:8]}

WebSearchTool = StructuredTool.from_function(
    func=_web_search,
    name="web_search",
    description="Quick web lookup for facts/news/scores using DuckDuckGo Instant Answer.",
    args_schema=WebSearchArgs,
)

class WikiSummaryArgs(BaseModel):
    topic: str = Field(..., description="Topic or page title to summarize from Wikipedia.")

def _wiki_summary(args: WikiSummaryArgs) -> Dict[str, Any]:
    title = args.topic.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    with httpx.Client(timeout=HTTP_TIMEOUT, headers={"User-Agent": UA}) as client:
        r = client.get(url)
        if r.status_code == 404:
            return {"title": args.topic, "summary": "Not found."}
        r.raise_for_status()
        data = r.json()
    summary = data.get("extract") or ""
    display = data.get("title") or args.topic
    canonical = data.get("content_urls", {}).get("desktop", {}).get("page", "")
    return {"title": display, "summary": summary, "url": canonical}

WikiSummaryTool = StructuredTool.from_function(
    func=_wiki_summary,
    name="wiki_summary",
    description="Fetch a concise encyclopedic summary of a topic from Wikipedia.",
    args_schema=WikiSummaryArgs,
)

class FetchUrlArgs(BaseModel):
    url: str = Field(..., description="HTTP/HTTPS URL to retrieve and trim to ~2k chars.")

_ALLOW_RE = re.compile(r"^https?://", re.I)
_DENY_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

def _fetch_url(args: FetchUrlArgs) -> Dict[str, Any]:
    if not _ALLOW_RE.match(args.url):
        raise ValueError("Only http(s) URLs are allowed.")
    host = re.sub(r"^https?://", "", args.url).split("/")[0].split(":")[0]
    if host in _DENY_HOSTS:
        raise ValueError("Local/loopback hosts are not allowed.")
    with httpx.Client(timeout=HTTP_TIMEOUT, headers={"User-Agent": UA}, follow_redirects=True) as client:
        r = client.get(args.url)
        r.raise_for_status()
        text = r.text
    snippet = re.sub(r"\s+", " ", text)[:2000]
    return {"url": args.url, "snippet": snippet}

FetchUrlTool = StructuredTool.from_function(
    func=_fetch_url,
    name="fetch_url",
    description="Fetch a web page and return a trimmed text snippet (for the LLM to summarize).",
    args_schema=FetchUrlArgs,
)

class CalcArgs(BaseModel):
    expression: str = Field(..., description="Math expression, e.g., '2*(3+4)/5 + sin(pi/2)'" )

def _calculator(args: CalcArgs) -> Dict[str, Any]:
    value = _eval_expr(args.expression)
    return {"expression": args.expression, "result": value}

CalculatorTool = StructuredTool.from_function(
    func=_calculator,
    name="calculator",
    description="Evaluate a safe math expression with common math functions.",
    args_schema=CalcArgs,
)

class UnitConvertArgs(BaseModel):
    value: float
    from_unit: str = Field(..., description="e.g., km, mi, kg, lb, c, f")
    to_unit: str = Field(..., description="target unit")

_CONV = {
    ("km", "mi"): 0.621371, ("mi", "km"): 1.60934,
    ("kg", "lb"): 2.20462,  ("lb", "kg"): 0.453592,
}

def _unit_convert(args: UnitConvertArgs) -> Dict[str, Any]:
    fu, tu = args.from_unit.lower(), args.to_unit.lower()
    if fu in {"c","f"} and tu in {"c","f"}:
        val = (args.value * 9/5 + 32) if (fu=="c" and tu=="f") else ((args.value - 32) * 5/9)
        return {"value": args.value, "from": fu, "to": tu, "result": val}
    key = (fu, tu)
    if key not in _CONV: raise ValueError(f"Unsupported conversion {fu}->{tu}")
    return {"value": args.value, "from": fu, "to": tu, "result": args.value * _CONV[key]}

UnitConvertTool = StructuredTool.from_function(
    func=_unit_convert,
    name="unit_convert",
    description="Convert between km/mi, kg/lb, and C/F.",
    args_schema=UnitConvertArgs,
)

class NowArgs(BaseModel):
    pass

def _now(_: NowArgs) -> Dict[str, Any]:
    from datetime import datetime
    return {"now_iso": datetime.now().isoformat(timespec="seconds")}

NowTool = StructuredTool.from_function(
    func=_now,
    name="now",
    description="Return current local datetime (ISO).",
    args_schema=NowArgs,
)

TOOLS: List[StructuredTool] = [
    WebSearchTool, WikiSummaryTool, FetchUrlTool, CalculatorTool, UnitConvertTool, NowTool
]
TOOL_MAP: Dict[str, StructuredTool] = {t.name: t for t in TOOLS}

PROMPT = ChatPromptTemplate.from_messages(
    [
        # System is injected from get_llm() but we keep a simple human+scratchpad scaffold
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# -----------------------
# Minimal manual agent loop (no factories)
# -----------------------
def _run_tool_calls(ai: AIMessage) -> List[ToolMessage]:
    """Execute tool calls emitted by the LLM and return ToolMessages."""
    results: List[ToolMessage] = []
    for call in ai.tool_calls or []:
        name: str = call["name"]
        args: Dict[str, Any] = call.get("args", {}) or {}
        call_id: str = call.get("id", "")
        tool = TOOL_MAP.get(name)
        if tool is None:
            results.append(ToolMessage(content=f"Tool '{name}' not found.", tool_call_id=call_id))
            continue
        try:
            # StructuredTool supports .invoke(args)
            out = tool.invoke(args)
            results.append(ToolMessage(content=str(out), tool_call_id=call_id))
        except Exception as e:
            results.append(ToolMessage(content=f"ERROR: {e}", tool_call_id=call_id))
    return results

def _agentic_answer(llm, user_input: str, max_steps: int = 4) -> str:
    """Simple ReAct-style loop using tool calling; no AgentExecutor needed."""
    # Bind tools so the model can emit tool_calls
    llm_with_tools = llm.bind_tools(TOOLS)

    messages: List[Any] = [HumanMessage(user_input)]
    for _ in range(max_steps):
        ai: AIMessage = llm_with_tools.invoke(messages)
        # If no tools called, return the model's final content
        if not ai.tool_calls:
            return ai.content if isinstance(ai.content, str) else str(ai.content)

        # Append the AI tool call message
        messages.append(ai)

        # Execute tools and append ToolMessages
        tool_msgs = _run_tool_calls(ai)
        messages.extend(tool_msgs)

    # Failsafe final pass (ask for a concise answer)
    final = llm.invoke(messages + [HumanMessage("Provide a concise final answer.")])
    return final.content if isinstance(final.content, str) else str(final.content)

def build_agent(system_instructions: Optional[str] = None, model: Optional[str] = None):
    # Returns a callable that runs the loop with the configured llm
    llm = get_llm(system_instructions=system_instructions, model=model)
    def _runner(user_input: str) -> str:
        return _agentic_answer(llm, user_input)
    return _runner

def run_task(
    user_prompt: str,
    system_instructions: Optional[str] = None,
    model: Optional[str] = None,
    session_id: str = "default",  # kept for API compatibility; not used in this factory-free loop
) -> str:
    runner = build_agent(system_instructions=system_instructions, model=model)
    return runner(user_prompt)
