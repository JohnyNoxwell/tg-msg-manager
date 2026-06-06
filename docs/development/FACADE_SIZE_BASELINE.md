# Facade Size Baseline

Measured on: `2026-06-05`

| Facade | Current line count | Role |
|---|---:|---|
| `tg_msg_manager/services/export/service.py` | 192 | sync/export orchestration facade |
| `tg_msg_manager/services/context/engine.py` | 208 | deep-context orchestration facade |
| `tg_msg_manager/services/db_export/service.py` | 358 | DB export public facade with run coordinator wiring |
| `tg_msg_manager/services/private_archive/service.py` | 109 | PM archive orchestration facade |
| `tg_msg_manager/services/channel_export/service.py` | 488 | direct channel export orchestration facade after Stage 3E.0 decomposition |

## Notes

- `services/db_export/service.py` delegates full/update run sequencing to focused DB export run coordinators.
- `services/channel_export/service.py` delegates included-file, manifest, and result construction to focused channel export modules.
- Wrapper files themselves remain intentionally tiny:
  - `services/exporter.py` -> 6 lines
  - `services/context_engine.py` -> 6 lines
  - `services/db_exporter.py` -> 6 lines
  - `services/private_archive.py` -> 6 lines

## Rule

New business logic should not be added directly to these facades. If a facade grows because of a new concern, extract a dedicated component first.
