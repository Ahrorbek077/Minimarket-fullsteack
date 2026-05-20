import factory
from factory.django import DjangoModelFactory
from companies.models import Branch, Company


class CompanyFactory(DjangoModelFactory):
    name  = factory.Sequence(lambda n: f"Company {n}")
    phone = factory.Faker("phone_number")
    inn   = factory.Sequence(lambda n: f"30000000{n:04d}")

    class Meta:
        model = Company


class BranchFactory(DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    name    = factory.Sequence(lambda n: f"Filial {n}")
    phone   = factory.Faker("phone_number")

    class Meta:
        model = Branch
