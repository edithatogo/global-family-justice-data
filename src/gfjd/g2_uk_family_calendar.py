"""Parse the exact UK Justice Data family-court publication-calendar section."""

from __future__ import annotations

from html.parser import HTMLParser


class _CalendarParser(HTMLParser):
    def __init__(self, section_id: str) -> None:
        super().__init__()
        self.section_id = section_id
        self.active = False
        self.in_heading = False
        self.in_paragraph = False
        self.heading = ""
        self.paragraphs: list[str] = []
        self.source_url = ""
        self._text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "h2":
            if self.active:
                self.active = False
            if values.get("id") == self.section_id:
                self.active = True
                self.in_heading = True
        elif self.active and tag == "p":
            self.in_paragraph = True
            self._text = ""
        elif self.active and tag == "a":
            href = values.get("href") or ""
            if href.startswith("https://www.gov.uk/government/collections/"):
                self.source_url = href

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2":
            self.in_heading = False
        elif tag == "p" and self.in_paragraph:
            normalized = " ".join(self._text.split())
            if normalized:
                self.paragraphs.append(normalized)
            self.in_paragraph = False

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.heading += data
        elif self.in_paragraph:
            self._text += data


def evaluate_calendar(html: str, contract: dict[str, object]) -> tuple[dict[str, str], str]:
    parser = _CalendarParser(str(contract["section_id"]))
    parser.feed(html)
    heading = " ".join(parser.heading.split())
    schedules = [value for value in parser.paragraphs if "Next publication:" in value]
    if heading != contract["expected_title"]:
        raise ValueError("family-court calendar heading missing or drifted")
    if parser.source_url != contract["expected_source_url"]:
        raise ValueError("family-court publication source missing or drifted")
    if len(schedules) != 1:
        raise ValueError("family-court schedule enumeration is ambiguous")
    observation = {"title": heading, "source_url": parser.source_url, "schedule_text": schedules[0]}
    outcome = (
        "baseline_unchanged"
        if schedules[0] == contract["expected_schedule_text"]
        else "review_required"
    )
    return observation, outcome
