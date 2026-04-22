"""
Migration 0002 — make User.email unique and install custom UserManager.

Why:
- Email uniqueness is a hard requirement now that login accepts
  {email, password} — a duplicate would make login ambiguous.
- Our check constraint `non_admin_has_school` rejects a user with
  role="" and school=NULL, which is exactly what Django's default
  `createsuperuser` would insert. The custom UserManager.create_superuser
  defaults role=MAIN_ADMIN + school=NULL, which satisfies the constraint.
"""

import apps.accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="email address"),
        ),
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", apps.accounts.models.UserManager()),
            ],
        ),
    ]
