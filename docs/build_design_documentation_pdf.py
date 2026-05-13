from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path("docs/dataset_comparison_tool_design_documentation.pdf")
TEMPLATE_IMAGE = Path("docs/template_assets/first_page_image_1.jpg")


class ArchitectureFlow(Flowable):
    def __init__(self, width: float, height: float = 170):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        canvas = self.canv
        boxes = [
            ("Upload files", "CSV / JSON / Excel"),
            ("Normalize input", "Preview + internal CSV"),
            ("Parquet", "temporary optimized files"),
            ("DuckDB", "mapped comparison"),
            ("Results", "tables + Excel report"),
        ]
        gap = 10
        box_width = (self.width - gap * (len(boxes) - 1)) / len(boxes)
        box_height = 72
        y = 52

        for index, (title, subtitle) in enumerate(boxes):
            x = index * (box_width + gap)
            canvas.setFillColor(colors.HexColor("#E7F0EA"))
            canvas.setStrokeColor(colors.HexColor("#0E5C5A"))
            canvas.roundRect(x, y, box_width, box_height, 8, stroke=1, fill=1)
            canvas.setFillColor(colors.HexColor("#0B1F24"))
            canvas.setFont("Helvetica-Bold", 9)
            canvas.drawCentredString(x + box_width / 2, y + 44, title)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(colors.HexColor("#52616B"))
            canvas.drawCentredString(x + box_width / 2, y + 24, subtitle)

            if index < len(boxes) - 1:
                arrow_x = x + box_width + 1
                arrow_y = y + box_height / 2
                canvas.setStrokeColor(colors.HexColor("#4FA39B"))
                canvas.setLineWidth(1.5)
                canvas.line(arrow_x, arrow_y, arrow_x + gap - 3, arrow_y)
                canvas.line(arrow_x + gap - 3, arrow_y, arrow_x + gap - 8, arrow_y + 4)
                canvas.line(arrow_x + gap - 3, arrow_y, arrow_x + gap - 8, arrow_y - 4)


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#0B1F24"),
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#52616B"),
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0E5C5A"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#111827"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#111827"),
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#52616B"),
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullet(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"&bull; {text}", style)


