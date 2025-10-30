# streamlit_app.py
import streamlit as st
import requests
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Agentic AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .response-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .tool-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px 0;
    }
    .wikipedia-badge {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .calculator-badge {
        background-color: #fff3e0;
        color: #f57c00;
    }
    .converter-badge {
        background-color: #e8f5e9;
        color: #388e3c;
    }
    h1 {
        color: #1e3a8a;
    }
    .example-button {
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# API endpoint
API_URL = "http://localhost:8000/prompt"

def call_api(prompt: str, model: str = None, system: str = None):
    """Call the FastAPI backend"""
    try:
        payload = {"prompt": prompt}
        if model:
            payload["model"] = model
        if system:
            payload["system"] = system
        
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the API server. Make sure it's running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The query is taking too long.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def detect_tool_type(prompt: str) -> str:
    """Detect which tool will likely be used"""
    prompt_lower = prompt.lower()
    
    # Calculator detection
    if any(word in prompt_lower for word in ["calculate", "compute", "what is", "+", "-", "*", "/"]):
        if any(char.isdigit() for char in prompt):
            return "calculator"
    
    # Converter detection
    if any(word in prompt_lower for word in ["convert", "to", "in"]) and any(char.isdigit() for char in prompt):
        return "converter"
    
    # Default to Wikipedia
    return "wikipedia"

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://em-content.zobj.net/thumbs/160/apple/325/robot_1f916.png", width=80)
with col2:
    st.title("🤖 Agentic AI Assistant")
    st.markdown("*Your intelligent assistant for Wikipedia search, calculations, and unit conversions*")

st.divider()

# Sidebar for optional configurations
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    model_input = st.text_input(
        "Model (optional)",
        placeholder="e.g., gpt-4o-mini",
        help="Override the default LLM model"
    )
    
    # System instructions
    system_input = st.text_area(
        "System Instructions (optional)",
        placeholder="Custom system instructions for the AI...",
        help="Override default system instructions",
        height=100
    )
    
    st.divider()
    
    # Server status check
    st.subheader("🔌 Server Status")
    try:
        health_response = requests.get("http://localhost:8000/healthz", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
    except:
        st.error("❌ Server not running")
        st.caption("Run: `uvicorn server:app --reload`")
    
    st.divider()
    
    # Clear history button
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# Main content area
st.header("💬 Ask Me Anything")

# Example queries
st.markdown("**Try these examples:**")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📚 Tell me about Python", key="ex1", use_container_width=True):
        st.session_state.current_prompt = "Tell me about Python programming"
with col2:
    if st.button("🔢 Calculate 144 / 12", key="ex2", use_container_width=True):
        st.session_state.current_prompt = "calculate 144 / 12"
with col3:
    if st.button("🔄 Convert 100km to miles", key="ex3", use_container_width=True):
        st.session_state.current_prompt = "convert 100 kilometers to miles"

st.divider()

# Input form
with st.form(key="query_form", clear_on_submit=True):
    # Use current prompt if set (from example buttons or previous input)
    default_value = st.session_state.get("current_prompt", "")
    
    prompt = st.text_area(
        "Your Question:",
        value=default_value,
        height=100,
        placeholder="Ask anything: search Wikipedia, calculate, or convert units...",
        key="prompt_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        submit_button = st.form_submit_button("🚀 Submit", use_container_width=True)
    with col2:
        # Show predicted tool
        if prompt:
            tool_type = detect_tool_type(prompt)
            if tool_type == "calculator":
                st.markdown('<span class="tool-badge calculator-badge">🔢 Calculator</span>', unsafe_allow_html=True)
            elif tool_type == "converter":
                st.markdown('<span class="tool-badge converter-badge">🔄 Converter</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="tool-badge wikipedia-badge">📚 Wikipedia</span>', unsafe_allow_html=True)

# Process the query
if submit_button and prompt:
    # Clear the current prompt from session state
    if "current_prompt" in st.session_state:
        del st.session_state.current_prompt
    
    with st.spinner("🤔 Processing your query..."):
        # Call API
        result = call_api(
            prompt=prompt,
            model=model_input if model_input else None,
            system=system_input if system_input else None
        )
        
        if result:
            # Add to history
            st.session_state.history.insert(0, {
                "timestamp": datetime.now(),
                "prompt": prompt,
                "response": result["output"],
                "model": model_input if model_input else "default",
                "tool": detect_tool_type(prompt)
            })
            
            st.success("✅ Response received!")

# Display current response
if st.session_state.history:
    st.header("📝 Latest Response")
    latest = st.session_state.history[0]
    
    # Tool badge
    tool_type = latest["tool"]
    if tool_type == "calculator":
        badge_class = "calculator-badge"
        icon = "🔢"
    elif tool_type == "converter":
        badge_class = "converter-badge"
        icon = "🔄"
    else:
        badge_class = "wikipedia-badge"
        icon = "📚"
    
    st.markdown(f'<span class="tool-badge {badge_class}">{icon} {tool_type.title()}</span>', unsafe_allow_html=True)
    
    # Response container
    with st.container():
        st.markdown(f"**Your Question:** _{latest['prompt']}_")
        st.divider()
        st.markdown(latest["response"])
        st.caption(f"⏰ {latest['timestamp'].strftime('%H:%M:%S')} | 🤖 Model: {latest['model']}")

# Display history
if len(st.session_state.history) > 1:
    st.divider()
    st.header("📜 History")
    
    with st.expander(f"View {len(st.session_state.history) - 1} previous queries"):
        for idx, item in enumerate(st.session_state.history[1:], 1):
            with st.container():
                st.markdown(f"**{idx}. {item['prompt']}**")
                st.markdown(f"_{item['response'][:200]}..._" if len(item['response']) > 200 else item['response'])
                st.caption(f"{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.divider()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🤖 Powered by LangChain & FastAPI | Built with ❤️ using Streamlit</p>
        <p style='font-size: 12px;'>
            <b>Capabilities:</b> Wikipedia Search 📚 | Calculator 🔢 | Unit Converter 🔄
        </p>
    </div>
    """, unsafe_allow_html=True)