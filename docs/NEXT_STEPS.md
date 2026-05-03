# Dataset Comparison Tool - Next Steps

## Immediate Goal

Build a small working MVP first: upload two CSV files, preview them, select matching key columns, map fields, compare records, show results, and export an Excel report.

## Step 1 - Create the Project Structure

Create this folder layout:

```text
dataset-compare-tool/
├── app.py
├── comparison/
│   ├── __init__.py
│   ├── loader.py
│   ├── normalizer.py
│   ├── mapper.py
│   ├── compare_pandas.py
│   └── report.py
├── sample_data/
├── reports/
├── tests/
├── requirements.txt
└── README.md
```

For the first version, leave DuckDB, Parquet, saved templates, login, and scheduled comparisons for later.

## Step 2 - Install the First Dependencies

Start with only the libraries needed for the MVP:

```bash
pip install streamlit pandas openpyxl altair pytest
```

Add DuckDB and PyArrow later when the small-file comparison works:

```bash
pip install duckdb pyarrow
```

## Step 3 - Create Small Sample CSV Files

Create two test files in `sample_data/`:

- `customers_system_a.csv`
- `customers_system_b.csv`

Include:

- matching records
- one record only in Dataset A
- one record only in Dataset B
- changed values
- different column names, such as `customer_id` and `cust_no`
- IDs with leading zeros, such as `00123`, to confirm IDs stay as text

## Step 4 - Build the First Streamlit Screen

In `app.py`, build:

- title
- two CSV upload fields
- preview table for Dataset A
- preview table for Dataset B
- dropdown for key column in Dataset A
- dropdown for key column in Dataset B

This proves the basic interface works before adding comparison logic.

## Step 5 - Add Field Mapping

Add a mapping screen where each selected Dataset A column can be linked to a Dataset B column.

Each mapped field should have:

- Dataset A field
- Dataset B field
- compare checkbox
- key checkbox or key selector
- comparison mode: exact text, normalized text, number, date, boolean

For MVP, start with exact text and normalized text only.

## Step 6 - Implement Basic Pandas Comparison

In `comparison/compare_pandas.py`, create comparison logic that returns:

- records only in Dataset A
- records only in Dataset B
- records found in both but with different values
- summary counts
- differences by field

Keep IDs and codes as strings to avoid losing leading zeros.

## Step 7 - Show Results in the App

Add a simple dashboard:

- total rows in Dataset A
- total rows in Dataset B
- only in A count
- only in B count
- different records count
- bar chart for result distribution
- table showing changed values

## Step 8 - Export Excel Report

In `comparison/report.py`, create an Excel file with these sheets:

- `Summary`
- `Only in A`
- `Only in B`
- `Different Values`

Add a Streamlit download button so the report can be saved.

## Step 9 - Add Tests

Create focused tests for:

- key matching
- only-in-A detection
- only-in-B detection
- changed value detection
- normalized text comparison
- leading-zero ID preservation

## Step 10 - Improve After MVP Works

After the MVP works with small CSV files, add improvements in this order:

1. Number, date, and boolean normalization.
2. Duplicate key detection.
3. Better charts for differences by field.
4. Excel upload support.
5. Parquet conversion.
6. DuckDB large-file comparison.
7. Saved mapping templates as JSON.
8. README with screenshots, limitations, testing notes, and future work.

## Recommended First Work Session

Start with Steps 1-4 only. The target result for the first session is simple:

- the project folder exists
- dependencies are listed
- two sample CSV files exist
- Streamlit runs
- two CSV files can be uploaded and previewed
- key columns can be selected

Once that works, the comparison engine can be added with much less confusion.
