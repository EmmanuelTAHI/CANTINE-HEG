"""
URLs pour l'API REST
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .api_views import (
    EleveViewSet,
    MenuViewSet,
    RepasViewSet,
    InscriptionMensuelleViewSet,
    FactureViewSet,
    ProfilPrestataireViewSet,
)

router = DefaultRouter()
router.register(r"eleves", EleveViewSet, basename="eleve")
router.register(r"menus", MenuViewSet, basename="menu")
router.register(r"repas", RepasViewSet, basename="repas")
router.register(r"inscriptions", InscriptionMensuelleViewSet, basename="inscription")
router.register(r"factures", FactureViewSet, basename="facture")
router.register(r"profil", ProfilPrestataireViewSet, basename="profil")

app_name = "api"

urlpatterns = [
    # Authentification JWT
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Routes API
    path("", include(router.urls)),
]
