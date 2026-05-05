# Analytics Boundary

This package is reserved for future read-only analytics services.

Rules:

- Analytics reads normalized storage data.
- Analytics does not fetch Telegram directly.
- Analytics does not mutate sync/export state.
- Analytics does not write message records.
- Analytics does not live inside `ExportService`, `DBExportService`, or `ContextEngine`.
- Analytics projections must use read-only storage contracts.
