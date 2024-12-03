venv:
    source ./.venv/bin/activate

test path: venv
    uv run -m unittest {{ path }} -v

tests: venv
    uv run -m unittest discover -v

shell:
    uv run main.py repl
