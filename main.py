import sys
import enum

from monkey.interpreter import repl


class Option(enum.StrEnum):
    REPL = "repl"


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        opt = Option(arg)
    except ValueError:
        opt = None

    if opt:
        match opt:
            case Option.REPL:
                try:
                    repl.Scanner().start()
                except (KeyboardInterrupt, EOFError):
                    print("\nBye!")
                return
    else:
        print("Usage: python main.py [repl]")


if __name__ == "__main__":
    main()
