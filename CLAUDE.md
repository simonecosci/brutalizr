# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

brutalizr renames the identifiers of a whole project (PHP, Python, JS, TS/TSX, Java, C#) with swear words, keeping the program runnable. Strings, comments and anything coming from external libraries stay untouched.

## Conventions

- Everything in the repo is English: code, comments, docstrings, CLI messages, docs. The swear word vocabularies in `words.py` are the only non-English content.
- Files are kept with LF line endings (`.gitattributes`): the round-trip test compares bytes.
- Work on `develop`, merge into `main` through a PR.

## Commands

```bash
pip install -e .                                  # deps: tree-sitter, tree-sitter-language-pack (Python >= 3.10)
python -m brutalizr tests/fixtures -n -v -l mix   # dry run: print the full name map, write nothing
python3 tests/check.py                            # end-to-end test suite
docker build -t brutalizr . && docker run --rm -v "$PWD:/work" brutalizr <dir>   # container, ENTRYPOINT is the CLI
```

CI (`.github/workflows/ci.yml`) runs `tests/check.py` with the full toolchain, plus a Docker build and smoke test.

There is no linter or unit test framework. `tests/check.py` is the only test: it brutalizes `tests/fixtures` (one small program per language) with every vocabulary (`it`, `en`, `es`, `mix`) × seeds 1-3. It runs both the original and the brutalized program and requires identical stdout. It then applies the inverted map and requires the original sources back byte for byte. It needs `python3`, `node`, `tsc`, `php`, `javac` and `java` on PATH. C# is only syntax-checked with tree-sitter. It has no filter for a single language: to iterate on one language, run the CLI on that fixture folder with `-n -v`.

`tests/fixtures/php/vendor/stubs.php` stands in for an external library. `vendor` is in `DEFAULT_EXCLUDES`, so the test copies it back into each output dir by hand.

## Architecture

The work is split across three modules. `cli.py` is just argparse plus report printing.

**`engine.py`: `Brutalizer.run()`** does all its work on tree-sitter syntax trees (never regex on source text):
1. `load`: walks the root (skipping `DEFAULT_EXCLUDES` and `-x`), picks a `LangSpec` by extension, and parses every file. Local Python module names are recorded here.
2. `collect_namespaces`: collects PHP namespaces and Java packages, so imports from them count as local.
3. `collect_imports`: collects names bound by imports from *external* packages into `self.external`. Import statements themselves go into `no_touch` byte ranges.
4. `collect_decls`: walks each tree, carrying an "in declaration" flag driven by `spec.decl` / `spec.stop_fields`. Declared names are grouped by `family`. `_is_member_decl` separates class members (`member_decls`) from locals/globals.
5. `build_mapping`: one generated name per declared name per family. A `--use-map` mapping replaces this step.
6. `edits_for` / `apply`: replace every identifier occurrence whose name is mapped, unless it is protected. Protection comes from `is_protected`: keep lists, externals, dunders, builtin members that the project also declares, and PHP magic names. Occurrences are also skipped in member position when the name is never declared as a member, on members of foreign objects, on object keys passed to foreign calls, and on kwargs of external calls. Edits are applied back-to-front on bytes.
7. The output tree is written (non-source files are copied too). Java/PHP files named after their class are renamed. The report's map lists only names that were actually replaced.

The key idea is **name families**. Python, PHP, JS/TS/TSX (shared), Java and C# each have their own namespace. The same name always maps to the same replacement within a family, across every file, and never across families. There is no type analysis: matching is by name plus syntactic position.

**`languages.py`** holds one `LangSpec` per grammar and everything language-specific:
- which node types are identifiers;
- which `(parent_type, field)` pairs start a declaration;
- member-access node shapes;
- class-body and function-boundary node types, which decide member vs. local;
- keep lists of builtins and framework conventions (Laravel, Angular, Airflow…);
- builtin type members (`builtin_members`).

To support a new language or construct, extend these tables first and touch the engine only if a tree shape can't be expressed through them. `BY_EXT` maps file extensions to specs.

**`words.py`**:
- `VOCAB` holds the per-language nouns (with gender) and adjectives, plus word order (`noun-adj` for it/es, `adj-noun` for en). Feminine nouns turn adjectives ending in `-o` into `-a`.
- `NameForge.forge` keeps the original's style (`camel`/`Pascal`/`snake`/`UPPER`, leading and trailing `_`). Names that are all lowercase get the spec's `lower_default`. It never returns a name already in `used` (seeded with every existing identifier in the project). When collisions persist it makes phrases longer and, as a last resort, adds a numeric suffix.
- Vocabulary entries must be lowercase ASCII (`[a-z_]`), because they become identifiers. `_` splits a single entry into several words.

## Known limits (by design, see README)

There is no type analysis, so the following can break at runtime:
- access by name: reflection, `getattr`, `$obj->$var`, ORM/JSON fields;
- name-based framework conventions: Laravel factories, `Controller@method` strings, templates;
- a name the project declares that is also a member of a library object the engine can't recognize as external.
