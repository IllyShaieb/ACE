"""Ensure the formatters correctly convert text between different formats."""

import pytest

from src.formatter import markdown_to_html


@pytest.mark.parametrize(
    "markdown_input, expected_html_output",
    [
        (
            "# Heading\n\nThis is a **bold** text.",
            "<h1>Heading</h1>\n<p>This is a <strong>bold</strong> text.</p>",
        ),
        (
            "## Subheading\n\nThis is *italic* text.",
            "<h2>Subheading</h2>\n<p>This is <em>italic</em> text.</p>",
        ),
        (
            "- Item 1\n- Item 2\n- Item 3",
            "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n<li>Item 3</li>\n</ul>",
        ),
        (
            "1. First\n2. Second\n3. Third",
            "<ol>\n<li>First</li>\n<li>Second</li>\n<li>Third</li>\n</ol>",
        ),
        (
            "[Link](https://example.com)",
            '<p><a href="https://example.com">Link</a></p>',
        ),
    ],
)
def test_markdown_to_html_conversion(markdown_input, expected_html_output):
    """Test that the markdown_to_html function correctly converts markdown to HTML."""
    # ACT and ARRANGE: Convert the markdown input to HTML using the formatter
    html_output = markdown_to_html(markdown_input)

    # ASSERT: Verify that the output matches the expected HTML output
    assert html_output == expected_html_output
