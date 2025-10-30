# agentic_processing.py
"""
Truly agentic tool processing where the LLM decides which tools to use.
Simple implementation without deprecated LangChain agent APIs.
"""
import logging
import json
from typing import Optional, Dict, Any
import warnings

# Disable SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests

# Patch requests to disable SSL verification
original_request = requests.Session.request
def patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return original_request(self, method, url, **kwargs)
requests.Session.request = patched_request

from llm_client import get_llm
from tools_langchain import get_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("agentic_processing")
log.setLevel(logging.INFO)

AGENTIC_SYSTEM_PROMPT = """You are an AI assistant with access to tools. When a user asks a question, you should:

1. Analyze what the user needs
2. Decide which tool(s) to use
3. Call the appropriate tool(s)
4. Provide a helpful response based on the tool results

Available tools:
- wikipedia_search: Search Wikipedia for information about topics, people, places, concepts
- calculator: Perform mathematical calculations (supports +, -, *, /, **, parentheses)
- unit_converter: Convert between units (format: "VALUE UNIT to UNIT", e.g., "100 km to miles")

To use a tool, respond with a JSON object like this:
{
  "tool": "tool_name",
  "input": "tool input"
}

If you need multiple tools, you can call them sequentially.

If you have enough information to answer directly without tools, just provide the answer.

Be helpful, concise, and accurate."""

def parse_llm_response(response: str) -> Dict[str, Any]:
    """
    Parse LLM response to check if it wants to use a tool.
    Returns: {"type": "tool_call" | "final_answer", "content": ...}
    """
    # Check if response contains a tool call
    try:
        # Look for JSON in the response
        if "{" in response and "}" in response:
            # Extract JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            tool_call = json.loads(json_str)
            
            if "tool" in tool_call and "input" in tool_call:
                return {
                    "type": "tool_call",
                    "tool": tool_call["tool"],
                    "input": tool_call["input"]
                }
    except:
        pass
    
    # If no tool call found, it's a final answer
    return {
        "type": "final_answer",
        "content": response
    }

def run_task(
    user_prompt: str,
    system_instructions: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    """
    Agentic processing pipeline where the LLM decides which tools to use.
    
    Simple ReAct-style loop:
    1. LLM analyzes query
    2. LLM decides if it needs a tool
    3. If yes, call the tool and feed result back to LLM
    4. LLM provides final answer
    
    Args:
        user_prompt: The user's natural language instruction
        system_instructions: Optional custom system instructions
        model: Optional model override
        
    Returns:
        The agent's response
    """
    
    print(f"\n{'='*60}")
    print(f"🤖 AGENTIC AI - Starting Task")
    print(f"{'='*60}")
    print(f"📝 User Query: '{user_prompt}'")
    print(f"{'='*60}\n")
    
    log.info(f"=== AGENTIC TASK ===")
    log.info(f"Query: '{user_prompt}'")
    
    try:
        # Get LLM instance
        llm = get_llm(
            system_instructions=system_instructions or AGENTIC_SYSTEM_PROMPT,
            model=model,
            temperature=0.2
        )
        
        # Get tools
        tools = get_tools()
        tool_map = {tool.name: tool for tool in tools}
        tool_names = list(tool_map.keys())
        
        print(f"🔧 Available Tools: {', '.join(tool_names)}")
        print(f"🧠 LLM will decide which tool(s) to use...\n")
        
        log.info(f"✅ Tools loaded: {tool_names}")
        
        # Agentic loop (max 3 iterations)
        conversation_history = []
        max_iterations = 3
        
        for iteration in range(max_iterations):
            print(f"\n{'─'*60}")
            print(f"🔄 Iteration {iteration + 1}/{max_iterations}")
            print(f"{'─'*60}\n")
            
            # Build the prompt with history
            if iteration == 0:
                # First iteration - just the user query
                prompt = f"User question: {user_prompt}\n\nWhat should I do?"
            else:
                # Subsequent iterations - include previous tool results
                prompt = f"User question: {user_prompt}\n\n"
                prompt += "Previous actions:\n"
                for entry in conversation_history:
                    prompt += f"- {entry}\n"
                prompt += "\nWhat should I do next? If you have enough information, provide the final answer."
            
            # Get LLM decision
            print(f"🧠 LLM Thinking...")
            messages = [
                {"role": "system", "content": system_instructions or AGENTIC_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response = llm.invoke(messages)
            llm_response = response.content if hasattr(response, 'content') else str(response)
            
            print(f"💭 LLM Response: {llm_response[:200]}...")
            log.info(f"LLM response: {llm_response[:200]}...")
            
            # Parse response
            parsed = parse_llm_response(llm_response)
            
            if parsed["type"] == "final_answer":
                # LLM provided final answer
                print(f"\n✅ Final Answer Ready")
                print(f"{'='*60}\n")
                log.info("✅ Task completed - final answer provided")
                return parsed["content"]
            
            elif parsed["type"] == "tool_call":
                # LLM wants to use a tool
                tool_name = parsed["tool"]
                tool_input = parsed["input"]
                
                print(f"\n🔧 Tool Call Detected:")
                print(f"   Tool: {tool_name}")
                print(f"   Input: {tool_input}")
                
                if tool_name not in tool_map:
                    error_msg = f"Unknown tool: {tool_name}"
                    print(f"   ❌ {error_msg}\n")
                    conversation_history.append(f"Tried to use {tool_name} but it doesn't exist")
                    continue
                
                # Execute the tool
                tool = tool_map[tool_name]
                try:
                    tool_result = tool.func(tool_input)
                    print(f"   ✅ Result: {tool_result[:200]}...\n")
                    conversation_history.append(f"Used {tool_name}('{tool_input}') → {tool_result[:100]}...")
                    log.info(f"Tool {tool_name} executed successfully")
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    print(f"   ❌ {error_msg}\n")
                    conversation_history.append(f"Tried {tool_name} but got error: {error_msg}")
                    log.error(f"Tool {tool_name} failed: {e}")
            
            else:
                # Unexpected response
                print(f"⚠️ Unexpected LLM response format\n")
                conversation_history.append("LLM response was unclear")
        
        # If we exhausted iterations, ask LLM for final answer
        print(f"\n{'='*60}")
        print(f"⏱️ Max iterations reached - requesting final answer")
        print(f"{'='*60}\n")
        
        final_prompt = f"User question: {user_prompt}\n\n"
        final_prompt += "Here's what we found:\n"
        for entry in conversation_history:
            final_prompt += f"- {entry}\n"
        final_prompt += "\nPlease provide a final answer to the user's question based on this information."
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Provide a clear, concise answer."},
            {"role": "user", "content": final_prompt}
        ]
        
        response = llm.invoke(messages)
        final_answer = response.content if hasattr(response, 'content') else str(response)
        
        print(f"✅ TASK COMPLETED\n")
        log.info("✅ Task completed after max iterations")
        
        return final_answer
        
    except Exception as e:
        error_msg = f"Error during agentic processing: {str(e)}"
        log.error(error_msg, exc_info=True)
        print(f"\n❌ ERROR: {error_msg}\n")
        
        return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your query."