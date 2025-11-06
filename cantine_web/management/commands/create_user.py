"""
Commande pour créer un utilisateur avec un rôle
Usage: python manage.py create_user username email password role [--entreprise "Nom entreprise"]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cantine_web.models import ProfilPrestataire
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = "Crée un utilisateur avec un rôle (ADMIN ou PRESTATAIRE)"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nom d'utilisateur")
        parser.add_argument("email", type=str, help="Email")
        parser.add_argument("password", type=str, help="Mot de passe")
        parser.add_argument(
            "role",
            type=str,
            choices=["ADMIN", "PRESTATAIRE"],
            help="Rôle (ADMIN ou PRESTATAIRE)",
        )
        parser.add_argument(
            "--entreprise", type=str, help="Nom de l'entreprise (pour prestataire)"
        )
        parser.add_argument("--first-name", type=str, help="Prénom")
        parser.add_argument("--last-name", type=str, help="Nom")
        parser.add_argument("--telephone", type=str, help="Téléphone")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        role = options["role"]
        entreprise = options.get("entreprise", "")
        first_name = options.get("first_name", "")
        last_name = options.get("last_name", "")
        telephone = options.get("telephone", "")

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'L\'utilisateur "{username}" existe déjà.')
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'L\'email "{email}" est déjà utilisé.'))
            return

        try:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,  # Permet d'accéder à l'admin Django
            )

            # Créer ou mettre à jour le profil
            profil, created = ProfilPrestataire.objects.get_or_create(user=user)
            profil.role = role
            profil.actif = True

            if entreprise:
                profil.entreprise = entreprise
            if telephone:
                profil.telephone = telephone

            profil.save()

            role_display = "Administrateur" if role == "ADMIN" else "Prestataire"
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Utilisateur "{username}" créé avec succès avec le rôle {role_display}.'
                )
            )
            self.stdout.write(self.style.SUCCESS(f"   Email: {email}"))
            if entreprise:
                self.stdout.write(self.style.SUCCESS(f"   Entreprise: {entreprise}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la création: {str(e)}"))
