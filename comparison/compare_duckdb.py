"""DuckDB and Parquet comparison engine for larger CSV files."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO

import pandas as pd


LOCAL_PACKAGE_DIR = Path(".python_packages")


def ensure_local_packages_available() -> None:
    """Allow workspace-local packages installed with pip --target to be imported."""
    package_path = str(LOCAL_PACKAGE_DIR.resolve())
    if LOCAL_PACKAGE_DIR.exists() and package_path not in sys.path:
        sys.path.insert(0, package_path)


def require_duckdb() -> Any:
    """Import DuckDB or raise a helpful error."""
    ensure_local_packages_available()
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "DuckDB is not installed. Install it with `python -m pip install duckdb`."
        ) from exc

    return duckdb


def quote_identifier(identifier: str) -> str:
    """Quote a SQL identifier for DuckDB."""
    return '"' + identifier.replace('"', '""') + '"'


def sql_literal(value: str) -> str:
    """Quote a SQL string literal."""
    return "'" + value.replace("'", "''") + "'"


def sql_path(path: Path) -> str:
    """Return a file path as a SQL string literal."""
    return sql_literal(path.resolve().as_posix())


def save_uploaded_file(uploaded_file: BinaryIO, path: Path) -> None:
    """Persist a Streamlit uploaded file to disk."""
    uploaded_file.seek(0)
    with path.open("wb") as target:
        shutil.copyfileobj(uploaded_file, target)
    uploaded_file.seek(0)


def convert_csv_to_parquet(csv_path: Path, parquet_path: Path) -> None:
    """Convert CSV to Parquet using DuckDB, keeping all columns as text."""
    duckdb = require_duckdb()
    with duckdb.connect() as connection:
        connection.execute(
            f"""
            COPY (
                SELECT *
                FROM read_csv_auto(
                    {sql_path(csv_path)},
                    all_varchar = true,
                    header = true
                )
            )
            TO {sql_path(parquet_path)}
            (FORMAT PARQUET)
            """
        )


def normalize_expression(expression: str, field_type: str) -> str:
    """Return SQL for comparison normalization."""
    text_value = f"trim(coalesce(cast({expression} as varchar), ''))"

    if field_type == "integer":
        return f"try_cast({text_value} as bigint)"
    if field_type == "float":
        return f"try_cast(replace({text_value}, ',', '.') as double)"
    if field_type == "date":
        return f"try_cast({text_value} as date)"
    if field_type == "boolean":
        return (
            "case "
            f"when lower({text_value}) in ('true', '1', 'yes', 'y') then true "
            f"when lower({text_value}) in ('false', '0', 'no', 'n') then false "
            "else null end"
        )

    return text_value


def comparable_fields(mapping: dict[str, Any]) -> list[dict[str, Any]]:
    """Return mapped fields selected for comparison."""
    return [
        field
        for field in mapping.get("fields", [])
        if field.get("compare")
    ]


def compare_parquet_files(
    parquet_a: Path,
    parquet_b: Path,
    mapping: dict[str, Any],
    limit: int = 1000,
) -> dict[str, Any]:
    """Compare two Parquet files with DuckDB using a field mapping."""
    duckdb = require_duckdb()
    key_a = mapping["key"]["a"]
    key_b = mapping["key"]["b"]
    key_a_sql = quote_identifier(key_a)
    key_b_sql = quote_identifier(key_b)

    with duckdb.connect() as connection:
        connection.execute(
            f"CREATE VIEW dataset_a AS SELECT * FROM read_parquet({sql_path(parquet_a)})"
        )
        connection.execute(
            f"CREATE VIEW dataset_b AS SELECT * FROM read_parquet({sql_path(parquet_b)})"
        )

        counts = connection.execute(
            """
            SELECT
                (SELECT count(*) FROM dataset_a) AS total_a,
                (SELECT count(*) FROM dataset_b) AS total_b
            """
        ).fetchdf().iloc[0].to_dict()

        only_a_count = connection.execute(
            f"""
            SELECT count(*) AS count
            FROM dataset_a a
            LEFT JOIN dataset_b b ON a.{key_a_sql} = b.{key_b_sql}
            WHERE b.{key_b_sql} IS NULL
            """
        ).fetchone()[0]

        only_b_count = connection.execute(
            f"""
            SELECT count(*) AS count
            FROM dataset_b b
            LEFT JOIN dataset_a a ON a.{key_a_sql} = b.{key_b_sql}
            WHERE a.{key_a_sql} IS NULL
            """
        ).fetchone()[0]

        only_a = connection.execute(
            f"""
            SELECT a.{key_a_sql} AS key
            FROM dataset_a a
            LEFT JOIN dataset_b b ON a.{key_a_sql} = b.{key_b_sql}
            WHERE b.{key_b_sql} IS NULL
            LIMIT {int(limit)}
            """
        ).fetchdf()

        only_b = connection.execute(
            f"""
            SELECT b.{key_b_sql} AS key
            FROM dataset_b b
            LEFT JOIN dataset_a a ON a.{key_a_sql} = b.{key_b_sql}
            WHERE a.{key_a_sql} IS NULL
            LIMIT {int(limit)}
            """
        ).fetchdf()

        difference_queries = []
        for field in comparable_fields(mapping):
            source = quote_identifier(field["source"])
            target = quote_identifier(field["target"])
            source_value = f"a.{source}"
            target_value = f"b.{target}"
            source_normalized = normalize_expression(source_value, field["type"])
            target_normalized = normalize_expression(target_value, field["type"])
            field_name = sql_literal(field["source"])

            difference_queries.append(
                f"""
                SELECT
                    a.{key_a_sql} AS key,
                    {field_name} AS field,
                    cast({source_value} AS varchar) AS dataset_a_value,
                    cast({target_value} AS varchar) AS dataset_b_value
                FROM dataset_a a
                INNER JOIN dataset_b b ON a.{key_a_sql} = b.{key_b_sql}
                WHERE {source_normalized} IS DISTINCT FROM {target_normalized}
                """
            )

        if difference_queries:
            difference_sql = " UNION ALL ".join(difference_queries)
            difference_count = connection.execute(
                f"SELECT count(*) AS count FROM ({difference_sql}) differences"
            ).fetchone()[0]
            differences = connection.execute(
                difference_sql + f" LIMIT {int(limit)}"
            ).fetchdf()
        else:
            difference_count = 0
            differences = pd.DataFrame(
                columns=["key", "field", "dataset_a_value", "dataset_b_value"]
            )

        differences_by_field = (
            differences.groupby("field", dropna=False)
            .size()
            .reset_index(name="differences")
            .sort_values("differences", ascending=False)
            if not differences.empty
            else pd.DataFrame(columns=["field", "differences"])
        )

    return {
        "summary": {
            "total_a": int(counts["total_a"]),
            "total_b": int(counts["total_b"]),
            "only_a": int(only_a_count),
            "only_b": int(only_b_count),
            "different_values": int(difference_count),
            "result_limit": limit,
        },
        "only_a": only_a,
        "only_b": only_b,
        "differences": differences,
        "differences_by_field": differences_by_field,
    }


def compare_uploaded_csvs_with_duckdb(
    file_a: BinaryIO,
    file_b: BinaryIO,
    mapping: dict[str, Any],
    limit: int = 1000,
) -> dict[str, Any]:
    """Save uploaded CSV files, convert them to Parquet, and compare with DuckDB."""
    with tempfile.TemporaryDirectory(prefix="dataset_compare_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        csv_a = temp_dir / "dataset_a.csv"
        csv_b = temp_dir / "dataset_b.csv"
        parquet_a = temp_dir / "dataset_a.parquet"
        parquet_b = temp_dir / "dataset_b.parquet"

        save_uploaded_file(file_a, csv_a)
        save_uploaded_file(file_b, csv_b)
        convert_csv_to_parquet(csv_a, parquet_a)
        convert_csv_to_parquet(csv_b, parquet_b)

        return compare_parquet_files(parquet_a, parquet_b, mapping, limit=limit)
