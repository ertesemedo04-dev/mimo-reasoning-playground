"""CLI entry point for MiMo Reasoning Playground."""

import asyncio
import argparse
import os
import sys
from dotenv import load_dotenv

from .client import MiMoClient
from .challenges import CHALLENGES, get_challenges


def print_colored(text: str, color: str = "white"):
    """Print with ANSI colors."""
    colors = {
        "purple": "\033[95m",
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "dim": "\033[90m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    c = colors.get(color, "")
    r = colors["reset"]
    print(f"{c}{text}{r}")


async def stream_to_terminal(client: MiMoClient, prompt: str, system: str = ""):
    """Stream reasoning to terminal with colored output."""
    print()
    print_colored("━" * 60, "dim")
    print_colored("🧠 REASONING TRACE", "purple")
    print_colored("━" * 60, "dim")
    print()

    in_reasoning = True

    async for event in client.stream_reasoning(prompt, system=system):
        if event["type"] == "reasoning":
            print_colored(event["content"], "cyan", )
        elif event["type"] == "answer":
            if in_reasoning:
                in_reasoning = False
                print()
                print_colored("━" * 60, "dim")
                print_colored("💡 ANSWER", "green")
                print_colored("━" * 60, "dim")
                print()
            print(event["content"], end="", flush=True)
        elif event["type"] == "done":
            data = event["data"]
            print()
            print()
            print_colored("━" * 60, "dim")
            print_colored(
                f"📊 {data.elapsed_ms:.0f}ms | {data.tokens_used} tokens | "
                f"{len(data.reasoning_steps)} steps",
                "yellow",
            )
            print_colored("━" * 60, "dim")
            print()
        elif event["type"] == "error":
            print_colored(f"❌ {event['message']}", "red")
            return


def list_challenges():
    """Print available challenges."""
    print()
    print_colored("🎯 Available Challenges", "bold")
    print_colored("━" * 50, "dim")
    for c in CHALLENGES:
        diff_color = {
            "easy": "green", "medium": "yellow",
            "hard": "red", "extreme": "purple",
        }.get(c.difficulty, "white")
        print(f"  {c.id:12s} ", end="")
        print_colored(f"[{c.difficulty}]", diff_color)
        print(f"               {c.title} ({c.category})")
        print_colored(f"               {c.description}", "dim")
        print()


async def run_challenge_cmd(client: MiMoClient, challenge_id: str, mode: str = "default"):
    """Run a challenge from CLI."""
    challenge = next((c for c in CHALLENGES if c.id == challenge_id), None)
    if not challenge:
        print_colored(f"❌ Challenge '{challenge_id}' not found", "red")
        list_challenges()
        return

    print_colored(f"\n🎯 {challenge.title}", "bold")
    print_colored(f"   {challenge.category} — {challenge.difficulty}", "dim")
    print_colored(f"   {challenge.description}", "dim")

    system = ""
    if mode == "step":
        system = "Think step by step. Show your complete reasoning process."
    elif mode == "socratic":
        system = "Use the Socratic method. Ask yourself clarifying questions."
    elif mode == "adversarial":
        system = "Argue both FOR and AGAINST before concluding."

    await stream_to_terminal(client, challenge.prompt, system=system)


async def interactive_mode(client: MiMoClient):
    """Interactive REPL for custom prompts."""
    print_colored("\n🧠 MiMo Reasoning Playground — Interactive Mode", "bold")
    print_colored("Type your prompt and watch MiMo reason. 'quit' to exit.\n", "dim")

    while True:
        try:
            prompt = input("\033[96mYou> \033[0m").strip()
            if not prompt:
                continue
            if prompt.lower() in ("quit", "exit", "q"):
                print_colored("👋 Bye!", "dim")
                break
            await stream_to_terminal(client, prompt)
        except KeyboardInterrupt:
            print_colored("\n👋 Bye!", "dim")
            break


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="MiMo Reasoning Playground — Explore reasoning model capabilities",
    )
    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="List available challenges")

    # run
    run_p = sub.add_parser("run", help="Run a challenge")
    run_p.add_argument("challenge_id", help="Challenge ID (e.g., logic-001)")
    run_p.add_argument("--mode", choices=["default", "step", "socratic", "adversarial"],
                       default="default", help="Reasoning mode")

    # chat
    chat_p = sub.add_parser("chat", help="Interactive chat mode")
    chat_p.add_argument("--system", default="", help="System prompt")

    # ask
    ask_p = sub.add_parser("ask", help="Ask a single question")
    ask_p.add_argument("prompt", help="Your prompt")
    ask_p.add_argument("--mode", choices=["default", "step", "socratic", "adversarial"],
                       default="default", help="Reasoning mode")

    # web
    web_p = sub.add_parser("web", help="Launch web UI")
    web_p.add_argument("--port", type=int, default=8501)
    web_p.add_argument("--share", action="store_true")

    args = parser.parse_args()

    client = MiMoClient(
        api_base=os.getenv("MIMO_API_BASE", "https://api.xiaomi.com/v1"),
        api_key=os.getenv("MIMO_API_KEY", ""),
        model=os.getenv("MIMO_MODEL", "xmtp/mimo-v2.5-pro"),
    )

    if args.command == "list":
        list_challenges()
    elif args.command == "run":
        asyncio.run(run_challenge_cmd(client, args.challenge_id, args.mode))
    elif args.command == "chat":
        asyncio.run(interactive_mode(client))
    elif args.command == "ask":
        asyncio.run(stream_to_terminal(client, args.prompt))
    elif args.command == "web":
        from .app import build_ui
        app = build_ui()
        app.launch(
            server_name="0.0.0.0",
            server_port=args.port,
            share=args.share,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
