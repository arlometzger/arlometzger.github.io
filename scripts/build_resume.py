#!/usr/bin/env python3
"""Build website resume data and a PDF from a structured DOCX resume."""

import argparse
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SECTIONS = {"education", "experience", "skills"}


def paragraph_fields(paragraph):
    fields = [""]
    for node in paragraph.iter():
        if node.tag == f"{WORD_NS}t":
            fields[-1] += node.text or ""
        elif node.tag == f"{WORD_NS}tab":
            fields.append("")
        elif node.tag == f"{WORD_NS}br":
            fields.append("")
    return [field.strip() for field in fields if field.strip()]


def paragraph_text(paragraph):
    return " ".join(paragraph_fields(paragraph))


def paragraph_style(paragraph):
    style = paragraph.find(f"{WORD_NS}pPr/{WORD_NS}pStyle")
    if style is None:
        return ""
    return style.attrib.get(f"{WORD_NS}val", "").replace("_", " ").lower()


def heading_level(style):
    compact_style = style.replace(" ", "")
    if compact_style in {"heading1", "title1"}:
        return 1
    if compact_style in {"heading2", "title2"}:
        return 2
    return 0


def extract_resume(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        raise ValueError(f"Could not read DOCX resume: {error}") from error

    resume = {"education": [], "experience": [], "skills": []}
    section = None
    current_entry = None
    seen_sections = set()

    for paragraph in document.iter(f"{WORD_NS}p"):
        fields = paragraph_fields(paragraph)
        if not fields:
            continue

        level = heading_level(paragraph_style(paragraph))
        text = " ".join(fields)
        normalized_text = text.lower()
        if level == 1 and normalized_text in SECTIONS:
            section = normalized_text
            seen_sections.add(section)
            current_entry = None
            continue

        if section == "skills":
            resume["skills"].extend(fields)
            continue

        if section in {"education", "experience"} and level == 2:
            key = "institution" if section == "education" else "title"
            current_entry = {
                key: fields[0],
                "location": fields[-1] if len(fields) > 1 else "",
                "subtitle": "",
                "dates": "",
                "details": [],
            }
            resume[section].append(current_entry)
        elif section in {"education", "experience"} and current_entry is not None:
            if not current_entry["subtitle"]:
                current_entry["subtitle"] = fields[0]
                if len(fields) > 1:
                    current_entry["dates"] = fields[-1]
                    current_entry["details"].extend(fields[1:-1])
            else:
                current_entry["details"].extend(fields)

    missing_sections = SECTIONS - seen_sections
    if missing_sections:
        raise ValueError(
            "DOCX must have Heading 1 sections named Education, Experience, and Skills."
        )

    for section in ("education", "experience"):
        if not resume[section]:
            raise ValueError(
                f"Add at least one Heading 2 entry under the {section.title()} section."
            )
    if not resume["skills"]:
        raise ValueError("Add at least one paragraph under the Skills section.")

    return resume


def make_pdf(docx_path, pdf_path):
    converter = shutil.which("libreoffice") or shutil.which("soffice")
    if not converter:
        raise RuntimeError("LibreOffice is required to convert the DOCX resume to PDF.")

    with tempfile.TemporaryDirectory() as output_directory:
        result = subprocess.run(
            [
                converter,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_directory,
                str(docx_path.resolve()),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        generated_pdf = Path(output_directory) / f"{docx_path.stem}.pdf"
        if result.returncode != 0 or not generated_pdf.is_file():
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"LibreOffice could not generate the resume PDF. {detail}")

        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(generated_pdf, pdf_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Source DOCX resume")
    parser.add_argument("--data-output", type=Path, required=True, help="Generated JS data file")
    parser.add_argument("--pdf-output", type=Path, help="Generated PDF path")
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="Generate website data without converting the document to PDF",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Source DOCX does not exist: {args.input}")
    if not args.data_only and not args.pdf_output:
        parser.error("--pdf-output is required unless --data-only is set")

    resume = extract_resume(args.input)
    resume["pdfUrl"] = (
        args.pdf_output.name if args.pdf_output else "ArloMetzgerResume.pdf"
    )
    args.data_output.parent.mkdir(parents=True, exist_ok=True)
    args.data_output.write_text(
        "window.resumeData = "
        + json.dumps(resume, ensure_ascii=False, indent=4)
        + ";\n",
        encoding="utf-8",
    )
    if not args.data_only:
        make_pdf(args.input, args.pdf_output)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as error:
        raise SystemExit(str(error)) from error
