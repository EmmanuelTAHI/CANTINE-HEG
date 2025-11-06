"""
Serializers pour l'API REST
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Eleve,
    Classe,
    Menu,
    Repas,
    InscriptionMensuelle,
    Facture,
    ProfilPrestataire,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur"""

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]
        read_only_fields = ["id", "username"]

    def get_role(self, obj):
        if hasattr(obj, "profil"):
            return obj.profil.get_role_display()
        return None


class ClasseSerializer(serializers.ModelSerializer):
    """Serializer pour les classes"""

    class Meta:
        model = Classe
        fields = ["id", "nom", "niveau"]
        read_only_fields = ["id"]


class EleveSerializer(serializers.ModelSerializer):
    """Serializer pour les élèves"""

    classe = ClasseSerializer(read_only=True)
    classe_id = serializers.PrimaryKeyRelatedField(
        queryset=Classe.objects.all(),
        source="classe",
        write_only=True,
        required=False,
        allow_null=True,
    )
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Eleve
        fields = [
            "id",
            "prenom",
            "nom",
            "classe",
            "classe_id",
            "date_inscription",
            "actif",
            "telephone_parent",
            "email_parent",
            "photo",
            "photo_url",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "date_inscription", "created_at", "updated_at"]

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class EleveListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des élèves"""

    classe = ClasseSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Eleve
        fields = ["id", "prenom", "nom", "classe", "actif", "photo_url"]

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class MenuSerializer(serializers.ModelSerializer):
    """Serializer pour les menus"""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id",
            "date",
            "jour_semaine",
            "plat_principal",
            "accompagnement",
            "dessert",
            "image",
            "image_url",
            "disponible",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class RepasSerializer(serializers.ModelSerializer):
    """Serializer pour les repas"""

    eleve = EleveListSerializer(read_only=True)
    eleve_id = serializers.PrimaryKeyRelatedField(
        queryset=Eleve.objects.all(), source="eleve", write_only=True
    )
    menu = MenuSerializer(read_only=True)
    menu_id = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all(),
        source="menu",
        write_only=True,
        required=False,
        allow_null=True,
    )
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Repas
        fields = [
            "id",
            "eleve",
            "eleve_id",
            "menu",
            "menu_id",
            "date",
            "note",
            "created_at",
            "created_by",
            "created_by_username",
        ]
        read_only_fields = ["id", "created_at", "created_by"]


class InscriptionMensuelleSerializer(serializers.ModelSerializer):
    """Serializer pour les inscriptions mensuelles"""

    eleve = EleveListSerializer(read_only=True)
    eleve_id = serializers.PrimaryKeyRelatedField(
        queryset=Eleve.objects.all(), source="eleve", write_only=True
    )

    class Meta:
        model = InscriptionMensuelle
        fields = [
            "id",
            "eleve",
            "eleve_id",
            "annee",
            "mois",
            "inscrit",
            "notes",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by"]


class FactureSerializer(serializers.ModelSerializer):
    """Serializer pour les factures"""

    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Facture
        fields = [
            "id",
            "numero",
            "annee",
            "mois",
            "nombre_jours_travail",
            "nombre_repas_servis",
            "prix_unitaire_repas",
            "montant_total",
            "statut",
            "date_emission",
            "date_paiement",
            "notes",
            "created_at",
            "created_by",
            "created_by_username",
        ]
        read_only_fields = ["id", "montant_total", "created_at", "created_by"]


class ProfilPrestataireSerializer(serializers.ModelSerializer):
    """Serializer pour le profil prestataire"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = ProfilPrestataire
        fields = [
            "id",
            "user",
            "role",
            "telephone",
            "entreprise",
            "actif",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
