import asyncio
import argparse
from melodie_relay.gateway import run


async def chat_command(args):
    prompt = input("Prompt: ")
    result = await run(prompt)
    print(result)


async def run_command(args):
    print(f"Running task with prompt: {args.prompt}")


async def test_command(args):
    print("Running tests...")


async def models_command(args):
    from melodie_kimini.models_catalog import get_all_model_ids, get_models_by_tier, get_tiers
    all_models = get_all_model_ids()
    print(f"\nKIMINI Models ({len(all_models)} total)\n")
    for tier in get_tiers():
        models = get_models_by_tier(tier)
        print(f"  [{tier.upper()}]")
        for mid in sorted(models.keys()):
            m = models[mid]
            print(f"    {mid:<30} ctx={m['context']:<10,} v{m['version']}")
        print()


async def status_command(args):
    from melodie_kimini.models_catalog import get_all_model_ids
    all_models = get_all_model_ids()
    print(f"Kimini Platform: {len(all_models)} models | Unlimited Tokens")


def main():
    parser = argparse.ArgumentParser(description="Kimini CLI Relay Service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("chat", help="Start a chat session")

    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("prompt", help="The prompt to run")

    subparsers.add_parser("test", help="Run tests")
    subparsers.add_parser("models", help="List all 56 Kimini models")
    subparsers.add_parser("status", help="Check platform status")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    if args.command == "chat":
        loop.run_until_complete(chat_command(args))
    elif args.command == "run":
        loop.run_until_complete(run_command(args))
    elif args.command == "test":
        loop.run_until_complete(test_command(args))
    elif args.command == "models":
        loop.run_until_complete(models_command(args))
    elif args.command == "status":
        loop.run_until_complete(status_command(args))


if __name__ == "__main__":
    main()
