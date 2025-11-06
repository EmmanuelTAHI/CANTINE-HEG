# Guide d'utilisation de l'administration Django

## Gestion des rôles dans l'interface d'administration Django

L'interface d'administration Django a été personnalisée pour permettre de gérer facilement les rôles ADMIN et PRESTATAIRE directement depuis la page de gestion des utilisateurs.

## Comment créer un utilisateur avec un rôle

### Méthode 1 : Via l'interface d'administration Django

1. **Accédez à l'administration Django** : `http://localhost:8000/admin/`

2. **Connectez-vous** avec un compte ayant les droits d'administration

3. **Allez dans "Utilisateurs"** (dans la section "Authentification et autorisation")

4. **Cliquez sur "Ajouter un utilisateur"** en haut à droite

5. **Remplissez les informations de base** :
   - Nom d'utilisateur
   - Mot de passe
   - Confirmation du mot de passe
   - Cliquez sur "Enregistrer et continuer l'édition"

6. **Dans la page suivante, vous verrez maintenant une section "Profil Cantine"** avec les champs suivants :
   - **Rôle** : Sélectionnez "ADMIN" ou "PRESTATAIRE"
   - **Entreprise** : (optionnel) Nom de l'entreprise pour les prestataires
   - **Téléphone** : (optionnel) Numéro de téléphone
   - **Actif** : Cochez cette case pour activer le profil

7. **Cliquez sur "Enregistrer"**

### Méthode 2 : Modifier le rôle d'un utilisateur existant

1. **Allez dans "Utilisateurs"**

2. **Cliquez sur l'utilisateur** que vous voulez modifier

3. **Dans la section "Profil Cantine"**, modifiez le rôle :
   - Changez le champ **Rôle** à "ADMIN" ou "PRESTATAIRE"
   - Modifiez les autres informations si nécessaire

4. **Cliquez sur "Enregistrer"**

## Fonctionnalités de l'interface

### Liste des utilisateurs

La liste des utilisateurs affiche maintenant :
- **Nom d'utilisateur**
- **Email**
- **Prénom**
- **Nom**
- **Rôle** : Affiche le rôle (Administrateur ou Prestataire), avec "(Inactif)" si le profil est désactivé
- **Staff** : Indique si l'utilisateur peut accéder à l'admin
- **Actif** : Statut de l'utilisateur
- **Date d'inscription**

### Filtres disponibles

Vous pouvez filtrer les utilisateurs par :
- **Staff status** : Utilisateurs avec accès admin
- **Superuser status** : Superutilisateurs
- **Active** : Utilisateurs actifs
- **Rôle** : Administrateur ou Prestataire
- **Profil actif** : Profils actifs ou inactifs

### Création automatique de profil

Quand vous créez un nouvel utilisateur, un profil est automatiquement créé avec le rôle "PRESTATAIRE" par défaut. Vous pouvez ensuite modifier ce rôle dans la section "Profil Cantine".

## Gestion séparée des profils

Vous pouvez aussi gérer les profils séparément :

1. **Allez dans "Cantine web" > "Profils prestataires"**

2. Ici vous pouvez :
   - Voir tous les profils
   - Créer un nouveau profil
   - Modifier un profil existant
   - Filtrer par rôle, statut actif, etc.

## Bonnes pratiques

1. **Toujours créer un profil** : Chaque utilisateur qui doit accéder à l'application doit avoir un profil avec un rôle défini

2. **Rôle ADMIN** : Réservé aux administrateurs de l'école qui gèrent les élèves, les inscriptions, et supervisent les prestataires

3. **Rôle PRESTATAIRE** : Pour les prestataires de cantine qui gèrent les menus, marquent les repas, et créent les factures

4. **Activer/Désactiver** : Utilisez le champ "Actif" dans le profil pour activer ou désactiver un compte sans le supprimer

## Notes importantes

- Les utilisateurs sans profil ne peuvent pas accéder à l'application web (seulement à l'admin Django s'ils ont `is_staff=True`)
- Un utilisateur ne peut avoir qu'un seul profil
- Le profil est créé automatiquement avec le rôle "PRESTATAIRE" par défaut lors de la création d'un utilisateur
- Vous pouvez modifier le rôle à tout moment depuis la page de modification de l'utilisateur
