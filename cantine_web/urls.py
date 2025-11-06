from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_auth
from . import views_extended

app_name = "cantine_web"

urlpatterns = [
    # Authentification
    path("login/", views_auth.login_view, name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="cantine_web:login"),
        name="logout",
    ),
    # Profil et mot de passe
    path("profile/", views_auth.profile_view, name="profile"),
    path("password/change/", views_auth.password_change_view, name="password_change"),
    path(
        "password/reset/",
        views_auth.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        views_auth.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views_auth.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        views_auth.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Élèves (Admin uniquement)
    path("eleves/", views.EleveListView.as_view(), name="eleve_list"),
    path("eleves/ajouter/", views.EleveCreateView.as_view(), name="eleve_create"),
    path("eleves/<int:pk>/", views.EleveDetailView.as_view(), name="eleve_detail"),
    path(
        "eleves/<int:pk>/modifier/",
        views.EleveUpdateView.as_view(),
        name="eleve_update",
    ),
    path(
        "eleves/<int:pk>/supprimer/",
        views.EleveDeleteView.as_view(),
        name="eleve_delete",
    ),
    path("eleves/import/", views_extended.eleve_import, name="eleve_import"),
    path("eleves/export/", views_extended.eleve_export, name="eleve_export"),
    # Inscriptions mensuelles (Admin uniquement)
    path(
        "inscriptions/",
        views.InscriptionMensuelleListView.as_view(),
        name="inscription_mensuelle_list",
    ),
    path(
        "inscriptions/ajouter/",
        views.InscriptionMensuelleCreateView.as_view(),
        name="inscription_mensuelle_create",
    ),
    path(
        "inscriptions/<int:pk>/modifier/",
        views.InscriptionMensuelleUpdateView.as_view(),
        name="inscription_mensuelle_update",
    ),
    path(
        "inscriptions/<int:pk>/supprimer/",
        views.InscriptionMensuelleDeleteView.as_view(),
        name="inscription_mensuelle_delete",
    ),
    # Menus (Admin et Prestataire)
    path("menus/", views.MenuListView.as_view(), name="menu_list"),
    path("menus/ajouter/", views.MenuCreateView.as_view(), name="menu_create"),
    path(
        "menus/<int:pk>/modifier/", views.MenuUpdateView.as_view(), name="menu_update"
    ),
    path(
        "menus/<int:pk>/supprimer/", views.MenuDeleteView.as_view(), name="menu_delete"
    ),
    path("menus/calendrier/", views_extended.menu_calendar_view, name="menu_calendar"),
    # Repas (Admin et Prestataire)
    path("repas/", views.RepasListView.as_view(), name="repas_list"),
    path("repas/marquer/", views.repas_marquer_multiples, name="repas_marquer"),
    path("repas/detail-plats/", views.detail_plats_servis, name="detail_plats_servis"),
    # Factures (Prestataire principalement, Admin peut consulter)
    path("factures/", views.FactureListView.as_view(), name="facture_list"),
    path("factures/ajouter/", views.FactureCreateView.as_view(), name="facture_create"),
    path(
        "factures/<int:pk>/", views.FactureDetailView.as_view(), name="facture_detail"
    ),
    path(
        "factures/<int:pk>/modifier/",
        views.FactureUpdateView.as_view(),
        name="facture_update",
    ),
    path(
        "factures/<int:pk>/supprimer/",
        views.FactureDeleteView.as_view(),
        name="facture_delete",
    ),
    # Statistiques
    path("statistiques/", views.statistiques, name="statistiques"),
    # Rapports
    path("rapports/", views.generer_rapport, name="generer_rapport"),
    # Décomptes (Prestataire)
    path("decompte-journalier/", views.decompte_journalier, name="decompte_journalier"),
    path("decompte-mensuel/", views.decompte_mensuel, name="decompte_mensuel"),
    # Élèves inscrits (Prestataire)
    path("eleves-inscrits/", views.eleves_inscrits, name="eleves_inscrits"),
    # Gestion des prestataires (Admin uniquement)
    path("prestataires/", views.PrestataireListView.as_view(), name="prestataire_list"),
    path(
        "prestataires/ajouter/",
        views.PrestataireCreateView.as_view(),
        name="prestataire_create",
    ),
    path(
        "prestataires/<int:pk>/modifier/",
        views.PrestataireUpdateView.as_view(),
        name="prestataire_update",
    ),
    path(
        "prestataires/<int:pk>/supprimer/",
        views.PrestataireDeleteView.as_view(),
        name="prestataire_delete",
    ),
    # Classes (Admin uniquement)
    path("classes/", views_extended.ClasseListView.as_view(), name="classe_list"),
    path(
        "classes/ajouter/",
        views_extended.ClasseCreateView.as_view(),
        name="classe_create",
    ),
    path(
        "classes/<int:pk>/modifier/",
        views_extended.ClasseUpdateView.as_view(),
        name="classe_update",
    ),
    path(
        "classes/<int:pk>/supprimer/",
        views_extended.ClasseDeleteView.as_view(),
        name="classe_delete",
    ),
    # Recherche globale
    path("recherche/", views_extended.search_global, name="search_global"),
    # Backup/Restore
    path("backup/", views_extended.backup_database, name="backup"),
    path("restore/", views_extended.restore_database, name="restore"),
]
