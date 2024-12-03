venv:
    source ./.venv/bin/activate

test match: venv
    uv run -m unittest discover -vk {{ match }}

tests: venv
    LOGLEVEL=CRITICAL uv run -m unittest discover -v

shell:
    uv run main.py repl
