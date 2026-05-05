# Private Archive Import Resolution

## 1. Existing paths

- Active package: `tg_msg_manager/services/private_archive/`
- Shadow wrapper file: `tg_msg_manager/services/private_archive.py`
- Active implementation: `tg_msg_manager/services/private_archive/service.py`
- Public package entrypoint: `tg_msg_manager/services/private_archive/__init__.py`

## 2. Python import result

Observed result:

```text
module: <module 'tg_msg_manager.services.private_archive' from '.../tg_msg_manager/services/private_archive/__init__.py'>
file: /Users/maczone/dev/TG_CLEANER/tg_msg_manager/services/private_archive/__init__.py
has service: True
```

## 3. Active implementation

- `PrivateArchiveService` is defined once in `services/private_archive/service.py`

## 4. Compatibility path

- `from tg_msg_manager.services.private_archive import PrivateArchiveService` resolves through the package `__init__.py`
- `tg_msg_manager/services/private_archive.py` remains a minimal compatibility shim only

## 5. Risk

- The file/package name overlap is still a maintenance hazard
- future edits must not add logic to `services/private_archive.py`
- future import migrations must keep the package path authoritative

## 6. Decision

- Keep `services/private_archive/` as the active package
- Keep `services/private_archive.py` as a harmless wrapper for now
- Protect the behavior with import-resolution and no-active-class guard tests

## 7. Guard tests

- `tests/test_architecture_wrappers.py::test_private_archive_wrapper_has_no_active_class_definition`
- `tests/test_architecture_wrappers.py::test_private_archive_import_resolution_uses_package`
- `tests/test_architecture_wrappers.py::test_private_archive_compat_import_points_to_new_service`
