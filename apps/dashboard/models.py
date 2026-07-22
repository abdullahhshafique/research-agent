"""
Dashboard app models.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets


class ApiKeyStore(models.Model):
    """
    Stores API keys for runtime rotation without restart.
    """
    KEY_CHOICES = [
        ('groq', 'GROQ_API_KEY'),
        ('tavily', 'TAVILY_API_KEY'),
        ('google', 'GOOGLE_API_KEY'),
    ]

    key_name = models.CharField(max_length=50, choices=KEY_CHOICES, unique=True)
    key_value = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    rotated_at = models.DateTimeField(null=True, blank=True)
    rotated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_key_store'
        ordering = ['key_name']

    def __str__(self):
        return f"{self.key_name} ({'active' if self.is_active else 'inactive'})"

    def rotate(self, new_value: str, user=None):
        """Rotate the API key to a new value."""
        self.key_value = new_value
        self.is_active = True
        self.rotated_by = user
        self.rotated_at = timezone.now()
        self.save()

    def deactivate(self):
        """Deactivate this key without deleting."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    @classmethod
    def get_key(cls, key_name: str) -> str:
        """Get active key value by name."""
        try:
            key_store = cls.objects.get(key_name=key_name, is_active=True)
            return key_store.key_value
        except cls.DoesNotExist:
            return ''

    @classmethod
    def sync_from_env(cls):
        """Sync keys from environment variables on startup."""
        env_keys = {
            'groq': getattr(settings, 'GROQ_API_KEY', ''),
            'tavily': getattr(settings, 'TAVILY_API_KEY', ''),
            'google': getattr(settings, 'GOOGLE_API_KEY', ''),
        }

        for key_name, key_value in env_keys.items():
            if key_value:
                cls.objects.update_or_create(
                    key_name=key_name,
                    defaults={
                        'key_value': key_value,
                        'is_active': True,
                    }
                )