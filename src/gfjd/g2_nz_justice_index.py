"""Parse a bounded NZ Ministry of Justice publication index."""

from __future__ import annotations

from html.parser import HTMLParser


class _IndexParser(HTMLParser):
    def __init__(self, tokens: list[str]) -> None:
        super().__init__()
        self.tokens = tokens
        self.locators: list[str] = []
        self.page_date_text = ""
        self.datetime_attribute = ""
        self._in_last_published = False
        self._in_time = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "p" and "last-published" in (values.get("class") or "").split():
            self._in_last_published = True
        if tag == "time" and self._in_last_published:
            self._in_time = True
            self.datetime_attribute = values.get("datetime") or ""
        if tag == "a":
            href = values.get("href") or ""
            if any(token in href for token in self.tokens):
                self.locators.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "time":
            self._in_time = False
        if tag == "p" and self._in_last_published:
            self._in_last_published = False

    def handle_data(self, data: str) -> None:
        if self._in_time:
            self.page_date_text += data.strip()


def evaluate_index(html: str, contract: dict[str, object]) -> tuple[dict[str, object], str]:
    """Return a metadata observation and whether the frozen baseline changed."""

    tokens = contract["locator_tokens"]
    expected = contract["expected_locators"]
    if not isinstance(tokens, list) or not all(isinstance(value, str) for value in tokens):
        raise ValueError("invalid locator-token contract")
    if not isinstance(expected, list) or not all(isinstance(value, str) for value in expected):
        raise ValueError("invalid expected-locator contract")
    parser = _IndexParser(tokens)
    parser.feed(html)
    if len(parser.locators) != len(tokens) or len(set(parser.locators)) != len(tokens):
        raise ValueError("family-justice locator enumeration is incomplete or ambiguous")
    for locator in parser.locators:
        if not locator.startswith("/assets/Documents/Publications/"):
            raise ValueError("prohibited family-justice locator")
    if not parser.page_date_text:
        raise ValueError("visible page update date is missing")
    observation = {
        "page_date_text": parser.page_date_text,
        "datetime_attribute": parser.datetime_attribute,
        "datetime_attribute_accepted": False,
        "locators": sorted(parser.locators),
    }
    changed = (
        parser.page_date_text != contract["expected_page_date_text"]
        or parser.datetime_attribute != contract["expected_datetime_attribute"]
        or sorted(parser.locators) != sorted(expected)
    )
    return observation, "review_required" if changed else "baseline_unchanged"
