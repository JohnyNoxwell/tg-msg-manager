# DBExportService Entrypoint Audit

## 1. Active implementation

- Class definition: `tg_msg_manager/services/db_export/service.py`
- Package re-export: `tg_msg_manager/services/db_export/__init__.py`
- Compatibility wrapper: `tg_msg_manager/services/db_exporter.py`

## 2. Wrapper classification

- `services/db_export/service.py`: active implementation
- `services/db_export/__init__.py`: package-level re-export entrypoint
- `services/db_exporter.py`: pure compatibility wrapper

`services/db_exporter.py` contains no active service logic and only re-exports the new class.

## 3. Import usage

### CLI and runtime

- `tg_msg_manager/cli/__init__.py` imports `DBExportService` from `tg_msg_manager.services.db_export`
- `tg_msg_manager/testing/runtime.py` imports `DBExportService` from `tg_msg_manager.services.db_export`
- `tg_msg_manager/services/export/export_writer.py` imports `DBExportService` from `tg_msg_manager.services.db_export`

### Tests using compatibility path

- `tests/test_db_exporter.py`
- `tests/test_db_export_components.py`
- `tests/test_compat_imports.py`

### Tests using direct implementation path

- `tests/test_compat_imports.py`

## 4. CLI wiring status

- Real CLI wiring uses the new package entrypoint.
- No runtime code inside `tg_msg_manager/` depends on `services/db_exporter.py`.

## 5. Result

- Active class definitions found: `1`
- Duplicate active implementation: `no`
- Old import path still works: `yes`
- Recommended public import for new code: `tg_msg_manager.services.db_export`
