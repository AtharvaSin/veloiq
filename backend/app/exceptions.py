from uuid import UUID


class VeloIQException(Exception):  # noqa: N818 — base class uses Exception suffix; subclasses use Error
    """Base exception for all VeloIQ application errors."""

    code: str = "VELOIQ_ERROR"
    message: str = "An error occurred"

    def __str__(self) -> str:
        return self.message


class NotFoundError(VeloIQException):
    """Raised when a requested entity does not exist."""

    code = "NOT_FOUND"

    def __init__(self, entity: str, entity_id: UUID | str) -> None:
        self.entity = entity
        self.entity_id = entity_id
        self.message = f"{entity} not found: {entity_id}"
        super().__init__(self.message)


class ValidationError(VeloIQException):
    """Raised when input data fails business validation (beyond Pydantic)."""

    code = "VALIDATION_ERROR"

    def __init__(self, message: str, fields: dict[str, str] | None = None) -> None:
        self.message = message
        self.fields = fields or {}
        super().__init__(self.message)


class AuditViolationError(VeloIQException):
    """Raised when a mutation is attempted without writing an audit entry.

    This is a safety-net exception. Should never fire in well-tested code.
    """

    code = "AUDIT_VIOLATION"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class BusinessRuleError(VeloIQException):
    """Raised when a business rule is violated."""

    code = "BUSINESS_RULE"

    def __init__(self, message: str, rule: str) -> None:
        self.message = message
        self.rule = rule
        super().__init__(self.message)
