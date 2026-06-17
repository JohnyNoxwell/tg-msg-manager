import ast
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "tg_msg_manager"
STORAGE_ROOT = PACKAGE_ROOT / "infrastructure" / "storage"
APPLICATION_ROOT = PACKAGE_ROOT / "application"

SQL_METHODS = {"execute", "executemany", "executescript"}
SQL_KEYWORD_RE = re.compile(
    r"\b(ALTER|CREATE|DELETE|DROP|INSERT|PRAGMA|REPLACE|SELECT|UPDATE)\b"
)
RAW_SQL_ALLOWLIST = {
    Path("tg_msg_manager/testing/fixtures.py"),
}

CLI_IMPORT_PREFIXES = (
    "tg_msg_manager.cli",
    "tg_msg_manager.cli_commands",
    "tg_msg_manager.cli_io",
    "tg_msg_manager.cli_menu",
    "tg_msg_manager.cli_parser",
    "tg_msg_manager.cli_support",
)
APPLICATION_LAYER_ALLOWED_IMPORT_PREFIXES = (
    "tg_msg_manager.core",
    "tg_msg_manager.infrastructure",
    "tg_msg_manager.services",
    "tg_msg_manager.utils",
)

STORAGE_COMPATIBILITY_SURFACES = (
    Path("tg_msg_manager/infrastructure/storage/interface.py"),
    Path("tg_msg_manager/infrastructure/storage/contracts/__init__.py"),
    Path("tg_msg_manager/infrastructure/storage/_sqlite_write_path.py"),
    Path("tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py"),
    Path("tg_msg_manager/infrastructure/storage/records.py"),
)


def _production_files() -> list[Path]:
    return sorted(
        path for path in PACKAGE_ROOT.rglob("*.py") if "__pycache__" not in path.parts
    )


