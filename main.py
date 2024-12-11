import sys
import enum

from monkey.interpreter import interface


class Option(enum.StrEnum):
    REPL = "repl"
    RUN = "run"


def main() -> None:
    func = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        opt = Option(func)
    except ValueError:
        opt = None

    match opt:
        case Option.REPL:
            if not len(sys.argv) == 3:
                print("Usage: python main.py [repl] <interpreter|vm>")
                return

            run_type = sys.argv[2]
        case Option.RUN:
            if not len(sys.argv) == 4:
                print("Usage: python main.py run [filename] <interpreter|vm>")
                return

            run_type = sys.argv[3]
        case None:
            run_type = None

    if opt:
        assert run_type
        try:
            rt = interface.RunType(run_type)
        except ValueError:
            print(run_type)
            print(
                "Usage: python main.py [repl <interpreter|vm>] | [run path <interpreter|vm>]"
            )
            return

        match opt:
            case Option.REPL:
                try:
                    interface.Repl().start(rt)
                except (KeyboardInterrupt, EOFError):
                    print("\nBye!")
                return
            case Option.RUN:
                if len(sys.argv) < 3:
                    print("Usage: python main.py run [filename] <interpreter|vm>")
                    return
                file = sys.argv[2]
                interface.Script().eval(file, rt)
    else:
        print("Usage: python main.py [repl] <interpreter|vm>")


if __name__ == "__main__":
    main()
