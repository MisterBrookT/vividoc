"""HTML validation for generated interactive components."""

from html.parser import HTMLParser
from typing import List, Tuple


class HTMLStructureParser(HTMLParser):
    """Parser that tracks HTML structure for validation."""

    SELF_CLOSING_TAGS = {
        "img",
        "br",
        "hr",
        "input",
        "meta",
        "link",
        "area",
        "base",
        "col",
        "embed",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__()
        self.tag_stack: List[str] = []
        self.root_tag: str = None
        self.root_classes: List[str] = []
        self.root_id: str = None
        self.unclosed_tags: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        """Handle opening tags."""
        if not self.root_tag:
            self.root_tag = tag
            attrs_dict = dict(attrs)
            self.root_id = attrs_dict.get("id", "")
            class_attr = attrs_dict.get("class", "")
            self.root_classes = class_attr.split() if class_attr else []

        if tag not in self.SELF_CLOSING_TAGS:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag: str):
        """Handle closing tags."""
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif tag not in self.SELF_CLOSING_TAGS:
            self.unclosed_tags.append(tag)

    def close(self):
        """Finalize parsing and check for unclosed tags."""
        super().close()
        if self.tag_stack:
            self.unclosed_tags.extend(self.tag_stack)


class HTMLValidator:
    """Validates HTML sections for structure and correctness."""

    def validate(self, html_code: str) -> tuple[bool, str]:
        """Validate HTML section.

        Checks:
        - Well-formed HTML structure
        - Root element is <section> with class "knowledge-unit"
        - Section has an id attribute
        - All opening tags have matching closing tags

        Args:
            html_code: HTML section to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        parser = HTMLStructureParser()

        try:
            parser.feed(html_code)
            parser.close()

            if not parser.root_tag:
                return False, "No root element found"

            if parser.root_tag != "section":
                return (
                    False,
                    f"Root element must be <section>, found <{parser.root_tag}>",
                )

            if "knowledge-unit" not in parser.root_classes:
                return False, "Root <section> must have class 'knowledge-unit'"

            if not parser.root_id:
                return False, "Root <section> must have an id attribute"

            if parser.unclosed_tags:
                return False, f"Unclosed tags: {', '.join(parser.unclosed_tags)}"

            return True, ""

        except Exception as e:
            return False, f"HTML parsing error: {str(e)}"
