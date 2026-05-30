#!/usr/bin/env python3

import re
import sys


def main(path):
    with open(path, encoding="utf-8") as f:
        contents = f.read()

    # Unnumbered subsections.
    contents = re.sub(r'\\subsection\{', r'\\subsection*{', contents)

    # longtable* is not a standard environment; normalize it.
    contents = contents.replace(r'\begin{longtable*}', r'\begin{longtable}')
    contents = contents.replace(r'\end{longtable*}', r'\end{longtable}')

    # Fix empty bold table header cells such as:
    #   \textbf{
    #
    #   } &
    contents = re.sub(r'\\textbf\{\s*\}\s*&', r' &', contents, flags=re.MULTILINE)

    # XeLaTeX/fontspec handles Unicode directly; these declarations are legacy
    # and can fail under the current toolchain.
    contents = re.sub(
        r'^\s*\\DeclareUnicodeCharacter\{[0-9A-Fa-f]+\}\{.*?\}\s*$',
        '',
        contents,
        flags=re.MULTILINE,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.tex>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
