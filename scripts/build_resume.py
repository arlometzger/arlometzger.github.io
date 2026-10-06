#!/usr/bin/env python3
"""Build website resume data from a DOCX and reference its existing PDF."""

import argparse
import json
import re
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


def is_date_field(value):
    return bool(re.search(r"\b(?:19|20)\d{2}\b", value))


def get_experience_employer(resume, organization, location):
    return next(
        (
            employer
            for employer in resume["experience"]
            if employer["title"] == organization and employer["location"] == location
        ),
        None,
    )


def add_experience_position(employer, fields):
    position = {
        "title": fields[0],
        "dates": fields[-1] if len(fields) > 1 else "",
        "details": fields[1:-1] if len(fields) > 2 else [],
    }
    employer["positions"].append(position)
    return position


def extract_resume(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        raise ValueError(f"Could not read DOCX resume: {error}") from error

    resume = {"education": [], "experience": [], "skills": []}
    section = None
    current_entry = None
    current_employer = None
    current_position = None
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
            current_employer = None
            current_position = None
            continue

        if section == "skills":
            resume["skills"].extend(fields)
            continue

        is_date_row = len(fields) > 1 and is_date_field(fields[-1])
        is_organization_row = (
            section == "experience"
            and not is_date_row
            and (level == 2 or len(fields) > 1)
        )
        is_education_row = (
            section == "education"
            and not is_date_row
            and (level == 2 or len(fields) > 1)
        )

        if is_organization_row:
            current_employer = get_experience_employer(
                resume,
                fields[0],
                fields[-1] if len(fields) > 1 else "",
            )
            if current_employer is None:
                current_employer = {
                    "title": fields[0],
                    "location": fields[-1] if len(fields) > 1 else "",
                    "positions": [],
                }
                resume["experience"].append(current_employer)
            current_position = None
        elif section == "experience" and is_date_row and current_employer:
            current_position = add_experience_position(current_employer, fields)
        elif section == "experience" and current_employer and len(fields) == 1:
            if current_position is None:
                current_position = add_experience_position(current_employer, fields)
            else:
                current_position["details"].append(fields[0].lstrip("• ").strip())
        elif is_education_row:
            current_entry = {
                "institution": fields[0],
                "location": fields[-1] if len(fields) > 1 else "",
                "subtitle": "",
                "dates": "",
                "details": [],
            }
            resume["education"].append(current_entry)
        elif section == "education" and is_date_row and current_entry is not None:
            current_entry["subtitle"] = fields[0]
            current_entry["dates"] = fields[-1]
            current_entry["details"].extend(fields[1:-1])
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Source DOCX resume")
    parser.add_argument("--data-output", type=Path, required=True, help="Generated JS data file")
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path("ArloMetzgerResume.pdf"),
        help="Existing PDF download to reference",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Source DOCX does not exist: {args.input}")
    if not args.pdf.is_file():
        parser.error(f"Matching PDF download does not exist: {args.pdf}")

    resume = extract_resume(args.input)
    resume["pdfUrl"] = args.pdf.as_posix()
    args.data_output.parent.mkdir(parents=True, exist_ok=True)
    args.data_output.write_text(
        "window.resumeData = "
        + json.dumps(resume, ensure_ascii=False, indent=4)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
