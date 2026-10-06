import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from scripts.build_resume import extract_resume, prepare_pdf_docx


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
    segments = text.split("\t")
    for index, segment in enumerate(segments):
        if segment:
            run = ElementTree.SubElement(paragraph, f"{{{WORD_NS}}}r")
            ElementTree.SubElement(run, f"{{{WORD_NS}}}t").text = segment
        if index < len(segments) - 1:
            run = ElementTree.SubElement(paragraph, f"{{{WORD_NS}}}r")
            ElementTree.SubElement(run, f"{{{WORD_NS}}}tab")
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
                        "location": "",
                        "subtitle": "Bachelor of Example Studies",
                        "dates": "",
                        "details": [],
                    }
                ],
                "experience": [
                    {
                        "title": "Example Maker",
                        "location": "",
                        "subtitle": "Example Workshop · 2024-present",
                        "dates": "",
                        "details": [],
                    }
                ],
                "skills": ["Woodworking", "Machining"],
            },
        )

    def test_splits_tab_aligned_location_and_dates(self):
        paragraphs = [
            make_paragraph("Education", "Heading1"),
            make_paragraph("Example University\t\tSpringfield, IL", "Heading2"),
            make_paragraph("Bachelor of Science\t\t2020 - 2024"),
            make_paragraph("Experience", "Heading1"),
            make_paragraph("Example Workshop\t\tPortland, OR", "Heading2"),
            make_paragraph("Project Maker\t\t2024 - Present"),
            make_paragraph("Designed and built custom furniture"),
            make_paragraph("Skills", "Heading1"),
            make_paragraph("Woodworking"),
        ]

        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "resume.docx"
            make_docx(docx_path, paragraphs)
            resume = extract_resume(docx_path)

        self.assertEqual(
            resume["education"][0],
            {
                "institution": "Example University",
                "location": "Springfield, IL",
                "subtitle": "Bachelor of Science",
                "dates": "2020 - 2024",
                "details": [],
            },
        )
        self.assertEqual(
            resume["experience"][0],
            {
                "title": "Example Workshop",
                "location": "Portland, OR",
                "subtitle": "Project Maker",
                "dates": "2024 - Present",
                "details": ["Designed and built custom furniture"],
            },
        )

    def test_extracts_multiple_positions_under_one_employer(self):
        paragraphs = [
            make_paragraph("Education", "Heading1"),
            make_paragraph("Example University\t\tSpringfield, IL", "Heading2"),
            make_paragraph("Bachelor of Science\t\t2020 - 2024"),
            make_paragraph("Experience", "Heading1"),
            make_paragraph("Example Company\t\tDenver, CO"),
            make_paragraph("Sales Representative\t\tMay 2021 - May 2024"),
            make_paragraph("Managed sales accounts"),
            make_paragraph("Content Author\t\tMay 2021 - July 2023"),
            make_paragraph("Wrote and edited articles"),
            make_paragraph("Skills", "Heading1"),
            make_paragraph("Writing"),
        ]

        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "resume.docx"
            make_docx(docx_path, paragraphs)
            resume = extract_resume(docx_path)

        self.assertEqual(
            resume["experience"],
            [
                {
                    "title": "Example Company",
                    "location": "Denver, CO",
                    "subtitle": "Sales Representative",
                    "dates": "May 2021 - May 2024",
                    "details": ["Managed sales accounts"],
                },
                {
                    "title": "Example Company",
                    "location": "Denver, CO",
                    "subtitle": "Content Author",
                    "dates": "May 2021 - July 2023",
                    "details": ["Wrote and edited articles"],
                },
            ],
        )

    def test_rejects_missing_required_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "resume.docx"
            make_docx(docx_path, [make_paragraph("Education", "Heading1")])

            with self.assertRaisesRegex(ValueError, "Heading 1 sections"):
                extract_resume(docx_path)

    def test_prepares_pdf_tabs_and_bullets_for_conversion(self):
        document_xml = (
            '<w:document xmlns:w="{}"><w:body>'
            '<w:p><w:pPr><w:rPr><w:b/></w:rPr></w:pPr>'
            '<w:r><w:t>Company</w:t></w:r>'
            '<w:r><w:tab/><w:tab/><w:t xml:space="preserve">  City</w:t></w:r></w:p>'
            '<w:sectPr><w:pgSz w:w="12240"/>'
            '<w:pgMar w:left="720" w:right="720"/></w:sectPr>'
            '</w:body></w:document>'
        ).format(WORD_NS)
        numbering_xml = (
            '<w:numbering xmlns:w="{}"><w:abstractNum><w:lvl>'
            '<w:numFmt w:val="bullet"/><w:lvlText w:val="●"/>'
            '</w:lvl><w:lvl><w:numFmt w:val="decimal"/>'
            '<w:lvlText w:val="%1."/></w:lvl></w:abstractNum></w:numbering>'
        ).format(WORD_NS)

        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "source.docx"
            prepared_path = Path(directory) / "prepared.docx"
            with zipfile.ZipFile(source_path, "w") as archive:
                archive.writestr("word/document.xml", document_xml)
                archive.writestr("word/numbering.xml", numbering_xml)

            prepare_pdf_docx(source_path, prepared_path)

            with zipfile.ZipFile(prepared_path) as archive:
                prepared_document = archive.read("word/document.xml").decode("utf-8")
                prepared_numbering = archive.read("word/numbering.xml").decode("utf-8")

        self.assertNotIn("<w:tab/>", prepared_document)
        self.assertIn("<w:t xml:space=\"preserve\">  |  </w:t>", prepared_document)
        self.assertIn("<w:t xml:space=\"preserve\">City</w:t>", prepared_document)
        self.assertIn('<w:lvlText w:val="•"/>', prepared_numbering)
        self.assertIn('w:ascii="Liberation Sans"', prepared_numbering)
        self.assertIn('<w:lvlText w:val="%1."/>', prepared_numbering)


if __name__ == "__main__":
    unittest.main()
