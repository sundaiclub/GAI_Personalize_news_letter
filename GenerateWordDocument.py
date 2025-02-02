from docx import Document


def generate_word_doc_from_markdown(mark_down_text: str) -> Document:
    """
    Converts markdown text into a Word Document object, preserving headers,
    paragraphs, and bullet lists.
    """
    doc = Document()
    # Split the input text into lines for processing
    lines = mark_down_text.splitlines()
    # We'll accumulate consecutive lines (that are not headers or list items) into a paragraph.
    paragraph_lines = []

    def flush_paragraph_lines():
        """Add the accumulated lines as a single paragraph and then clear the accumulator."""
        if paragraph_lines:
            paragraph_text = " ".join(paragraph_lines)
            doc.add_paragraph(paragraph_text)
            paragraph_lines.clear()

    for line in lines:
        stripped = line.strip()
        # If the line is empty, flush any accumulated paragraph lines.
        if not stripped:
            flush_paragraph_lines()
            continue

        # Check for markdown headers (lines starting with one or more '#' characters).
        if stripped.startswith("#"):
            flush_paragraph_lines()
            # Count the number of '#' characters to determine header level.
            header_level = 0
            while header_level < len(stripped) and stripped[header_level] == "#":
                header_level += 1
            # Limit header levels to Word's standard (1-6)
            header_level = min(header_level, 6)
            header_text = stripped[header_level:].strip()
            doc.add_heading(header_text, level=header_level)
        # Check for unordered list items (lines starting with '-', '*', or '+')
        elif stripped[0] in "-*+":
            flush_paragraph_lines()
            # Remove the list marker and any extra whitespace
            list_text = stripped[1:].strip()
            doc.add_paragraph(list_text, style='List Bullet')
        else:
            # If the line does not match a special markdown element, add it to the current paragraph.
            paragraph_lines.append(stripped)

    # Flush any remaining paragraph content after the loop
    flush_paragraph_lines()

    return doc


# Example usage:
if __name__ == '__main__':
    # Example markdown text
    markdown_input = """
# Header 1
This is the first paragraph of the document.

## Header 2
This is another paragraph that follows a header.

- Item 1 in a list
- Item 2 in a list

Another paragraph here.
    """
    # Generate the document from the markdown text.
    document = generate_word_doc_from_markdown(markdown_input)
    # Save the document to a file.
    document.save("output.docx")
    print("Word document 'output.docx' created successfully.")
