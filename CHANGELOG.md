# CHANGELOG: TG_MSG_MNGR

All notable changes to this project will be documented in this file.

## [4.0.0] - 2026-04-20
### Added
- **Target Attribution System**: Implemented a reference-counting mechanism using `message_target_links`. Every message and its surrounding context is now explicitly linked to a primary sync target.
- **Smart Purge (Garbage Collection)**: Redesigned the data removal logic. Context messages are now only deleted from the database if they are no longer referenced by any active sync target, preventing data orphans and preserving shared conversation context.
- **Async-Native Signal Handling**: Refactored the core process manager to use `asyncio.EventLoop.add_signal_handler`. This ensures immediate and reliable response to Ctrl+C (SIGINT) even during heavy I/O or network operations.
- **Emergency JSON Dumps**: Guaranteed export of partial data to `DB_EXPORTS/*.jsonl` upon interruption. The CLI now provides explicit feedback and the filesystem path of the dump.
- **Stateful Resume Engine**: Implemented a dual-sync model (Head/Tail) tracking synchronization boundaries per target. The system now skips already-synced history blocks and resumes instantly.

### Changed
- **Database Schema**: Significant upgrades to support normalization (`users`, `chats`, `message_target_links`).
- **Worker Logic**: Added granular shutdown checks to all export workers for immediate termination upon interrupt signals.
- **CLI UX**: Enhanced 24-bit ANSI gradient aesthetics and interactive sub-menu navigation.

### Fixed
- Resolved `NameError` in `process.py` by restoring missing `asyncio` imports.
- Fixed `AttributeError` in `Exporter` related to missing `should_stop` method in storage.
- Corrected database initialization logic to prevent missing table errors after full wipes.

## [3.5.0] - Previously
- Refactored project into modular `core/`, `services/`, `infrastructure/` layers.
- Implemented `TelethonClientWrapper` with advanced throttling and FloodWait protection.
- Added interactive terminal sub-menus with raw input support.
- Centralized logging into `LOGS/` directory.
