# Contributing to brutalizr

Thanks for wanting to make code worse to read. Bug reports, new swear words, new
language rules and fixes are all welcome.

## Reporting a bug

The most useful bug report is a **minimal snippet that breaks after brutalizing**:
the original code, the command you ran (`-l`, `-s` included, so the names are
reproducible), and what went wrong (a runtime error, a different output, a library
member that got renamed…). Run `brutalizr <dir> -n -v` to see the full name map.

Before opening an issue, check the *Limitations* section of the README: dynamic
access by name (reflection, `getattr`, ORM fields, template files) is a known limit.

## Development setup

```bash
git clone https://github.com/simonecosci/brutalizr.git
cd brutalizr
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
python -m brutalizr tests/fixtures -n -v        # dry run on the sample projects
```

## Tests

```bash
python3 tests/check.py
```

The suite brutalizes every project in `tests/fixtures` with all vocabularies and
three seeds. It then checks two things:

- the brutalized program prints exactly what the original prints;
- inverting the map restores the sources byte for byte.

It needs `python3`, `node`, `tsc`, `php`, `javac` and `java` on PATH. If you can't install
them all, CI runs the full suite on every push and pull request.

When you fix a bug, extend the fixture of that language so the broken construct is
covered and its effect shows up in the program's output.

## Branches and pull requests

- Branch off `develop` and open pull requests against `develop`; `develop` is merged
  into `main` for releases.
- Keep pull requests focused, and make sure CI is green.

## Conventions

- **English only**: code, comments, docstrings, CLI messages and docs. The
  vocabularies are the only exception.
- Match the style of the surrounding code; there is no formatter or linter to lean on.
- Files use LF line endings (enforced by `.gitattributes`).

## Adding swear words

Vocabularies live in `brutalizr/words.py`.

- Entries must be lowercase ASCII (`[a-z_]`): they become identifiers, so no
  accents or `ñ`. A `_` splits an entry into separate words (`piss_poor`).
- Nouns carry a gender (`"m"`, `"f"`, and `"n"` for German). Adjectives are written in
  the masculine form and inflected by the vocabulary's `inflect` function (default:
  `-o` → `-a`; French and German have their own rules). When the rule gets a word
  wrong, write both forms as `masc/fem` (`damne/damnee`, `stuorto/storta`).
- No duplicates within a list.
- Keep it to generic profanity: no slurs targeting people for who they are.

A new vocabulary language is a new key in `VOCAB` (with `order`, `nouns`, `adjs` and,
if needed, `inflect`)
plus the `--lang` choices in `cli.py`.

## Adding or improving a programming language

Language rules are data in `brutalizr/languages.py`: one `LangSpec` per tree-sitter
grammar, covering:

- which node types are identifiers;
- which `(parent_type, field)` pairs start a declaration;
- member access shapes;
- class and function boundaries;
- names that must never be touched.

Prefer extending these tables over special-casing the engine. A new language also
needs a fixture in `tests/fixtures/<lang>/` and a line in `run_dir()` in
`tests/check.py` that runs it.

## License

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE).
