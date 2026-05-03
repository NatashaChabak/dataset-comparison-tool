# Dataset Comparison Tool

A Streamlit application for comparing exported datasets when direct database access is not available.

## Project Goal

The tool will let a user upload two CSV or JSON files, preview them, select key columns, map fields between datasets, compare records, view results, and export an Excel report.

## Current Status

Steps 1-4 are complete: the project structure is ready, dependencies are installed, sample CSV files are available, and the upload/preview screen works.

The field mapping screen is now implemented too. It can map Dataset A columns to Dataset B columns, mark compare/key fields, choose field types, preview the mapping JSON, save mappings into `mappings/`, and restore saved mappings from JSON.

CSV and JSON uploads are supported. JSON files are flattened into table columns, converted to CSV internally, and then used in the same comparison flow as CSV files.

Large CSV uploads are handled carefully on the setup screen: the app reads only the first 100 rows for preview and field mapping, and displays the first 20 rows.

DuckDB and Parquet are now used in the comparison step. Uploaded CSV files, including JSON files converted to CSV internally, are saved temporarily, converted to Parquet, and compared with DuckDB using the active field mapping.

## Project Structure

```text
.
+-- app.py
+-- comparison/
|   +-- __init__.py
|   +-- loader.py
|   +-- normalizer.py
|   +-- mapper.py
|   +-- compare_pandas.py
|   +-- compare_duckdb.py
|   +-- report.py
+-- docs/
|   +-- current_stage_documentation.md
+-- sample_data/
+-- reports/
+-- mappings/
+-- tests/
+-- requirements.txt
+-- README.md
```

## Documentation

Current stage documentation is available in `docs/current_stage_documentation.md`.

## Next Step

Improve the result dashboard and add Excel report export.

Sample files are available in `sample_data/`:

- `customers_system_a.csv`
- `customers_system_b.csv`
- `customers_system_a.json`
- `customers_system_b.json`
