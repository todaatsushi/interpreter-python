def read_script(filename: str) -> str:
    script = ""
    with open(filename) as file:
        for line in file.readlines():
            script = f"{script}\n{line.strip('\n')}"
    script = script.strip()
    return script
