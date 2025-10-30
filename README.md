# 🤖 Agentic AI Assistant - LLM Gateway Integration

A truly agentic AI system built for **Eli Lilly** that demonstrates how to leverage the company's **LLM Gateway** to create autonomous AI agents. The LLM autonomously decides which tools to use based on understanding user queries, showcasing enterprise-grade agentic AI capabilities.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [LLM Gateway Integration](#llm-gateway-integration)
- [What is Agentic AI?](#what-is-agentic-ai)
- [How This System Works](#how-this-system-works)
- [Why This is Truly Agentic](#why-this-is-truly-agentic)
- [Architecture](#architecture)
- [Detailed Flow](#detailed-flow)
- [Setup & Installation](#setup--installation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)

---

## 🎯 Project Overview

### Main Objective
**Demonstrate agentic AI capabilities using Eli Lilly's LLM Gateway infrastructure.**

This project showcases:
- ✅ How to build agentic AI applications using enterprise LLM Gateway
- ✅ Secure authentication with Azure AD OAuth
- ✅ Multi-model support through gateway configuration
- ✅ ReAct (Reasoning + Acting) pattern implementation
- ✅ Tool orchestration where LLM makes autonomous decisions

### Key Features
- **Agentic Tool Selection**: LLM decides which tools to use (not hardcoded rules)
- **Multi-Model Support**: Switch between GPT-4, GPT-4o-mini, or other models via gateway
- **Enterprise Security**: Azure AD authentication and token management
- **Three Tool Capabilities**: Wikipedia search, Calculator, Unit Converter
- **Multiple Interfaces**: FastAPI backend, Streamlit UI, CLI

---

## 🌐 LLM Gateway Integration

### What is the LLM Gateway?

The **LLM Gateway** is Eli Lilly's enterprise infrastructure for accessing Large Language Models. It provides:

1. **Centralized Access**: Single endpoint for multiple LLM providers (Azure OpenAI, etc.)
2. **Security & Compliance**: Enterprise-grade authentication and audit logging
3. **Cost Management**: Usage tracking and budget controls
4. **Model Flexibility**: Easy switching between different models without code changes
5. **Rate Limiting**: Prevents abuse and ensures fair resource allocation
6. **Monitoring**: Track usage, performance, and errors

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Eli Lilly Network                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Your Agentic AI Application             │  │
│  │  (This Project - Running on Developer Machine)      │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                 │
│                           │ HTTPS + OAuth Token             │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Azure AD (Authentication)                 │  │
│  │  • Issues OAuth 2.0 tokens                          │  │
│  │  • Validates client credentials                     │  │
│  │  • Token expiry: ~1 hour                           │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │ Valid Token                     │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LLM Gateway (gateway.apim-dev.lilly.com)    │  │
│  │                                                      │  │
│  │  Features:                                          │  │
│  │  • Authentication validation                        │  │
│  │  • Request routing                                  │  │
│  │  • Rate limiting                                    │  │
│  │  • Usage logging                                    │  │
│  │  • Response caching                                 │  │
│  │  • Error handling                                   │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
                    ┌───────────────┐
                    │  Azure OpenAI │
                    │   (External)  │
                    │               │
                    │  • GPT-4      │
                    │  • GPT-4o     │
                    │  • GPT-4o-mini│
                    └───────────────┘
```

### Supported Models

The gateway provides access to various models. Configure via environment variables:

| Model | Use Case | Speed | Cost |
|-------|----------|-------|------|
| `gpt-4o` | Complex reasoning | Medium | High |
| `gpt-4o-mini` | Fast responses, simple tasks | Fast | Low |
| `gpt-4` | Advanced reasoning | Slow | Highest |

**Example Configuration:**
```env
LLM_MODEL=gpt-4o-mini  # Default model for this project
```

### Authentication Flow

```
1. Application Startup
   ├─ Reads credentials from .env
   │  ├─ TENANT_ID (Azure AD tenant)
   │  ├─ CLIENT_ID (Application ID)
   │  └─ CLIENT_SECRET (Secret key)
   │
   └─ auth.py: get_access_token()

2. Token Request
   ├─ POST to Azure AD token endpoint
   │  ├─ grant_type: client_credentials
   │  ├─ client_id: DEV_CLIENT_ID
   │  ├─ client_secret: DEV_CLIENT_SECRET
   │  └─ scope: api://llm-gateway.lilly.com/.default
   │
   └─ Response: Bearer token (valid ~1 hour)

3. API Request to LLM Gateway
   ├─ Headers:
   │  ├─ Authorization: Bearer <token>
   │  └─ X-LLM-Gateway-Key: <optional-apim-key>
   │
   └─ POST to https://gateway.apim-dev.lilly.com/llm-gateway/v1/chat/completions

4. Token Refresh
   └─ Automatic refresh when token expires (< 60s remaining)
```

### Benefits of Using LLM Gateway

#### For Developers:
- **Easy Integration**: OpenAI-compatible API
- **No Direct API Keys**: Centralized credential management
- **Multi-Environment**: dev/qa/prod configurations
- **Model Switching**: Change models without code changes

#### For Eli Lilly:
- **Cost Control**: Track and limit spending per application
- **Compliance**: All requests logged and auditable
- **Security**: No direct internet access to OpenAI
- **Governance**: Centralized policy enforcement
- **Reliability**: Built-in retry and failover mechanisms

### Environment Configuration

```bash
# .env file structure

# Environment selector (dev/qa/prod)
KEYS=dev

# Azure AD Configuration
TENANT_ID=your-azure-tenant-id
AAD_SCOPE=api://llm-gateway.lilly.com/.default

# Development Environment
DEV_CLIENT_ID=your-dev-client-id
DEV_CLIENT_SECRET=your-dev-secret
DEV_BASE_URL=https://gateway.apim-dev.lilly.com/llm-gateway

# Optional: API Management Key
DEV_GATEWAY_KEY=your-optional-apim-key

# Model Configuration
LLM_MODEL=gpt-4o-mini

# Optional: Additional Headers (JSON format)
LLM_EXTRA_HEADERS={"Ocp-Apim-Subscription-Key":"your-key"}
```

### Code Integration

**Authentication (`auth.py`):**
```python
def get_access_token() -> str:
    """
    Gets OAuth token from Azure AD.
    - Caches token until expiry
    - Auto-refreshes when needed
    - Validates credentials
    """
    # Token request to Azure AD
    # Returns: Bearer token for LLM Gateway
```

**LLM Client (`llm_client.py`):**
```python
def get_llm(model=None, temperature=0.2):
    """
    Creates LLM client connected to gateway.
    - Adds OAuth token to headers
    - Supports model override
    - OpenAI-compatible interface
    """
    return ChatOpenAI(
        model=model or DEFAULT_MODEL,
        openai_api_base=BASE_URL,
        default_headers=_headers()  # Includes auth token
    )
```

---

## 🎯 What is Agentic AI?

**Agentic AI** refers to AI systems that can:
1. **Autonomously make decisions** about which actions to take
2. **Use tools/functions** to accomplish tasks
3. **Reason through multi-step problems**
4. **Adapt behavior** based on context

### Traditional AI vs Agentic AI

| Feature | Traditional AI | Agentic AI (This Project) |
|---------|---------------|---------------------------|
| **Decision Making** | Hardcoded rules (`if/else`) | LLM analyzes and decides |
| **Tool Selection** | Fixed mapping | Dynamic based on understanding |
| **Flexibility** | Rigid patterns | Adapts to any query |
| **Multi-step Tasks** | Single action | Can chain multiple tools |
| **Reasoning** | None | Shows thought process (ReAct) |

---

## 🔍 How This System Works

### The Core Concept

Instead of using **hardcoded rules** like:
```python
if "calculate" in query:
    use_calculator()  # ❌ Not agentic
elif "convert" in query:
    use_converter()   # ❌ Not agentic
```

We use an **LLM (via Gateway) to decide**:
```python
# LLM reads query and available tools
# LLM decides: "This needs the calculator tool"
# LLM outputs: {"tool": "calculator", "input": "5+3"}
# System executes the tool LLM chose  # ✅ Agentic!
```

### Three Available Tools

1. **Wikipedia Search** - Fetches information from Wikipedia
2. **Calculator** - Performs mathematical calculations
3. **Unit Converter** - Converts between units (length, weight, temperature, volume)

The LLM (accessed through the gateway) reads descriptions of these tools and decides which to use!

---

## ✅ Why This is Truly Agentic

### 1. **LLM Makes Tool Selection Decisions**

**Example Query:** "Convert 10 km to miles"

```
🧠 LLM Reasoning (via Gateway):
- Reads query: "Convert 10 km to miles"
- Sees available tools and their descriptions
- Thinks: "This is a unit conversion task"
- Decides: "I should use unit_converter tool"
- Outputs: {"tool": "unit_converter", "input": "10 km to miles"}
```

**No hardcoded rules!** The LLM understood the query semantically and chose the right tool.

### 2. **Implements ReAct Pattern**

ReAct = **Reasoning + Acting**

```
Iteration 1:
├─ Thought: LLM analyzes user query
├─ Action: LLM decides to use a tool
├─ Observation: Tool executes and returns result
└─ Thought: LLM processes result

Iteration 2:
├─ Thought: "Do I need more information?"
├─ Action: Use another tool OR provide final answer
└─ ...
```

### 3. **Multi-Tool Capability**

**Example:** "Tell me about Python and calculate 2+2"

```
Step 1: LLM uses wikipedia_search("Python")
Step 2: LLM uses calculator("2+2")
Step 3: LLM combines both results into coherent answer
```

### 4. **Context-Aware Reasoning**

The LLM adapts based on context:

- "Tell me about cats" → Uses Wikipedia
- "Calculate 5+3" → Uses Calculator  
- "100 km to miles" → Uses Converter
- "What's the capital of France and how far is it from Paris in km?" → Could use Wikipedia, then potentially Calculator

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Streamlit UI    │        │   CLI (main.py)  │          │
│  │  (Web Browser)   │        │   (Terminal)     │          │
│  └────────┬─────────┘        └────────┬─────────┘          │
└───────────┼──────────────────────────┼────────────────────┘
            │                          │
            └──────────┬───────────────┘
                       │ HTTP/Direct Call
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (server.py)                    │
│              FastAPI - Receives & Routes Requests            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│           AGENTIC ORCHESTRATOR (agentic_processing.py)      │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │  1. Receives user query                          │     │
│  │  2. Initializes LLM via Gateway                  │     │
│  │  3. Provides tool descriptions to LLM            │     │
│  │  4. Starts agentic loop (max 3 iterations)       │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  🔄 Agentic Loop:                                          │
│  ┌─────────────────────────────────────────────────┐      │
│  │  FOR each iteration:                            │      │
│  │    • LLM analyzes current state                 │      │
│  │    • LLM decides: use tool OR final answer      │      │
│  │    • IF tool: Execute & feed result back to LLM │      │
│  │    • IF final answer: Return to user            │      │
│  └─────────────────────────────────────────────────┘      │
└─────────┬──────────────────┬──────────────────┬────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌───────────┐      ┌──────────┐      ┌──────────┐
    │ LLM Client│      │  Tools   │      │   Auth   │
    │(llm_client│      │(tools_   │      │ (auth.py)│
    │    .py)   │      │langchain)│      │          │
    │           │      │          │      │          │
    │ • Gateway │      │• Wikipedia│      │• OAuth   │
    │   API     │      │• Calculator│     │• Tokens  │
    │ • Auth    │      │• Converter│      │• Azure AD│
    │   Headers │      │          │      │          │
    └─────┬─────┘      └──────────┘      └────┬─────┘
          │                                    │
          │                                    │
          └────────────┬───────────────────────┘
                       │ 
                       ▼
            ┌──────────────────────┐
            │   LLM GATEWAY        │
            │ (Eli Lilly)          │
            │                      │
            │ • Authentication     │
            │ • Rate Limiting      │
            │ • Usage Tracking     │
            │ • Model Routing      │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   Azure OpenAI       │
            │   (External)         │
            │                      │
            │ • GPT-4o-mini        │
            │ • GPT-4o             │
            │ • GPT-4              │
            └──────────────────────┘
```

---

## 🔄 Detailed Flow

### Step-by-Step Execution

**User Query:** "Convert 10 km to miles"

#### Step 1: Query Received
```
User types in Streamlit UI or CLI
    ↓
POST /prompt to FastAPI server
    ↓
server.py calls run_task(prompt="Convert 10 km to miles")
```

#### Step 2: Authentication & LLM Initialization
```python
# agentic_processing.py

# Get OAuth token from Azure AD
token = get_access_token()

# Initialize LLM with gateway connection
llm = get_llm()
# Configures:
# - Base URL: https://gateway.apim-dev.lilly.com/llm-gateway/v1
# - Headers: Authorization: Bearer <token>
# - Model: gpt-4o-mini (or configured model)
```

#### Step 3: Agentic Processing Starts
```python
# Get available tools with descriptions
tools = get_tools()
# Returns: [wikipedia_search, calculator, unit_converter]

# Tools have rich descriptions for LLM to understand:
# unit_converter: "Useful for converting between different units..."
```

#### Step 4: First Iteration - LLM Reasoning
```python
# LLM receives (via Gateway):
prompt = """
User question: Convert 10 km to miles

Available tools:
- wikipedia_search: For searching information...
- calculator: For math calculations...
- unit_converter: For converting units... (format: "X unit to unit")

What should I do?
"""

# Request sent to Gateway
# Gateway forwards to Azure OpenAI (gpt-4o-mini)
# LLM thinks and responds:
llm_response = {
    "tool": "unit_converter",
    "input": "10 km to miles"
}
```

**🎯 KEY AGENTIC MOMENT:** The LLM (accessed through Gateway) read the query, understood it's about unit conversion, saw the available tools, and **autonomously decided** to use `unit_converter`!

#### Step 5: Tool Execution
```python
# System parses LLM response
tool_name = "unit_converter"
tool_input = "10 km to miles"

# Executes the tool the LLM chose
result = unit_converter_function("10 km to miles")
# Returns: "10.0 km = **6.2137 miles**"

# Logs show:
# 🔧 Tool Call Detected:
#    Tool: unit_converter
#    Input: 10 km to miles
#    ✅ Result: 10.0 km = **6.2137 miles**
```

#### Step 6: Second Iteration - Final Answer
```python
# LLM receives (via Gateway):
prompt = """
User question: Convert 10 km to miles

Previous actions:
- Used unit_converter('10 km to miles') → 10.0 km = **6.2137 miles**

What should I do next?
"""

# LLM decides it has enough information:
llm_response = "10 kilometers is approximately 6.2137 miles."
# (No tool call - just final answer)
```

#### Step 7: Response Returned
```
agentic_processing.py returns final answer
    ↓
server.py wraps in JSON: {"output": "10 kilometers is..."}
    ↓
Streamlit UI displays to user
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- Access to Eli Lilly LLM Gateway
- Valid Azure AD credentials (Client ID & Secret)
- Eli Lilly network access (VPN if remote)

### Installation Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd trial

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install fastapi uvicorn streamlit requests python-dotenv wikipedia

# 4. Create .env file with your credentials
cat > .env << EOF
# Environment Configuration
KEYS=dev

# Azure AD Configuration
TENANT_ID=your-tenant-id-from-azure
AAD_SCOPE=api://llm-gateway.lilly.com/.default

# Development Environment Credentials
DEV_CLIENT_ID=your-dev-client-id
DEV_CLIENT_SECRET=your-dev-client-secret
DEV_BASE_URL=https://gateway.apim-dev.lilly.com/llm-gateway

# Optional: APIM Gateway Key (if required)
DEV_GATEWAY_KEY=your-apim-subscription-key

# Model Selection
LLM_MODEL=gpt-4o-mini

# Optional: System Prompt Override
LLM_SYSTEM="You are a helpful AI assistant..."
EOF

# 5. Run the FastAPI server
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# 6. In another terminal, run Streamlit UI
streamlit run streamlit_app.py
```

### Access Points
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **Streamlit UI**: http://localhost:8501

### Verifying Gateway Connection

```bash
# Check if server can reach gateway
curl http://localhost:8000/healthz

# Expected response:
{"status": "ok"}

# Test a simple query
curl -X POST http://localhost:8000/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?"}'

# Check logs for gateway connection:
# INFO: HTTP Request: POST https://gateway.apim-dev.lilly.com/...
```

---

## 📝 Usage Examples

### Example 1: Wikipedia Search (LLM Chooses Wikipedia)
```json
{
  "prompt": "Tell me about quantum computing"
}
```

**Agentic Behavior:**
```
🧠 LLM (via Gateway) analyzes: "This is an information query"
🤖 LLM decides: "I should use wikipedia_search"
📚 Executes: wikipedia_search("quantum computing")
✅ Returns: Formatted summary from Wikipedia
```

**Log Output:**
```
🤖 AGENTIC AI - Starting Task
📝 User Query: 'Tell me about quantum computing'
🔧 Available Tools: wikipedia_search, calculator, unit_converter
🧠 LLM will decide which tool(s) to use...

────────────────────────────────────────────────────────────
🔄 Iteration 1/3
────────────────────────────────────────────────────────────
🧠 LLM Thinking...
HTTP Request: POST https://gateway.apim-dev.lilly.com/llm-gateway/v1/...
💭 LLM Response: {"tool": "wikipedia_search", "input": "quantum computing"}
🔧 Tool Call Detected:
   Tool: wikipedia_search
   Input: quantum computing
📚 Wikipedia Tool: Searching for 'quantum computing'
✅ Wikipedia Tool: Found 'Quantum computing'
```

### Example 2: Calculation (LLM Chooses Calculator)
```json
{
  "prompt": "What is 144 divided by 12?"
}
```

**Agentic Behavior:**
```
🧠 LLM analyzes: "This is a math problem"
🤖 LLM decides: "I should use calculator"
🔢 Executes: calculator("144/12")
✅ Returns: "The result is: 12"
```

### Example 3: Unit Conversion (LLM Chooses Converter)
```json
{
  "prompt": "Convert 100 celsius to fahrenheit"
}
```

**Agentic Behavior:**
```
🧠 LLM analyzes: "This is a unit conversion"
🤖 LLM decides: "I should use unit_converter"
🔄 Executes: unit_converter("100 celsius to fahrenheit")
✅ Returns: "100 celsius = 212.0 fahrenheit"
```

### Example 4: Model Override
```json
{
  "prompt": "Explain quantum mechanics",
  "model": "gpt-4o"
}
```

Uses the more powerful `gpt-4o` model via the gateway for complex reasoning.

### Example 5: Custom System Instructions
```json
{
  "prompt": "Tell me about Python",
  "system": "You are a programming tutor. Explain concepts simply with examples."
}
```

Overrides the default system prompt for specialized behavior.

---

## 📁 Project Structure

```
trial/
├── README.md                      # This file
├── .env                           # Environment variables & credentials
├── requirements.txt               # Python dependencies
│
├── auth.py                        # 🔐 Azure AD OAuth authentication
│                                  #     - Token management
│                                  #     - Auto-refresh
│                                  #     - Credential validation
│
├── llm_client.py                  # 🌐 LLM Gateway client
│                                  #     - Gateway connection
│                                  #     - Header management
│                                  #     - Model configuration
│
├── tools_langchain.py             # 🔧 Tool definitions
│                                  #     - Wikipedia search
│                                  #     - Calculator
│                                  #     - Unit converter
│
├── agentic_processing.py          # 🤖 AGENTIC CORE
│                                  #     - ReAct loop implementation
│                                  #     - LLM decision making
│                                  #     - Tool orchestration
│
├── server.py                      # 🚀 FastAPI server
│                                  #     - HTTP endpoints
│                                  #     - Request handling
│
├── main.py                        # 💻 CLI interface
│                                  #     - Terminal interaction
│
└── streamlit_app.py               # 🎨 Web UI
                                   #     - Visual interface
                                   #     - History tracking
```

### Key Files Explained

#### `auth.py` - Gateway Authentication 🔐
```python
# Handles OAuth 2.0 authentication with Azure AD
# Required for accessing LLM Gateway

def get_access_token() -> str:
    """
    - Requests token from Azure AD
    - Caches token until expiry
    - Auto-refreshes when needed
    - Returns: Bearer token for gateway
    """
```

**Environment variables used:**
- `TENANT_ID`: Azure AD tenant identifier
- `{ENV}_CLIENT_ID`: Application (client) ID
- `{ENV}_CLIENT_SECRET`: Client secret key
- `AAD_SCOPE`: Token scope (api://llm-gateway.lilly.com/.default)

#### `llm_client.py` - Gateway Connection 🌐
```python
# Creates LLM client connected to Eli Lilly's gateway

def get_llm(system_instructions, model, temperature):
    """
    - Constructs gateway URL
    - Adds authentication headers
    - Configures model selection
    - Returns: ChatOpenAI instance
    """
```

**Environment variables used:**
- `{ENV}_BASE_URL`: Gateway endpoint
- `{ENV}_GATEWAY_KEY`: Optional APIM key
- `LLM_MODEL`: Default model name
- `LLM_EXTRA_HEADERS`: Additional headers (JSON)

#### `agentic_processing.py` - The Agentic Brain 🤖
```python
# This is where the agentic magic happens!
# Implements the ReAct (Reasoning + Acting) pattern

def run_task(user_prompt):
    """
    1. Get LLM with agentic system prompt
    2. Load tools with descriptions
    3. Run agentic loop:
       - LLM analyzes situation
       - LLM decides which tool to use
       - Execute tool and feed result back
       - Repeat or provide final answer
    """
```

**Key feature:** LLM makes ALL decisions about tool usage!

#### `tools_langchain.py` - Tool Library 🔧
```python
# Defines tools the LLM can use

class SimpleTool:
    name: str          # Identifier for LLM
    description: str   # Tells LLM when to use it
    func: Callable     # Actual implementation

# Example:
SimpleTool(
    name="calculator",
    description="Use for mathematical calculations...",
    func=calculator_function
)
```

**The descriptions are crucial** - they teach the LLM when to use each tool!

---

## 🎓 Key Concepts

### What Makes This "Agentic"?

#### ❌ NOT Agentic:
```python
# Hardcoded decision tree
if "calculate" in query:
    return calculator(query)
elif "convert" in query:
    return converter(query)
else:
    return wikipedia(query)
```

#### ✅ IS Agentic:
```python
# LLM (via Gateway) makes the decision
tools_description = """
- calculator: for math
- converter: for units
- wikipedia: for information
"""

llm_decision = llm.decide(query, tools_description)
return execute_tool(llm_decision)
```

### The ReAct Pattern

**Re**asoning + **Act**ing = ReAct

1. **Thought**: LLM reasons about the problem
2. **Action**: LLM chooses a tool to use
3. **Observation**: Tool executes and returns result
4. **Thought**: LLM processes the observation
5. **Action**: Use another tool OR provide final answer

This mirrors how humans solve problems!

### Why Use LLM Gateway for Agentic AI?

1. **Consistent Access**: Same agentic patterns work across dev/qa/prod
2. **Model Flexibility**: Can A/B test different models for agent performance
3. **Cost Tracking**: Monitor which tools/queries consume most resources
4. **Security**: Enterprise-grade auth for autonomous agents
5. **Scalability**: Gateway handles load balancing as agent usage grows

---

## 🔧 Extending the System

### Adding a New Tool

1. **Define the tool function** in `tools_langchain.py`:
```python
def weather_function(location: str) -> str:
    """Get weather for a location."""
    # Your implementation
    return f"Weather in {location}: Sunny, 72°F"
```

2. **Create SimpleTool wrapper**:
```python
weather_tool = SimpleTool(
    name="weather_checker",
    description=(
        "Use this to get current weather information. "
        "Input should be a city name or location. "
        "Use when user asks about weather, temperature, or conditions."
    ),
    func=weather_function
)
```

3. **Add to get_tools()**:
```python
def get_tools():
    return [
        wikipedia_tool,
        calculator_tool,
        converter_tool,
        weather_tool  # Add new tool
    ]
```

That's it! The LLM (via Gateway) will automatically learn about this new tool and use it when appropriate!

### Switching Models

```bash
# In .env file
LLM_MODEL=gpt-4o        # For complex reasoning
# or
LLM_MODEL=gpt-4o-mini   # For faster, cost-effective responses
```

### Using Different Environments

```bash
# Development
KEYS=dev
DEV_CLIENT_ID=...
DEV_BASE_URL=https://gateway.apim-dev.lilly.com/...

# QA
KEYS=qa
QA_CLIENT_ID=...
QA_BASE_URL=https://gateway.apim-qa.lilly.com/...

# Production
KEYS=prod
PROD_CLIENT_ID=...
PROD_BASE_URL=https://gateway.apim.lilly.com/...
```

---

## 🎯 Future Enhancements

- [ ] Add memory across conversations (conversation history)
- [ ] Implement tool result validation
- [ ] Add more tools (database queries, email, Slack integration)
- [ ] Improve error recovery and retry logic
- [ ] Add streaming responses for better UX
- [ ] Implement parallel tool execution
- [ ] Add tool usage analytics dashboard
- [ ] Create tool composition (tools that use other tools)
- [ ] A/B test different models for optimal performance
- [ ] Add prompt optimization for better tool selection

---

## 📚 Further Reading

### Agentic AI Patterns
- **ReAct Pattern**: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- **Tool Use**: [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)

### LangChain Resources
- [LangChain Documentation](https://python.langchain.com/)
- [Building Agents with LangChain](https://python.langchain.com/docs/modules/agents/)

### Enterprise LLM Best Practices
- Token management and refresh strategies
- Rate limiting and retry patterns
- Error handling in production
- Cost optimization techniques

---

## 🤝 Contributing

This project demonstrates agentic AI using LLM Gateway. 

---

## 📄 License

Eli Lilly project. 

---

## 👥 Credits

Built to showcase **agentic AI capabilities** using **Eli Lilly's LLM Gateway infrastructure**.

**Key Achievement:** Demonstrated that LLM-powered agents can autonomously decide which tools to use, moving beyond hardcoded decision trees to true adaptive AI behavior.

---

## 🔗 Related Resources

### Internal Eli Lilly Resources
- LLM Gateway Documentation (Internal Portal)
- Azure AD App Registration Guide
- API Management Portal
- Model Performance Benchmarks

### Support
- For gateway access issues: Contact IT Service Desk
- For credentials: Azure AD Portal
- For model selection guidance: AI Team

---

**Remember**: The key to agentic AI is that the **LLM makes decisions via the Gateway**, not hardcoded rules. This system demonstrates that principle using enterprise infrastructure! 🚀
