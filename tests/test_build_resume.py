import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from scripts.build_resume import extract_resume


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def make_paragraph(text, style=""):
    paragraph = ElementTree.Element(f"{{{WORD_NS}}}p")
    if style:
        properties = ElementTree.SubElement(paragraph, f"{{{WORD_NS}}}pPr")
        ElementTree.SubElement(
            properties,
            f"{{{WORD_NS}}}pStyle",
            {f"{{{WORD_NS}}}val": style},
        )
    run = ElementTree.SubElement(paragraph, f"{{{WORD_NS}}}r")
    ElementTree.SubElement(run, f"{{{WORD_NS}}}t").text = text
    return paragraph


def make_docx(path, paragraphs):
    document = ElementTree.Element(f"{{{WORD_NS}}}document")
    body = ElementTree.SubElement(document, f"{{{WORD_NS}}}body")
    for paragraph in paragraphs:
        body.append(paragraph)

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", ElementTree.tostring(document))


class BuildResumeTests(unittest.TestCase):
    def test_extracts_heading_sections_and_entries(self):
        paragraphs = [
            make_paragraph("Education", "Heading1"),
            make_paragraph("Example University", "Heading2"),
            make_paragraph("Bachelor of Example Studies"),
            make_paragraph("Experience", "Heading 1"),
            make_paragraph("Example Maker", "Heading 2"),
            make_paragraph("Example Workshop · 2024-present"),
            make_paragraph("Skills", "Heading 1"),
            make_paragraph("Woodworking"),
            make_paragraph("Machining"),
        ]

        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "resume.docx"
            make_docx(docx_path, paragraphs)
            resume = extract_resume(docx_path)

        self.assertEqual(
            resume,
            {
                "education": [
                    {
                        "institution": "Example University",
                        "details": ["Bachelor of Example Studies"],
                    }
                ],
                "experience": [
                    {
                        "title": "Example Maker",
                        "details": ["Example Workshop · 2024-present"],
                    }
                ],
                "skills": ["Woodworking", "Machining"],
            },
        )

    def test_rejects_missing_required_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "resume.docx"
            make_docx(docx_path, [make_paragraph("Education", "Heading1")])

            with self.assertRaisesRegex(ValueError, "Heading 1 sections"):
                extract_resume(docx_path)


if __name__ == "__main__":
    unittest.main()
