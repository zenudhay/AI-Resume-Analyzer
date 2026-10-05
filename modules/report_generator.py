
from io import BytesIO
from datetime import datetime
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# --------------------------------------------------
# COLORS
# --------------------------------------------------

NAVY = colors.HexColor("#17365D")
LIGHT_BG = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
WHITE = colors.white


# --------------------------------------------------
# TEXT HELPERS
# --------------------------------------------------

def clean_text(text):
    """Clean Markdown, HTML, and unsupported Unicode characters."""

    if not text:
        return ""

    text = str(text)

    # Replace unsupported Unicode characters
    replacements = {
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u00ad": "",
    "\u2022": "-",
    "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Convert common HTML line breaks
    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"</?para\s*>|</?p\s*>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]*>", "", text)

    # Replace unsupported or problematic characters
    replacements = {
        "✓": "Yes",
        "✔": "Yes",
        "✖": "No",
        "✗": "No",
        "–": "-",
        "—": "-",
        "−": "-",
        "■": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "•": "-",
        "\u00a0": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Basic Markdown cleanup
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")

    return text.strip()


def make_paragraph(text, style):
    """Create a safe ReportLab paragraph."""

    safe_text = escape(str(text))
    safe_text = safe_text.replace("\n", "<br/>")

    return Paragraph(safe_text, style)


def is_table_separator(line):
    """Identify Markdown table separator rows."""

    cells = line.strip().strip("|").split("|")

    if not cells:
        return False

    return all(
        re.fullmatch(r"\s*:?-{3,}:?\s*", cell)
        for cell in cells
    )


def parse_table_row(line):
    """Split a Markdown table row into cells."""

    return [
        cell.strip()
        for cell in line.strip().strip("|").split("|")
    ]


# --------------------------------------------------
# AI FEEDBACK FORMATTER
# --------------------------------------------------

def add_ai_feedback(story, ai_feedback, styles):
    """Convert AI Markdown into readable PDF elements."""

    body_style = styles["body"]
    heading_style = styles["ai_heading"]
    table_header_style = styles["table_header"]
    table_cell_style = styles["table_cell"]

    if not ai_feedback:
        story.append(
            make_paragraph(
                "AI feedback was unavailable. "
                "Traditional ML analysis is included "
                "in this report.",
                body_style
            )
        )
        return

    text = clean_text(ai_feedback)
    lines = text.splitlines()

    index = 0
    paragraph_buffer = []

    def flush_paragraph():
        if paragraph_buffer:
            paragraph_text = " ".join(
                part.strip() for part in paragraph_buffer
            )

            if paragraph_text:
                story.append(
                    make_paragraph(
                        paragraph_text,
                        body_style
                    )
                )
                story.append(Spacer(1, 4))

            paragraph_buffer.clear()

    while index < len(lines):
        line = lines[index].strip()

        if not line:
            flush_paragraph()
            index += 1
            continue

        # ------------------------------------------
        # MARKDOWN TABLES
        # ------------------------------------------

        if "|" in line and index + 1 < len(lines):
            next_line = lines[index + 1].strip()

            if "|" in next_line and is_table_separator(next_line):
                flush_paragraph()

                raw_rows = [parse_table_row(line)]
                index += 2

                while index < len(lines):
                    current = lines[index].strip()

                    if not current or "|" not in current:
                        break

                    if is_table_separator(current):
                        index += 1
                        continue

                    raw_rows.append(parse_table_row(current))
                    index += 1

                if raw_rows:
                    column_count = max(
                        len(row) for row in raw_rows
                    )

                    formatted_rows = []

                    for row_number, row in enumerate(raw_rows):
                        row += [""] * (
                            column_count - len(row)
                        )

                        if row_number == 0:
                            formatted_rows.append([
                                make_paragraph(
                                    cell,
                                    table_header_style
                                )
                                for cell in row
                            ])
                        else:
                            formatted_rows.append([
                                make_paragraph(
                                    cell,
                                    table_cell_style
                                )
                                for cell in row
                            ])

                    available_width = A4[0] - 90
                    column_width = (
                        available_width / column_count
                    )

                    ai_table = Table(
                        formatted_rows,
                        colWidths=[
                            column_width
                        ] * column_count,
                        repeatRows=1,
                        splitByRow=1
                    )

                    ai_table.setStyle(
                        TableStyle([
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, 0),
                                NAVY
                            ),
                            (
                                "TEXTCOLOR",
                                (0, 0),
                                (-1, 0),
                                WHITE
                            ),
                            (
                                "GRID",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                BORDER
                            ),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [WHITE, LIGHT_BG]
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP"
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                6
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                6
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                6
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                6
                            )
                        ])
                    )

                    story.append(ai_table)
                    story.append(Spacer(1, 8))

                continue

        # ------------------------------------------
        # HEADINGS
        # ------------------------------------------

        heading_match = re.match(
            r"^(#{1,6})\s+(.+)$",
            line
        )

        numbered_heading = re.match(
            r"^\d+\.\s+(.+)$",
            line
        )

        if heading_match:
            flush_paragraph()

            heading_text = heading_match.group(2).strip()

            story.append(
                Paragraph(
                    escape(heading_text),
                    heading_style
                )
            )

            index += 1
            continue

        if numbered_heading and len(line) < 100:
            flush_paragraph()

            story.append(
                Paragraph(
                    escape(line),
                    heading_style
                )
            )

            index += 1
            continue

        # ------------------------------------------
        # BULLET POINTS
        # ------------------------------------------

        bullet_match = re.match(
            r"^\s*[-*]\s+(.+)$",
            line
        )

        if bullet_match:
            flush_paragraph()

            bullet_text = bullet_match.group(1).strip()

            story.append(
                make_paragraph(
                    "- " + bullet_text,
                    body_style
                )
            )

            story.append(Spacer(1, 3))
            index += 1
            continue

        # ------------------------------------------
        # NORMAL TEXT
        # ------------------------------------------

        paragraph_buffer.append(line)
        index += 1

    flush_paragraph()


