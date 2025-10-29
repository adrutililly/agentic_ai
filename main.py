# main.py
import argparse
from processing import run_task

# Examples:
#   python main.py --prompt "Who won the India vs Pakistan cricket match yesterday?"
#   python main.py --prompt "What is dengue? Keep it brief."
#   python main.py --prompt "Summarize this page: https://en.wikipedia.org/wiki/LangChain"
#   python main.py --prompt "Convert 5 miles to km"
#   python main.py --interactive
# Optional:
#   --model "gpt-4o-mini"  --system "Be extra concise and show sources."

def main():
    ap = argparse.ArgumentParser(description="General-purpose Agentic AI (via LLM Gateway)")
    ap.add_argument("--prompt", type=str, help="Run a single natural-language task")
    ap.add_argument("--interactive", action="store_true", help="Start interactive REPL")
    ap.add_argument("--model", type=str, default=None, help="Override model for this run")
    ap.add_argument("--system", type=str, default=None, help="Override system instructions for this run")
    args = ap.parse_args()

    if args.prompt:
        print(run_task(args.prompt, system_instructions=args.system, model=args.model))
        return

    if args.interactive:
        print("Agent ready. Try:\n"
              "  - Who won El Clásico last night?\n"
              "  - What is migraine? Cite a source.\n"
              "  - Convert 72°F to °C\n"
              "  - Summarize https://blog.langchain.dev\n"
              "Type 'exit' to quit.\n")
        while True:
            try:
                user = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if user.lower() in {"exit", "quit"}:
                break
            try:
                print("\nAssistant:", run_task(user, system_instructions=args.system, model=args.model), "\n")
            except Exception as e:
                print("Error:", e)
        return

    ap.print_help()

if __name__ == "__main__":
    main()
