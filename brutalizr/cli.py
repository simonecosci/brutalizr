"""brutalizr — makes a project's sources readable only by people with a strong stomach."""
from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path

from . import __version__
from .engine import DEFAULT_EXCLUDES, Brutalizer


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="brutalizr",
        description="Renames the variables, functions, constants, classes and methods of a project "
                    "(PHP, Python, JS, TS, Java, C#) with swear words. Strings and comments "
                    "stay intact; names from external libraries are left alone.",
    )
    p.add_argument("source", type=Path, help="root folder of the sources")
    p.add_argument("-o", "--output", type=Path,
                   help="destination folder (default: <source>-brutalized)")
    p.add_argument("--in-place", action="store_true",
                   help="modify the files in the source folder (DESTRUCTIVE)")
    p.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")
    p.add_argument("-l", "--lang", choices=["it", "en", "es", "fr", "de", "nap", "mix"], default="it",
                   help="swear word vocabulary (default: it)")
    p.add_argument("-s", "--seed", type=int, help="seed to always get the same names")
    p.add_argument("-k", "--keep", action="append", default=[],
                   help="names to leave alone (repeatable or comma separated)")
    p.add_argument("--keep-file", type=Path, help="file with one name to leave alone per line")
    p.add_argument("-x", "--exclude", action="append", default=[],
                   help="folders to exclude, in addition to: " + ", ".join(sorted(DEFAULT_EXCLUDES)))
    p.add_argument("--no-rename-files", action="store_true",
                   help="do not rename Java/PHP files named after their class")
    p.add_argument("--dump-map", type=Path, help="save the name->swear word map as JSON")
    p.add_argument("--use-map", type=Path, help="use an existing JSON map instead of generating one")
    p.add_argument("--reverse", action="store_true",
                   help="with --use-map: invert the map (restore the original names)")
    p.add_argument("-n", "--dry-run", action="store_true", help="show what would happen, without writing")
    p.add_argument("-v", "--verbose", action="store_true", help="print the whole map")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p.parse_args(argv)


def main(argv=None) -> int:
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)   # brutalizr ... | head
    a = parse_args(argv)
    src: Path = a.source
    if not src.is_dir():
        print(f"brutalizr: '{src}' is not a folder", file=sys.stderr)
        return 2

    keep = {k.strip() for item in a.keep for k in item.split(",") if k.strip()}
    if a.keep_file:
        keep |= {line.strip() for line in a.keep_file.read_text().splitlines()
                 if line.strip() and not line.startswith("#")}

    mapping = None
    if a.use_map:
        mapping = json.loads(a.use_map.read_text())
        if a.reverse:
            mapping = {fam: {v: k for k, v in m.items()} for fam, m in mapping.items()}

    if a.in_place:
        out = None
        if not a.yes and not a.dry_run:
            ans = input(f"Overwrite the sources in '{src}'? There is no going back "
                        f"(unless you use --dump-map). [y/N] ")
            if ans.strip().lower() not in ("y", "yes"):
                print("Aborted.")
                return 1
    else:
        out = a.output or src.resolve().with_name(src.resolve().name + "-brutalized")
        if out.exists() and any(out.iterdir()) and not a.dry_run:
            print(f"brutalizr: destination '{out}' exists and is not empty", file=sys.stderr)
            return 2

    b = Brutalizer(src, lang=a.lang, seed=a.seed, keep=keep, excludes=set(a.exclude),
                   mapping=mapping, rename_files=not a.no_rename_files)
    report = b.run(out, dry_run=a.dry_run)

    if not report.files:
        print("No PHP/Python/JS/TS/Java/C# sources found.")
        return 1

    if a.dump_map and not a.use_map:
        a.dump_map.write_text(json.dumps(report.mapping, indent=2, ensure_ascii=False))

    langs = ", ".join(f"{n} {k}" for k, n in sorted(report.files.items()))
    print(f"Files analyzed: {sum(report.files.values())} ({langs})")
    total = sum(len(m) for m in report.mapping.values())
    print(f"Names brutalized: {total} — occurrences replaced: {report.occurrences}")
    for fam, m in sorted(report.mapping.items()):
        items = list(m.items())
        shown = items if a.verbose else items[:8]
        print(f"[{fam}]")
        for orig, new in shown:
            print(f"  {orig:30} -> {new}")
        if len(items) > len(shown):
            print(f"  ... and {len(items) - len(shown)} more (use -v or --dump-map)")
    for old, new in report.renamed_files:
        print(f"  file: {old} -> {new}")
    if report.parse_errors:
        print(f"Warning: parse errors (partial result) in {len(report.parse_errors)} file(s):")
        for p in report.parse_errors[:10]:
            print(f"  {p}")
    if a.dry_run:
        print("Dry run: no files written.")
    else:
        what = "Original names restored" if a.reverse else "Offensive sources"
        print(f"Done. {what} in: {out or src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
