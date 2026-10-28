"""Per-language rules: which nodes are identifiers, where a declaration happens,
what must never be touched."""
from __future__ import annotations

import builtins
from dataclasses import dataclass, field


@dataclass
class LangSpec:
    name: str                      # tree-sitter grammar name
    extensions: tuple[str, ...]
    ident_types: frozenset[str]    # node types that are identifiers
    # (parent_type, field) -> the child (and its subtree) is a declaration.
    # field "*" = any child
    decl: frozenset[tuple[str, str]]
    # fields that break the declaration context (default values, types, bodies...)
    stop_fields: frozenset[str] = frozenset(
        {"value", "right", "body", "type", "return_type", "arguments", "default",
         "key", "subscript", "index", "condition", "decorator", "superclass",
         "type_parameters", "annotation", "initializer"})
    # "member access" nodes: (type, object_field, member_field)
    member: tuple[tuple[str, str, str], ...] = ()
    self_names: frozenset[str] = frozenset()
    keep: frozenset[str] = frozenset()
    lower_default: str = "camel"   # style for all-lowercase names (e.g. "i", "data")
    rename_class_files: bool = False
    family: str = ""               # languages sharing a namespace (js/ts/tsx)
    class_bodies: frozenset[str] = frozenset()   # class/interface/enum body
    func_nodes: frozenset[str] = frozenset()     # function boundaries (local scope)
    # identifiers always in "member position" (e.g. property_identifier in JS)
    member_ident_types: frozenset[str] = frozenset()
    # member names of base types (dict.items, Array.push, List.add...): if the project
    # declares a member with the same name, that name is left untouched everywhere
    builtin_members: frozenset[str] = frozenset()


def _fs(*items):
    return frozenset(items)


_PY_TYPES = (dict, list, str, bytes, set, frozenset, tuple, int, float, object,
             bytearray, type, BaseException, range, slice, memoryview, complex)
PY_BUILTIN_MEMBERS = _fs(*(n for t in _PY_TYPES for n in dir(t)), "append", "update",
                         "get", "items", "keys", "values", "read", "write", "close")
PY_KEEP = _fs(
    *dir(builtins), "self", "cls", "__name__", "__main__", "__file__", "__all__",
    "__init__", "__doc__", "__slots__", "args", "kwargs",
    # common overrides (airflow, unittest, django, threading...)
    "execute", "poke", "on_kill", "pre_execute", "post_execute", "template_fields",
    "template_ext", "ui_color", "ui_fgcolor", "setUp", "tearDown", "setUpClass",
    "tearDownClass", "run", "Meta", "get", "post", "put", "delete", "patch",
    "default", "dag", "task", "context",
)

JS_GLOBALS_BASE = _fs(
    "console", "window", "document", "globalThis", "global", "process", "module",
    "exports", "require", "__dirname", "__filename", "arguments", "undefined",
    "NaN", "Infinity", "this", "super", "Object", "Array", "String", "Number",
    "Boolean", "Symbol", "BigInt", "Math", "JSON", "Date", "RegExp", "Error",
    "TypeError", "RangeError", "Promise", "Map", "Set", "WeakMap", "WeakSet",
    "Proxy", "Reflect", "Intl", "setTimeout", "setInterval", "clearTimeout",
    "clearInterval", "fetch", "localStorage", "sessionStorage", "navigator",
    "location", "history", "alert", "parseInt", "parseFloat", "isNaN", "isFinite",
    "encodeURIComponent", "decodeURIComponent", "structuredClone", "queueMicrotask",
    "constructor", "prototype", "default", "Function", "Event", "HTMLElement",
    "Element", "Node", "Buffer", "URL", "URLSearchParams", "FormData", "Headers",
    "Request", "Response", "Blob", "File", "Partial", "Record", "Readonly",
    "Pick", "Omit", "Exclude", "Extract", "ReturnType", "Parameters", "Awaited",
    "Required", "NonNullable", "InstanceType", "Array", "ReadonlyArray", "unknown",
    "any", "never", "object", "string", "number", "boolean",
    # Angular / React / Node lifecycle and interfaces
    "ngOnInit", "ngOnDestroy", "ngOnChanges", "ngAfterViewInit", "ngAfterContentInit",
    "ngDoCheck", "ngAfterViewChecked", "ngAfterContentChecked", "transform",
    "canActivate", "canActivateChild", "canDeactivate", "canLoad", "canMatch",
    "resolve", "intercept", "writeValue", "registerOnChange", "registerOnTouched",
    "setDisabledState", "validate", "render", "componentDidMount",
    "componentWillUnmount", "componentDidUpdate", "shouldComponentUpdate",
)

