from gfjd.g2_nz_justice_index import evaluate_index

CONTRACT = {
    "locator_tokens": ["Family-Court-applications_", "Children-adopted_"],
    "expected_locators": [
        "/assets/Documents/Publications/a_Family-Court-applications_dec2025.xlsx",
        "/assets/Documents/Publications/b_Children-adopted_dec2025.xlsx",
    ],
    "expected_page_date_text": "17th March 2026",
    "expected_datetime_attribute": "2026-45-17",
}


def _html(date: str = "17th March 2026") -> str:
    return f"""<a href="/assets/Documents/Publications/a_Family-Court-applications_dec2025.xlsx">
A</a>
<a href="/assets/Documents/Publications/b_Children-adopted_dec2025.xlsx">B</a>
<p class="last-published">Updated <time datetime="2026-45-17">{date}</time></p>"""


def test_frozen_baseline_is_unchanged_and_datetime_is_rejected() -> None:
    observation, outcome = evaluate_index(_html(), CONTRACT)
    assert outcome == "baseline_unchanged"
    assert observation["datetime_attribute"] == "2026-45-17"
    assert observation["datetime_attribute_accepted"] is False


def test_visible_date_change_requires_review() -> None:
    _, outcome = evaluate_index(_html("1st September 2026"), CONTRACT)
    assert outcome == "review_required"


def test_machine_date_correction_requires_review_but_is_not_accepted() -> None:
    html = _html().replace('datetime="2026-45-17"', 'datetime="2026-03-17"')
    observation, outcome = evaluate_index(html, CONTRACT)
    assert outcome == "review_required"
    assert observation["datetime_attribute_accepted"] is False


def test_missing_locator_fails_closed() -> None:
    try:
        evaluate_index('<p class="last-published"><time>17th March 2026</time></p>', CONTRACT)
    except ValueError as exc:
        assert "incomplete or ambiguous" in str(exc)
    else:
        raise AssertionError("missing locators must fail closed")
