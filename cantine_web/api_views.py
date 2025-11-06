"""
Vues API REST pour Flutter (Prestataire)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, date, timedelta
from decimal import Decimal

from .models import Eleve, Menu, Repas, InscriptionMensuelle, Facture, ProfilPrestataire
from .serializers import (
    EleveSerializer,
    EleveListSerializer,
    MenuSerializer,
    RepasSerializer,
    InscriptionMensuelleSerializer,
    FactureSerializer,
    ProfilPrestataireSerializer,
    UserSerializer,
)


class EleveViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les élèves (lecture seule pour le prestataire)
    """

    queryset = Eleve.objects.filter(actif=True).select_related("classe")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return EleveListSerializer
        return EleveSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par classe si fourni
        classe_id = self.request.query_params.get("classe_id")
        if classe_id:
            queryset = queryset.filter(classe_id=classe_id)

        # Filtrer par recherche
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) | Q(prenom__icontains=search)
            )

        # Filtrer les élèves inscrits ce mois
        mois = self.request.query_params.get("mois_inscrit")
        annee = self.request.query_params.get("annee")
        if mois and annee:
            queryset = queryset.filter(
                inscriptions_mensuelles__annee=int(annee),
                inscriptions_mensuelles__mois=int(mois),
                inscriptions_mensuelles__inscrit=True,
            ).distinct()

        return queryset.order_by("classe", "nom", "prenom")

    @action(detail=False, methods=["get"])
    def inscrits_ce_mois(self, request):
        """Retourner les élèves inscrits ce mois"""
        today = timezone.now().date()
        eleves = (
            self.get_queryset()
            .filter(
                inscriptions_mensuelles__annee=today.year,
                inscriptions_mensuelles__mois=today.month,
                inscriptions_mensuelles__inscrit=True,
            )
            .distinct()
        )

        serializer = self.get_serializer(eleves, many=True)
        return Response(serializer.data)


class MenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les menus (CRUD complet pour prestataire)
    """

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par date
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Filtrer par recherche
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(plat_principal__icontains=search)
                | Q(accompagnement__icontains=search)
                | Q(dessert__icontains=search)
            )

        return queryset.order_by("-date")

    @action(detail=False, methods=["get"])
    def aujourdhui(self, request):
        """Retourner le menu du jour"""
        today = timezone.now().date()
        menu = Menu.objects.filter(date=today).first()

        if menu:
            serializer = self.get_serializer(menu)
            return Response(serializer.data)
        return Response(
            {"detail": "Aucun menu pour aujourd'hui"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["get"])
    def mois(self, request):
        """Retourner tous les menus d'un mois"""
        annee = request.query_params.get("annee", timezone.now().year)
        mois = request.query_params.get("mois", timezone.now().month)

        first_day = date(int(annee), int(mois), 1)
        if int(mois) == 12:
            last_day = date(int(annee) + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(int(annee), int(mois) + 1, 1) - timedelta(days=1)

        menus = Menu.objects.filter(date__gte=first_day, date__lte=last_day).order_by(
            "date"
        )

        serializer = self.get_serializer(menus, many=True)
        return Response(serializer.data)


class RepasViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les repas
    """

    queryset = Repas.objects.select_related("eleve", "menu", "created_by")
    serializer_class = RepasSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par date
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        date_specific = self.request.query_params.get("date")

        if date_specific:
            queryset = queryset.filter(date=date_specific)
        else:
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)

        # Filtrer par élève
        eleve_id = self.request.query_params.get("eleve_id")
        if eleve_id:
            queryset = queryset.filter(eleve_id=eleve_id)

        return queryset.order_by("-date", "eleve")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["post"])
    def marquer_multiples(self, request):
        """Marquer plusieurs élèves comme ayant mangé"""
        eleve_ids = request.data.get("eleves", [])
        date_repas = request.data.get("date", timezone.now().date().isoformat())

        if not eleve_ids:
            return Response(
                {"detail": "Aucun élève sélectionné"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_obj = datetime.strptime(date_repas, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format de date invalide. Utilisez YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        menu = Menu.objects.filter(date=date_obj).first()
        repas_crees = 0

        for eleve_id in eleve_ids:
            eleve = Eleve.objects.filter(id=eleve_id, actif=True).first()
            if eleve and not Repas.objects.filter(eleve=eleve, date=date_obj).exists():
                Repas.objects.create(
                    eleve=eleve, menu=menu, date=date_obj, created_by=request.user
                )
                repas_crees += 1

        return Response(
            {
                "detail": f"{repas_crees} repas enregistré(s) avec succès",
                "repas_crees": repas_crees,
            }
        )

    @action(detail=False, methods=["get"])
    def aujourdhui(self, request):
        """Retourner les repas d'aujourd'hui"""
        today = timezone.now().date()
        repas = Repas.objects.filter(date=today).select_related("eleve", "menu")

        serializer = self.get_serializer(repas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistiques(self, request):
        """Statistiques des repas"""
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        queryset = Repas.objects.all()

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        stats = {
            "total_repas": queryset.count(),
            "par_jour": queryset.values("date")
            .annotate(count=Count("id"))
            .order_by("date"),
            "par_eleve": queryset.values("eleve__nom", "eleve__prenom")
            .annotate(count=Count("id"))
            .order_by("-count")[:10],
        }

        return Response(stats)


class InscriptionMensuelleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les inscriptions mensuelles (lecture seule)
    """

    queryset = InscriptionMensuelle.objects.select_related("eleve")
    serializer_class = InscriptionMensuelleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par année et mois
        annee = self.request.query_params.get("annee")
        mois = self.request.query_params.get("mois")

        if annee:
            queryset = queryset.filter(annee=int(annee))
        if mois:
            queryset = queryset.filter(mois=int(mois))

        return queryset.order_by("-annee", "-mois", "eleve")


class FactureViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les factures
    """

    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par année et mois
        annee = self.request.query_params.get("annee")
        mois = self.request.query_params.get("mois")
        statut = self.request.query_params.get("statut")

        if annee:
            queryset = queryset.filter(annee=int(annee))
        if mois:
            queryset = queryset.filter(mois=int(mois))
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset.order_by("-annee", "-mois", "-date_emission")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

        # Calculer le montant total si nécessaire
        instance = serializer.instance
        if not instance.montant_total:
            instance.montant_total = (
                instance.nombre_repas_servis * instance.prix_unitaire_repas
            )
            instance.save()


class ProfilPrestataireViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour le profil du prestataire connecté
    """

    serializer_class = ProfilPrestataireSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, "profil"):
            return ProfilPrestataire.objects.filter(user=self.request.user)
        return ProfilPrestataire.objects.none()

    @action(detail=False, methods=["get"])
    def mon_profil(self, request):
        """Retourner le profil de l'utilisateur connecté"""
        if hasattr(request.user, "profil"):
            serializer = self.get_serializer(request.user.profil)
            return Response(serializer.data)
        return Response(
            {"detail": "Aucun profil trouvé"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Statistiques du dashboard pour le prestataire"""
        today = timezone.now().date()
        premier_jour_mois = today.replace(day=1)

        stats = {
            "total_eleves_actifs": Eleve.objects.filter(actif=True).count(),
            "repas_aujourd_hui": Repas.objects.filter(date=today).count(),
            "repas_ce_mois": Repas.objects.filter(
                date__gte=premier_jour_mois, date__lte=today
            ).count(),
            "eleves_inscrits_mois": InscriptionMensuelle.objects.filter(
                annee=today.year, mois=today.month, inscrit=True
            ).count(),
            "factures_en_attente": Facture.objects.filter(
                statut="ENVOYEE", created_by=request.user
            ).count(),
            "menu_du_jour": None,
        }

        menu_du_jour = Menu.objects.filter(date=today).first()
        if menu_du_jour:
            stats["menu_du_jour"] = MenuSerializer(
                menu_du_jour, context={"request": request}
            ).data

        return Response(stats)