def table(data, widths=None) -> Table:
    t = Table(data, colWidths=widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E5C5A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#111827")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F8F4")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5D1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#52616B"))
    canvas.drawString(2 * cm, 1.15 * cm, "Dataset Comparison Tool - Design Documentation")
    canvas.drawRightString(A4[0] - 2 * cm, 1.15 * cm, str(doc.page))
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    if TEMPLATE_IMAGE.exists():
        canvas.drawImage(
            str(TEMPLATE_IMAGE),
            0,
            0,
            width=A4[0],
            height=A4[1],
            preserveAspectRatio=False,
            mask="auto",
        )

    canvas.setFillColor(colors.HexColor("#111827"))
    canvas.setFont("Helvetica", 11)
    canvas.drawString(2.55 * cm, 23.6 * cm, "Karelia University of Applied Sciences")
    canvas.drawString(2.55 * cm, 23.05 * cm, "Information and Communication Technology")

    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawCentredString(A4[0] / 2, 15.15 * cm, "Dataset Comparison Tool")
    canvas.setFont("Helvetica", 16)
    canvas.drawCentredString(A4[0] / 2, 14.25 * cm, "Design Documentation")

    canvas.setFont("Helvetica", 11)
    canvas.drawString(2.55 * cm, 6.2 * cm, "Zhitnikova")
    canvas.drawString(2.55 * cm, 5.65 * cm, "Natalia")
    canvas.drawString(2.55 * cm, 5.1 * cm, "2207363")
    canvas.drawString(2.55 * cm, 4.55 * cm, "07/05/2026")
    canvas.restoreState()


def build() -> None:
    styles = make_styles()
    OUTPUT.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Dataset Comparison Tool - Design Documentation",
    )

    story = []
    story.append(Spacer(1, 1))
    story.append(PageBreak())
    story.append(p("Dataset Comparison Tool", styles["title"]))
    story.append(p("Design Documentation", styles["subtitle"]))
    story.append(
        p(
            "This document describes the current design of a Streamlit application for comparing exported datasets when direct database access is not available.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(ArchitectureFlow(doc.width))

    story.append(p("1. Project Purpose", styles["h1"]))
    for item in [
        "Compare exported datasets from two systems without connecting directly to databases.",
        "Support practical input formats: CSV, JSON, and Excel.",
        "Allow users to map different field names before comparison.",
        "Use DuckDB and Parquet for a more scalable comparison path.",
        "Export business-friendly Excel reports.",
    ]:
        story.append(bullet(item, styles["body"]))

    story.append(p("2. User Workflow", styles["h1"]))
    workflow = [
        ["Step", "User action", "System response"],
        ["1", "Upload Dataset A and Dataset B", "Reads preview data and detects columns"],
        ["2", "Select key columns", "Defines how records are matched"],
        ["3", "Map fields", "Stores source-target field relationships"],
        ["4", "Choose compare/type settings", "Builds a mapping configuration"],
        ["5", "Run comparison", "Converts files to Parquet and compares with DuckDB"],
        ["6", "Review and export", "Shows result tables and creates an Excel report"],
    ]
    story.append(table(workflow, [1.1 * cm, 5.2 * cm, 8.4 * cm]))

    story.append(p("3. Application Structure", styles["h1"]))
    structure = [
        ["File or folder", "Responsibility"],
        ["app.py", "Streamlit user interface and page flow"],
        ["comparison/loader.py", "CSV, JSON, and Excel loading; JSON flattening; conversion to CSV"],
        ["comparison/mapper.py", "Save, list, restore, and read JSON field mappings"],
        ["comparison/compare_duckdb.py", "Temporary CSV storage, Parquet conversion, DuckDB comparison"],
        ["comparison/report.py", "Excel report generation"],
        ["sample_data/", "CSV, JSON, and Excel sample files"],
        ["docs/", "Project and design documentation"],
    ]
    story.append(table(structure, [4.5 * cm, 10.2 * cm]))

    story.append(PageBreak())
    story.append(p("4. Data Design", styles["h1"]))
    story.append(
        p(
            "The system treats IDs and codes as text to preserve values such as leading zeros. JSON and Excel files are converted to a tabular CSV-like form before full comparison.",
            styles["body"],
        )
    )
    data_table = [
        ["Format", "How it is handled", "Design note"],
        ["CSV", "Previewed with Pandas, converted to Parquet by DuckDB", "Primary input format"],
        ["JSON", "Flattened with pandas.json_normalize and converted to CSV internally", "Supports record lists and nested objects"],
        ["Excel", "First sheet is read automatically and converted to CSV internally", "Simple first version; sheet selector can be added later"],
        ["Parquet", "Temporary internal processing format", "Improves comparison performance"],
        ["Excel report", "Generated after comparison", "Business-friendly output"],
    ]
    story.append(table(data_table, [2.5 * cm, 6.4 * cm, 5.8 * cm]))

    story.append(p("5. Mapping Design", styles["h1"]))
    story.append(
        p(
            "Field mapping separates business meaning from column names. This is important because different systems often export the same concept with different field names.",
            styles["body"],
        )
    )
    mapping_table = [
        ["Mapping property", "Meaning"],
        ["source", "Column name from Dataset A"],
        ["target", "Matching column name from Dataset B"],
        ["compare", "Whether this field should be compared"],
        ["key", "Whether this field is used to match records"],
        ["type", "Comparison mode: string, integer, float, date, or boolean"],
    ]
    story.append(table(mapping_table, [4.2 * cm, 10.5 * cm]))

    story.append(p("6. Processing Architecture", styles["h1"]))
    for item in [
        "The preview screen loads only a small number of rows to keep the interface responsive.",
        "Full-file processing starts only when the user clicks the comparison button.",
        "Uploaded or converted CSV files are saved to a temporary folder.",
        "DuckDB converts temporary CSV files to Parquet.",
        "DuckDB joins records by selected key fields and compares only mapped fields.",
        "Result tables are returned to Streamlit and can be exported to Excel.",
    ]:
        story.append(bullet(item, styles["body"]))

    story.append(p("7. User Interface Design", styles["h1"]))
    ui_table = [
        ["Screen section", "Purpose"],
        ["Upload area", "Accepts Dataset A and Dataset B in CSV, JSON, or Excel format"],
        ["Preview tables", "Shows a safe sample of uploaded data"],
        ["Key selection", "Lets the user choose matching record identifiers"],
        ["Field mapping", "Lets the user connect different schemas"],
        ["DuckDB comparison", "Runs full comparison and displays result metrics"],
        ["Download button", "Exports results as an Excel workbook"],
    ]
    story.append(table(ui_table, [4.2 * cm, 10.5 * cm]))

    story.append(PageBreak())
    story.append(p("8. Report Design", styles["h1"]))
    story.append(
        p(
            "The Excel report is designed for sharing and review. It separates summary information from detailed records so users can quickly understand the result and then inspect examples.",
            styles["body"],
        )
    )
    report_table = [
        ["Sheet", "Content"],
        ["Summary", "Total rows and result counts"],
        ["Only in A", "Keys found only in Dataset A"],
        ["Only in B", "Keys found only in Dataset B"],
        ["Different Values", "Field-level mismatches"],
        ["Differences by Field", "Mismatch counts grouped by field"],
    ]
    story.append(table(report_table, [4.2 * cm, 10.5 * cm]))

    story.append(p("9. AI-Assisted Development", styles["h1"]))
    story.append(
        p(
            "AI agents supported the project under user supervision. They helped read project documents, propose implementation steps, generate code drafts, debug problems, and prepare documentation. The user supervised feature choices, tested behavior, and approved the direction of the project.",
            styles["body"],
        )
    )

    story.append(p("10. Design Limitations", styles["h1"]))
    for item in [
        "Excel upload currently reads the first sheet automatically; manual sheet selection is future work.",
        "Very large JSON files are flattened in memory before conversion.",
        "Duplicate key detection is not yet implemented.",
        "The dashboard is functional but can be improved with richer charts.",
        "More automated tests should be added around edge cases and file formats.",
    ]:
        story.append(bullet(item, styles["body"]))

    story.append(p("11. Future Improvements", styles["h1"]))
    future = [
        ["Improvement", "Reason"],
        ["Duplicate key warnings", "Prevents misleading comparison results"],
        ["Excel sheet selector", "Improves support for real workbooks"],
        ["Charts in dashboard", "Makes results easier to understand visually"],
        ["Saved comparison templates", "Supports repeated business workflows"],
        ["More tests", "Improves reliability and maintainability"],
    ]
    story.append(table(future, [5 * cm, 9.7 * cm]))

    story.append(Spacer(1, 10))
    story.append(
        p(
            "Current status: the project has a working upload, mapping, DuckDB/Parquet comparison, and Excel export flow.",
            styles["small"],
        )
    )

    doc.build(story, onFirstPage=cover_page, onLaterPages=footer)


if __name__ == "__main__":
    build()
    print(OUTPUT)
