from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
ARCHIVE_DIR = PROJECT_ROOT / "archive"
LOGS_DIR = PROJECT_ROOT / "logs"

REQUIRED_COLUMNS = ["name", "email", "phone", "date"]

COLUMN_ALIASES = {
    "name": [
        "name",
        "full_name",
        "customer_name",
        "client_name",
    ],
    "email": [
        "email",
        "email_address",
        "e_mail",
        "e-mail",
    ],
    "phone": [
        "phone",
        "phone_number",
        "mobile",
        "mobile_number",
        "tel",
        "telephone",
    ],
    "date": [
        "date",
        "created_at",
        "signup_date",
        "registration_date",
    ],
}
