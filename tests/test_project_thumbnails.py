from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectCardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.current_card = None
        self.card_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if self.current_card is None and "project-card" in classes:
            self.current_card = {"images": [], "fallbacks": []}
            self.card_depth = 1
            return

        if self.current_card is None:
            return

        if tag not in {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
        }:
            self.card_depth += 1

        if tag == "img" and "project-image" in classes:
            self.current_card["images"].append(attributes)
        elif tag == "div" and "project-image-fallback" in classes:
            self.current_card["fallbacks"].append(attributes)

    def handle_endtag(self, tag):
        if self.current_card is None:
            return

        self.card_depth -= 1
        if self.card_depth == 0:
            self.cards.append(self.current_card)
            self.current_card = None


def test_every_project_card_has_a_unique_accessible_thumbnail_and_fallback():
    parser = ProjectCardParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

    assert parser.cards, "No project cards were found"
    image_paths = []

    for index, card in enumerate(parser.cards, start=1):
        assert len(card["images"]) == 1, f"Project card {index} must have one thumbnail"
        assert len(card["fallbacks"]) == 1, f"Project card {index} must have one image fallback"

        image = card["images"][0]
        source = image.get("src", "")
        alt = image.get("alt", "").strip()
        assert source, f"Project card {index} thumbnail must have a source"
        assert alt, f"Project card {index} thumbnail must have descriptive alternative text"
        assert (ROOT / source).is_file(), f"Project card {index} image does not exist: {source}"
        image_paths.append(source)

        fallback = card["fallbacks"][0]
        assert fallback.get("hidden") is None or fallback.get("hidden") == "", (
            f"Project card {index} fallback must start hidden"
        )
        assert fallback.get("aria-label", "").strip(), (
            f"Project card {index} fallback must have an accessible label"
        )

    assert len(set(image_paths)) == len(parser.cards), "Each project must have its own thumbnail"
