import sys

from interpreter import repl


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg:
        if arg == "repl":
            try:
                repl.Scanner().start()
            except (KeyboardInterrupt, EOFError):
                print("\nBye!")

            return

    print("Usage: python main.py [repl]")


if __name__ == "__main__":
    main()
