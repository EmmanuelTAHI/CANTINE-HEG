from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import (
    Classe,
    Eleve,
    Menu,
    Repas,
    InscriptionMensuelle,
    Facture,
    ProfilPrestataire,
    ActionLog,
)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ["nom", "niveau"]
    search_fields = ["nom", "niveau"]
    list_filter = ["niveau"]


# Inline pour afficher le profil dans la page User
class ProfilPrestataireInline(admin.StackedInline):
    model = ProfilPrestataire
    can_delete = False
    verbose_name_plural = "Canteen Profile"
    fields = ("role", "entreprise", "telephone", "actif", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fk_name = "user"


# Personnaliser l'admin User pour inclure le profil
class UserAdmin(BaseUserAdmin):
    inlines = (ProfilPrestataireInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_role",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "profil__role",
        "profil__actif",
    )

    def get_role(self, obj):
        if hasattr(obj, "profil"):
            role_display = obj.profil.get_role_display()
            if not obj.profil.actif:
                return f"{role_display} (Inactive)"
            return role_display
        return "No profile"

    get_role.short_description = "Role"
    get_role.admin_order_field = "profil__role"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Créer automatiquement un profil s'il n'existe pas
        if not hasattr(obj, "profil"):
            ProfilPrestataire.objects.create(
                user=obj, role="PRESTATAIRE", actif=True  # Rôle par défaut
            )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ProfilPrestataire):
                instance.save()
        formset.save_m2m()


# Désenregistrer l'admin User par défaut et enregistrer le nouveau
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ProfilPrestataire)
class ProfilPrestataireAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "entreprise", "actif", "created_at"]
    list_filter = ["role", "actif", "created_at"]
    search_fields = ["user__username", "user__email", "entreprise"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Role", {"fields": ("role", "actif")}),
        ("Information", {"fields": ("entreprise", "telephone")}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = [
        "photo_preview_list",
        "nom",
        "prenom",
        "classe",
        "actif",
        "date_inscription",
    ]
    list_filter = ["actif", "classe", "date_inscription"]
    search_fields = ["nom", "prenom", "telephone_parent", "email_parent"]
    readonly_fields = ["date_inscription", "created_at", "updated_at", "photo_preview"]
    fieldsets = (
        ("Personal Information", {"fields": ("prenom", "nom", "classe")}),
        ("Photo", {"fields": ("photo_preview", "photo"), "classes": ("wide",)}),
        ("Contact Information", {"fields": ("telephone_parent", "email_parent")}),
        ("Canteen", {"fields": ("actif", "date_inscription")}),
        ("Notes", {"fields": ("notes",)}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def photo_preview(self, obj):
        """Afficher la photo actuelle dans le formulaire d'édition"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 50%;" />',
                obj.photo.url,
            )
        return "Aucune photo"

    photo_preview.short_description = "Photo actuelle"

    def photo_preview_list(self, obj):
        """Afficher une miniature de la photo dans la liste"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.photo.url,
            )
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background: #e5e7eb; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #6b7280;">{}{}</div>',
            obj.prenom[0] if obj.prenom else "",
            obj.nom[0] if obj.nom else "",
        )

    photo_preview_list.short_description = "Photo"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["date", "plat_principal", "disponible"]
    list_filter = ["disponible", "date"]
    search_fields = ["plat_principal", "accompagnement", "dessert"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]


@admin.register(InscriptionMensuelle)
class InscriptionMensuelleAdmin(admin.ModelAdmin):
    list_display = ["eleve", "annee", "mois", "inscrit", "created_by", "created_at"]
    list_filter = ["inscrit", "annee", "mois", "created_by"]
    search_fields = ["eleve__nom", "eleve__prenom"]
    readonly_fields = ["created_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Repas)
class RepasAdmin(admin.ModelAdmin):
    list_display = ["eleve", "date", "menu", "created_by", "created_at"]
    list_filter = ["date", "eleve__classe"]
    search_fields = ["eleve__nom", "eleve__prenom"]
    date_hierarchy = "date"
    readonly_fields = ["created_at"]
    autocomplete_fields = ["eleve", "menu"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = [
        "numero",
        "annee",
        "mois",
        "nombre_repas_servis",
        "montant_total",
        "statut",
        "created_by",
    ]
    list_filter = ["statut", "annee", "mois", "created_by"]
    search_fields = ["numero", "notes"]
    readonly_fields = ["created_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            # Générer un numéro de facture si non fourni
            if not obj.numero:
                last_facture = Facture.objects.order_by("-id").first()
                if last_facture:
                    last_num = (
                        int(last_facture.numero.split("-")[-1])
                        if "-" in last_facture.numero
                        else 0
                    )
                else:
                    last_num = 0
                obj.numero = f"FAC-{obj.annee}-{obj.mois:02d}-{last_num + 1:04d}"
        super().save_model(request, obj, form, change)


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action_type", "model_name", "description", "created_at"]
    list_filter = ["action_type", "model_name", "created_at"]
    search_fields = ["user__username", "description", "model_name"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]


# Admin customization
admin.site.site_header = "HEG Canteen Management"
admin.site.site_title = "HEG Canteen"
admin.site.index_title = "Administration"
