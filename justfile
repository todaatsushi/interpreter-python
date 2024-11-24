venv:
    source ./.venv/bin/activate

test: venv
    uv run test.py
