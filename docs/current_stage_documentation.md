# Dataset Comparison Tool - Current Stage Documentation

## Stage Summary

This stage contains the first working setup flow for the Dataset Comparison Tool. The application can upload two CSV files, preview a small part of each file, select key columns, create field mappings, save mappings as JSON, and restore saved mappings from JSON.

The comparison engine is not implemented yet. DuckDB is also not used yet; it is planned for a later large-file comparison step.

## Implemented Features

- Streamlit application entry point in `app.py`
- Upload controls for Dataset A and Dataset B
- CSV preview with Pandas
- Large-file friendly preview behavior
- Key-column selection for both datasets
- Field mapping screen
- Compare/key checkboxes for mapped fields
- Field type selection
- JSON mapping preview
- Save mapping to `mappings/`
- Restore mapping from a saved JSON file
- Sample CSV files for testing

## Current User Workflow

1. Start the Streamlit app.
2. Upload Dataset A as a CSV file.
3. Upload Dataset B as a CSV file.
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

This keeps the setup screen responsive for large files. Full-file processing will be handled later in the comparison step.

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
| `comparison/mapper.py` | Save, list, load, and restore JSON mappings |
| `sample_data/` | Example CSV files |
| `mappings/` | Saved JSON mapping files |
| `reports/` | Future Excel reports |
| `requirements.txt` | Python dependencies |
| `README.md` | Project overview |

## Current Limitations

- No actual dataset comparison is implemented yet.
- No Excel report export is implemented yet.
- DuckDB is not used yet.
- Only CSV upload is supported.
- Mapping is based on preview columns from the first 100 rows.
- Type choices are stored, but normalization and comparison rules are not applied yet.
- Duplicate key detection is not implemented yet.

## Manual Test Checklist

Use this checklist to confirm the current stage works:

- App opens at `http://localhost:8501`
- Dataset A CSV can be uploaded
- Dataset B CSV can be uploaded
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

## Recommended Next Stage

The next stage should implement the first comparison engine using Pandas and the saved mapping.

Recommended result outputs:

- Records only in Dataset A
- Records only in Dataset B
- Records found in both but with different values
- Summary counts
- Differences by field

After the Pandas version works, DuckDB and Parquet can be added for large-file processing.
