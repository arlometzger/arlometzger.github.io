#!/usr/bin/env python3
"""Build website resume data and a PDF from a structured DOCX resume."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SECTIONS = {"education", "experience", "skills"}


def normalize_document_xml(document_xml):
    page_size = re.search(r"<w:pgSz\b([^>]*)>", document_xml)
    page_margins = re.search(r"<w:pgMar\b([^>]*)>", document_xml)
    if not page_size or not page_margins:
        raise ValueError("Could not determine DOCX page width and margins.")

    page_width = re.search(r'\bw:w="(\d+)"', page_size.group(1))
    left_margin = re.search(r'\bw:left="(\d+)"', page_margins.group(1))
    right_margin = re.search(r'\bw:right="(\d+)"', page_margins.group(1))
    if not page_width or not left_margin or not right_margin:
        raise ValueError("Could not determine DOCX page width and margins.")

    tab_position = (
        int(page_width.group(1))
        - int(left_margin.group(1))
        - int(right_margin.group(1))
    )
    if tab_position <= 0:
        raise ValueError("DOCX page margins leave no room for a right-aligned tab.")
    tab_stop = f'<w:tab w:val="right" w:pos="{tab_position}"/>'

    def normalize_paragraph(match):
        paragraph = match.group(0)
        if "<w:tab" not in paragraph:
            return paragraph

        paragraph = re.sub(r"(?:<w:tab\b[^>]*/>){2,}", "<w:tab/>", paragraph)
        paragraph = re.sub(
            r'(<w:tab\b[^>]*/>)(<w:t\b[^>]*>)[ \t]+',
            r"\1\2",
            paragraph,
            count=1,
        )

        tabs = re.search(r"<w:tabs\b[^>]*>.*?</w:tabs>", paragraph, re.DOTALL)
        if tabs:
            existing_stops = re.sub(
                r'<w:tab\b(?=[^>]*\bw:val="right")[^>]*/>',
                "",
                tabs.group(0),
            )
            paragraph = (
                paragraph[: tabs.start()]
                + existing_stops.replace("</w:tabs>", tab_stop + "</w:tabs>")
                + paragraph[tabs.end() :]
            )
        else:
            properties = re.search(
                r"<w:pPr\b[^>]*>.*?</w:pPr>",
                paragraph,
                re.DOTALL,
            )
            if properties:
                paragraph_properties = properties.group(0)
                run_properties = re.search(r"<w:rPr\b", paragraph_properties)
                insertion_point = (
                    run_properties.start()
                    if run_properties
                    else paragraph_properties.rfind("</w:pPr>")
                )
                updated_properties = (
                    paragraph_properties[:insertion_point]
                    + f"<w:tabs>{tab_stop}</w:tabs>"
                    + paragraph_properties[insertion_point:]
                )
                paragraph = (
                    paragraph[: properties.start()]
                    + updated_properties
                    + paragraph[properties.end() :]
                )
            else:
                paragraph = re.sub(
                    r"(<w:p\b[^>]*>)",
                    rf"\1<w:pPr><w:tabs>{tab_stop}</w:tabs></w:pPr>",
                    paragraph,
                    count=1,
                )
        return paragraph

    return re.sub(
        r"<w:p\b[^>]*>.*?</w:p>",
        normalize_paragraph,
        document_xml,
        flags=re.DOTALL,
    )


def normalize_numbering_xml(numbering_xml):
    def normalize_bullet_level(match):
        level = match.group(0)
        if not re.search(r'<w:numFmt\b[^>]*\bw:val="bullet"', level):
            return level

        level = re.sub(
            r'(<w:lvlText\b[^>]*\bw:val=")[^"]*(")',
            r"\1•\2",
            level,
            count=1,
        )
        bullet_font = (
            '<w:rFonts w:ascii="Liberation Sans" w:hAnsi="Liberation Sans" '
            'w:eastAsia="Liberation Sans" w:cs="Liberation Sans"/>'
        )
        run_properties = re.search(
            r"<w:rPr\b[^>]*>.*?</w:rPr>",
            level,
            re.DOTALL,
        )
        if run_properties:
            fonts = re.search(r"<w:rFonts\b[^>]*/>", run_properties.group(0))
            if fonts:
                updated = run_properties.group(0).replace(
                    fonts.group(0),
                    bullet_font,
                    1,
                )
            else:
                updated = run_properties.group(0).replace(
                    ">",
                    ">" + bullet_font,
                    1,
                )
            level = level[: run_properties.start()] + updated + level[run_properties.end() :]
        else:
            level = level.replace("</w:lvl>", f"<w:rPr>{bullet_font}</w:rPr></w:lvl>", 1)
        return level

    return re.sub(
        r"<w:lvl\b[^>]*>.*?</w:lvl>",
        normalize_bullet_level,
        numbering_xml,
        flags=re.DOTALL,
    )


def prepare_pdf_docx(docx_path, pdf_docx_path):
    with zipfile.ZipFile(docx_path) as source, zipfile.ZipFile(
        pdf_docx_path, "w", zipfile.ZIP_DEFLATED
    ) as destination:
        for item in source.infolist():
            content = source.read(item.filename)
            if item.filename == "word/document.xml":
                content = normalize_document_xml(content.decode("utf-8")).encode("utf-8")
            elif item.filename == "word/numbering.xml":
                content = normalize_numbering_xml(content.decode("utf-8")).encode("utf-8")
            destination.writestr(item, content)


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
        pdf_docx_path = Path(output_directory) / docx_path.name
        prepare_pdf_docx(docx_path, pdf_docx_path)
        result = subprocess.run(
            [
                converter,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_directory,
                str(pdf_docx_path.resolve()),
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
