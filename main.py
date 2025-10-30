# main.py
import logging
from agentic_processing import run_task  # ✅ Using agentic version!

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("main")

def main():
    """
    Interactive CLI for the agentic AI system.
    Users can:
    - Enter a topic to search Wikipedia and get a summary
    - Provide a Wikipedia URL to summarize that page
    - Ask general questions
    """
    print("=" * 60)
    print("Welcome to Agentic AI - Wikipedia Search & Summarizer")
    print("=" * 60)
    print("\nExamples:")
    print("  - 'Tell me about quantum computing'")
    print("  - 'Summarize https://en.wikipedia.org/wiki/Artificial_intelligence'")
    print("  - 'Search for Machine Learning and summarize it'")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            user_input = input("\n🔹 Your prompt: ").strip()
            
            if not user_input:
                print("⚠️  Please enter a prompt.")
                continue
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break
            
            print("\n🤖 Processing your request...\n")
            
            # Call the task processing pipeline
            result = run_task(
                user_prompt=user_input,
                system_instructions=None,  # Use default from llm_client
                model=None  # Use default model
            )
            
            print(f"\n📝 Response:\n{result}")
            print("\n" + "-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            log.error(f"Error processing request: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
            print("Please try again with a different prompt.")

if __name__ == "__main__":
    main()