# methods/properties of JS base types (generated from Object.getOwnPropertyNames of the prototypes)
JS_BUILTIN_MEMBERS = _fs(
    "BYTES_PER_ELEMENT", "Console", "E", "EPSILON", "LN10", "LN2", "LOG10E", "LOG2E",
    "MAX_SAFE_INTEGER", "MAX_VALUE", "MIN_SAFE_INTEGER", "MIN_VALUE", "NEGATIVE_INFINITY", "NaN", "PI", "POSITIVE_INFINITY",
    "SQRT1_2", "SQRT2", "UTC", "abs", "acos", "acosh", "add", "all",
    "allSettled", "anchor", "any", "apply", "arguments", "asin", "asinh", "assert",
    "assign", "at", "atan", "atan2", "atanh", "big", "bind", "blink",
    "bold", "byteLength", "call", "caller", "captureStackTrace", "catch", "cbrt", "ceil",
    "charAt", "charCodeAt", "clear", "clz32", "codePointAt", "compile", "concat", "constructor",
    "context", "copyWithin", "cos", "cosh", "count", "countReset", "create", "createTask",
    "debug", "defineProperties", "defineProperty", "delete", "detached", "difference", "dir", "dirxml",
    "dotAll", "endsWith", "entries", "error", "every", "exec", "exp", "expm1",
    "fill", "filter", "finally", "find", "findIndex", "findLast", "findLastIndex", "fixed",
    "flags", "flat", "flatMap", "floor", "fontcolor", "fontsize", "forEach", "freeze",
    "from", "fromAsync", "fromCharCode", "fromCodePoint", "fromEntries", "fround", "get", "getDate",
    "getDay", "getFullYear", "getHours", "getMilliseconds", "getMinutes", "getMonth", "getOwnPropertyDescriptor", "getOwnPropertyDescriptors",
    "getOwnPropertyNames", "getOwnPropertySymbols", "getPrototypeOf", "getSeconds", "getTime", "getTimezoneOffset", "getUTCDate", "getUTCDay",
    "getUTCFullYear", "getUTCHours", "getUTCMilliseconds", "getUTCMinutes", "getUTCMonth", "getUTCSeconds", "getYear", "global",
    "group", "groupBy", "groupCollapsed", "groupEnd", "has", "hasIndices", "hasOwn", "hasOwnProperty",
    "hypot", "ignoreCase", "imul", "includes", "indexOf", "info", "input", "intersection",
    "is", "isArray", "isDisjointFrom", "isExtensible", "isFinite", "isFrozen", "isInteger", "isNaN",
    "isPrototypeOf", "isRawJSON", "isSafeInteger", "isSealed", "isSubsetOf", "isSupersetOf", "isView", "isWellFormed",
    "italics", "join", "keys", "lastIndexOf", "lastMatch", "lastParen", "leftContext", "length",
    "link", "localeCompare", "log", "log10", "log1p", "log2", "map", "match",
    "matchAll", "max", "maxByteLength", "message", "min", "multiline", "name", "normalize",
    "now", "of", "padEnd", "padStart", "parse", "parseFloat", "parseInt", "pop",
    "pow", "prepareStackTrace", "preventExtensions", "profile", "profileEnd", "propertyIsEnumerable", "prototype", "push",
    "race", "random", "raw", "rawJSON", "reduce", "reduceRight", "reject", "repeat",
    "replace", "replaceAll", "resizable", "resize", "resolve", "reverse", "rightContext", "round",
    "seal", "search", "set", "setDate", "setFullYear", "setHours", "setMilliseconds", "setMinutes",
    "setMonth", "setPrototypeOf", "setSeconds", "setTime", "setUTCDate", "setUTCFullYear", "setUTCHours", "setUTCMilliseconds",
    "setUTCMinutes", "setUTCMonth", "setUTCSeconds", "setYear", "shift", "sign", "sin", "sinh",
    "size", "slice", "small", "some", "sort", "source", "splice", "split",
    "sqrt", "stackTraceLimit", "startsWith", "sticky", "strike", "stringify", "sub", "substr",
    "substring", "sup", "symmetricDifference", "table", "tan", "tanh", "test", "then",
    "time", "timeEnd", "timeLog", "timeStamp", "toDateString", "toExponential", "toFixed", "toGMTString",
    "toISOString", "toJSON", "toLocaleDateString", "toLocaleLowerCase", "toLocaleString", "toLocaleTimeString", "toLocaleUpperCase", "toLowerCase",
    "toPrecision", "toReversed", "toSorted", "toSpliced", "toString", "toTimeString", "toUTCString", "toUpperCase",
    "toWellFormed", "trace", "transfer", "transferToFixedLength", "trim", "trimEnd", "trimLeft", "trimRight",
    "trimStart", "trunc", "unicode", "unicodeSets", "union", "unshift", "valueOf", "values",
    "warn", "with", "withResolvers",
)

