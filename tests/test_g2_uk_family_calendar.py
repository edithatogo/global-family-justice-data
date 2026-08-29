from gfjd.g2_uk_family_calendar import evaluate_calendar

CONTRACT = {
    "section_id": "publication-courts-family",
    "expected_title": "Family court statistics quarterly",
    "expected_source_url": "https://www.gov.uk/government/collections/family-court-statistics-quarterly",
    "expected_schedule_text": (
        "Published: 25 June 2026. Next publication: 24 September 2026 9:30am."
    ),
}


def _html(schedule: str = CONTRACT["expected_schedule_text"]) -> str:
    return f"""<h2 id="publication-courts-family">Family court statistics quarterly</h2>
<p><a href="https://www.gov.uk/government/collections/family-court-statistics-quarterly">
Source</a></p><p>{schedule}</p><h2 id="next">Next</h2>"""


def test_baseline_is_unchanged() -> None:
    observation, outcome = evaluate_calendar(_html(), CONTRACT)
    assert outcome == "baseline_unchanged"
    assert observation["title"] == "Family court statistics quarterly"


def test_schedule_change_requires_review() -> None:
    _, outcome = evaluate_calendar(
        _html("Published: 24 September 2026. Next publication: 17 December 2026 9:30am."), CONTRACT
    )
    assert outcome == "review_required"
