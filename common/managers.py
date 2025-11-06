from django.utils import timezone
from django.db import models


class SoftDeleteManager(models.Manager):
    """Custom manager that excludes soft-deleted objects by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """Return all objects including soft-deleted ones"""
        return super().get_queryset()
