"""Tests for tenant_service — tenant isolation keystone."""
import uuid as _uuid
from unittest.mock import MagicMock

import pytest

from app.models.base import RoleEnum
from app.models.company_member import CompanyMember
from app.services.tenant_service import (
    assert_membership,
    get_membership,
    require_role,
)


@pytest.fixture()
def fake_db():
    """A MagicMock Session whose .query(...).filter(...).first() is configurable."""
    db = MagicMock()
    chain = db.query.return_value.filter.return_value
    db._chain = chain
    return db


@pytest.fixture()
def membership_row():
    row = MagicMock(spec=CompanyMember)
    row.role = RoleEnum.admin
    return row


def _member_query(db, row):
    """Configure fake_db so query(...).filter(...).first() returns `row`."""
    db.query.return_value.filter.return_value.first.return_value = row


# --- assert_membership ----------------------------------------------------

def test_assert_membership_returns_row_when_found(fake_db, membership_row):
    _member_query(fake_db, membership_row)

    result = assert_membership(fake_db, "11111111-1111-1111-1111-111111111111",
                                "22222222-2222-2222-2222-222222222222")

    assert result is membership_row
    fake_db.query.assert_called_once_with(CompanyMember)


def test_assert_membership_accepts_uuid_objects(fake_db, membership_row):
    _member_query(fake_db, membership_row)
    cid = _uuid.uuid4()
    uid = _uuid.uuid4()

    assert assert_membership(fake_db, cid, uid) is membership_row


def test_assert_membership_raises_forbidden_when_missing(fake_db):
    fake_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Forbidden"):
        assert_membership(fake_db, "11111111-1111-1111-1111-111111111111",
                          "22222222-2222-2222-2222-222222222222")


# --- get_membership -------------------------------------------------------

def test_get_membership_returns_row_when_found(fake_db, membership_row):
    _member_query(fake_db, membership_row)
    assert get_membership(fake_db, "11111111-1111-1111-1111-111111111111",
                          "22222222-2222-2222-2222-222222222222") is membership_row


def test_get_membership_returns_none_when_missing(fake_db):
    fake_db.query.return_value.filter.return_value.first.return_value = None
    assert get_membership(fake_db, _uuid.uuid4(), _uuid.uuid4()) is None


# --- require_role ---------------------------------------------------------

def test_require_role_passes_when_role_allowed(membership_row):
    require_role(membership_row, RoleEnum.admin, RoleEnum.auditor)


def test_require_role_passes_for_single_allowed_role(membership_row):
    require_role(membership_row, RoleEnum.admin)


def test_require_role_raises_forbidden_when_role_not_allowed(membership_row):
    with pytest.raises(ValueError, match="Forbidden"):
        require_role(membership_row, RoleEnum.reader)


def test_require_role_raises_when_no_roles_provided(membership_row):
    with pytest.raises(ValueError, match="Forbidden"):
        require_role(membership_row)