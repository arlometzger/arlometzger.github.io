import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

from scripts.build_resume import extract_resume, main


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
                        "positions": [
                            {
                                "title": "Example Workshop · 2024-present",
                                "dates": "",
                                "details": [],
                            }
                        ],
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
                "positions": [
                    {
                        "title": "Project Maker",
                        "dates": "2024 - Present",
                        "details": ["Designed and built custom furniture"],
                    }
                ],
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
                    "positions": [
                        {
                            "title": "Sales Representative",
                            "dates": "May 2021 - May 2024",
                            "details": ["Managed sales accounts"],
                        },
                        {
                            "title": "Content Author",
                            "dates": "May 2021 - July 2023",
                            "details": ["Wrote and edited articles"],
                        },
                    ],
                },
            ],
        )

    def test_rejects_missing_required_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            docx_path = Path(directory) / "resume.docx"
            make_docx(docx_path, [make_paragraph("Education", "Heading1")])

            with self.assertRaisesRegex(ValueError, "Heading 1 sections"):
                extract_resume(docx_path)

    def test_build_references_existing_pdf_without_modifying_it(self):
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "resume.docx"
            pdf_path = Path(directory) / "ArloMetzgerResume.pdf"
            data_path = Path(directory) / "resume-data.js"
            make_docx(
                source_path,
                [
                    make_paragraph("Education", "Heading1"),
                    make_paragraph("Example University", "Heading2"),
                    make_paragraph("Bachelor of Example Studies"),
                    make_paragraph("Experience", "Heading1"),
                    make_paragraph("Example Maker", "Heading2"),
                    make_paragraph("Example Workshop · 2024-present"),
                    make_paragraph("Skills", "Heading1"),
                    make_paragraph("Woodworking"),
                ],
            )
            pdf_path.write_bytes(b"user-supplied-pdf")

            with patch(
                "sys.argv",
                [
                    "build_resume.py",
                    "--input",
                    str(source_path),
                    "--data-output",
                    str(data_path),
                    "--pdf",
                    str(pdf_path),
                ],
            ):
                main()

            self.assertIn(f'"pdfUrl": "{pdf_path.as_posix()}"', data_path.read_text())
            self.assertEqual(pdf_path.read_bytes(), b"user-supplied-pdf")


if __name__ == "__main__":
    unittest.main()
