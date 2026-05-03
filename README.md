# Dataset Comparison Tool

A Streamlit application for comparing exported datasets when direct database access is not available.

## Project Goal

The tool will let a user upload two CSV files, preview them, select key columns, map fields between datasets, compare records, view results, and export an Excel report.

## Current Status

Steps 1-4 are complete: the project structure is ready, dependencies are installed, sample CSV files are available, and the upload/preview screen works.

The field mapping screen is now implemented too. It can map Dataset A columns to Dataset B columns, mark compare/key fields, choose field types, preview the mapping JSON, save mappings into `mappings/`, and restore saved mappings from JSON.

Large CSV uploads are handled carefully on the setup screen: the app reads only the first 100 rows for preview and field mapping, and displays the first 20 rows. Full-file loading will be added later in the comparison step using a more suitable approach for large files.

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

Implement the first comparison logic using the saved field mapping.

Sample files are available in `sample_data/`:

- `customers_system_a.csv`
- `customers_system_b.csv`
