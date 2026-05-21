"""
Seed migration: default o'lchov birliklari va kategoriyalar.
"""
from django.db import migrations


UNITS = [
    ("Kilogramm",  "kg"),
    ("Gramm",      "g"),
    ("Litr",       "L"),
    ("Millilitr",  "mL"),
    ("Metr",       "m"),
    ("Santimetr",  "sm"),
    ("Dona",       "dona"),
    ("Paket",      "pkt"),
    ("Quti",       "quti"),
    ("Blok",       "blok"),
    ("Pachka",     "pch"),
]

CATEGORIES = [
    "Oziq-ovqat",
    "Ichimliklar",
    "Sut mahsulotlari",
    "Non va non mahsulotlari",
    "Go'sht va baliq",
    "Meva va sabzavot",
    "Shirinliklar va pechenye",
    "Tozalik va gigiyena",
    "Maishiy kimyo",
    "Choy va qahva",
    "Ziravorlar va souslar",
    "Konservalar",
    "Boshqa",
]


def seed_units(apps, schema_editor):
    Unit = apps.get_model("products", "Unit")
    for name, short_name in UNITS:
        Unit.objects.get_or_create(name=name, defaults={"short_name": short_name})


def seed_categories(apps, schema_editor):
    Category = apps.get_model("products", "Category")
    for name in CATEGORIES:
        Category.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(seed_units, migrations.RunPython.noop),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
