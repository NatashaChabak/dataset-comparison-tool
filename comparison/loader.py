"""File loading helpers."""

from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd


LOCAL_PACKAGE_DIR = Path(".python_packages")


def ensure_local_packages_available() -> None:
    """Allow workspace-local packages installed with pip --target to be imported."""
    package_path = str(LOCAL_PACKAGE_DIR.resolve())
    if LOCAL_PACKAGE_DIR.exists() and package_path not in sys.path:
        sys.path.insert(0, package_path)


def dataframe_as_text(data: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe with values represented as text."""
    return data.astype("string").fillna("")


def read_csv_preview(file: BinaryIO, rows: int) -> pd.DataFrame:
    """Read a small CSV preview while preserving IDs and codes as text."""
    file.seek(0)
    data = pd.read_csv(file, dtype=str, nrows=rows).fillna("")
    file.seek(0)
    return data


def find_record_list(data: Any) -> list[Any] | None:
    """Find the most likely record list inside JSON data."""
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return None

    record_lists = [
        value
        for value in data.values()
        if isinstance(value, list)
        and value
        and all(isinstance(item, dict) for item in value)
    ]
    if not record_lists:
        return None

    return max(record_lists, key=len)


def json_to_dataframe(file: BinaryIO) -> pd.DataFrame:
    """Convert JSON data into a flat dataframe."""
    file.seek(0)
    raw = file.read()
    file.seek(0)

    if isinstance(raw, str):
        raw = raw.encode("utf-8")

    data = json.loads(raw.decode("utf-8-sig"))
    records = find_record_list(data)

    if records is not None:
        return dataframe_as_text(pd.json_normalize(records))

    return dataframe_as_text(pd.json_normalize(data))


def read_json_preview(file: BinaryIO, rows: int) -> pd.DataFrame:
    """Read JSON as a flat dataframe and return only preview rows."""
    return json_to_dataframe(file).head(rows)


def excel_to_dataframe(file: BinaryIO) -> pd.DataFrame:
    """Read the first Excel sheet as a dataframe."""
    ensure_local_packages_available()
    file.seek(0)
    data = pd.read_excel(file, dtype=str, sheet_name=0).fillna("")
    file.seek(0)
    return dataframe_as_text(data)


def read_excel_preview(file: BinaryIO, rows: int) -> pd.DataFrame:
    """Read the first Excel sheet and return only preview rows."""
    return excel_to_dataframe(file).head(rows)


def uploaded_file_extension(file: BinaryIO) -> str:
    """Return the uploaded file extension."""
    name = getattr(file, "name", "")
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def read_upload_preview(file: BinaryIO, rows: int) -> pd.DataFrame:
    """Read a CSV, JSON, or Excel upload for the setup preview screen."""
    extension = uploaded_file_extension(file)
    if extension == "json":
        return read_json_preview(file, rows)
    if extension in {"xlsx", "xls"}:
        return read_excel_preview(file, rows)

    return read_csv_preview(file, rows)


def upload_as_csv_buffer(file: BinaryIO) -> BinaryIO:
    """Return an uploaded CSV, JSON, or Excel file as a CSV byte buffer."""
    extension = uploaded_file_extension(file)
    if extension == "csv":
        file.seek(0)
        return file

    if extension == "json":
        data = json_to_dataframe(file)
    elif extension in {"xlsx", "xls"}:
        data = excel_to_dataframe(file)
    else:
        raise ValueError(f"Unsupported file type: {extension or 'unknown'}")

    buffer = BytesIO()
    data.to_csv(buffer, index=False)
    buffer.seek(0)
    buffer.name = f"{getattr(file, 'name', 'upload')}.csv"
    return buffer
