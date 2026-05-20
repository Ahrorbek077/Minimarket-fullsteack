"""
AuditLog utils testlari.
pytest -v history/tests/test_utils.py
"""
import pytest
from history.models import AuditAction, AuditLog
from history.utils import audit_log, audit_update, _diff
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestAuditLog:

    def test_create_log_with_instance(self):
        user = UserFactory()
        log  = audit_log(
            action   = AuditAction.CREATE,
            user     = user,
            instance = user,
        )
        assert log.pk           is not None
        assert log.action       == AuditAction.CREATE
        assert log.model_name   == "User"
        assert log.object_id    == user.pk
        assert log.user         == user

    def test_create_log_without_instance(self):
        log = audit_log(
            action      = AuditAction.LOGIN,
            model_name  = "User",
            object_id   = 99,
            object_repr = "test@test.com",
        )
        assert log.model_name == "User"
        assert log.object_id  == 99

    def test_log_with_extra(self):
        log = audit_log(
            action  = AuditAction.SALE_CHECKOUT,
            extra   = {"invoice_no": "INV-001", "amount": "50000"},
        )
        assert log.extra["invoice_no"] == "INV-001"
        assert log.extra["amount"]     == "50000"

    def test_log_with_changes(self):
        user = UserFactory()
        log  = audit_log(
            action   = AuditAction.UPDATE,
            instance = user,
            changes  = {"full_name": ["Eski", "Yangi"]},
        )
        assert log.changes["full_name"] == ["Eski", "Yangi"]

    def test_system_log_no_user(self):
        """User=None bo'lsa — tizim harakati."""
        log = audit_log(
            action      = AuditAction.CREATE,
            model_name  = "Product",
            object_repr = "Test mahsulot",
        )
        assert log.user is None

    def test_object_repr_truncated(self):
        """Uzun repr 255 belgiga kesiladi."""
        long_repr = "A" * 300
        log = audit_log(
            action      = AuditAction.CREATE,
            model_name  = "Test",
            object_id   = 1,
            object_repr = long_repr[:255],  # utils._get_repr truncate qiladi
        )
        assert len(log.object_repr) <= 255


@pytest.mark.django_db
class TestAuditUpdate:

    def test_update_with_changes(self):
        user     = UserFactory(full_name="Eski Ism")
        old_data = {"full_name": "Eski Ism", "language": "uz"}
        new_data = {"full_name": "Yangi Ism", "language": "uz"}

        log = audit_update(user=user, instance=user, old_data=old_data, new_data=new_data)
        assert log is not None
        assert log.action == AuditAction.UPDATE
        assert "full_name" in log.changes
        assert log.changes["full_name"] == ["Eski Ism", "Yangi Ism"]
        assert "language" not in log.changes   # o'zgarmaganlar kiritilmaydi

    def test_no_changes_returns_none(self):
        user     = UserFactory()
        old_data = {"full_name": "Ali", "language": "uz"}
        new_data = {"full_name": "Ali", "language": "uz"}

        result = audit_update(user=user, instance=user, old_data=old_data, new_data=new_data)
        assert result is None


class TestDiff:
    """_diff helper."""

    def test_diff_finds_changes(self):
        old = {"a": "1", "b": "2"}
        new = {"a": "1", "b": "3"}
        assert _diff(old, new) == {"b": ["2", "3"]}

    def test_diff_no_changes(self):
        d = {"a": "1", "b": "2"}
        assert _diff(d, d) == {}

    def test_diff_new_field(self):
        old = {"a": "1"}
        new = {"a": "1", "b": "2"}
        assert "b" in _diff(old, new)

    def test_diff_removed_field(self):
        old = {"a": "1", "b": "2"}
        new = {"a": "1"}
        assert "b" in _diff(old, new)
