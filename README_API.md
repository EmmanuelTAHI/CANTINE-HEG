# API REST pour Application Flutter

## Résumé

Une API REST complète a été créée pour permettre au prestataire d'utiliser une application Flutter mobile. L'administration continue d'utiliser l'interface web Django.

## Installation

1. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

2. **Appliquer les migrations :**
```bash
python manage.py migrate
```

3. **Démarrer le serveur :**
```bash
python manage.py runserver
```

## Structure

- **Backend Django (Admin)** : Interface web complète à `/admin/` et `/`
- **API REST (Prestataire)** : Endpoints API à `/api/`

## Endpoints Principaux

### Authentification
- `POST /api/auth/login/` - Connexion (obtenir token JWT)
- `POST /api/auth/refresh/` - Rafraîchir le token
- `POST /api/auth/verify/` - Vérifier le token

### Endpoints API
- `/api/eleves/` - Gestion des élèves
- `/api/menus/` - Gestion des menus (CRUD)
- `/api/repas/` - Gestion des repas
- `/api/factures/` - Gestion des factures
- `/api/inscriptions/` - Consultation des inscriptions
- `/api/profil/` - Profil et dashboard

## Documentation Complète

Consultez `GUIDE_API_FLUTTER.md` pour :
- La documentation complète de tous les endpoints
- Des exemples d'utilisation en Flutter/Dart
- La gestion de l'authentification JWT
- Les codes de réponse et gestion d'erreurs

## Configuration CORS

En développement, vous pouvez activer CORS pour tous les origines :
```python
CORS_ALLOW_ALL_ORIGINS = True  # Uniquement en développement !
```

En production, configurez les origines autorisées dans `settings.py`.

## Test de l'API

Vous pouvez tester l'API avec :
- **Postman** : Importez les endpoints
- **curl** : Commandes HTTP
- **Flutter** : Application mobile

### Exemple de connexion avec curl :
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "prestataire", "password": "motdepasse"}'
```

## Sécurité

- Authentification JWT obligatoire
- Tokens expirent après 24h
- Refresh tokens expirent après 7 jours
- Utilisez HTTPS en production

## Support

Pour toute question sur l'API, consultez `GUIDE_API_FLUTTER.md`.
