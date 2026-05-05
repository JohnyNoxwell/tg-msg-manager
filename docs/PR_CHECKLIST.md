# PR Checklist

- [ ] CLI behavior unchanged
- [ ] Tests pass
- [ ] Smoke scenario checked
- [ ] No raw SQL in service layer
- [ ] No new feature added to hot-path files
- [ ] New module has single responsibility
- [ ] No new logic added to DBExportService facade
- [ ] No new logic added to PrivateArchiveService facade
- [ ] Service depends on narrow storage contract
- [ ] New payload models placed in domain payload module
- [ ] Analytics logic not added to export/context/db_export services
- [ ] Context relation table decision respected
- [ ] Live smoke checklist updated if Telegram behavior changed
- [ ] Docs updated if architecture changed
- [ ] Legacy path marked if retained
