from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProfilPrestataire


@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    """Créer un profil pour chaque nouvel utilisateur"""
    if created:
        ProfilPrestataire.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    """Sauvegarder le profil quand l'utilisateur est sauvegardé"""
    if hasattr(instance, "profil"):
        instance.profil.save()
