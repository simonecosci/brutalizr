"""Engine: two passes over the whole project.

1. collect the names *declared* in the project (classes, functions, methods, variables,
   constants, parameters, properties) and the ones imported from external libraries;
2. replace every occurrence of the declared names with the same vulgar name in
   every file, so the code stays consistent (and, as far as possible, runnable).
"""
from __future__ import annotations

import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from tree_sitter_language_pack import get_parser

from .languages import BY_EXT, LangSpec
from .words import NameForge

DEFAULT_EXCLUDES = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "__pycache__", ".venv", "venv",
    "env", "dist", "build", "bin", "obj", "target", ".idea", ".vscode", ".angular",
    "storage", "bootstrap/cache", ".mypy_cache", ".pytest_cache", ".tox", "coverage",
}

_DUNDER = re.compile(r"^__\w+__$")
_HAS_LETTER = re.compile(r"[A-Za-z]")


@dataclass
class SourceFile:
    path: Path            # relative to the root
    spec: LangSpec
    src: bytes
    tree: object = None


@dataclass
class Report:
    files: Counter = field(default_factory=Counter)
    occurrences: int = 0
    renamed_files: list = field(default_factory=list)
    parse_errors: list = field(default_factory=list)
    mapping: dict = field(default_factory=dict)


def _core(node, spec: LangSpec) -> tuple[str, int]:
    """Identifier text without prefixes (#private) and the prefix offset."""
    text = node.text.decode("utf-8", "replace")
    if node.type == "private_property_identifier" and text.startswith("#"):
        return text[1:], 1
    return text, 0


def _root_ident(node) -> str | None:
    """Leftmost identifier of a chain a.b.c / $a->b / A::b."""
    while node is not None:
        if node.type in ("identifier", "name", "type_identifier"):
            return node.text.decode()
        if node.type == "variable_name":
            n = node.named_children[0] if node.named_children else None
            return n.text.decode() if n else None
        if node.type in ("this", "self"):
            return node.type
        node = node.named_children[0] if node.named_children else None
    return None


