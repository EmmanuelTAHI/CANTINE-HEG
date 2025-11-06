from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date


class Classe(models.Model):
    """Classe scolaire (6ème, 5ème, Seconde, etc.)"""

    nom = models.CharField(max_length=100, unique=True)
    niveau = models.CharField(max_length=50, help_text="Ex: Collège, Lycée")

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class ProfilPrestataire(models.Model):
    """Profil pour les prestataires de cantine"""

    ROLE_CHOICES = [
        ("ADMIN", "Administrateur"),
        ("PRESTATAIRE", "Prestataire"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="PRESTATAIRE")
    telephone = models.CharField(max_length=20, blank=True)
    entreprise = models.CharField(
        max_length=200, blank=True, help_text="Nom de l'entreprise prestataire"
    )
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provider Profile"
        verbose_name_plural = "Provider Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == "ADMIN"

    @property
    def is_prestataire(self):
        return self.role == "PRESTATAIRE"


class Eleve(models.Model):
    """Élève inscrit à la cantine"""

    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    date_inscription = models.DateField(auto_now_add=True)
    actif = models.BooleanField(
        default=True, help_text="Élève actuellement inscrit à la cantine"
    )
    telephone_parent = models.CharField(max_length=20, blank=True)
    email_parent = models.EmailField(blank=True)
    photo = models.ImageField(
        upload_to="eleves/",
        blank=True,
        null=True,
        help_text="Photo de profil de l'élève",
    )
    notes = models.TextField(blank=True, help_text="Notes supplémentaires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["classe", "nom", "prenom"]
        indexes = [
            models.Index(fields=["nom", "prenom"]),
            models.Index(fields=["actif"]),
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.classe or 'Sans classe'})"

    @property
    def nombre_repas_ce_mois(self):
        """Nombre de repas consommés ce mois"""
        today = timezone.now().date()
        first_day = today.replace(day=1)
        return self.repas_set.filter(date__gte=first_day, date__lte=today).count()

    def est_inscrit_mois(self, annee, mois):
        """Vérifie si l'élève est inscrit pour un mois donné"""
        return self.inscriptions_mensuelles.filter(annee=annee, mois=mois).exists()


class Menu(models.Model):
    """Menu de la cantine pour une date donnée"""

    JOURS_SEMAINE = [
        ("LUNDI", "Lundi"),
        ("MARDI", "Mardi"),
        ("MERCREDI", "Mercredi"),
        ("JEUDI", "Jeudi"),
        ("VENDREDI", "Vendredi"),
        ("SAMEDI", "Samedi"),
    ]

    date = models.DateField(unique=True)
    jour_semaine = models.CharField(max_length=10, choices=JOURS_SEMAINE, blank=True)
    plat_principal = models.CharField(max_length=200)
    accompagnement = models.CharField(max_length=200, blank=True)
    dessert = models.CharField(max_length=200, blank=True)
    image = models.ImageField(
        upload_to="menus/", blank=True, null=True, help_text="Image du menu"
    )
    disponible = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["disponible"]),
        ]

    def __str__(self):
        return f"Menu du {self.date.strftime('%d/%m/%Y')} - {self.plat_principal}"

    def save(self, *args, **kwargs):
        if not self.jour_semaine:
            self.jour_semaine = self.date.strftime("%A").upper()
        super().save(*args, **kwargs)


class InscriptionMensuelle(models.Model):
    """Inscription mensuelle d'un élève à la cantine"""

    eleve = models.ForeignKey(
        Eleve, on_delete=models.CASCADE, related_name="inscriptions_mensuelles"
    )
    annee = models.IntegerField()
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    inscrit = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="inscriptions_crees"
    )

    class Meta:
        verbose_name = "Monthly Registration"
        verbose_name_plural = "Monthly Registrations"
        ordering = ["-annee", "-mois", "eleve"]
        unique_together = [["eleve", "annee", "mois"]]
        indexes = [
            models.Index(fields=["annee", "mois"]),
            models.Index(fields=["eleve", "annee", "mois"]),
        ]

    def __str__(self):
        return f"{self.eleve} - {self.mois}/{self.annee}"


class Repas(models.Model):
    """Repas consommé par un élève"""

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="repas_crees"
    )

    class Meta:
        verbose_name = "Meal"
        verbose_name_plural = "Meals"
        ordering = ["-date", "eleve"]
        unique_together = [["eleve", "date"]]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["eleve", "date"]),
        ]

    def __str__(self):
        return f"{self.eleve} - {self.date.strftime('%d/%m/%Y')}"


class Facture(models.Model):
    """Facture générée par la prestataire pour l'école"""

    STATUT_CHOICES = [
        ("BROUILLON", "Brouillon"),
        ("ENVOYEE", "Envoyée"),
        ("PAYEE", "Payée"),
        ("ANNULEE", "Annulée"),
    ]

    numero = models.CharField(max_length=50, unique=True, help_text="Numéro de facture")
    annee = models.IntegerField()
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    nombre_jours_travail = models.IntegerField(
        default=0, help_text="Nombre de jours travaillés dans le mois"
    )
    nombre_repas_servis = models.IntegerField(default=0)
    prix_unitaire_repas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Prix unitaire d'un repas en FCFA",
    )
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="BROUILLON"
    )
    date_emission = models.DateField(default=timezone.now)
    date_paiement = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="factures_crees"
    )

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-annee", "-mois", "-date_emission"]
        indexes = [
            models.Index(fields=["annee", "mois"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return f"Facture {self.numero} - {self.mois}/{self.annee} - {self.montant_total} FCFA"

    def save(self, *args, **kwargs):
        # Calculer le montant total si nécessaire
        if not self.montant_total or self.pk is None:
            self.montant_total = self.nombre_repas_servis * self.prix_unitaire_repas
        super().save(*args, **kwargs)


class ActionLog(models.Model):
    """Log des actions effectuées dans l'application"""

    ACTION_TYPES = [
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("DELETE", "Suppression"),
        ("VIEW", "Consultation"),
        ("EXPORT", "Export"),
        ("IMPORT", "Import"),
        ("LOGIN", "Connexion"),
        ("LOGOUT", "Déconnexion"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="action_logs"
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, help_text="Nom du modèle concerné")
    object_id = models.IntegerField(
        null=True, blank=True, help_text="ID de l'objet concerné"
    )
    description = models.TextField(help_text="Description de l'action")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Action Log"
        verbose_name_plural = "Action Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["action_type", "created_at"]),
            models.Index(fields=["model_name"]),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.model_name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
