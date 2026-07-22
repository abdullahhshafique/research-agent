"""
Signal handlers for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created."""
    if created:
        from .models import Profile
        Profile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()