# --------------------------------------------------
# PDF REPORT GENERATOR
# --------------------------------------------------

def generate_pdf_report(
    match_score,
    matched_skills,
    missing_skills,
    skill_percentage,
    ai_feedback=None
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
        title="AI Resume Analysis Report",
        author="AI Resume Analyzer"
    )

    # ----------------------------------------------
    # STYLES
    # ----------------------------------------------

    base_styles = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base_styles["Title"],
            fontSize=22,
            leading=28,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8
        ),

        "heading": ParagraphStyle(
            "SectionHeading",
            parent=base_styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8
        ),

        "ai_heading": ParagraphStyle(
            "AIHeading",
            parent=base_styles["Heading3"],
            fontSize=11,
            leading=15,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        ),

        "body": ParagraphStyle(
            "ReportBody",
            parent=base_styles["BodyText"],
            fontSize=9,
            leading=14,
            spaceAfter=5,
            wordWrap="CJK"
        ),

        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=WHITE,
            wordWrap="CJK"
        ),

        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base_styles["BodyText"],
            fontSize=8,
            leading=11,
            wordWrap="CJK"
        )
    }

    story = []

    # ----------------------------------------------
    # TITLE
    # ----------------------------------------------

    story.append(
        Paragraph(
            "AI Resume Analysis Report",
            styles["title"]
        )
    )

    generated_date = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        make_paragraph(
            f"Generated on: {generated_date}",
            styles["body"]
        )
    )

    story.append(Spacer(1, 15))

    # ----------------------------------------------
    # MATCH RESULTS
    # ----------------------------------------------

    story.append(
        Paragraph(
            "Resume Match Results",
            styles["heading"]
        )
    )

    total_skills = (
        len(matched_skills) + len(missing_skills)
    )

    score_data = [
        [
            make_paragraph(
                "Metric",
                styles["table_header"]
            ),
            make_paragraph(
                "Result",
                styles["table_header"]
            )
        ],
        [
            "Resume Match Score",
            f"{match_score:.2f}%"
        ],
        [
            "Matched Skills",
            f"{len(matched_skills)} / {total_skills}"
        ],
        [
            "Skill Match Percentage",
            f"{skill_percentage:.2f}%"
        ]
    ]

    score_table = Table(
        score_data,
        colWidths=[3.2 * inch, 2.3 * inch],
        repeatRows=1
    )

    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    story.append(score_table)

    # ----------------------------------------------
    # SKILLS COMPARISON
    # ----------------------------------------------

    story.append(
        Paragraph(
            "Skills Comparison",
            styles["heading"]
        )
    )

    skill_data = [[
        make_paragraph(
            "Matched Skills",
            styles["table_header"]
        ),
        make_paragraph(
            "Missing Skills",
            styles["table_header"]
        )
    ]]

    max_rows = max(
        len(matched_skills),
        len(missing_skills),
        1
    )

    for i in range(max_rows):
        matched = (
            matched_skills[i]
            if i < len(matched_skills)
            else ""
        )

        missing = (
            missing_skills[i]
            if i < len(missing_skills)
            else ""
        )

        skill_data.append([
            make_paragraph(
                matched,
                styles["table_cell"]
            ),
            make_paragraph(
                missing,
                styles["table_cell"]
            )
        ])

    skill_table = Table(
        skill_data,
        colWidths=[2.75 * inch, 2.75 * inch],
        repeatRows=1,
        splitByRow=1
    )

    skill_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [WHITE, LIGHT_BG]
            ),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ])
    )

    story.append(skill_table)

    # ----------------------------------------------
    # AI FEEDBACK
    # ----------------------------------------------

    story.append(
        Paragraph(
            "AI-Powered Resume Analysis",
            styles["heading"]
        )
    )

    add_ai_feedback(
        story,
        ai_feedback,
        styles
    )

    # ----------------------------------------------
    # BUILD PDF
    # ----------------------------------------------

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()
