import sys
import enum

from monkey.interpreter import interface


class Option(enum.StrEnum):
    REPL = "repl"
    RUN = "run"


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
                    interface.Repl().start()
                except (KeyboardInterrupt, EOFError):
                    print("\nBye!")
                return
    else:
        print("Usage: python main.py [repl]")


if __name__ == "__main__":
    main()
