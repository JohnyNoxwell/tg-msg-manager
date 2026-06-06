from pathlib import Path

from tg_msg_manager.services.artifact_purger import purge_user_artifacts


def _write(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("artifact", encoding="utf-8")


def test_purge_user_artifacts_stays_within_explicit_roots(tmp_path):
    artifact_root = tmp_path / "artifacts"
    outside_root = tmp_path / "outside"
    inside = artifact_root / "export_42.json"
    outside = outside_root / "export_42.json"
    _write(inside)
    _write(outside)

    deleted = purge_user_artifacts([str(artifact_root)], 42)

    assert deleted == 1
    assert not inside.exists()
    assert outside.exists()


def test_purge_user_artifacts_matches_files_directories_and_sidecars(tmp_path):
    artifact_root = tmp_path / "artifacts"
    matched_file = artifact_root / "nested" / "messages_42.jsonl"
    matched_sidecar = artifact_root / "nested" / "archive_42.db-wal"
    matched_sidecar_shm = artifact_root / "nested" / "archive_42.db-shm"
    matched_dir = artifact_root / "dataset_42"
    unmatched_file = artifact_root / "nested" / "messages_24.jsonl"
    unmatched_dir = artifact_root / "dataset_24"
    for path in (
        matched_file,
        matched_sidecar,
        matched_sidecar_shm,
        matched_dir / "manifest.json",
        unmatched_file,
        unmatched_dir / "manifest.json",
    ):
        _write(path)

    deleted = purge_user_artifacts([str(artifact_root)], 42)

    assert deleted == 4
    assert not matched_file.exists()
    assert not matched_sidecar.exists()
    assert not matched_sidecar_shm.exists()
    assert not matched_dir.exists()
    assert unmatched_file.exists()
    assert unmatched_dir.exists()


def test_purge_user_artifacts_ignores_missing_roots(tmp_path):
    assert purge_user_artifacts([str(tmp_path / "missing")], 42) == 0
