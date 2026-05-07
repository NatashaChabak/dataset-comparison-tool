"""Streamlit entry point for the Dataset Comparison Tool."""

from __future__ import annotations

from typing import BinaryIO

import pandas as pd
import streamlit as st

from comparison.compare_duckdb import compare_uploaded_csvs_with_duckdb
from comparison.loader import read_upload_preview, upload_as_csv_buffer, uploaded_file_extension
from comparison.mapper import (
    FIELD_TYPES,
    IGNORE_FIELD,
    get_field_config,
    list_mapping_files,
    restore_mapping_from_json,
    save_mapping,
)


PREVIEW_ROWS = 100
DISPLAY_ROWS = 20


def format_file_size(size: int | None) -> str:
    """Return a readable file size."""
    if size is None:
        return "Unknown"

    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024 or unit == "GB":
            return f"{size_float:.1f} {unit}"
        size_float /= 1024

    return f"{size_float:.1f} GB"


def show_dataset_preview(
    label: str,
    data: pd.DataFrame,
    file_size: int | None,
    file_type: str,
) -> None:
    """Show basic dataset details and the first rows."""
    st.subheader(label)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Preview rows loaded", f"{len(data):,}")
    metric_cols[1].metric("Columns", f"{len(data.columns):,}")
    metric_cols[2].metric("File size", format_file_size(file_size))

    st.dataframe(data.head(DISPLAY_ROWS), use_container_width=True)
    if file_type == "json":
        st.caption(
            f"Showing first {min(DISPLAY_ROWS, len(data))} rows. "
            "JSON is flattened to table columns before preview and comparison."
        )
    elif file_type in {"xlsx", "xls"}:
        st.caption(
            f"Showing first {min(DISPLAY_ROWS, len(data))} rows. "
            "The first Excel sheet is read automatically before preview and comparison."
        )
    else:
        st.caption(
            f"Showing first {min(DISPLAY_ROWS, len(data))} rows. "
            f"Only first {PREVIEW_ROWS} rows are loaded for this setup screen."
        )


def field_index(options: list[str], value: str | None) -> int:
    """Return a safe selectbox index."""
    if value in options:
        return options.index(value)

    return 0


def render_mapping_screen(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    selected_key_a: str,
    selected_key_b: str,
) -> dict:
    """Render field mapping controls and save mappings as JSON."""
    st.divider()
    st.subheader("Field Mapping")

    saved_files = list_mapping_files()
    loaded_mapping = st.session_state.get("restored_mapping")
    selected_file = "Create new mapping"

    if saved_files:
        load_options = ["Create new mapping"] + [path.name for path in saved_files]
        selected_file = st.selectbox("Saved mapping file", load_options)
        restore_disabled = selected_file == "Create new mapping"
        if restore_disabled:
            loaded_mapping = None

        if st.button("Restore mapping from JSON", disabled=restore_disabled):
            loaded_path = next(path for path in saved_files if path.name == selected_file)
            loaded_mapping = restore_mapping_from_json(loaded_path)
            st.session_state["restored_mapping"] = loaded_mapping
            st.session_state["restored_mapping_file"] = selected_file
            st.session_state["mapping_restore_version"] = (
                st.session_state.get("mapping_restore_version", 0) + 1
            )
            st.success(f"Restored mapping from `{selected_file}`.")
    else:
        st.info("No saved mappings yet. Save a mapping first to restore it later.")

    restored_file = st.session_state.get("restored_mapping_file", "new_mapping")
    restore_version = st.session_state.get("mapping_restore_version", 0)
    widget_context = f"{restored_file}_{restore_version}".replace(".", "_")

    mapping_name = st.text_input(
        "Mapping name",
        value=(loaded_mapping or {}).get("table", "customers"),
        key=f"mapping_name_{widget_context}",
    )

    field_options_b = [IGNORE_FIELD] + list(df_b.columns)
    fields = []

    st.caption("Choose which Dataset B field matches each Dataset A field.")

    header_cols = st.columns([2, 2, 1, 1, 1.4])
    header_cols[0].markdown("**Dataset A field**")
    header_cols[1].markdown("**Dataset B field**")
    header_cols[2].markdown("**Compare**")
    header_cols[3].markdown("**Key**")
    header_cols[4].markdown("**Type / mode**")

    for source_field in df_a.columns:
        saved_config = get_field_config(loaded_mapping, source_field)
        default_target = saved_config.get("target")
        if source_field == selected_key_a and not default_target:
            default_target = selected_key_b

        default_compare = bool(
            saved_config.get("compare", default_target not in (None, IGNORE_FIELD))
        )
        default_key = bool(saved_config.get("key", source_field == selected_key_a))
        default_type = saved_config.get("type", "string")

        row_cols = st.columns([2, 2, 1, 1, 1.4])
        row_cols[0].write(source_field)

        target_field = row_cols[1].selectbox(
            "Dataset B field",
            field_options_b,
            index=field_index(field_options_b, default_target),
            key=f"map_target_{widget_context}_{source_field}",
            label_visibility="collapsed",
        )
        compare = row_cols[2].checkbox(
            "Compare",
            value=default_compare and target_field != IGNORE_FIELD,
            key=f"map_compare_{widget_context}_{source_field}",
            disabled=target_field == IGNORE_FIELD,
            label_visibility="collapsed",
        )
        is_key = row_cols[3].checkbox(
            "Key",
            value=default_key,
            key=f"map_key_{widget_context}_{source_field}",
            label_visibility="collapsed",
        )
        field_type = row_cols[4].selectbox(
            "Type / mode",
            FIELD_TYPES,
            index=field_index(FIELD_TYPES, default_type),
            key=f"map_type_{widget_context}_{source_field}",
            label_visibility="collapsed",
        )

        if target_field != IGNORE_FIELD:
            fields.append(
                {
                    "source": source_field,
                    "target": target_field,
                    "type": field_type,
                    "compare": compare,
                    "key": is_key,
                }
            )

    key_fields = [field for field in fields if field["key"]]
    mapping = {
        "table": mapping_name,
        "key": {
            "a": key_fields[0]["source"] if key_fields else selected_key_a,
            "b": key_fields[0]["target"] if key_fields else selected_key_b,
        },
        "fields": fields,
    }

    st.markdown("**Mapping Preview**")
    st.json(mapping)

    if st.button("Save mapping as JSON", type="primary"):
        saved_path = save_mapping(mapping, mapping_name)
        st.success(f"Mapping saved to `{saved_path}`.")

    return mapping


