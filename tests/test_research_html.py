"""Dependency-free structural checks for the offline research pages.

Run from the repository root: python3 -m unittest discover -s tests -v
These checks do not replace browser, visual, keyboard, print, or source review.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted((ROOT / "docs/research").glob("*.html"))
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Page:
    """The authored structure needed for cross-page validation."""

    source: str
    ids: set[str] = field(default_factory=set)
    duplicates: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    aria_targets: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    outline: list[str] = field(default_factory=list)
    slides: list[str] = field(default_factory=list)
    footers: list[str] = field(default_factory=list)
    body_classes: set[str] = field(default_factory=set)
    language: str = ""
    theme: str = ""
    description: str = ""
    viewport: str = ""
    h1_count: int = 0
    main_count: int = 0


class Inspector(HTMLParser):
    """Inspect our explicit, balanced markup—not arbitrary HTML5 tag recovery."""

    def __init__(self, page: Page) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.footer_index: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        classes = set(values.get("class", "").split())
        identity = values.get("id", "")
        if identity:
            if identity in self.page.ids:
                self.page.duplicates.append(identity)
            self.page.ids.add(identity)
        for key in ("aria-labelledby", "aria-describedby", "aria-controls"):
            self.page.aria_targets.extend(values.get(key, "").split())
        if tag == "html":
            self.page.language = values.get("lang", "")
            self.page.theme = values.get("data-io-theme", "")
        elif tag == "body":
            self.page.body_classes = classes
        elif tag == "meta":
            if values.get("name") == "description":
                self.page.description = values.get("content", "")
            elif values.get("name") == "viewport":
                self.page.viewport = values.get("content", "")
        elif tag == "h1":
            self.page.h1_count += 1
        elif tag == "main":
            self.page.main_count += 1
        elif tag == "a":
            href = values.get("href", "")
            self.page.links.append(href)
            if any("deck-nav" in ancestor.get("class", "").split() or
                   "research-index" in ancestor.get("class", "").split()
                   for _, ancestor in self.stack):
                self.page.outline.append(href)
        if tag == "section" and any(parent == "main" for parent, _ in self.stack):
            if not any(parent == "section" for parent, _ in self.stack):
                self.page.sections.append(identity)
            if "slide" in classes:
                self.page.slides.append(identity)
                assert values.get("tabindex") == "-1", "Slides must accept native fragment focus"
                assert values.get("aria-labelledby"), "Slides need a named heading"
        if tag == "footer" and "slide-footer" in classes:
            self.footer_index = len(self.page.footers)
            self.page.footers.append("")
        if tag == "link" and "stylesheet" in values.get("rel", "").split():
            self.page.assets.append(values.get("href", ""))
        if tag == "script" and values.get("src"):
            self.page.assets.append(values["src"])
        if tag not in VOID_TAGS:
            self.stack.append((tag, values))

    def handle_endtag(self, tag: str) -> None:
        assert self.stack and self.stack[-1][0] == tag, f"Unbalanced closing tag: {tag}"
        self.stack.pop()
        if tag == "footer":
            self.footer_index = None

    def handle_data(self, data: str) -> None:
        if self.footer_index is not None:
            self.page.footers[self.footer_index] += data


@cache
def inspect(path: Path) -> Page:
    page = Page(source=path.read_text(encoding="utf-8"))
    parser = Inspector(page)
    parser.feed(page.source)
    parser.close()
    assert not parser.stack, f"Unclosed tags in {path.name}: {parser.stack}"
    return page


class ResearchHTMLTests(unittest.TestCase):
    def test_semantics_and_labels(self) -> None:
        self.assertTrue(PAGES)
        for path in PAGES:
            with self.subTest(page=path.name):
                page = inspect(path)
                self.assertFalse(page.duplicates)
                self.assertEqual((page.language, page.theme), ("en", "v2"))
                self.assertEqual((page.h1_count, page.main_count), (1, 1))
                self.assertTrue(page.description)
                self.assertIn("width=device-width", page.viewport)
                self.assertTrue(set(page.aria_targets) <= page.ids)
                self.assertRegex(page.source, r'class="skip-link"\s+href="#')
                self.assertTrue(all(page.sections))

    def test_local_links_and_offline_assets(self) -> None:
        for path in PAGES:
            page = inspect(path)
            for target in page.links + page.assets:
                with self.subTest(page=path.name, target=target):
                    parsed = urlsplit(target)
                    if parsed.scheme or parsed.netloc:
                        self.assertNotIn(target, page.assets, "Reading must not require remote assets")
                        continue
                    destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
                    self.assertTrue(destination.is_file(), f"Missing local target: {target}")
                    if parsed.fragment and destination.suffix == ".html":
                        self.assertIn(unquote(parsed.fragment), inspect(destination).ids)
            sheets = [asset for asset in page.assets if urlsplit(asset).path.endswith(".css")]
            self.assertTrue(sheets[0].endswith("io-design-system.css"))
            self.assertTrue(sheets[-1].endswith("io-theme-v2.css"))

    def test_outlines_and_slide_counts(self) -> None:
        for path in PAGES:
            with self.subTest(page=path.name):
                page = inspect(path)
                self.assertEqual(page.outline, [f"#{identity}" for identity in page.sections])
                if "io-presentation" not in page.body_classes:
                    continue
                self.assertEqual(len(page.footers), len(page.slides))
                for index, footer in enumerate(page.footers, start=1):
                    self.assertIn(f"{index:02d} / {len(page.slides):02d}", footer)
        self.assertEqual(len(inspect(ROOT / "docs/research/cognitive-routing-research-document.html").sections), 10)
        self.assertEqual(len(inspect(ROOT / "docs/research/cognitive-routing-presentation-deck.html").slides), 12)

    def test_native_mathml(self) -> None:
        for path in PAGES:
            for fragment in re.findall(r"<math\b.*?</math>", inspect(path).source, re.S):
                with self.subTest(page=path.name, equation=fragment[:80]):
                    node = ET.fromstring(fragment)
                    self.assertEqual(node.tag, "{http://www.w3.org/1998/Math/MathML}math")


if __name__ == "__main__":
    unittest.main()
