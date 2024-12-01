from interpreter import lexers


class Scanner:
    PROMPT = ">>>> "

    def start(self) -> None:
        while True:
            line = input(self.PROMPT)
            parsed = line.strip().split(self.PROMPT)[0].strip()
            lexer = lexers.Lexer.new(parsed)

            while (token := lexer.next_token()) and token.value:
                print(token)