class Brutalizer:
    def __init__(self, root: Path, lang: str = "it", seed: int | None = None,
                 keep: set[str] | None = None, excludes: set[str] | None = None,
                 mapping: dict[str, str] | None = None, rename_files: bool = True):
        self.root = root.resolve()
        self.forge = NameForge(lang, seed)
        self.user_keep = set(keep or ())
        self.excludes = DEFAULT_EXCLUDES | set(excludes or ())
        self.fixed_mapping = mapping
        self.rename_files = rename_files
        self.files: list[SourceFile] = []
        self.declared: dict[str, set[str]] = defaultdict(set)
        self.member_decls: dict[str, set[str]] = defaultdict(set)
        self.php_functions: set[str] = set()
        self.external: set[str] = set()      # names imported from external libraries
        self.all_idents: set[str] = set()
        self.no_touch: dict[Path, list[tuple[int, int]]] = defaultdict(list)
        self.local_py_modules: set[str] = set()
        self.local_namespaces: set[str] = set()   # PHP namespace / Java package
        self.class_decls: dict[Path, set[str]] = defaultdict(set)
        self.mapping: dict[str, dict[str, str]] = {}
        self.used_names: dict[str, set[str]] = defaultdict(set)

    # ------------------------------------------------------------------ scan
    def iter_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            rel_dir = Path(dirpath).relative_to(self.root)
            dirnames[:] = sorted(
                d for d in dirnames
                if d not in self.excludes and str(rel_dir / d) not in self.excludes)
            for fn in sorted(filenames):
                yield rel_dir / fn

    def load(self):
        for rel in self.iter_files():
            spec = BY_EXT.get(rel.suffix.lower())
            if not spec:
                continue
            if spec.name == "python":
                self.local_py_modules.add(rel.stem)
                self.local_py_modules.update(rel.parts[:-1])
            src = (self.root / rel).read_bytes()
            sf = SourceFile(rel, spec, src)
            sf.tree = get_parser(spec.name).parse(src)
            self.files.append(sf)

    # ---------------------------------------------------- pass 0: namespaces
    def collect_namespaces(self):
        for sf in self.files:
            for node in self._iter(sf.tree.root_node):
                if node.type == "namespace_definition":         # PHP
                    n = node.child_by_field_name("name")
                    if n:
                        self.local_namespaces.add(n.text.decode().strip("\\"))
                elif node.type == "package_declaration":         # Java
                    for c in node.named_children:
                        if c.type in ("scoped_identifier", "identifier"):
                            self.local_namespaces.add(c.text.decode())

    def _is_local_ns(self, qualified: str) -> bool:
        q = qualified.strip("\\").replace("\\", ".")
        for ns in self.local_namespaces:
            n = ns.replace("\\", ".")
            top = n.split(".")[0]
            if q == n or q.startswith(n + ".") or q.split(".")[0] == top:
                return True
        return False

    @staticmethod
    def _iter(node):
        stack = [node]
        while stack:
            n = stack.pop()
            yield n
            stack.extend(reversed(n.children))

    # ------------------------------------------- pass 1: external imports
    def collect_imports(self, sf: SourceFile):
        lang = sf.spec.name
        for node in self._iter(sf.tree.root_node):
            t = node.type
            if lang == "python" and t in ("import_statement", "import_from_statement"):
                external = True
                if t == "import_from_statement":
                    mod = node.child_by_field_name("module_name")
                    if mod is not None and (mod.type == "relative_import" or
                                            mod.text.decode().split(".")[0] in self.local_py_modules):
                        external = False
                else:
                    first = node.named_children[0] if node.named_children else None
                    if first is not None and first.text.decode().split(".")[0].split(" ")[0] in self.local_py_modules:
                        external = False
                if external:
                    self._protect_bound_names(sf, node, "python")
                else:
                    # module names map to files: leave them alone
                    mods = [node.child_by_field_name("module_name")] if t == "import_from_statement" \
                        else [c for c in node.named_children if c.type == "dotted_name"] + \
                             [c.child_by_field_name("name") for c in node.named_children
                              if c.type == "aliased_import"]
                    for m in mods:
                        if m is not None:
                            self.no_touch[sf.path].append((m.start_byte, m.end_byte))
            elif lang in ("javascript", "typescript", "tsx") and t in ("import_statement", "export_statement"):
                srcn = node.child_by_field_name("source")
                if srcn is not None:
                    s = srcn.text.decode().strip("'\"`")
                    if not s.startswith((".", "/")):
                        self._protect_bound_names(sf, node, "js")
            elif lang in ("javascript", "typescript", "tsx") and t == "call_expression":
                fn = node.child_by_field_name("function")
                args = node.child_by_field_name("arguments")
                if fn is not None and fn.text == b"require" and args is not None and args.named_children:
                    s = args.named_children[0].text.decode().strip("'\"`")
                    if not s.startswith((".", "/")) and node.parent and node.parent.type == "variable_declarator":
                        nm = node.parent.child_by_field_name("name")
                        for c in self._iter(nm):
                            if c.type in sf.spec.ident_types:
                                self.external.add(c.text.decode())
            elif lang == "java" and t in ("import_declaration", "package_declaration"):
                if t == "import_declaration" and not self._is_local_ns(
                        node.text.decode().replace("import", "").replace("static", "").strip(" ;")):
                    ids = [c for c in self._iter(node) if c.type == "identifier"]
                    if ids:
                        self.external.add(ids[-1].text.decode())
                    self.no_touch[sf.path].append((node.start_byte, node.end_byte))
                elif t == "package_declaration":
                    self.no_touch[sf.path].append((node.start_byte, node.end_byte))
            elif lang == "csharp" and t in ("using_directive", "file_scoped_namespace_declaration"):
                self.no_touch[sf.path].append((node.start_byte, node.end_byte))
            elif lang == "csharp" and t == "namespace_declaration":
                n = node.child_by_field_name("name")
                if n is not None:
                    self.no_touch[sf.path].append((n.start_byte, n.end_byte))
            elif lang == "php" and t == "namespace_definition":
                n = node.child_by_field_name("name")
                if n is not None:
                    self.no_touch[sf.path].append((n.start_byte, n.end_byte))
            elif lang == "php" and t == "namespace_use_clause":
                q = node.named_children[0] if node.named_children else None
                if q is not None and not self._is_local_ns(q.text.decode()):
                    self._protect_bound_names(sf, node, "php")

    def _protect_bound_names(self, sf, node, kind):
        """Protect only the names the import makes visible in the file (the alias, if any),
        and mark the import statement as untouchable."""
        bound = []
        if kind == "php":
            alias = node.child_by_field_name("alias")
            if alias is not None:
                bound.append(alias)
            else:
                names = [c for c in self._iter(node) if c.type == "name"]
                bound.extend(names[-1:])
        elif kind == "python":
            for i, c in enumerate(node.children):
                f = node.field_name_for_child(i)
                if c.type == "aliased_import":
                    bound.append(c.child_by_field_name("alias"))
                elif c.type == "dotted_name" and f == "name":
                    ids = [x for x in c.named_children if x.type == "identifier"]
                    if node.type == "import_statement":
                        bound.extend(ids[:1])
                    else:
                        bound.extend(ids[-1:])
        elif kind == "js":
            for c in self._iter(node):
                if c.type == "import_specifier" or c.type == "export_specifier":
                    bound.append(c.child_by_field_name("alias") or c.child_by_field_name("name"))
                elif c.type in ("import_clause", "namespace_import"):
                    bound.extend(x for x in c.named_children if x.type == "identifier")
        for b in bound:
            if b is not None:
                self.external.add(b.text.decode())
        self.no_touch[sf.path].append((node.start_byte, node.end_byte))

    # --------------------------------------------- pass 1: declarations
    def _is_member_decl(self, ident, spec: LangSpec) -> bool:
        """True if the declaration is a class member (method, field, property,
        class constant, enum value) rather than a local/global variable."""
        p = ident.parent
        if p is None:
            return False
        if p.type == "variable_name":              # PHP: $name
            p = p.parent
        if p.type in ("property_promotion_parameter",):
            return True
        if p.type in ("required_parameter", "optional_parameter") and any(
                c.type == "accessibility_modifier" or c.type == "readonly" for c in p.children):
            return True
        if spec.member and p.type in {m[0] for m in spec.member}:   # self.x = / this.x =
            return True
        n = p.parent
        while n is not None:
            if n.type in spec.func_nodes:
                return False
            if n.type in spec.class_bodies:
                return True
            n = n.parent
        # in Python module-level names are module attributes (mod.name)
        return spec.name == "python"

    def collect_decls(self, sf: SourceFile):
        spec = sf.spec
        fam = spec.family
        member_types = {m[0]: m for m in spec.member}

        def declare(node):
            name, _ = _core(node, spec)
            self.declared[fam].add(name)
            if self._is_member_decl(node, spec):
                self.member_decls[fam].add(name)
            if spec.name == "php" and node.parent is not None and node.parent.type == "function_definition":
                self.php_functions.add(name)
            if node.parent is not None and node.parent.type.endswith(
                    ("class_declaration", "interface_declaration", "enum_declaration",
                     "trait_declaration", "record_declaration")):
                self.class_decls[sf.path].add(name)

        stack = [(sf.tree.root_node, False)]
        while stack:
            node, in_decl = stack.pop()
            if node.type in spec.ident_types:
                self.all_idents.add(_core(node, spec)[0])
                if in_decl:
                    declare(node)
            if spec.name == "php" and node.type == "variable_name" and node.named_children:
                declare(node.named_children[0])
            mt = member_types.get(node.type)
            children = []
            for i, child in enumerate(node.children):
                f = node.field_name_for_child(i)
                d = in_decl
                if (node.type, f) in spec.decl or (node.type, "*") in spec.decl:
                    d = True
                if f in spec.stop_fields:
                    d = False
                if mt and in_decl:
                    if f == mt[1]:
                        d = False
                    elif f == mt[2]:
                        obj = node.child_by_field_name(mt[1])
                        d = obj is not None and _root_ident(obj) in spec.self_names
                children.append((child, d))
            stack.extend(reversed(children))

    # ------------------------------------------------------------ mapping
    def is_protected(self, name: str, spec: LangSpec) -> bool:
        return (name in self.user_keep or name in spec.keep or name in self.external
                or (name in spec.builtin_members and name in self.member_decls.get(spec.family, ()))
                or bool(_DUNDER.match(name)) or not _HAS_LETTER.search(name)
                or name == "_" or (spec.name == "php" and self._php_magic(name)))

    @staticmethod
    def _php_magic(name: str) -> bool:
        # Eloquent scopes (scopeActive -> ->active()), accessors/mutators, magic __x
        return (name.startswith("__") or re.match(r"^scope[A-Z]", name) is not None
                or re.match(r"^(get|set)[A-Z]\w*Attribute$", name) is not None)

    def build_mapping(self):
        if self.fixed_mapping is not None:
            self.mapping = {fam: dict(m) for fam, m in self.fixed_mapping.items()}
            return
        self.forge.used |= self.all_idents
        styles = {sf.spec.family: sf.spec.lower_default for sf in self.files}
        for fam in sorted(self.declared):
            self.mapping[fam] = {name: self.forge.forge(name, styles[fam])
                                 for name in sorted(self.declared[fam])}

    # ---------------------------------------------------- pass 2: rename
    def _in_member_position(self, node, spec: LangSpec) -> bool:
        parent = node.parent
        if parent is None:
            return False
        for typ, obj_f, mem_f in spec.member:
            if parent.type == typ and parent.child_by_field_name(mem_f) == node:
                return True
        if node.type in spec.member_ident_types:
            return True
        if spec.name == "php" and parent.type == "class_constant_access_expression":
            return parent.named_children and parent.named_children[-1] == node
        return False

    def _is_foreign_root(self, root: str | None, spec: LangSpec) -> bool:
        if root is None or root in spec.self_names:
            return False
        return root in self.external or (root in spec.keep and root not in
                                          self.declared.get(spec.family, ()))

    def _key_of_foreign_call_arg(self, node, spec: LangSpec) -> bool:
        """{key: ...} passed straight to fetch(), new Request(), lib.method()..."""
        p = node.parent
        if p is not None and p.type == "pair" and p.child_by_field_name("key") == node:
            obj = p.parent
        elif node.type == "shorthand_property_identifier":
            obj = p
        else:
            return False
        if obj is None or obj.type != "object" or obj.parent is None or obj.parent.type != "arguments":
            return False
        call = obj.parent.parent
        if call is None:
            return False
        fn = call.child_by_field_name("function") or call.child_by_field_name("constructor")
        return fn is not None and self._is_foreign_root(_root_ident(fn), spec)

    def edits_for(self, sf: SourceFile):
        spec = sf.spec
        fam = spec.family
        mapping = self.mapping.get(fam, {})
        members = self.member_decls.get(fam, set())
        ranges = self.no_touch.get(sf.path, [])
        member_types = {m[0]: m for m in spec.member}
        edits = []
        for node in self._iter(sf.tree.root_node):
            if node.type not in spec.ident_types:
                continue
            if any(a <= node.start_byte and node.end_byte <= b for a, b in ranges):
                continue
            name, off = _core(node, spec)
            new = mapping.get(name)
            if new is None or self.is_protected(name, spec):
                continue
            parent = node.parent
            if parent is not None:
                if parent.type == "namespace_name":
                    continue
                if self.fixed_mapping is None and self._in_member_position(node, spec) \
                        and name not in members:
                    continue
                mt = member_types.get(parent.type)
                if mt and parent.child_by_field_name(mt[2]) == node:
                    obj = parent.child_by_field_name(mt[1])
                    if obj is not None and self._is_foreign_root(_root_ident(obj), spec):
                        continue
                if spec.family == "js" and self._key_of_foreign_call_arg(node, spec):
                    continue
                if (spec.name == "php" and parent.type == "function_call_expression"
                        and name not in self.php_functions and self.fixed_mapping is None):
                    continue
                if (spec.name == "python" and parent.type == "keyword_argument"
                        and parent.child_by_field_name("name") == node):
                    call = parent.parent.parent if parent.parent else None
                    if call is not None and call.type == "call":
                        fn = call.child_by_field_name("function")
                        if fn is not None and _root_ident(fn) in self.external:
                            continue
            self.used_names[fam].add(name)
            edits.append((node.start_byte + off, node.end_byte, new.encode()))
        return edits

    @staticmethod
    def apply(src: bytes, edits) -> bytes:
        out = bytearray(src)
        for start, end, new in sorted(edits, reverse=True):
            out[start:end] = new
        return bytes(out)

    # -------------------------------------------------------------- run
    def run(self, out_root: Path | None, dry_run: bool = False) -> Report:
        report = Report()
        self.load()
        self.collect_namespaces()
        for sf in self.files:
            if sf.tree.root_node.has_error:
                report.parse_errors.append(str(sf.path))
            self.collect_imports(sf)
        for sf in self.files:
            self.collect_decls(sf)
        self.build_mapping()
        processed = {}
        for sf in self.files:
            edits = self.edits_for(sf)
            report.occurrences += len(edits)
            report.files[sf.spec.name] += 1
            processed[sf.path] = (self.apply(sf.src, edits), sf)
        # only names actually replaced go into the final map
        report.mapping = {fam: {k: v for k, v in m.items() if k in self.used_names[fam]}
                          for fam, m in self.mapping.items() if self.used_names[fam]}

        if dry_run:
            return report

        in_place = out_root is None or out_root.resolve() == self.root
        dest_root = self.root if in_place else out_root.resolve()

        if not in_place:
            for rel in self.iter_files():
                if rel not in processed:
                    dst = dest_root / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes((self.root / rel).read_bytes())

        for rel, (data, sf) in processed.items():
            new_rel = rel
            if self.rename_files and sf.spec.rename_class_files and rel.stem in self.class_decls[rel]:
                new_name = report.mapping.get(sf.spec.family, {}).get(rel.stem)
                if new_name:
                    new_rel = rel.with_name(new_name + rel.suffix)
                    report.renamed_files.append((str(rel), str(new_rel)))
            dst = dest_root / new_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            if in_place and new_rel != rel:
                (self.root / rel).unlink()
        return report
