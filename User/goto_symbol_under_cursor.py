import sublime
import sublime_plugin
import re


class GotoSymbolUnderCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        symbol = self.view.substr(self.view.word(self.view.sel()[0]))

        if not symbol:
            return

        results = window.lookup_symbol_in_index(symbol)

        if not results:
            return

        candidates = []


        for filename, _, (line, col) in results:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                text = lines[line].strip()
                print(repr(text), symbol)

                # typedef foo BAR;
                if re.search(
                    r"\btypedef\b.*\b" + re.escape(symbol) + r"\s*;",
                    text
                ):
                    candidates.append((filename, line, col, 100))
                    continue

                # struct/union/enum definitions:
                # struct String8 {
                # enum Foo {
                if re.search(
                    r"\b(struct|union|enum)\s+" + re.escape(symbol) + r"\b",
                    text
                ):
                    candidates.append((filename, line, col, 90))
                    continue

                # typedef struct { ... } Name;
                if re.search(
                    r"}\s*" + re.escape(symbol) + r"\s*;",
                    text
                ):
                    candidates.append((filename, line, col, 100))
                    continue

                # function definitions:
                # String8 foo(...)
                # foo(...)
                if re.search(
                    r"\b" + re.escape(symbol) + r"\s*\(",
                    text
                ):
                    candidates.append((filename, line, col, 80))
                    continue

                # fallback
                if re.search(r"\b" + re.escape(symbol) + r"\b", text):
                    candidates.append((filename, line, col, 1))

            except Exception:
                pass

        if not candidates:
            return

        # highest score first
        candidates.sort(key=lambda x: x[3], reverse=True)

        filename, line, col, _ = candidates[0]

        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        text = lines[line]

        match = re.search(r"\b" + re.escape(symbol) + r"\b", text)

        if match:
            col = match.start()
        else:
            col = 0

        window.open_file(
            f"{filename}:{line+1}:{col+1}",
            sublime.ENCODED_POSITION
        )

