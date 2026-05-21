# PrivateArchiveService Entrypoint Audit

## 1. Active implementation

- Class definition: `tg_msg_manager/services/private_archive/service.py`
- Package re-export: `tg_msg_manager/services/private_archive/__init__.py`
- Shadow compatibility file: `tg_msg_manager/services/private_archive.py`

## 2. Wrapper classification

- `services/private_archive/service.py`: active implementation
- `services/private_archive/__init__.py`: package-level re-export entrypoint
- `services/private_archive.py`: pure compatibility wrapper with no business logic

## 3. Import resolution check

Command result:

```text
<module 'tg_msg_manager.services.private_archive' from '.../tg_msg_manager/services/private_archive/__init__.py'>
True
```

Interpretation:

- `from tg_msg_manager.services.private_archive import PrivateArchiveService` resolves to the package `__init__.py`
- the package exposes `PrivateArchiveService`
- the same-named file `services/private_archive.py` does not become the imported module in normal package resolution

## 4. Import usage

### CLI and runtime

- `tg_msg_manager/cli/__init__.py` imports `PrivateArchiveService` from `tg_msg_manager.services.private_archive`
- `tg_msg_manager/testing/runtime.py` imports `PrivateArchiveService` from `tg_msg_manager.services.private_archive`

### Tests using public package path

- `tests/test_services.py`
- `tests/test_compat_imports.py`
- `tests/test_cli.py` patches `tg_msg_manager.cli.PrivateArchiveService`

### Tests using direct implementation path

- `tests/test_compat_imports.py`

## 5. CLI wiring status

- Real CLI wiring uses the package entrypoint.
- Public compatibility import is preserved through `services/private_archive/__init__.py`.
- New code should treat the package path as authoritative and should not add logic to `services/private_archive.py`.

## 6. Result

- Active class definitions found: `1`
- Duplicate active implementation: `no`
- Import conflict detected: `no`
- Recommended public import for new code: `tg_msg_manager.services.private_archive`
