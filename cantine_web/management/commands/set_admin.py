"""
Commande pour définir un utilisateur comme administrateur
Usage: python manage.py set_admin username
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cantine_web.models import ProfilPrestataire


class Command(BaseCommand):
    help = "Définit un utilisateur comme administrateur"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nom d'utilisateur")

    def handle(self, *args, **options):
        username = options["username"]

        try:
            user = User.objects.get(username=username)
            profil, created = ProfilPrestataire.objects.get_or_create(user=user)
            profil.role = "ADMIN"
            profil.actif = True
            profil.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"L'utilisateur {username} a été défini comme ADMIN avec succès."
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"L'utilisateur {username} n'existe pas.")
            )