def _relative(path: Path) -> Path:
    return path.relative_to(PROJECT_ROOT)


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(_relative(path)))


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _constant_text(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return " ".join(
            part.value
            for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
    return ""


def _imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module)
                modules.update(f"{node.module}.{alias.name}" for alias in node.names)
    return modules


def _import_references(tree: ast.AST) -> set[str]:
    references: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            references.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            references.add(module)
            references.update(
                f"{module}.{alias.name}" if module else alias.name
                for alias in node.names
            )
    return references


def _references_layer(reference: str, layer: str) -> bool:
    parts = reference.split(".")
    if layer == "cli":
        return any(part == "cli" or part.startswith("cli_") for part in parts)
    return layer in parts


def _imports_prefix(module: str, prefix: str) -> bool:
    return module == prefix or module.startswith(f"{prefix}.")


def _is_allowed_application_import(module: str) -> bool:
    if not module.startswith("tg_msg_manager."):
        return True
    if _imports_prefix(module, "tg_msg_manager.application"):
        return True
    return any(
        _imports_prefix(module, prefix)
        for prefix in APPLICATION_LAYER_ALLOWED_IMPORT_PREFIXES
    )


class TestStaticArchitectureBoundaries(unittest.TestCase):
    def test_raw_sql_stays_under_storage_boundary(self):
        offenders: set[Path] = set()
        for path in _production_files():
            if _is_relative_to(path, STORAGE_ROOT):
                continue
            tree = _parse(path)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in SQL_METHODS
                ):
                    offenders.add(_relative(path))
                text = _constant_text(node)
                if text and SQL_KEYWORD_RE.search(text):
                    offenders.add(_relative(path))

        unexpected = sorted(offenders - RAW_SQL_ALLOWLIST)
        self.assertEqual(unexpected, [])
        self.assertEqual(offenders & RAW_SQL_ALLOWLIST, RAW_SQL_ALLOWLIST)

    def test_core_does_not_import_infrastructure(self):
        offenders: dict[str, list[str]] = {}
        for path in sorted((PACKAGE_ROOT / "core").rglob("*.py")):
            imports = _imported_modules(_parse(path))
            bad = sorted(
                module
                for module in imports
                if _imports_prefix(module, "tg_msg_manager.infrastructure")
            )
            if bad:
                offenders[str(_relative(path))] = bad

        self.assertEqual(offenders, {})

    def test_infrastructure_does_not_import_services(self):
        offenders: dict[str, list[str]] = {}
        for path in sorted((PACKAGE_ROOT / "infrastructure").rglob("*.py")):
            imports = _imported_modules(_parse(path))
            bad = sorted(
                module
                for module in imports
                if _imports_prefix(module, "tg_msg_manager.services")
            )
            if bad:
                offenders[str(_relative(path))] = bad

        self.assertEqual(offenders, {})

    def test_core_services_and_infrastructure_do_not_import_cli_modules(self):
        roots = [
            PACKAGE_ROOT / "core",
            PACKAGE_ROOT / "services",
            PACKAGE_ROOT / "infrastructure",
        ]
        offenders: dict[str, list[str]] = {}
        for root in roots:
            for path in sorted(root.rglob("*.py")):
                imports = _imported_modules(_parse(path))
                bad = sorted(
                    module
                    for module in imports
                    if any(
                        _imports_prefix(module, prefix)
                        for prefix in CLI_IMPORT_PREFIXES
                    )
                )
                if bad:
                    offenders[str(_relative(path))] = bad

        self.assertEqual(offenders, {})

    def test_application_runtime_boundary_import_expectation(self):
        if not APPLICATION_ROOT.exists():
            self.assertFalse(APPLICATION_ROOT.exists())
            return

        offenders: dict[str, list[str]] = {}
        for path in sorted(APPLICATION_ROOT.rglob("*.py")):
            imports = _imported_modules(_parse(path))
            bad = sorted(
                module
                for module in imports
                if any(
                    _imports_prefix(module, prefix) for prefix in CLI_IMPORT_PREFIXES
                )
                or not _is_allowed_application_import(module)
            )
            if bad:
                offenders[str(_relative(path))] = bad

        self.assertEqual(offenders, {})
        self.assertEqual(
            APPLICATION_LAYER_ALLOWED_IMPORT_PREFIXES,
            (
                "tg_msg_manager.core",
                "tg_msg_manager.infrastructure",
                "tg_msg_manager.services",
                "tg_msg_manager.utils",
            ),
        )

    def test_cli_context_does_not_import_service_constructors(self):
        cli_module = PACKAGE_ROOT / "cli" / "__init__.py"
        text = cli_module.read_text(encoding="utf-8")

        self.assertNotIn("from ..services", text)
        self.assertIn("from ..application.session import ApplicationSession", text)

    def test_cli_context_does_not_construct_runtime_resources_directly(self):
        cli_module = PACKAGE_ROOT / "cli" / "__init__.py"
        tree = _parse(cli_module)
        cli_context = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "CLIContext"
        )
        forbidden_calls = {
            "AliasManager",
            "ChannelExportService",
            "CleanerService",
            "DBExportService",
            "ExportService",
            "PrivateArchiveService",
            "ProcessManager",
            "RetryWorker",
            "RuntimeResourceFactory",
            "SQLiteStorage",
            "TelethonClientWrapper",
            "create_service_bundle",
        }
        observed: set[str] = set()
        for node in ast.walk(cli_context):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                observed.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                observed.add(node.func.attr)

        self.assertEqual(sorted(observed & forbidden_calls), [])

    def test_new_code_does_not_import_storage_interface_aggregator(self):
        broad_interface = "tg_msg_manager.infrastructure.storage.interface"
        offenders: dict[str, list[str]] = {}
        for path in _production_files():
            if _relative(path) == Path(
                "tg_msg_manager/infrastructure/storage/interface.py"
            ):
                continue
            imports = _imported_modules(_parse(path))
            bad = sorted(
                module for module in imports if _imports_prefix(module, broad_interface)
            )
            if bad:
                offenders[str(_relative(path))] = bad

        self.assertEqual(offenders, {})

    def test_services_do_not_depend_on_legacy_base_storage(self):
        offenders: dict[str, list[str]] = {}
        for path in sorted((PACKAGE_ROOT / "services").rglob("*.py")):
            references = _import_references(_parse(path))
            bad = sorted(
                reference
                for reference in references
                if reference.endswith("storage.interface")
                or reference.endswith("storage.interface.BaseStorage")
                or reference.endswith(".BaseStorage")
            )
            if bad:
                offenders[str(_relative(path))] = bad

        self.assertEqual(offenders, {})

    def test_storage_compatibility_surfaces_do_not_import_services_or_cli(self):
        offenders: dict[str, list[str]] = {}
        for relative_path in STORAGE_COMPATIBILITY_SURFACES:
            references = _import_references(_parse(PROJECT_ROOT / relative_path))
            bad = sorted(
                reference
                for reference in references
                if _references_layer(reference, "services")
                or _references_layer(reference, "cli")
            )
            if bad:
                offenders[str(relative_path)] = bad

        self.assertEqual(offenders, {})


if __name__ == "__main__":
    unittest.main()