JS_GLOBALS = JS_GLOBALS_BASE
JS_MEMBERS = JS_BUILTIN_MEMBERS | _fs(
    "toJSON", "then", "catch", "finally", "props", "state", "setState", "children",
    "key", "ref", "emit", "subscribe", "pipe", "next", "complete", "unsubscribe")

PHP_KEEP = _fs(
    "this", "GLOBALS", "_SERVER", "_GET", "_POST", "_FILES", "_COOKIE", "_SESSION",
    "_REQUEST", "_ENV", "argv", "argc", "http_response_header", "self", "parent",
    "static",
    # Laravel / Eloquent / PHP interfaces
    "handle", "boot", "booted", "register", "up", "down", "run", "toArray",
    "toJson", "rules", "authorize", "messages", "attributes", "render", "report",
    "via", "toMail", "toDatabase", "toBroadcast", "broadcastOn", "broadcastAs",
    "broadcastWith", "failed", "middleware", "definition", "configure", "schedule",
    "commands", "map", "model", "collection", "jsonSerialize", "offsetGet",
    "offsetSet", "offsetExists", "offsetUnset", "getIterator", "count",
    "fillable", "guarded", "table", "casts", "hidden", "visible", "appends",
    "with", "withCount", "primaryKey", "keyType", "incrementing", "timestamps",
    "connection", "dates", "dateFormat", "perPage", "signature", "description",
    "listen", "subscribe", "policies", "routeMiddleware", "middlewareGroups",
    "middlewareAliases", "namespace", "redirectTo", "dontReport", "dontFlash",
    "except", "tries", "timeout", "backoff", "queue", "delay", "afterCommit",
    "maxExceptions", "uniqueFor", "uniqueId", "broadcastQueue", "data", "request",
    "app", "config", "env", "id", "name", "email", "password", "created_at",
    "updated_at", "deleted_at", "remember_token", "pivot",
)

JAVA_KEEP = _fs(
    "String", "Object", "System", "Integer", "Long", "Double", "Float", "Boolean",
    "Character", "Byte", "Short", "Math", "List", "Map", "Set", "Optional",
    "Exception", "RuntimeException", "Override", "Deprecated", "FunctionalInterface",
    "SuppressWarnings", "Thread", "Runnable", "Iterable", "Comparable", "Class",
    "main", "toString", "equals", "hashCode", "run", "call", "compareTo", "close",
    "iterator", "apply", "accept", "test", "get", "clone", "finalize", "compare",
    "out", "err", "in", "println", "print", "printf",
)
JAVA_MEMBERS = _fs(
    "length", "value",
    # common String / Collection / Map / Stream / Optional methods
    "add", "addAll", "remove", "removeIf", "size", "isEmpty", "contains", "containsKey",
    "containsValue", "put", "putAll", "putIfAbsent", "getOrDefault", "keySet", "values",
    "entrySet", "getKey", "getValue", "clear", "stream", "map", "filter", "collect",
    "forEach", "reduce", "sorted", "toList", "findFirst", "anyMatch", "allMatch",
    "orElse", "orElseThrow", "ifPresent", "isPresent", "of", "ofNullable", "empty",
    "charAt", "substring", "indexOf", "split", "trim", "format", "join", "valueOf",
    "toUpperCase", "toLowerCase", "startsWith", "endsWith", "replace", "matches",
    "append", "builder", "build", "next", "hasNext", "sum", "count", "max", "min",
    "getMessage", "getClass", "getName", "parseInt", "parseDouble", "sort", "asList",
)

