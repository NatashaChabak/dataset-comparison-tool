"""Excel report creation helpers."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd


def summary_to_dataframe(summary: dict[str, Any]) -> pd.DataFrame:
    """Convert comparison summary metrics to a report dataframe."""
    labels = {
        "total_a": "Rows in Dataset A",
        "total_b": "Rows in Dataset B",
        "only_a": "Records only in Dataset A",
        "only_b": "Records only in Dataset B",
        "matched": "Records matched by key",
        "different_values": "Different mapped values",
        "result_limit": "Result row display limit",
    }
    return pd.DataFrame(
        [
            {"Metric": labels.get(key, key), "Value": value}
            for key, value in summary.items()
        ]
    )


def write_sheet(
    writer: pd.ExcelWriter,
    sheet_name: str,
    data: pd.DataFrame,
) -> None:
    """Write a dataframe to an Excel sheet with basic column sizing."""
    safe_data = data.copy()
    if safe_data.empty:
        safe_data = pd.DataFrame({"Message": ["No records found."]})

    safe_data.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]

    for column_index, column_name in enumerate(safe_data.columns, start=1):
        values = safe_data[column_name].astype(str).head(100)
        max_value_length = max([len(str(column_name)), *values.map(len).tolist()])
        worksheet.column_dimensions[
            worksheet.cell(row=1, column=column_index).column_letter
        ].width = min(max(max_value_length + 2, 12), 60)


def build_comparison_excel_report(results: dict[str, Any]) -> bytes:
    """Build an Excel workbook from comparison results."""
    output = BytesIO()
    matched_data = results.get("matched_data", pd.DataFrame())

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        write_sheet(writer, "Summary", summary_to_dataframe(results["summary"]))
        write_sheet(writer, "Only in A", results["only_a"])
        write_sheet(writer, "Only in B", results["only_b"])
        write_sheet(writer, "Matched Data", matched_data)
        write_sheet(writer, "Different Values", results["differences"])
        write_sheet(writer, "Differences by Field", results["differences_by_field"])

    output.seek(0)
    return output.getvalue()