def render_duckdb_comparison_screen(
    file_a: BinaryIO,
    file_b: BinaryIO,
    mapping: dict,
) -> None:
    """Render DuckDB/Parquet comparison controls and results."""
    st.divider()
    st.subheader("DuckDB / Parquet Comparison")
    st.caption(
        "This step converts uploaded CSV files, or JSON files flattened as CSV, "
        "or Excel first sheets converted as CSV, to temporary Parquet files and "
        "uses DuckDB to compare the mapped fields."
    )

    comparable_count = len(
        [
            field
            for field in mapping.get("fields", [])
            if field.get("compare")
        ]
    )
    if not mapping.get("fields") or comparable_count == 0:
        st.warning("Map at least one field and mark it for comparison first.")
        return

    result_limit = st.number_input(
        "Maximum rows to show per result table",
        min_value=10,
        max_value=10000,
        value=1000,
        step=100,
    )

    if not st.button("Run DuckDB comparison", type="primary"):
        return

    with st.spinner("Converting CSV files to Parquet and comparing with DuckDB..."):
        try:
            csv_file_a = upload_as_csv_buffer(file_a)
            csv_file_b = upload_as_csv_buffer(file_b)
            results = compare_uploaded_csvs_with_duckdb(
                csv_file_a,
                csv_file_b,
                mapping,
                limit=int(result_limit),
            )
        except Exception as exc:
            st.error(f"Could not run DuckDB comparison: {exc}")
            return

    summary = results["summary"]
    metric_cols = st.columns(5)
    metric_cols[0].metric("Rows in A", f"{summary['total_a']:,}")
    metric_cols[1].metric("Rows in B", f"{summary['total_b']:,}")
    metric_cols[2].metric("Only in A", f"{summary['only_a']:,}")
    metric_cols[3].metric("Only in B", f"{summary['only_b']:,}")
    metric_cols[4].metric("Different values", f"{summary['different_values']:,}")

    st.markdown("**Differences by Field**")
    st.dataframe(results["differences_by_field"], use_container_width=True)

    tab_only_a, tab_only_b, tab_diff = st.tabs(
        ["Only in Dataset A", "Only in Dataset B", "Different Values"]
    )
    with tab_only_a:
        st.dataframe(results["only_a"], use_container_width=True)
    with tab_only_b:
        st.dataframe(results["only_b"], use_container_width=True)
    with tab_diff:
        st.dataframe(results["differences"], use_container_width=True)


def main() -> None:
    """Run the application."""
    st.set_page_config(page_title="Dataset Comparison Tool", layout="wide")
    st.title("Dataset Comparison Tool")

    upload_col_a, upload_col_b = st.columns(2)
    with upload_col_a:
        file_a = st.file_uploader(
            "Upload Dataset A", type=["csv", "json", "xlsx", "xls"], key="dataset_a"
        )
    with upload_col_b:
        file_b = st.file_uploader(
            "Upload Dataset B", type=["csv", "json", "xlsx", "xls"], key="dataset_b"
        )

    if not file_a or not file_b:
        st.info(
            "Upload two CSV, JSON, or Excel files to preview the datasets and select "
            "key columns. Excel files use the first sheet automatically."
        )
        return

    try:
        df_a = read_upload_preview(file_a, PREVIEW_ROWS)
        df_b = read_upload_preview(file_b, PREVIEW_ROWS)
    except Exception as exc:
        st.error(f"Could not read one of the uploaded files: {exc}")
        return

    preview_col_a, preview_col_b = st.columns(2)
    with preview_col_a:
        show_dataset_preview(
            "Dataset A Preview",
            df_a,
            getattr(file_a, "size", None),
            uploaded_file_extension(file_a),
        )
    with preview_col_b:
        show_dataset_preview(
            "Dataset B Preview",
            df_b,
            getattr(file_b, "size", None),
            uploaded_file_extension(file_b),
        )

    st.divider()
    st.subheader("Key Column Selection")

    key_col_a, key_col_b = st.columns(2)
    with key_col_a:
        selected_key_a = st.selectbox("Key column in Dataset A", df_a.columns)
    with key_col_b:
        selected_key_b = st.selectbox("Key column in Dataset B", df_b.columns)

    st.success(
        f"Selected keys: Dataset A `{selected_key_a}` and Dataset B `{selected_key_b}`."
    )

    mapping = render_mapping_screen(df_a, df_b, selected_key_a, selected_key_b)
    render_duckdb_comparison_screen(file_a, file_b, mapping)


if __name__ == "__main__":
    main()