CS_KEEP = _fs(
    "System", "Console", "String", "Object", "Math", "Task", "List", "Dictionary",
    "Exception", "Main", "ToString", "Equals", "GetHashCode", "Dispose",
    "DisposeAsync", "CompareTo", "GetEnumerator", "Invoke", "Configure",
    "ConfigureServices", "OnModelCreating", "OnConfiguring", "value", "var",
    "dynamic", "nameof", "get", "set", "init", "add", "remove", "async", "await",
    "args", "Program", "where", "select", "from", "orderby", "group", "into",
    "join", "let", "ascending", "descending", "on", "equals", "by", "global",
    "Startup", "Up", "Down", "BuildTargetModel", "WriteLine", "Write", "ReadLine",
)
CS_MEMBERS = _fs(
    # common string / collection / LINQ / Task members
    "Add", "AddRange", "Remove", "RemoveAt", "Clear", "Count", "Length", "Contains",
    "ContainsKey", "TryGetValue", "Keys", "Values", "Key", "Value", "Where", "Select",
    "SelectMany", "OrderBy", "OrderByDescending", "GroupBy", "ToList", "ToArray",
    "ToDictionary", "First", "FirstOrDefault", "Single", "SingleOrDefault", "Any",
    "All", "Sum", "Min", "Max", "Average", "Skip", "Take", "Distinct", "Join",
    "Format", "Split", "Trim", "Replace", "Substring", "StartsWith", "EndsWith",
    "IndexOf", "ToUpper", "ToLower", "IsNullOrEmpty", "IsNullOrWhiteSpace", "Concat",
    "Result", "Wait", "WhenAll", "Run", "Message", "Name", "Id", "Parse", "TryParse", "Now", "UtcNow", "Today", "Empty", "Append",
)


PYTHON = LangSpec(
    name="python",
    extensions=(".py", ".pyi"),
    ident_types=_fs("identifier"),
    decl=_fs(
        ("function_definition", "name"), ("class_definition", "name"),
        ("parameters", "*"), ("lambda_parameters", "*"),
        ("assignment", "left"), ("augmented_assignment", "left"),
        ("for_statement", "left"), ("for_in_clause", "left"),
        ("as_pattern", "alias"), ("named_expression", "name"),
        ("except_clause", "alias"), ("global_statement", "*"),
    ),
    member=(("attribute", "object", "attribute"),),
    self_names=_fs("self", "cls"),
    keep=PY_KEEP,
    builtin_members=PY_BUILTIN_MEMBERS,
    lower_default="snake",
    family="python",
    class_bodies=_fs("class_definition"),
    func_nodes=_fs("function_definition", "lambda"),
)

_JS_DECL = (
    ("variable_declarator", "name"), ("function_declaration", "name"),
    ("generator_function_declaration", "name"), ("class_declaration", "name"),
    ("class", "name"), ("function_expression", "name"), ("method_definition", "name"),
    ("field_definition", "property"), ("formal_parameters", "*"),
    ("arrow_function", "parameter"), ("catch_clause", "parameter"),
    ("assignment_expression", "left"), ("for_in_statement", "left"),
)
_TS_DECL = _JS_DECL + (
    ("public_field_definition", "name"), ("required_parameter", "pattern"),
    ("optional_parameter", "pattern"), ("interface_declaration", "name"),
    ("type_alias_declaration", "name"), ("enum_declaration", "name"),
    ("enum_body", "name"), ("enum_assignment", "name"), ("property_signature", "name"),
    ("method_signature", "name"), ("abstract_method_signature", "name"),
    ("abstract_class_declaration", "name"), ("type_parameter", "name"),
)
_JS_FUNCS = _fs("function_declaration", "function_expression", "arrow_function",
                "method_definition", "generator_function_declaration",
                "generator_function")
_JS_MEMBER_IDENTS = _fs("property_identifier", "private_property_identifier")
_JS_IDENTS = ("identifier", "property_identifier", "shorthand_property_identifier",
              "shorthand_property_identifier_pattern", "private_property_identifier")

