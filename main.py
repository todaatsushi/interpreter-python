import sys


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg:
        pass

    print("Usage: python main.py [repl]")


if __name__ == "__main__":
    main()
