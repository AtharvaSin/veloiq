from uuid import uuid4

import pytest

from app.exceptions import (
    AuditViolationError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
    VeloIQException,
)


def test_not_found_error_has_entity_and_id():
    entity_id = uuid4()
    exc = NotFoundError(entity="standard", entity_id=entity_id)

    assert exc.entity == "standard"
    assert exc.entity_id == entity_id
    assert exc.code == "NOT_FOUND"
    assert "standard" in str(exc)


def test_validation_error_captures_fields():
    exc = ValidationError(message="Invalid payload", fields={"ac_code": "required"})

    assert exc.message == "Invalid payload"
    assert exc.fields == {"ac_code": "required"}
    assert exc.code == "VALIDATION_ERROR"


def test_audit_violation_error_is_critical():
    exc = AuditViolationError(message="Mutation without audit")

    assert exc.code == "AUDIT_VIOLATION"
    assert exc.message == "Mutation without audit"


def test_business_rule_error_includes_rule_name():
    exc = BusinessRuleError(message="Cannot suspend active cert", rule="cert_status_transition")

    assert exc.rule == "cert_status_transition"
    assert exc.code == "BUSINESS_RULE"


def test_all_exceptions_inherit_from_base():
    assert issubclass(NotFoundError, VeloIQException)
    assert issubclass(ValidationError, VeloIQException)
    assert issubclass(AuditViolationError, VeloIQException)
    assert issubclass(BusinessRuleError, VeloIQException)
