"""
Factory Boy factory classlar — test ma'lumotlari yaratish uchun.
"""
import factory
from factory.django import DjangoModelFactory

from users.models import User, UserRole, UserLanguage


class UserFactory(DjangoModelFactory):
    """Oddiy user (kassir)."""
    email     = factory.Sequence(lambda n: f"user{n}@test.com")
    full_name = factory.Faker("name")
    phone     = factory.Faker("phone_number")
    role      = UserRole.CASHIER
    language  = UserLanguage.UZ
    is_active = True
    password  = factory.PostGenerationMethodCall("set_password", "Test1234!")

    class Meta:
        model = User
        django_get_or_create = ["email"]


class AdminFactory(UserFactory):
    """Admin user."""
    email = factory.Sequence(lambda n: f"admin{n}@test.com")
    role  = UserRole.ADMIN
    is_staff = True


class SuperAdminFactory(UserFactory):
    """Super admin user."""
    email        = factory.Sequence(lambda n: f"superadmin{n}@test.com")
    role         = UserRole.SUPER_ADMIN
    is_staff     = True
    is_superuser = True


class StorekeeperFactory(UserFactory):
    """Omborchi user."""
    email = factory.Sequence(lambda n: f"storekeeper{n}@test.com")
    role  = UserRole.STOREKEEPER


class AccountantFactory(UserFactory):
    """Buxgalter user."""
    email = factory.Sequence(lambda n: f"accountant{n}@test.com")
    role  = UserRole.ACCOUNTANT
