"""
Commande pour créer les profils manquants pour les utilisateurs existants
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cantine_web.models import ProfilPrestataire


class Command(BaseCommand):
    help = "Crée les profils manquants pour les utilisateurs existants"

    def handle(self, *args, **options):
        users_without_profil = User.objects.filter(profil__isnull=True)
        count = 0

        for user in users_without_profil:
            ProfilPrestataire.objects.create(
                user=user,
                role="PRESTATAIRE",  # Par défaut, on met PRESTATAIRE
                actif=True,
            )
            count += 1
            self.stdout.write(self.style.SUCCESS(f"Profil créé pour {user.username}"))

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("Tous les utilisateurs ont déjà un profil.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"{count} profil(s) créé(s) avec succès.")
            )
