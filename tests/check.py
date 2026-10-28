"""End-to-end check: the brutalized code must produce the same output as the original.

    python3 tests/check.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tree_sitter_language_pack import get_parser

HERE = Path(__file__).parent
FIX = HERE / "fixtures"
sys.path.insert(0, str(HERE.parent))
from brutalizr.engine import Brutalizer  # noqa: E402


def sh(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd} in {cwd}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def run_dir(d: Path) -> dict:
    out = {}
    out["python"] = sh("python3 pipeline.py", d / "py")
    out["javascript"] = sh("node cart.js", d / "js")
    tsdir = d / "ts"
    ts = next(tsdir.glob("*.ts")).name
    sh(f"tsc --strict --target es2020 --outDir build {ts}", tsdir)
    out["typescript"] = sh(f"node build/{ts[:-3]}.js", tsdir)
    php = [p.name for p in (d / "php").glob("*.php")]
    out["php"] = sh(f"php {php[0]}", d / "php")
    java = next((d / "java").glob("*.java"))
    sh(f"javac -d build {java.name}", d / "java")
    out["java"] = sh(f"java -cp build {java.stem}", d / "java")
    for f in d.rglob("*.cs"):
        tree = get_parser("csharp").parse(f.read_bytes())
        assert not tree.root_node.has_error, f"invalid C#: {f}"
    return out


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        orig = tmp / "orig"
        shutil.copytree(FIX, orig)
        expected = run_dir(orig)
        for lang in ("it", "en", "es", "fr", "de", "nap", "mix"):
            for seed in (1, 2, 3):
                dst = tmp / f"out-{lang}-{seed}"
                rep = Brutalizer(orig, lang=lang, seed=seed).run(dst)
                shutil.copytree(orig / "php" / "vendor", dst / "php" / "vendor")
                got = run_dir(dst)
                for k in expected:
                    if expected[k] != got[k]:
                        ok = False
                        print(f"FAIL {lang}/{seed} {k}:\n  expected: {expected[k]!r}\n  got: {got[k]!r}")
                # round trip with the inverted map
                back = tmp / f"back-{lang}-{seed}"
                inv = {f: {v: k for k, v in m.items()} for f, m in rep.mapping.items()}
                Brutalizer(dst, mapping=inv).run(back)
                shutil.copytree(orig / "php" / "vendor", back / "php" / "vendor")
                for f in orig.rglob("*"):
                    if f.is_file() and "build" not in f.parts:
                        b = back / f.relative_to(orig)
                        if not b.exists() or b.read_bytes() != f.read_bytes():
                            ok = False
                            print(f"FAIL round trip {lang}/{seed}: {f.relative_to(orig)}")
        print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
