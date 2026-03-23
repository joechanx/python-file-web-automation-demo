# Python File Automation Demo

A lightweight, config-driven Python automation tool for cleaning, merging, deduplicating, and reporting Excel/CSV files in a repeatable workflow.

## UI Version Included

This project now includes a lightweight Streamlit interface so non-technical users can configure field mapping and processing rules without editing raw JSON files.

The UI supports:

- CSV / XLSX upload
- field mapping through dropdowns
- required field selection
- output field selection
- dedupe rule selection
- cleanup rule toggles for email, phone, date, and amount
- preview and download of processed results

Run the UI with:

```bash
streamlit run app.py
```

## Overview

This project demonstrates a practical Python automation workflow for handling repetitive file-processing tasks. It imports multiple Excel and CSV files, normalizes inconsistent column names, cleans common data issues, removes duplicates, generates summary reports, and archives processed files.

The workflow is designed to be config-driven, so many column changes can be handled through configuration updates instead of rewriting the core script. The Streamlit UI sits on top of the same processing engine.

## Why This Project Matters

Many businesses receive operational or customer data in multiple spreadsheet files with:

- inconsistent column names
- formatting issues
- duplicate records
- missing required values
- repetitive manual cleanup work

This project shows how Python can automate that process in a reusable and maintainable way.

## Key Highlights

- Batch import of CSV and XLSX files
- Streamlit UI for non-technical users
- Column alias mapping through JSON config or UI selections
- Configurable required fields and output columns
- Email, phone, date, and amount normalization
- Duplicate removal using configurable keys
- Summary report generation
- Rejected rows export
- Process logging
- Archive workflow for processed files

## Project Structure

```text
python-file-automation-demo/
├─ app.py
├─ config/
│  ├─ column_mapping.json
│  └─ rules.json
├─ input/
├─ output/
├─ archive/
├─ logs/
├─ samples/
├─ src/
│  ├─ main.py
│  ├─ pipeline.py
│  ├─ config.py
│  ├─ reader.py
│  ├─ cleaner.py
│  ├─ merger.py
│  ├─ reporter.py
│  └─ utils.py
├─ tests/
├─ requirements.txt
└─ README.md
```

## How It Works

The workflow follows these steps:

1. Read all supported files from `input/` or from the UI uploader
2. Normalize incoming column names based on config or UI-selected mapping
3. Validate required fields
4. Clean selected columns
5. Merge all records into a single dataset
6. Remove duplicates using configured keys
7. Export clean output files
8. Write logs and summary reports
9. Move processed files to `archive/` in CLI mode

## Supported File Types

- `.csv`
- `.xlsx`

## Configuration-Driven Design

This project uses external JSON configuration so the workflow is easier to maintain. The UI can generate equivalent config choices without requiring manual JSON edits.

## Amount Normalization Rule

This project also includes an extensible field transformation example for financial values through the `amount_decimal` rule.

Example source values:

- `1000`
- `1,000`
- `$1,000`
- `NT$ 1,000.5`
- `(1,200.75)`

Normalized output values:

- `1000.00`
- `1000.00`
- `1000.00`
- `1000.50`
- `-1200.75`

## Installation

### 1. Clone the repository

### 2. Create and activate a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the UI

```bash
streamlit run app.py
```

## Run the CLI Version

Place your input files into the `input/` folder, then run:

```bash
python src/main.py
```

## Example Output

After execution, the project will generate files such as:

- `output/master.csv`
- `output/summary.json`
- `output/rejected_rows.csv`
- `logs/process.log`

## Portfolio Positioning

This project is suitable for showcasing skills in:

- Python automation
- Excel/CSV processing
- file workflow automation
- config-driven scripting
- lightweight internal tools
- user-friendly data operations UI

## Business Value

This project demonstrates both config-driven schema handling and a simple UI layer for non-technical users, making it more suitable for real client delivery than a one-off script.
