from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager


class BaseModel(models.Model):
    """Abstract base model with common fields and methods"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            # Composite index for common query patterns
            models.Index(fields=['is_deleted', 'created_at']),
            models.Index(fields=['is_deleted', 'updated_at']),
        ]

    def delete(self, using=None, keep_parents=False):
        """Soft delete instance"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete instance"""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore soft-deleted instance"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

