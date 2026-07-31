from gfjd.resilience import _entry_set_sha256


def test_entry_set_digest_is_independent_of_filesystem_traversal_order() -> None:
    entries = [
        ("b" * 64, "data/seed/source_edition_template.csv"),
        ("a" * 64, "config/project.toml"),
    ]

    assert _entry_set_sha256(entries) == _entry_set_sha256(reversed(entries))
