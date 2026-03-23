from __future__ import annotations

try:
    from .config import load_column_aliases, load_rules
    from .pipeline import process_dataframes
    from .reader import load_input_data
    from .reporter import setup_logging, write_master_file, write_rejected_rows, write_summary
    from .utils import archive_file, ensure_directories
except ImportError:
    from config import load_column_aliases, load_rules
    from pipeline import process_dataframes
    from reader import load_input_data
    from reporter import setup_logging, write_master_file, write_rejected_rows, write_summary
    from utils import archive_file, ensure_directories


def run() -> dict:
    ensure_directories()
    logger = setup_logging()
    column_aliases = load_column_aliases()
    rules = load_rules()

    dataframes, file_paths = load_input_data()
    result = process_dataframes(
        dataframes=dataframes,
        file_names=[path.name for path in file_paths],
        column_aliases=column_aliases,
        rules=rules,
    )

    if not dataframes:
        logger.info('No input files found.')
        write_summary(result['summary'])
        return result['summary']

    output_path = write_master_file(result['output'])
    write_rejected_rows(result['rejected'])
    summary = dict(result['summary'])
    summary['output_file'] = str(output_path.relative_to(output_path.parent.parent))
    write_summary(summary)

    for file_path in file_paths:
        archived_path = archive_file(file_path)
        logger.info('Archived processed file: %s', archived_path.name)

    logger.info('Processing completed: %s', summary)
    return summary


if __name__ == '__main__':
    result = run()
    print('Processing completed.')
    print(result)
