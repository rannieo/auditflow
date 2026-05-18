"""Unit tests for app.services.csv_parser."""

import pytest

from app.services.csv_parser import REQUIRED_HEADERS, CsvParseError, parse_csv


def test_parse_csv_with_valid_rows_returns_dicts(good_csv_bytes: bytes) -> None:
    rows = parse_csv(good_csv_bytes)

    assert len(rows) == 2
    assert rows[0]["client_name"] == "Acme Inc"
    assert rows[0]["email"] == "ops@acme.com"
    assert rows[1]["client_name"] == "Beta LLC"


def test_parse_csv_trims_whitespace_from_values() -> None:
    raw = b"client_name,email,amount,service_type,status,date\n  Acme  ,  a@b.co  ,100,tax_filing,pending,2026-05-18\n"

    rows = parse_csv(raw)

    assert rows[0]["client_name"] == "Acme"
    assert rows[0]["email"] == "a@b.co"


def test_parse_csv_with_missing_header_raises() -> None:
    raw = b"client_name,email,amount,service_type,status\nAcme,a@b.co,100,tax_filing,pending\n"

    with pytest.raises(CsvParseError, match="date"):
        parse_csv(raw)


def test_parse_csv_with_empty_file_raises() -> None:
    with pytest.raises(CsvParseError, match="empty"):
        parse_csv(b"")


def test_parse_csv_with_non_utf8_raises() -> None:
    # 0xFF is not valid UTF-8 in this position.
    raw = b"\xff\xfe\x00\x00bogus"

    with pytest.raises(CsvParseError, match="UTF-8"):
        parse_csv(raw)


def test_parse_csv_with_only_headers_returns_empty_list() -> None:
    raw = ",".join(REQUIRED_HEADERS).encode("utf-8") + b"\n"

    rows = parse_csv(raw)

    assert rows == []
