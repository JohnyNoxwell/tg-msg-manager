# Payloads Split Map

| Current model | Domain | Target module | Used by | Public? |
|---|---|---|---|---|
| `ExportSyncStartedPayload` | export | `core/models/payloads/export.py` | export services, CLI IO, tests | yes |
| `ExportSyncSummaryPayload` | export | `core/models/payloads/export.py` | export services, CLI IO, tests | yes |
| `ExportSyncProgressPayload` | export | `core/models/payloads/export.py` | export/sync progress emitters, CLI IO | yes |
| `ExportSyncFinishedPayload` | export | `core/models/payloads/export.py` | export chat sync, CLI IO | yes |
| `ExportTargetedDialogSearchStartedPayload` | export | `core/models/payloads/export.py` | dialog sync, CLI IO | yes |
| `ExportDialogSearchStartedPayload` | export | `core/models/payloads/export.py` | dialog sync, CLI IO | yes |
| `ExportDialogSearchScanningPayload` | export | `core/models/payloads/export.py` | dialog sync, CLI IO | yes |
| `ExportDialogScanStartedPayload` | export | `core/models/payloads/export.py` | dialog sync, CLI IO | yes |
| `ExportGlobalExportFinishedPayload` | export | `core/models/payloads/export.py` | dialog sync, CLI IO | yes |
| `ExportTrackedUpdateStartedPayload` | export/sync | `core/models/payloads/export.py` | tracked sync runner, CLI IO | yes |
| `PrivateArchiveStartedPayload` | private_archive | `core/models/payloads/private_archive.py` | archive service, CLI IO, tests | yes |
| `PrivateArchiveMediaStats` | private_archive | `core/models/payloads/private_archive.py` | archive service/events/tests | yes |
| `PrivateArchiveTransferStats` | private_archive | `core/models/payloads/private_archive.py` | archive service/events/tests | yes |
| `PrivateArchiveProgressPayload` | private_archive | `core/models/payloads/private_archive.py` | archive event emitter | yes |
| `PrivateArchiveMediaSavedPayload` | private_archive | `core/models/payloads/private_archive.py` | archive event emitter/tests | yes |
| `PrivateArchiveCompletedPayload` | private_archive | `core/models/payloads/private_archive.py` | archive event emitter/tests | yes |
| `CleanerDialogScanStartedPayload` | cleaner | `core/models/payloads/cleaner.py` | cleaner service, CLI IO, tests | yes |
| `CleanerDialogMessagesFoundPayload` | cleaner | `core/models/payloads/cleaner.py` | cleaner service, CLI IO, tests | yes |

Additional Stage 1 package placeholders created for future domain-local payloads:

- `core/models/payloads/sync.py`
- `core/models/payloads/db_export.py`
- `core/models/payloads/context.py`
- `core/models/payloads/retry.py`
- `core/models/payloads/report.py`
- `core/models/payloads/telemetry.py`
