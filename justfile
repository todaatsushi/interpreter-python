venv:
    source ./.venv/bin/activate

test match: venv
    uv run -m unittest discover -vk {{ match }}

tests: venv
    LOGLEVEL=CRITICAL uv run -m unittest discover -v

shell vm_or_interpreter: venv
    uv run main.py repl {{ vm_or_interpreter }}
