# Guide de création d'utilisateurs

Ce guide explique comment créer des utilisateurs avec les rôles ADMIN et PRESTATAIRE dans l'application Gestion Cantine HEG.

## Méthode 1 : Commande de management (RECOMMANDÉ)

### Créer un utilisateur ADMIN

```bash
python manage.py create_user admin admin@heg.com motdepasse123 ADMIN --first-name "Admin" --last-name "HEG"
```

### Créer un utilisateur PRESTATAIRE

```bash
python manage.py create_user prestataire prestataire@example.com motdepasse123 PRESTATAIRE --entreprise "Restaurant ABC" --telephone "+225 07 12 34 56 78"
```

### Options disponibles

- `username` : Nom d'utilisateur (obligatoire)
- `email` : Email (obligatoire)
- `password` : Mot de passe (obligatoire)
- `role` : ADMIN ou PRESTATAIRE (obligatoire)
- `--entreprise` : Nom de l'entreprise (optionnel, pour prestataire)
- `--telephone` : Numéro de téléphone (optionnel)
- `--first-name` : Prénom (optionnel)
- `--last-name` : Nom (optionnel)

## Méthode 2 : Interface d'administration Django

1. Accédez à l'interface d'administration : `http://localhost:8000/admin/`
2. Connectez-vous avec un compte ayant les droits d'administration
3. Allez dans **Prestataires** > **Profils prestataires**
4. Cliquez sur **Ajouter un profil prestataire**
5. Créez d'abord un utilisateur dans **Autentification et autorisation** > **Utilisateurs** si nécessaire
6. Sélectionnez l'utilisateur et définissez le rôle (ADMIN ou PRESTATAIRE)

## Méthode 3 : Shell Django

### Créer un ADMIN

```python
python manage.py shell
```

Puis dans le shell :

```python
from django.contrib.auth.models import User
from cantine_web.models import ProfilPrestataire

# Créer l'utilisateur
user = User.objects.create_user(
    username='admin',
    email='admin@heg.com',
    password='motdepasse123',
    first_name='Admin',
    last_name='HEG',
    is_staff=True
)

# Créer le profil avec le rôle ADMIN
profil = ProfilPrestataire.objects.create(
    user=user,
    role='ADMIN',
    actif=True
)

print(f"✅ Utilisateur {user.username} créé avec le rôle ADMIN")
```

### Créer un PRESTATAIRE

```python
from django.contrib.auth.models import User
from cantine_web.models import ProfilPrestataire

# Créer l'utilisateur
user = User.objects.create_user(
    username='prestataire',
    email='prestataire@example.com',
    password='motdepasse123',
    first_name='Jean',
    last_name='Dupont',
    is_staff=True
)

# Créer le profil avec le rôle PRESTATAIRE
profil = ProfilPrestataire.objects.create(
    user=user,
    role='PRESTATAIRE',
    entreprise='Restaurant ABC',
    telephone='+225 07 12 34 56 78',
    actif=True
)

print(f"✅ Utilisateur {user.username} créé avec le rôle PRESTATAIRE")
```

## Méthode 4 : Modifier le rôle d'un utilisateur existant

### Via la commande de management

```bash
python manage.py set_admin username
```

### Via le shell Django

```python
from django.contrib.auth.models import User
from cantine_web.models import ProfilPrestataire

# Récupérer l'utilisateur
user = User.objects.get(username='nom_utilisateur')

# Créer ou mettre à jour le profil
profil, created = ProfilPrestataire.objects.get_or_create(user=user)
profil.role = 'ADMIN'  # ou 'PRESTATAIRE'
profil.actif = True
profil.save()

print(f"✅ Rôle de {user.username} mis à jour")
```

## Vérifier les rôles

Pour vérifier les rôles des utilisateurs :

```python
from django.contrib.auth.models import User

for user in User.objects.all():
    if hasattr(user, 'profil'):
        print(f"{user.username}: {user.profil.get_role_display()} ({user.profil.role})")
    else:
        print(f"{user.username}: Pas de profil")
```

## Permissions

- **ADMIN** : Accès complet à toutes les fonctionnalités (élèves, inscriptions, menus, repas, factures, prestataires, statistiques, rapports)
- **PRESTATAIRE** : Accès limité (menus, repas, factures, décomptes, statistiques, rapports)

## Notes importantes

1. Tous les utilisateurs doivent avoir `is_staff=True` pour accéder à l'interface d'administration Django
2. Un utilisateur ne peut avoir qu'un seul profil
3. Si un utilisateur n'a pas de profil, il ne pourra pas accéder à l'application
4. Utilisez la commande `create_missing_profils` pour créer automatiquement des profils pour les utilisateurs existants sans profil
