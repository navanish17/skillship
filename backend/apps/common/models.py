"""
Abstract base models every other app inherits from.

TimeStampedModel — created_at / updated_at on every table.
TenantModel     — UUID pk + school FK, enforcing multi-tenancy at the ORM level.
"""

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base that adds created_at / updated_at to every child table."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantQuerySet(models.QuerySet):
    """QuerySet with a .for_school() shortcut so views never forget the filter."""

    def for_school(self, school_id):
        return self.filter(school_id=school_id)


class TenantManager(models.Manager):
    """Default manager that exposes TenantQuerySet methods."""

    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_school(self, school_id):
        return self.get_queryset().for_school(school_id)


class TenantModel(TimeStampedModel):
    """
    Abstract base for every model that belongs to a school.

    Provides:
    - UUID primary key (no sequential ID leaks)
    - school FK (CASCADE — if the school is deleted, all its data goes)
    - Composite index on (school, created_at) for the most common query pattern
    - .for_school() manager method so views can't forget the tenant filter
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    objects = TenantManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["school", "created_at"]),
        ]
