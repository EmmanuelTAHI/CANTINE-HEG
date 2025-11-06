# Guide d'Intégration API REST pour Flutter

## Vue d'ensemble

L'API REST Django est disponible pour l'application Flutter du prestataire. L'administration continue d'utiliser l'interface web Django.

## Base URL

```
http://votre-domaine.com/api/
```

Pour le développement local :
```
http://localhost:8000/api/
```

## Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

### 1. Connexion

**Endpoint:** `POST /api/auth/login/`

**Body:**
```json
{
  "username": "prestataire_username",
  "password": "mot_de_passe"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Rafraîchir le token

**Endpoint:** `POST /api/auth/refresh/`

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "nouveau_token..."
}
```

### 3. Utilisation du token

Ajoutez le token dans les headers de toutes les requêtes :
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Endpoints API

### Élèves

- **GET** `/api/eleves/` - Liste des élèves actifs
- **GET** `/api/eleves/{id}/` - Détails d'un élève
- **GET** `/api/eleves/inscrits_ce_mois/` - Élèves inscrits ce mois

**Paramètres de requête:**
- `search` - Recherche par nom/prénom
- `classe_id` - Filtrer par classe
- `mois_inscrit` - Mois d'inscription
- `annee` - Année d'inscription

### Menus

- **GET** `/api/menus/` - Liste des menus
- **POST** `/api/menus/` - Créer un menu
- **GET** `/api/menus/{id}/` - Détails d'un menu
- **PUT/PATCH** `/api/menus/{id}/` - Modifier un menu
- **DELETE** `/api/menus/{id}/` - Supprimer un menu
- **GET** `/api/menus/aujourdhui/` - Menu du jour
- **GET** `/api/menus/mois/?annee=2024&mois=1` - Menus d'un mois

**Paramètres de requête:**
- `date_from` - Date de début
- `date_to` - Date de fin
- `search` - Recherche dans les plats

### Repas

- **GET** `/api/repas/` - Liste des repas
- **POST** `/api/repas/` - Créer un repas
- **GET** `/api/repas/{id}/` - Détails d'un repas
- **PUT/PATCH** `/api/repas/{id}/` - Modifier un repas
- **DELETE** `/api/repas/{id}/` - Supprimer un repas
- **POST** `/api/repas/marquer_multiples/` - Marquer plusieurs élèves comme ayant mangé
- **GET** `/api/repas/aujourdhui/` - Repas d'aujourd'hui
- **GET** `/api/repas/statistiques/` - Statistiques des repas

**Marquer plusieurs repas:**
```json
POST /api/repas/marquer_multiples/
{
  "eleves": [1, 2, 3, 4],
  "date": "2024-01-15"
}
```

### Inscriptions mensuelles

- **GET** `/api/inscriptions/` - Liste des inscriptions
- **GET** `/api/inscriptions/{id}/` - Détails d'une inscription

**Paramètres de requête:**
- `annee` - Année
- `mois` - Mois (1-12)

### Factures

- **GET** `/api/factures/` - Liste des factures
- **POST** `/api/factures/` - Créer une facture
- **GET** `/api/factures/{id}/` - Détails d'une facture
- **PUT/PATCH** `/api/factures/{id}/` - Modifier une facture
- **DELETE** `/api/factures/{id}/` - Supprimer une facture

**Paramètres de requête:**
- `annee` - Année
- `mois` - Mois
- `statut` - Statut (BROUILLON, ENVOYEE, PAYEE, ANNULEE)

### Profil

- **GET** `/api/profil/mon_profil/` - Profil du prestataire connecté
- **GET** `/api/profil/dashboard/` - Statistiques du dashboard

## Exemple d'utilisation dans Flutter

