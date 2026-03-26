from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.web_extractor import extract_record_from_html  # noqa: E402


def test_extract_record_from_html_returns_expected_fields() -> None:
    html = """
    <html>
      <head>
        <title>Demo Company</title>
        <meta name="description" content="Contact us for automation services">
      </head>
      <body>
        <h1>Automation Experts</h1>
        <p>Email sales@example.com or call +1 (555) 123-4567</p>
      </body>
    </html>
    """

    record = extract_record_from_html(
        url='https://example.com',
        html=html,
        extract_fields=['page_title', 'meta_description', 'h1', 'emails_found', 'phones_found'],
    )

    assert record['page_title'] == 'Demo Company'
    assert record['meta_description'] == 'Contact us for automation services'
    assert record['h1'] == 'Automation Experts'
    assert record['emails_found'] == 'sales@example.com'
    assert '555' in record['phones_found']
    assert record['fetch_status'] == 'ok'


def test_extract_record_from_html_keeps_multiple_emails() -> None:
    html = """
    <html>
      <body>
        <p>Contact press@example.org and fundraising@example.org for more information.</p>
      </body>
    </html>
    """

    record = extract_record_from_html(
        url='https://example.org/contact',
        html=html,
        extract_fields=['emails_found'],
    )

    assert record['emails_found'] == 'press@example.org; fundraising@example.org'

