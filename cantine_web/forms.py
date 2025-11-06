from django import forms
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


class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = [
            "prenom",
            "nom",
            "classe",
            "telephone_parent",
            "email_parent",
            "photo",
            "actif",
            "notes",
        ]
        widgets = {
            "prenom": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "nom": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "classe": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "telephone_parent": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "email_parent": forms.EmailInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "photo": forms.FileInput(
                attrs={
                    "class": "file-input file-input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "actif": forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "rows": 4,
                }
            ),
        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ["nom", "niveau"]
        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "niveau": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                },
                choices=[
                    ("", "Sélectionner un niveau"),
                    ("Collège", "Collège"),
                    ("Lycée", "Lycée"),
                ],
            ),
        }


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = [
            "date",
            "jour_semaine",
            "plat_principal",
            "accompagnement",
            "dessert",
            "image",
            "disponible",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                }
            ),
            "jour_semaine": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "plat_principal": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "accompagnement": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "dessert": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "file-input file-input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "disponible": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "rows": 3,
                }
            ),
        }


class RepasForm(forms.ModelForm):
    class Meta:
        model = Repas
        fields = ["eleve", "menu", "date", "note"]
        widgets = {
            "eleve": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "menu": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "rows": 3,
                }
            ),
        }


class InscriptionMensuelleForm(forms.ModelForm):
    class Meta:
        model = InscriptionMensuelle
        fields = ["eleve", "annee", "mois", "inscrit", "notes"]
        widgets = {
            "eleve": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "annee": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "mois": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "min": 1,
                    "max": 12,
                }
            ),
            "inscrit": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "rows": 3,
                }
            ),
        }


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            "numero",
            "annee",
            "mois",
            "nombre_jours_travail",
            "nombre_repas_servis",
            "prix_unitaire_repas",
            "statut",
            "date_emission",
            "date_paiement",
            "notes",
        ]
        widgets = {
            "numero": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "annee": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "mois": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "min": 1,
                    "max": 12,
                }
            ),
            "nombre_jours_travail": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "nombre_repas_servis": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "prix_unitaire_repas": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "step": "0.01",
                }
            ),
            "statut": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "date_emission": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                }
            ),
            "date_paiement": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                    "rows": 4,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        nombre_repas = cleaned_data.get("nombre_repas_servis")
        prix_unitaire = cleaned_data.get("prix_unitaire_repas")

        if nombre_repas and prix_unitaire:
            cleaned_data["montant_total"] = nombre_repas * prix_unitaire

        return cleaned_data


class ProfilPrestataireForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150, required=True, help_text="Nom d'utilisateur"
    )
    email = forms.EmailField(required=True, help_text="Email")
    first_name = forms.CharField(max_length=30, required=False, help_text="Prénom")
    last_name = forms.CharField(max_length=150, required=False, help_text="Nom")

    class Meta:
        model = ProfilPrestataire
        fields = ["role", "telephone", "entreprise", "actif"]
        widgets = {
            "role": forms.Select(
                attrs={
                    "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "entreprise": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "actif": forms.CheckboxInput(attrs={"class": "checkbox checkbox-primary"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profil = super().save(commit=False)
        if profil.pk:
            profil.user.username = self.cleaned_data["username"]
            profil.user.email = self.cleaned_data["email"]
            profil.user.first_name = self.cleaned_data["first_name"]
            profil.user.last_name = self.cleaned_data["last_name"]
            if commit:
                profil.user.save()
                profil.save()
        else:
            if commit:
                user = User.objects.create_user(
                    username=self.cleaned_data["username"],
                    email=self.cleaned_data["email"],
                    first_name=self.cleaned_data["first_name"],
                    last_name=self.cleaned_data["last_name"],
                )
                profil.user = user
                profil.save()
        return profil


class ReportFilterForm(forms.Form):
    TYPE_RAPPORT_CHOICES = [
        ("JOURNALIER", "Journalier"),
        ("HEBDOMADAIRE", "Hebdomadaire"),
        ("MENSUEL", "Mensuel"),
    ]

    FORMAT_EXPORT_CHOICES = [
        ("PDF", "PDF"),
        ("EXCEL", "Excel"),
    ]

    type_rapport = forms.ChoiceField(
        choices=TYPE_RAPPORT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
            }
        ),
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
            }
        ),
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
            }
        ),
    )
    annee = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
            }
        ),
    )
    mois = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                "min": 1,
                "max": 12,
            }
        ),
    )
    format_export = forms.ChoiceField(
        choices=FORMAT_EXPORT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "select select-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
            }
        ),
    )


class UserProfileForm(forms.ModelForm):
    """Formulaire pour modifier les informations du profil utilisateur"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none"
                }
            ),
        }


class EleveImportForm(forms.Form):
    """Formulaire pour l'import d'élèves depuis Excel"""

    fichier = forms.FileField(
        label="Fichier Excel",
        help_text="Format accepté: .xlsx, .xls",
        widget=forms.FileInput(
            attrs={
                "class": "file-input file-input-bordered w-full bg-white border-gray-300 focus:border-primary focus:outline-none",
                "accept": ".xlsx,.xls",
            }
        ),
    )