### Configuration HTTP

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://votre-domaine.com/api/';
  String? _accessToken;

  // Connexion
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('${baseUrl}auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _accessToken = data['access'];
      return data;
    } else {
      throw Exception('Erreur de connexion');
    }
  }

  // Headers avec authentification
  Map<String, String> getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_accessToken',
    };
  }

  // Récupérer les élèves
  Future<List<dynamic>> getEleves() async {
    final response = await http.get(
      Uri.parse('${baseUrl}eleves/'),
      headers: getHeaders(),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['results'] ?? data;
    } else {
      throw Exception('Erreur lors de la récupération des élèves');
    }
  }

  // Récupérer le menu du jour
  Future<Map<String, dynamic>> getMenuAujourdhui() async {
    final response = await http.get(
      Uri.parse('${baseUrl}menus/aujourdhui/'),
      headers: getHeaders(),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Aucun menu pour aujourd\'hui');
    }
  }

  // Marquer plusieurs repas
  Future<Map<String, dynamic>> marquerRepas(
    List<int> eleveIds,
    String date,
  ) async {
    final response = await http.post(
      Uri.parse('${baseUrl}repas/marquer_multiples/'),
      headers: getHeaders(),
      body: jsonEncode({
        'eleves': eleveIds,
        'date': date,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur lors de l\'enregistrement des repas');
    }
  }

  // Créer un menu
  Future<Map<String, dynamic>> creerMenu(Map<String, dynamic> menuData) async {
    final response = await http.post(
      Uri.parse('${baseUrl}menus/'),
      headers: getHeaders(),
      body: jsonEncode(menuData),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur lors de la création du menu');
    }
  }

  // Dashboard
  Future<Map<String, dynamic>> getDashboard() async {
    final response = await http.get(
      Uri.parse('${baseUrl}profil/dashboard/'),
      headers: getHeaders(),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur lors de la récupération du dashboard');
    }
  }
}
```

### Utilisation dans un widget Flutter

```dart
import 'package:flutter/material.dart';

class ElevesList extends StatefulWidget {
  @override
  _ElevesListState createState() => _ElevesListState();
}

class _ElevesListState extends State<ElevesList> {
  final ApiService _apiService = ApiService();
  List<dynamic> _eleves = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadEleves();
  }

  Future<void> _loadEleves() async {
    try {
      final eleves = await _apiService.getEleves();
      setState(() {
        _eleves = eleves;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _loading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Center(child: CircularProgressIndicator());
    }

    return ListView.builder(
      itemCount: _eleves.length,
      itemBuilder: (context, index) {
        final eleve = _eleves[index];
        return ListTile(
          leading: eleve['photo_url'] != null
              ? CircleAvatar(
                  backgroundImage: NetworkImage(eleve['photo_url']),
                )
              : CircleAvatar(
                  child: Text(
                    '${eleve['prenom'][0]}${eleve['nom'][0]}',
                  ),
                ),
          title: Text('${eleve['prenom']} ${eleve['nom']}'),
          subtitle: Text(eleve['classe']?['nom'] ?? 'Sans classe'),
        );
      },
    );
  }
}
```

## Gestion des erreurs

L'API retourne des codes HTTP standard :
- `200` - Succès
- `201` - Créé
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Interdit
- `404` - Non trouvé
- `500` - Erreur serveur

Les erreurs sont retournées au format :
```json
{
  "detail": "Message d'erreur"
}
```

## Pagination

Les listes sont paginées (20 éléments par page). La réponse inclut :
```json
{
  "count": 100,
  "next": "http://api/eleves/?page=2",
  "previous": null,
  "results": [...]
}
```

## Configuration CORS

En production, configurez CORS dans `settings.py` :
```python
CORS_ALLOWED_ORIGINS = [
    "https://votre-app-flutter.com",
    # Ajoutez vos domaines
]
```

## Sécurité

- Le token JWT expire après 24h (configurable)
- Utilisez HTTPS en production
- Stockez le token de manière sécurisée (flutter_secure_storage)
- Rafraîchissez le token avant expiration

## Support

Pour toute question, contactez l'administrateur du système.
