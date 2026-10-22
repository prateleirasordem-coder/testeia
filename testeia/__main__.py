import argparse
import os
import sys
from .plugin import AIPlugin, DemoProvider, RemoteProvider


def main():
    parser = argparse.ArgumentParser(description="Testeia: núcleo de plugin de IA")
    parser.add_argument("prompt", help="Texto enviado ao provedor")
    parser.add_argument("--provider", choices=["demo", "remote"], default="demo")
    args = parser.parse_args()
    try:
        provider = DemoProvider() if args.provider == "demo" else RemoteProvider(
            os.getenv("TESTEIA_ENDPOINT", ""), os.getenv("TESTEIA_MODEL", ""),
            os.getenv("TESTEIA_API_KEY", ""))
        print(AIPlugin(provider).run(args.prompt))
    except (ValueError, RuntimeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
