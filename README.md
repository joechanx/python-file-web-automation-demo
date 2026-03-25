# Python File + Web Data Automation Demo

A lightweight, Railway-ready Python automation demo with Streamlit UI for two common client workflows:

1. **File automation** for CSV/XLSX cleanup, deduplication, and reporting
2. **Public webpage data intake** for URL-based extraction followed by cleanup and export

## Live Demo

**Demo URL:** [Home](https://python-file-automation-demo-production.up.railway.app)

> Upload spreadsheet files or enter public URLs, then run a reusable automation workflow that extracts, cleans, deduplicates, and exports business-ready output files.

![Process](.\samples\file-automation-cover.png)

## What This Demo Shows

This project is designed to look closer to a real client deliverable than a one-off script. It combines:

- CSV/XLSX batch processing
- UI-based rule selection
- config-driven schema handling
- extensible Python transformation rules
- public webpage data extraction
- Railway deployment setup

## Workflow Modes

### 1) File Automation

```text
CSV/XLSX files -> column mapping -> cleaning -> deduplication -> summary -> export
```

### 2) URL Data Import

```text
Single URL / URL list -> webpage extraction -> structured records -> cleaning -> deduplication -> summary -> export
```

## Extracted Web Fields

The URL intake workflow can extract these fields from public webpages:

- `source_url`
- `page_title`
- `meta_description`
- `h1`
- `emails_found`
- `phones_found`
- `fetch_status`
- `fetch_error`

This makes the demo suitable for positioning around:

- website data extraction
- lead collection automation
- contact enrichment workflows
- small business research automation

## Why This Is Useful for Freelance Positioning

Many clients do not only need file cleanup. They need a broader workflow such as:

- collect data from public webpages
- normalize the results
- remove duplicates
- export a clean master file
- generate a summary they can review

This demo is intentionally designed around that end-to-end use case.

## Key Features

- Streamlit UI for non-technical users
- CSV/XLSX upload and processing
- single URL input, pasted URL list, or uploaded URL list
- column mapping and rule configuration through the UI
- email, phone, date, and amount normalization
- deduplication with configurable keys
- rejected rows export
- summary JSON generation
- Railway-ready deployment

## Project Structure

```text
python-file-automation-demo/
├─ .streamlit/
│  └─ config.toml
├─ config/
│  ├─ column_mapping.json
│  └─ rules.json
├─ input/
│  ├─ customers_january.csv
│  ├─ customers_february.xlsx
│  ├─ leads_sample.csv
│  └─ sample_urls.csv
├─ src/
│  ├─ cleaner.py
│  ├─ config.py
│  ├─ main.py
│  ├─ merger.py
│  ├─ pipeline.py
│  ├─ reader.py
│  ├─ reporter.py
│  ├─ url_loader.py
│  ├─ utils.py
│  ├─ web_extractor.py
│  └─ web_fetcher.py
├─ tests/
├─ app.py
├─ railway.json
├─ requirements.txt
└─ README.md
```

## Configuration Design

The underlying workflow remains config-driven even though users interact through a UI.

### `config/column_mapping.json`
Maps input columns into standard internal fields.

### `config/rules.json`
Controls required fields, output fields, dedupe keys, and cleaning rules.

This means the project can support:

- evolving spreadsheet schemas
- reusable file-processing logic
- custom transformation rules such as `amount_decimal`
- new input adapters like URL extraction

## Amount Rule Example

The demo includes a Python-based normalization rule for financial values. Inputs like:

- `1,000`
- `$1,000`
- `NT$ 1,000.5`
- `(1,200.75)`

can be normalized to:

- `1000.00`
- `1000.00`
- `1000.50`
- `-1200.75`

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

### Streamlit UI

```bash
streamlit run app.py
```

### CLI mode for bundled file input

```bash
python src/main.py
```

## Railway Deployment

This repo includes:

- `railway.json`
- `.streamlit/config.toml`

Deploy flow:

1. Push the repo to GitHub
2. Create a Railway project
3. Choose **Deploy from GitHub repo**
4. Select the repository
5. Generate a public domain

The app starts with:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## Recommended Use Cases

- clean and merge messy customer spreadsheets
- collect title/contact data from public webpages
- create lead research lists from small URL batches
- normalize exported operational spreadsheets for reporting

## Tests

```bash
pytest -q
```

## License

This project is provided for demonstration and portfolio purposes.
