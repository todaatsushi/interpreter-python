venv:
    source ./.venv/bin/activate

test path: venv
    uv run -m unittest {{ path }}

shell:
    uv run main.py repl
