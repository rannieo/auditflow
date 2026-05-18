"""Unit tests for app.services.validation_service.

Each rule is exercised via @pytest.mark.parametrize so adding a rule means
adding a row, not a function.
"""

import pytest

from app.services.validation_service import (
    DUPLICATE,
    FAILED,
    PASSED,
    validate_rows,
)


def _row(**overrides: str) -> dict[str, str]:
    base = {
        "client_name": "Acme",
        "email": "ops@acme.com",
        "amount": "100",
        "service_type": "tax_filing",
        "status": "pending",
        "date": "2026-05-18",
    }
    base.update(overrides)
    return base


def test_validate_rows_with_clean_row_returns_passed() -> None:
    records = validate_rows([_row()])

    assert records[0].validation_status == PASSED
    assert records[0].validation_errors == []


@pytest.mark.parametrize(
    "field,bad_value,expected_error_fragment",
    [
        pytest.param("client_name", "", "client_name is required", id="missing-client-name"),
        pytest.param("email", "", "email is required", id="missing-email"),
        pytest.param("email", "not-an-email", "valid email", id="invalid-email"),
        pytest.param("amount", "", "amount is required", id="missing-amount"),
        pytest.param("amount", "abc", "amount must be a number", id="non-numeric-amount"),
        pytest.param("amount", "0", "greater than 0", id="zero-amount"),
        pytest.param("amount", "-1", "greater than 0", id="negative-amount"),
        pytest.param("service_type", "", "service_type is required", id="missing-service"),
        pytest.param("service_type", "wat", "service_type must be one of", id="unknown-service"),
        pytest.param("status", "", "status is required", id="missing-status"),
        pytest.param("status", "wat", "status must be one of", id="unknown-status"),
        pytest.param("date", "", "date is required", id="missing-date"),
        pytest.param("date", "not-a-date", "valid ISO date", id="bad-date"),
    ],
)
def test_validate_rows_flags_each_rule_violation(
    field: str, bad_value: str, expected_error_fragment: str
) -> None:
    record = validate_rows([_row(**{field: bad_value})])[0]

    assert record.validation_status == FAILED
    assert any(expected_error_fragment in err for err in record.validation_errors)


def test_validate_rows_marks_exact_duplicates_as_duplicate() -> None:
    rows = [_row(), _row()]

    records = validate_rows(rows)

    assert all(r.validation_status == DUPLICATE for r in records)
    assert all("duplicate record" in r.validation_errors for r in records)


def test_validate_rows_does_not_mark_unique_rows_as_duplicate() -> None:
    rows = [_row(client_name="Acme"), _row(client_name="Beta")]

    records = validate_rows(rows)

    assert {r.validation_status for r in records} == {PASSED}


def test_validate_rows_does_not_match_failed_rows_with_unparseable_amount_as_duplicates() -> None:
    rows = [_row(amount="abc"), _row(amount="abc")]

    records = validate_rows(rows)

    # Both failed; neither is flagged duplicate because amount is None on both
    # and the duplicate key skips records missing the comparison fields.
    assert all(r.validation_status == FAILED for r in records)


def test_validate_rows_preserves_input_order() -> None:
    rows = [_row(client_name="A"), _row(client_name="B"), _row(client_name="C")]

    records = validate_rows(rows)

    assert [r.client_name for r in records] == ["A", "B", "C"]
