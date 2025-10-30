# 🤖 Agentic AI Assistant

A truly agentic AI system where the LLM autonomously decides which tools to use based on understanding user queries. Built with LangChain patterns, FastAPI, and Streamlit.

---

## 📋 Table of Contents

- [What is Agentic AI?](#what-is-agentic-ai)
- [How This System Works](#how-this-system-works)
- [Why This is Truly Agentic](#why-this-is-truly-agentic)
- [Architecture](#architecture)
- [Detailed Flow](#detailed-flow)
- [Setup & Installation](#setup--installation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)

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

We use an **LLM to decide**:
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

The LLM reads descriptions of these tools and decides which to use!

---

## ✅ Why This is Truly Agentic

### 1. **LLM Makes Tool Selection Decisions**

**Example Query:** "Convert 10 km to miles"

```
🧠 LLM Reasoning:
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
│  │  2. Initializes LLM with system prompt           │     │
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
└────────────────┬───────────────────┬────────────────────────┘
                 │                   │
                 │                   │
      ┌──────────┴────────┐   ┌─────┴──────────┐
      ▼                   ▼   ▼                ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│   LLM Client │  │ Tools          │  │ Auth         │
│ (llm_client) │  │(tools_langchain│  │ (auth.py)    │
│              │  │     .py)       │  │              │
│ • OAuth Auth │  │                │  │ • Token Mgmt │
│ • API Calls  │  │ • Wikipedia    │  │ • Azure AD   │
│              │  │ • Calculator   │  │              │
│              │  │ • Converter    │  │              │
└──────────────┘  └────────────────┘  └──────────────┘
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

#### Step 2: Agentic Processing Starts
```python
# agentic_processing.py

# Initialize LLM with agentic system prompt
llm = get_llm()

# Get available tools with descriptions
tools = get_tools()
# Returns: [wikipedia_search, calculator, unit_converter]

# Tools have rich descriptions for LLM to understand:
# unit_converter: "Useful for converting between different units..."
```

#### Step 3: First Iteration - LLM Reasoning
```python
# LLM receives:
prompt = """
User question: Convert 10 km to miles

Available tools:
- wikipedia_search: For searching information...
- calculator: For math calculations...
- unit_converter: For converting units... (format: "X unit to unit")

What should I do?
"""

# LLM thinks and responds:
llm_response = {
    "tool": "unit_converter",
    "input": "10 km to miles"
}
```

**🎯 KEY AGENTIC MOMENT:** The LLM read the query, understood it's about unit conversion, saw the available tools, and **autonomously decided** to use `unit_converter`!

#### Step 4: Tool Execution
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

#### Step 5: Second Iteration - Final Answer
```python
# LLM receives:
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

#### Step 6: Response Returned
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
- Access to LLM Gateway (Azure OpenAI)
- Environment variables configured

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

# 4. Create .env file
cat > .env << EOF
KEYS=dev
TENANT_ID=your-tenant-id
DEV_CLIENT_ID=your-client-id
DEV_CLIENT_SECRET=your-client-secret
DEV_BASE_URL=your-llm-gateway-url
LLM_MODEL=gpt-4o-mini
EOF

# 5. Run the FastAPI server
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# 6. In another terminal, run Streamlit UI
streamlit run streamlit_app.py
```

### Access Points
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501

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
🧠 LLM analyzes: "This is an information query"
🤖 LLM decides: "I should use wikipedia_search"
📚 Executes: wikipedia_search("quantum computing")
✅ Returns: Formatted summary from Wikipedia
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

### Example 4: Multi-Tool Query (LLM Uses Multiple Tools)
```json
{
  "prompt": "Tell me about Python programming and calculate how old it is if created in 1991"
}
```

**Agentic Behavior:**
```
Iteration 1:
  🧠 LLM: "I need info about Python"
  🤖 Decision: Use wikipedia_search
  📚 Executes: wikipedia_search("Python programming")
  
Iteration 2:
  🧠 LLM: "Now I need to calculate age: 2025 - 1991"
  🤖 Decision: Use calculator
  🔢 Executes: calculator("2025-1991")
  
Iteration 3:
  🧠 LLM: "I have all information needed"
  ✅ Provides combined answer
```

---

## 📁 Project Structure

```
trial/
├── README.md                      # This file
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
│
├── auth.py                        # Azure AD OAuth authentication
├── llm_client.py                  # LLM gateway client
│
├── tools_langchain.py             # Tool definitions (Wikipedia, Calculator, Converter)
├── agentic_processing.py          # 🤖 AGENTIC CORE - ReAct loop implementation
│
├── server.py                      # FastAPI server
├── main.py                        # CLI interface
├── streamlit_app.py               # Web UI
│
└── [Old files - can delete]
    ├── tool_processing.py         # Old rule-based version
    ├── query_router.py            # Old regex router
    └── tools.py                   # Old tool implementations
```

### Key Files Explained

#### `agentic_processing.py` - The Heart of Agentic AI ❤️
```python
# This is where the magic happens!
# Implements the ReAct (Reasoning + Acting) pattern

def run_task(user_prompt):
    # 1. Get LLM with agentic system prompt
    llm = get_llm(system_instructions=AGENTIC_SYSTEM_PROMPT)
    
    # 2. Get tools with descriptions
    tools = get_tools()
    
    # 3. Agentic loop
    for iteration in range(max_iterations):
        # LLM decides what to do
        llm_response = llm.invoke(prompt)
        
        # Parse LLM decision
        if wants_to_use_tool:
            execute_tool()
            # Feed result back to LLM
        elif has_final_answer:
            return answer
```

#### `tools_langchain.py` - Tool Definitions
```python
# Each tool has:
# 1. Name: identifier for LLM
# 2. Description: tells LLM when to use it
# 3. Function: actual implementation

SimpleTool(
    name="wikipedia_search",
    description="Use this when user asks about topics, people, places...",
    func=wikipedia_search_function
)
```

#### `llm_client.py` - LLM Communication
```python
# Handles:
# - Authentication via Azure AD
# - API calls to LLM gateway
# - Token refresh
# - Error handling
```

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
# LLM makes the decision
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

This is inspired by how humans solve problems!

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

That's it! The LLM will automatically learn about this new tool and use it when appropriate!

---

## 🎯 Future Enhancements

- [ ] Add memory across conversations
- [ ] Implement tool result validation
- [ ] Add more tools (web search, database queries, email)
- [ ] Improve error recovery
- [ ] Add streaming responses
- [ ] Implement parallel tool execution
- [ ] Add tool usage analytics
- [ ] Create tool composition (tools that use other tools)

---

## 📚 Further Reading

### Papers & Research
- **ReAct Pattern**: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- **Tool Use**: [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)
- **Agents**: [AutoGPT and Autonomous Agents](https://github.com/Significant-Gravitas/AutoGPT)

### Related Projects
- **LangChain**: Framework for building LLM applications
- **AutoGPT**: Autonomous AI agents
- **BabyAGI**: Task-driven autonomous agent
- **GPT-Engineer**: AI software engineer

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add more tools
- Improve error handling
- Enhance LLM prompts
- Add tests
- Improve documentation

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 👥 Authors

Built with ❤️ as a demonstration of agentic AI principles.

---

**Remember**: The key to agentic AI is that the **LLM makes decisions**, not hardcoded rules. This system demonstrates that principle in action! 🚀
