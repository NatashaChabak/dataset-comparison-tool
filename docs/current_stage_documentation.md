# Dataset Comparison Tool - Current Stage Documentation

## Stage Summary

This stage contains the first working setup and comparison flow for the Dataset Comparison Tool. The application can upload CSV, JSON, or Excel files, preview a small part of each file, select key columns, create field mappings, save mappings as JSON, restore saved mappings from JSON, and compare the uploaded files with DuckDB and Parquet.

DuckDB is now used for the comparison step. The app converts uploaded CSV files to temporary Parquet files, then compares the mapped fields through DuckDB.

## Implemented Features

- Streamlit application entry point in `app.py`
- Upload controls for Dataset A and Dataset B
- CSV preview with Pandas
- JSON upload, flattening, and internal CSV conversion
- Excel upload with automatic first-sheet reading
- Large-file friendly preview behavior
- Key-column selection for both datasets
- Field mapping screen
- Compare/key checkboxes for mapped fields
- Field type selection
- JSON mapping preview
- Save mapping to `mappings/`
- Restore mapping from a saved JSON file
- DuckDB/Parquet comparison engine
- Result summary metrics
- Result tables for only-in-A, only-in-B, and different values
- Sample CSV files for testing

## Current User Workflow

1. Start the Streamlit app.
2. Upload Dataset A as a CSV, JSON, or Excel file.
3. Upload Dataset B as a CSV, JSON, or Excel file.
4. Review the preview tables.
5. Select the key column in Dataset A.
6. Select the key column in Dataset B.
7. Map Dataset A fields to Dataset B fields.
8. Choose which mapped fields should be compared.
9. Mark key fields.
10. Choose field types.
11. Review the generated JSON mapping.
12. Save the mapping as JSON.
13. Restore a saved mapping later with the restore button.
14. Run the DuckDB comparison.
15. Review summary counts and result tables.

## How to Run

From the project folder, run:

```powershell
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Test Files

Sample files are available in `sample_data/`:

- `customers_system_a.csv`
- `customers_system_b.csv`
- `customers_system_a.json`
- `customers_system_b.json`
- `customers_system_a.xlsx`
- `customers_system_b.xlsx`

Recommended test setup:

- Dataset A key: `customer_id`
- Dataset B key: `cust_no`

Example field mappings:

| Dataset A field | Dataset B field | Compare | Key | Type |
| --- | --- | --- | --- | --- |
| customer_id | cust_no | Yes | Yes | string |
| first_name | fname | Yes | No | string |
| last_name | surname | Yes | No | string |
| email | email_address | Yes | No | string |
| created_at | creation_date | Yes | No | date |
| amount | total_amount | Yes | No | float |
| status | customer_status | Yes | No | string |

## Large CSV Behavior

The setup screen does not load the full CSV file into memory.

Current behavior:

- Reads first 100 rows for preview and mapping setup.
- Displays first 20 rows in each preview table.
- Preserves IDs and codes as text, including leading zeros such as `00123`.
- Shows preview row count, column count, and file size.

This keeps the setup screen responsive for large files. Full-file processing happens only when the user runs the DuckDB comparison.

## JSON Upload Behavior

JSON files are converted to a table before preview and comparison.

Supported JSON shapes:

- list of records
- object containing a list of records, such as `{ "customers": [...] }`
- nested object, flattened into columns with dot-style names

For example, this nested JSON:

```json
{
    "customer_id": "00123",
    "name": {
        "first": "Aino",
        "last": "Korhonen"
    }
}
```

becomes columns like:

```text
customer_id
name.first
name.last
```

During comparison, JSON is converted to CSV internally, then DuckDB converts that CSV to Parquet.

## Excel Upload Behavior

Excel files are supported with the simplest first version:

- `.xlsx` and `.xls` files are accepted.
- The first sheet is read automatically.
- Values are preserved as text where possible.
- The first sheet is converted to CSV internally before DuckDB/Parquet comparison.

If an Excel workbook has several sheets, the current version does not ask which sheet to use. It always uses the first sheet.

## DuckDB and Parquet Processing

The comparison step uses this process:

1. Convert JSON and Excel uploads to CSV internally when needed.
2. Save the uploaded or converted CSV files into a temporary folder.
3. Convert each CSV file to Parquet with DuckDB.
4. Keep all CSV columns as text during conversion to preserve IDs and codes such as `00123`.
5. Read the Parquet files with DuckDB.
6. Join records by the selected key fields.
7. Compare only fields marked with `compare = true`.
8. Normalize values according to the selected field type before comparison.

Current comparison outputs:

- total rows in Dataset A
- total rows in Dataset B
- count of records only in Dataset A
- count of records only in Dataset B
- count of different mapped values
- table of records only in Dataset A
- table of records only in Dataset B
- table of field-level differences
- table of differences grouped by field

## Mapping JSON

Saved mappings are stored in the `mappings/` folder as JSON files.

The mapping stores:

- mapping/table name
- key column from Dataset A
- key column from Dataset B
- source field names from Dataset A
- target field names from Dataset B
- field type
- compare flag
- key flag

Example structure:

```json
{
    "table": "customers",
    "key": {
        "a": "customer_id",
        "b": "cust_no"
    },
    "fields": [
        {
            "source": "customer_id",
            "target": "cust_no",
            "type": "string",
            "compare": true,
            "key": true
        }
    ]
}
```

## Main Files

| File or folder | Purpose |
| --- | --- |
| `app.py` | Streamlit user interface |
| `comparison/loader.py` | CSV, JSON, and Excel loading, preview, flattening, and conversion to CSV |
| `comparison/mapper.py` | Save, list, load, and restore JSON mappings |
| `comparison/compare_duckdb.py` | Convert CSV to Parquet and compare with DuckDB |
| `sample_data/` | Example CSV files |
| `mappings/` | Saved JSON mapping files |
| `reports/` | Future Excel reports |
| `requirements.txt` | Python dependencies |
| `README.md` | Project overview |

## Current Limitations

- No Excel report export is implemented yet.
- Mapping is based on preview columns from the first 100 rows.
- Duplicate key detection is not implemented yet.
- Result tables are limited for display, while summary counts show full counts.
- Very large JSON files are flattened in memory before comparison.

## Manual Test Checklist

Use this checklist to confirm the current stage works:

- App opens at `http://localhost:8501`
- Dataset A CSV can be uploaded
- Dataset B CSV can be uploaded
- Dataset A JSON can be uploaded
- Dataset B JSON can be uploaded
- Dataset A Excel file can be uploaded
- Dataset B Excel file can be uploaded
- Preview tables appear for both datasets
- Preview metrics show rows, columns, and file size
- Dataset A key can be selected
- Dataset B key can be selected
- Field mapping controls appear
- Fields can be mapped from Dataset A to Dataset B
- Compare checkboxes can be changed
- Key checkboxes can be changed
- Field type dropdowns can be changed
- Mapping JSON preview updates
- Mapping can be saved as JSON
- Saved JSON file appears in `mappings/`
- Saved mapping can be selected and restored with the restore button
- DuckDB comparison can be run
- Summary counts appear after comparison
- Only-in-A, only-in-B, and different-value result tables appear

## Recommended Next Stage

The next stage should improve reporting and usability around the comparison results.

Recommended next additions:

- Excel report export
- duplicate key warnings
- better result charts
- saved comparison result files
- clearer validation messages when mapped fields are missing
