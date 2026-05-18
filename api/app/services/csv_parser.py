"""Parse the uploaded CSV into a list of raw row dicts.

The parser is intentionally permissive — it does not validate field values, only
that the required headers are present. Field-level validation lives in
``validation_service``.
"""

import csv
import io

REQUIRED_HEADERS = (
    "client_name",
    "email",
    "amount",
    "service_type",
    "status",
    "date",
)


class CsvParseError(ValueError):
    """Raised when the uploaded CSV cannot be read or is missing headers."""


def parse_csv(raw: bytes) -> list[dict[str, str]]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CsvParseError("File is not valid UTF-8 text.") from exc

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise CsvParseError("CSV file is empty.")

    headers = {h.strip() for h in reader.fieldnames}
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise CsvParseError(f"CSV is missing required headers: {', '.join(missing)}")

    rows: list[dict[str, str]] = []
    for row in reader:
        rows.append({k: (v or "").strip() for k, v in row.items() if k is not None})
    return rows
