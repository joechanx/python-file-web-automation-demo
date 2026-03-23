# Python File Automation Demo

A lightweight Python automation tool for cleaning, merging, and reporting Excel/CSV files in a repeatable workflow.

## Overview

This project demonstrates a simple but practical Python automation workflow:

1. Read multiple CSV/XLSX files from `input/`
2. Normalize column names
3. Clean email / phone / date formats
4. Validate required fields
5. Merge records into a master file
6. Remove duplicate rows
7. Generate a summary report and processing log
8. Move processed files to `archive/`

## Use Case

Many clients receive messy Excel or CSV files from different sources.  
Cleaning them manually is repetitive, error-prone, and time-consuming.

This demo shows how a repeatable Python script can automate that workflow.

## Features

- Batch import CSV and XLSX files
- Standardize columns such as:
  - `Email`, `email address`, `E-mail` -> `email`
  - `Phone`, `mobile`, `phone_number` -> `phone`
  - `Date`, `created_at`, `signup_date` -> `date`
  - `Name`, `full_name`, `customer_name` -> `name`
- Normalize field values
- Remove duplicates
- Export `output/master.csv`
- Preserve source file traceability with `source_file`
- Export `output/summary.json`
- Export `output/rejected_rows.csv`
- Write `logs/process.log`
- Archive processed files automatically

## Folder Structure

```text
python-file-automation-demo/
├─ input/
├─ output/
├─ archive/
├─ logs/
├─ samples/
├─ src/
├─ tests/
├─ requirements.txt
└─ README.md
```

## Required Standard Columns

The workflow normalizes incoming files into these target fields:

- `name`
- `email`
- `phone`
- `date`

## How to Run

```bash
pip install -r requirements.txt
python src/main.py
```

## Example Output

After running the script, you will get:

- `output/master.csv`
- `output/summary.json`
- `output/rejected_rows.csv`
- `logs/process.log`

## Sample Summary

```json
{
  "files_processed": 3,
  "rows_read": 8,
  "rows_after_cleaning": 4,
  "duplicates_removed": 1,
  "invalid_rows": 3,
  "output_file": "output/master.csv"
}
```

## Good Portfolio Positioning

This repository is suitable for showcasing:

- Python automation
- File processing automation
- Excel / CSV automation
- Data workflow scripting
- Custom Python tools

## Demo Pitch

Built a lightweight Python automation tool that processes multiple Excel/CSV files, normalizes fields, removes duplicates, generates summary reports, and creates a repeatable workflow that reduces manual file handling.