JAVASCRIPT = LangSpec(
    name="javascript",
    extensions=(".js", ".mjs", ".cjs", ".jsx"),
    ident_types=_fs(*_JS_IDENTS),
    decl=_fs(*_JS_DECL),
    member=(("member_expression", "object", "property"),),
    self_names=_fs("this"),
    keep=JS_GLOBALS,
    builtin_members=JS_MEMBERS,
    family="js",
    class_bodies=_fs("class_body", "object"),
    func_nodes=_JS_FUNCS,
    member_ident_types=_JS_MEMBER_IDENTS,
)
TYPESCRIPT = LangSpec(
    name="typescript",
    extensions=(".ts", ".mts", ".cts"),
    ident_types=_fs(*_JS_IDENTS, "type_identifier"),
    decl=_fs(*_TS_DECL),
    member=JAVASCRIPT.member,
    self_names=_fs("this"),
    keep=JS_GLOBALS,
    builtin_members=JS_MEMBERS,
    family="js",
    class_bodies=_fs("class_body", "interface_body", "object_type", "enum_body", "object"),
    func_nodes=_JS_FUNCS,
    member_ident_types=_JS_MEMBER_IDENTS,
)
TSX = LangSpec(**{**TYPESCRIPT.__dict__, "name": "tsx", "extensions": (".tsx",)})

PHP = LangSpec(
    name="php",
    extensions=(".php",),
    ident_types=_fs("name"),
    decl=_fs(
        ("class_declaration", "name"), ("interface_declaration", "name"),
        ("trait_declaration", "name"), ("enum_declaration", "name"),
        ("enum_case", "name"), ("function_definition", "name"),
        ("method_declaration", "name"), ("const_element", "*"),
        # every $variable is a declaration (handled separately in the engine)
    ),
    member=(("member_access_expression", "object", "name"),
            ("member_call_expression", "object", "name"),
            ("nullsafe_member_access_expression", "object", "name"),
            ("nullsafe_member_call_expression", "object", "name"),
            ("scoped_call_expression", "scope", "name"),
            ("scoped_property_access_expression", "scope", "name")),
    self_names=_fs("this"),
    keep=PHP_KEEP,
    rename_class_files=True,
    family="php",
    class_bodies=_fs("declaration_list", "enum_declaration_list"),
    func_nodes=_fs("function_definition", "method_declaration", "anonymous_function",
                   "arrow_function", "anonymous_function_creation_expression"),
)

JAVA = LangSpec(
    name="java",
    extensions=(".java",),
    ident_types=_fs("identifier", "type_identifier"),
    decl=_fs(
        ("class_declaration", "name"), ("interface_declaration", "name"),
        ("enum_declaration", "name"), ("record_declaration", "name"),
        ("annotation_type_declaration", "name"), ("method_declaration", "name"),
        ("constructor_declaration", "name"), ("variable_declarator", "name"),
        ("formal_parameter", "name"), ("catch_formal_parameter", "name"),
        ("enhanced_for_statement", "name"), ("enum_constant", "name"),
        ("lambda_expression", "parameters"), ("inferred_parameters", "*"),
    ),
    member=(("field_access", "object", "field"), ("method_invocation", "object", "name")),
    self_names=_fs("this"),
    keep=JAVA_KEEP,
    builtin_members=JAVA_MEMBERS,
    rename_class_files=True,
    family="java",
    class_bodies=_fs("class_body", "interface_body", "enum_body",
                     "enum_body_declarations", "annotation_type_body"),
    func_nodes=_fs("method_declaration", "constructor_declaration", "lambda_expression",
                   "compact_constructor_declaration"),
)

CSHARP = LangSpec(
    name="csharp",
    extensions=(".cs",),
    ident_types=_fs("identifier"),
    decl=_fs(
        ("class_declaration", "name"), ("interface_declaration", "name"),
        ("struct_declaration", "name"), ("enum_declaration", "name"),
        ("record_declaration", "name"), ("delegate_declaration", "name"),
        ("method_declaration", "name"), ("constructor_declaration", "name"),
        ("property_declaration", "name"), ("variable_declarator", "name"),
        ("parameter", "name"), ("local_function_statement", "name"),
        ("foreach_statement", "left"), ("enum_member_declaration", "name"),
        ("event_declaration", "name"), ("catch_declaration", "name"),
        ("implicit_parameter", "*"),
    ),
    member=(("member_access_expression", "expression", "name"),),
    self_names=_fs("this"),
    keep=CS_KEEP,
    builtin_members=CS_MEMBERS,
    family="csharp",
    class_bodies=_fs("declaration_list", "enum_member_declaration_list"),
    func_nodes=_fs("method_declaration", "constructor_declaration", "local_function_statement",
                   "lambda_expression", "accessor_declaration", "anonymous_method_expression"),
)

ALL = (PYTHON, JAVASCRIPT, TYPESCRIPT, TSX, PHP, JAVA, CSHARP)
BY_EXT = {ext: spec for spec in ALL for ext in spec.extensions}
