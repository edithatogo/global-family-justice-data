from pathlib import Path

from gfjd.products import build_products, verify_products


def test_candidate_product_bundle_is_reproducible_and_fail_closed(project_root: Path) -> None:
    output = project_root / "build" / "test-products"
    result = build_products(project_root, output)
    assert "index.html" in result.artifacts
    html = (output / "index.html").read_text(encoding="utf-8")
    for marker in (
        "lang='en'",
        "viewport",
        "Skip to main content",
        "Limitations and responsible use",
        "Corrections and takedown",
    ):
        assert marker in html
    assert verify_products(project_root, output) == []
    manifest = output / "manifest.json"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            '"publication_authorized": false', '"publication_authorized": true'
        ),
        encoding="utf-8",
    )
    assert any("publication_authorized" in error for error in verify_products(project_root, output))


def test_candidate_product_verifier_rejects_inaccessible_html(project_root: Path) -> None:
    output = project_root / "build" / "test-products-accessibility"
    build_products(project_root, output)
    (output / "index.html").write_text(
        "<html><body><h1>broken</h1></body></html>\n", encoding="utf-8"
    )
    errors = verify_products(project_root, output)
    assert any("responsive viewport" in error for error in errors)
    assert any("responsible-use guidance" in error for error in errors)
