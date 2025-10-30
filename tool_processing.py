# tool_processing.py
import logging
import re
import urllib.parse
from typing import Optional
import ssl
import warnings
import wikipedia
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from llm_client import get_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("tool_processing")
log.setLevel(logging.INFO)

# Disable SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch requests to disable SSL verification globally
original_request = requests.Session.request

def patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return original_request(self, method, url, **kwargs)

requests.Session.request = patched_request

def extract_wikipedia_title(text: str) -> Optional[str]:
    """
    Extract Wikipedia page title from a URL if present in the text.
    Returns None if no Wikipedia URL is found.
    """
    # Look for Wikipedia URLs
    wiki_pattern = r'https?://[a-z]*\.?wikipedia\.org/wiki/([^/\s]+)'
    match = re.search(wiki_pattern, text)
    
    if match:
        title = match.group(1)
        # Replace underscores with spaces and decode URL encoding
        title = urllib.parse.unquote(title.replace("_", " "))
        log.info(f"Extracted Wikipedia title: {title}")
        return title
    return None

def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia and return summary information using the wikipedia library directly.
    """
    try:
        # Clean up the query thoroughly
        clean_query = query.strip()
        # Remove punctuation
        clean_query = clean_query.rstrip('?!.,;:').strip()
        # Remove extra spaces
        clean_query = ' '.join(clean_query.split())
        
        log.info(f"Original query: '{query}'")
        log.info(f"Cleaned query: '{clean_query}'")
        
        # Print for debugging
        print(f"WIKIPEDIA SEARCH:")
        print(f"  Original: '{query}'")
        print(f"  Cleaned: '{clean_query}'\n")
        
        # Try to get the page directly WITHOUT auto_suggest first
        try:
            log.info(f"Attempting to get Wikipedia page for: '{clean_query}'")
            
            # First try: Direct page lookup without auto-suggest
            try:
                page = wikipedia.page(clean_query, auto_suggest=False)
                log.info(f"SUCCESS (direct) - Got page: '{page.title}' (URL: {page.url})")
            except:
                # Second try: With auto-suggest
                log.info(f"Direct lookup failed, trying with auto_suggest...")
                page = wikipedia.page(clean_query, auto_suggest=True)
                log.info(f"SUCCESS (auto-suggest) - Got page: '{page.title}' (URL: {page.url})")
            
            # Print result
            print(f"WIKIPEDIA RESULT:")
            print(f"  Searched for: '{clean_query}'")
            print(f"  Got page: '{page.title}'")
            print(f"  URL: {page.url}\n")
            
            content = f"Title: {page.title}\n\n"
            content += f"Summary: {page.summary}\n\n"
            content += f"URL: {page.url}"
            log.info(f"Successfully retrieved Wikipedia page: {page.title}")
            return content
        except wikipedia.DisambiguationError as e:
            # Multiple options available, use the first one
            log.info(f"Disambiguation found for '{clean_query}', options: {e.options[:5]}")
            log.info(f"Using first option: {e.options[0]}")
            page = wikipedia.page(e.options[0])
            log.info(f"Got disambiguation page: '{page.title}'")
            content = f"Title: {page.title}\n\n"
            content += f"Summary: {page.summary}\n\n"
            content += f"URL: {page.url}"
            return content
        except wikipedia.PageError:
            # Page not found, try searching
            log.info(f"Page not found directly for '{clean_query}', trying search...")
            search_results = wikipedia.search(clean_query, results=3)
            log.info(f"Search results: {search_results}")
            
            if not search_results:
                return f"No Wikipedia pages found for '{clean_query}'"
            
            # Get the first search result
            log.info(f"Using first search result: '{search_results[0]}'")
            page = wikipedia.page(search_results[0])
            log.info(f"Got search result page: '{page.title}'")
            content = f"Title: {page.title}\n\n"
            content += f"Summary: {page.summary}\n\n"
            content += f"URL: {page.url}"
            log.info(f"Found via search: {page.title}")
            return content
            
    except Exception as e:
        log.error(f"Wikipedia search error: {e}", exc_info=True)
        return f"Error searching Wikipedia: {str(e)}"

def run_task(
    user_prompt: str,
    system_instructions: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    """
    Main processing pipeline that:
    1. Checks if user provided a Wikipedia URL and extracts the title
    2. Searches Wikipedia for the topic
    3. Uses LLM to summarize the information
    
    Args:
        user_prompt: The user's natural language instruction
        system_instructions: Optional custom system instructions
        model: Optional model override
        
    Returns:
        The LLM's summarized response
    """
    log.info(f"=== NEW TASK ===")
    log.info(f"Raw prompt received: '{user_prompt}'")
    log.info(f"Prompt type: {type(user_prompt)}")
    log.info(f"Prompt repr: {repr(user_prompt)}")
    
    # Also print to stdout for debugging
    print(f"\n{'='*60}")
    print(f"NEW TASK - Raw prompt: '{user_prompt}'")
    print(f"{'='*60}\n")
    
    # Check if there's a Wikipedia URL in the prompt
    wiki_title = extract_wikipedia_title(user_prompt)
    
    # Determine what to search for
    if wiki_title:
        # User provided a URL, search for that specific title
        search_query = wiki_title
        context = f"User provided Wikipedia URL. Searching for: {wiki_title}"
    else:
        # Extract topic from natural language prompt
        search_query = user_prompt
        # Remove common phrases (case-insensitive)
        search_lower = search_query.lower()
        for phrase in ["tell me about", "search for", "summarize", "what is", "who is", "explain", "wikipedia page about", "information about", "give me information on"]:
            if phrase in search_lower:
                # Find the position and remove it
                idx = search_lower.find(phrase)
                search_query = search_query[:idx] + search_query[idx + len(phrase):]
                break
        
        # Clean up the query
        search_query = search_query.strip().rstrip('?!.,;:').strip()
        search_query = ' '.join(search_query.split())  # Remove extra whitespace
        
        context = f"Searching Wikipedia for: {search_query}"
    
    log.info(context)
    
    # Print what we're about to search
    print(f"EXTRACTED SEARCH QUERY: '{search_query}'\n")
    
    # Search Wikipedia
    wiki_content = search_wikipedia(search_query)
    
    # Check if search failed
    if "Error searching Wikipedia" in wiki_content or "No Wikipedia pages found" in wiki_content:
        return wiki_content
    
    # Get LLM instance
    try:
        llm = get_llm(
            system_instructions=system_instructions,
            model=model,
            temperature=0.2
        )
        
        # Create prompt for LLM to summarize
        summarization_prompt = f"""Based on the following Wikipedia content, provide a clear and concise summary that answers the user's question.

Wikipedia Content:
{wiki_content}

User's Request: {user_prompt}

Please provide a helpful, well-structured summary. Keep it informative but concise. Mention that this information is from Wikipedia."""
        
        # Use LLM to generate summary
        messages = [
            llm._system_message if hasattr(llm, '_system_message') else None,
            {"role": "user", "content": summarization_prompt}
        ]
        messages = [m for m in messages if m is not None]
        
        response = llm.invoke(messages)
        output = response.content if hasattr(response, 'content') else str(response)
        
        log.info("Task completed successfully")
        return output
        
    except Exception as e:
        log.error(f"Error during LLM processing: {e}", exc_info=True)
        # Fallback: return raw Wikipedia content if LLM fails
        return f"Here's the Wikipedia content (LLM summarization unavailable):\n\n{wiki_content}"