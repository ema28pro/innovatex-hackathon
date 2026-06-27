"""Tenant membership & role authorization keystone.

Every tenant-scoped request must call ``assert_membership`` before touching
company data — this is the IDOR guard that prevents cross-tenant leaks.
``require_role`` layers RBAC on top of a resolved membership row.
"""
import uuid as _uuid
from typing import Union

from sqlalchemy.orm import Session

from app.models.company_member import CompanyMember

_UUIDish = Union[str, _uuid.UUID]


def _to_uuid(value: _UUIDish) -> _uuid.UUID:
    """Coerce ``str`` | ``UUID`` -> ``UUID`` (raises ValueError on bad input)."""
    return _uuid.UUID(str(value))


def get_membership(
    db: Session, company_id: _UUIDish, user_id: _UUIDish
) -> CompanyMember | None:
    """Return the membership row for ``(company_id, user_id)`` or ``None``.

    Non-raising variant — use when the caller wants to branch on presence.
    """
    cid = _to_uuid(company_id)
    uid = _to_uuid(user_id)
    return (
        db.query(CompanyMember)
        .filter(
            (CompanyMember.company_id == cid)
            & (CompanyMember.profile_id == uid)
        )
        .first()
    )


def assert_membership(
    db: Session, company_id: _UUIDish, user_id: _UUIDish
) -> CompanyMember:
    """Resolve and return the membership row, raising ``ValueError`` if absent.

    This is the IDOR guard: callers must invoke it before reading or mutating
    any tenant-scoped resource so a user from company A can never reach
    company B's data.
    """
    membership = get_membership(db, company_id, user_id)
    if membership is None:
        raise ValueError("Forbidden")
    return membership


def require_role(membership: CompanyMember, *allowed_roles) -> None:
    """Raise ``ValueError("Forbidden")`` unless the membership's role is allowed.

    ``allowed_roles`` are compared against ``membership.role``. Enum members and
    their string values are both accepted. With no ``allowed_roles`` supplied,
    no role can match, so the call always forbids — useful as a fail-safe.
    """
    if not allowed_roles:
        raise ValueError("Forbidden")

    role = membership.role
    allowed = set()
    for r in allowed_roles:
        allowed.add(r)
        allowed.add(getattr(r, "value", r))

    # Compare both the enum and its string value to tolerate str-based checks.
    if role in allowed or getattr(role, "value", None) in allowed:
        return
    raise ValueError("Forbidden")