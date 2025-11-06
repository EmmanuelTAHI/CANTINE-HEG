"""
Vues supplémentaires pour les nouvelles fonctionnalités
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, date, timedelta
from calendar import monthrange
import os
import json
import shutil
from pathlib import Path

from .models import (
    Eleve,
    Classe,
    Menu,
    Repas,
    InscriptionMensuelle,
    Facture,
    ProfilPrestataire,
    ActionLog,
)
from .forms import ClasseForm, EleveImportForm
from .mixins import AdminRequiredMixin
from .decorators import admin_required, admin_or_prestataire_required
from .utils import (
    log_action,
    export_to_excel,
    import_from_excel,
    validate_file_upload,
    get_cached_stats,
)
from .reports import generate_pdf_report


# ============ GESTION DES CLASSES ============


class ClasseListView(AdminRequiredMixin, ListView):
    model = Classe
    template_name = "cantine_web/classe_list.html"
    context_object_name = "classes"
    paginate_by = 50


class ClasseCreateView(AdminRequiredMixin, CreateView):
    model = Classe
    form_class = ClasseForm
    template_name = "cantine_web/classe_form.html"
    success_url = reverse_lazy("cantine_web:classe_list")

    def form_valid(self, form):
        messages.success(self.request, f"Classe {form.instance} créée avec succès.")
        log_action(
            self.request.user,
            "CREATE",
            "Classe",
            f"Création de la classe {form.instance}",
        )
        return super().form_valid(form)


class ClasseUpdateView(AdminRequiredMixin, UpdateView):
    model = Classe
    form_class = ClasseForm
    template_name = "cantine_web/classe_form.html"
    success_url = reverse_lazy("cantine_web:classe_list")

    def form_valid(self, form):
        messages.success(self.request, f"Classe {form.instance} modifiée avec succès.")
        log_action(
            self.request.user,
            "UPDATE",
            "Classe",
            f"Modification de la classe {form.instance}",
            self.object.pk,
        )
        return super().form_valid(form)


class ClasseDeleteView(AdminRequiredMixin, DeleteView):
    model = Classe
    template_name = "cantine_web/classe_confirm_delete.html"
    success_url = reverse_lazy("cantine_web:classe_list")

    def form_valid(self, form):
        messages.success(self.request, f"Classe {self.object} supprimée avec succès.")
        log_action(
            self.request.user,
            "DELETE",
            "Classe",
            f"Suppression de la classe {self.object}",
            self.object.pk,
        )
        return super().form_valid(form)


# ============ IMPORT/EXPORT ÉLÈVES ============


@login_required
@admin_required
def eleve_import(request):
    """Importer des élèves depuis Excel"""
    if request.method == "POST":
        form = EleveImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["fichier"]

            # Valider le fichier
            is_valid, error_msg = validate_file_upload(file)
            if not is_valid:
                messages.error(request, error_msg)
                return render(request, "cantine_web/eleve_import.html", {"form": form})

            def mapping_func(row):
                """Mapper les données Excel vers le modèle Eleve"""
                if len(row) < 2:
                    return None

                prenom = str(row[0]).strip() if row[0] else ""
                nom = str(row[1]).strip() if row[1] else ""

                if not prenom or not nom:
                    return None

                data = {
                    "prenom": prenom,
                    "nom": nom,
                    "actif": True,
                }

                # Classe (optionnel)
                if len(row) > 2 and row[2]:
                    try:
                        classe_nom = str(row[2]).strip()
                        classe = Classe.objects.filter(nom=classe_nom).first()
                        if classe:
                            data["classe"] = classe
                    except:
                        pass

                # Téléphone parent (optionnel)
                if len(row) > 3 and row[3]:
                    data["telephone_parent"] = str(row[3]).strip()

                # Email parent (optionnel)
                if len(row) > 4 and row[4]:
                    data["email_parent"] = str(row[4]).strip()

                return data

            imported, errors = import_from_excel(file, Eleve, mapping_func)

            if imported > 0:
                messages.success(
                    request, f"{imported} élève(s) importé(s) avec succès."
                )
                log_action(
                    request.user, "IMPORT", "Eleve", f"Import de {imported} élèves"
                )

            if errors:
                messages.warning(request, f"{len(errors)} erreur(s) lors de l'import.")
                for error in errors[:10]:  # Limiter à 10 erreurs
                    messages.warning(request, error)

            return redirect("cantine_web:eleve_list")
    else:
        form = EleveImportForm()

    return render(request, "cantine_web/eleve_import.html", {"form": form})


@login_required
@admin_required
def eleve_export(request):
    """Exporter les élèves vers Excel"""
    queryset = Eleve.objects.select_related("classe").all()

    headers = [
        "Prénom",
        "Nom",
        "Classe",
        "Téléphone Parent",
        "Email Parent",
        "Actif",
        "Date Inscription",
    ]

    def data_func(obj):
        return [
            obj.prenom,
            obj.nom,
            str(obj.classe) if obj.classe else "",
            obj.telephone_parent or "",
            obj.email_parent or "",
            "Oui" if obj.actif else "Non",
            obj.date_inscription.strftime("%d/%m/%Y") if obj.date_inscription else "",
        ]

    log_action(request.user, "EXPORT", "Eleve", f"Export de {queryset.count()} élèves")

    filename = f"eleves_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
    return export_to_excel(queryset, filename, headers, data_func)


# ============ RECHERCHE GLOBALE ============


@login_required
@admin_or_prestataire_required
def search_global(request):
    """Recherche globale dans l'application"""
    query = request.GET.get("q", "").strip()
    results = {}

    if query and len(query) >= 2:
        # Recherche dans les élèves
        if request.user.profil.is_admin:
            eleves = Eleve.objects.filter(
                Q(nom__icontains=query) | Q(prenom__icontains=query)
            )[:10]
            results["eleves"] = eleves

        # Recherche dans les menus
        menus = Menu.objects.filter(
            Q(plat_principal__icontains=query) | Q(accompagnement__icontains=query)
        )[:10]
        results["menus"] = menus

        # Recherche dans les factures
        if request.user.profil.is_admin or request.user.profil.is_prestataire:
            factures = Facture.objects.filter(
                Q(numero__icontains=query) | Q(notes__icontains=query)
            )[:10]
            results["factures"] = factures

        log_action(request.user, "VIEW", "Search", f"Recherche: {query}")

    context = {
        "query": query,
        "results": results,
    }

    return render(request, "cantine_web/search.html", context)


# ============ CALENDRIER MENUS ============


@login_required
@admin_or_prestataire_required
def menu_calendar_view(request):
    """Vue calendrier pour les menus"""
    year = int(request.GET.get("year", timezone.now().year))
    month = int(request.GET.get("month", timezone.now().month))

    # Récupérer tous les menus du mois
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    menus = Menu.objects.filter(date__gte=first_day, date__lte=last_day).order_by(
        "date"
    )

    # Créer un dictionnaire pour faciliter l'accès
    menus_dict = {menu.date: menu for menu in menus}

    # Créer le calendrier
    today = timezone.now().date()
    calendar_days = []

    # Premier jour du mois
    first_weekday = first_day.weekday()  # 0 = Lundi, 6 = Dimanche
    # Ajuster pour que lundi = 0 (Python utilise lundi = 0 par défaut)

    # Jours du mois précédent
    if first_weekday > 0:
        prev_month_last_day = first_day - timedelta(days=1)
        for i in range(first_weekday):
            day_date = prev_month_last_day - timedelta(days=first_weekday - i - 1)
            calendar_days.append(
                {
                    "day": day_date.day,
                    "date": day_date,
                    "other_month": True,
                    "menu": None,
                    "is_today": False,
                }
            )

    # Jours du mois actuel
    current_date = first_day
    while current_date <= last_day:
        is_today = current_date == today
        menu = menus_dict.get(current_date)
        calendar_days.append(
            {
                "day": current_date.day,
                "date": current_date,
                "other_month": False,
                "menu": menu,
                "is_today": is_today,
            }
        )
        current_date += timedelta(days=1)

    # Jours du mois suivant pour compléter la grille
    remaining_days = 42 - len(calendar_days)  # 6 semaines * 7 jours
    if remaining_days > 0:
        next_month_first_day = last_day + timedelta(days=1)
        for i in range(remaining_days):
            day_date = next_month_first_day + timedelta(days=i)
            calendar_days.append(
                {
                    "day": day_date.day,
                    "date": day_date,
                    "other_month": True,
                    "menu": None,
                    "is_today": False,
                }
            )

    context = {
        "year": year,
        "month": month,
        "menus": menus_dict,
        "first_day": first_day,
        "last_day": last_day,
        "calendar_days": calendar_days,
    }

    return render(request, "cantine_web/menu_calendar.html", context)


# ============ BACKUP/RESTORE ============


@login_required
@admin_required
def backup_database(request):
    """Créer une sauvegarde de la base de données"""
    from django.conf import settings

    if request.method == "POST":
        try:
            db_path = settings.DATABASES["default"]["NAME"]
            backup_dir = Path(settings.BASE_DIR) / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.sqlite3"
            backup_path = backup_dir / backup_filename

            # Copier la base de données
            shutil.copy2(db_path, backup_path)

            messages.success(
                request, f"Sauvegarde créée avec succès: {backup_filename}"
            )
            log_action(
                request.user, "EXPORT", "Database", f"Backup créé: {backup_filename}"
            )

            # Retourner le fichier
            response = FileResponse(
                open(backup_path, "rb"), content_type="application/octet-stream"
            )
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{backup_filename}"'
            return response

        except Exception as e:
            messages.error(request, f"Erreur lors de la sauvegarde: {str(e)}")
            return redirect("cantine_web:dashboard")

    return render(request, "cantine_web/backup.html")


@login_required
@admin_required
def restore_database(request):
    """Restaurer une sauvegarde de la base de données"""
    from django.conf import settings

    if request.method == "POST":
        file = request.FILES.get("backup_file")
        if not file:
            messages.error(request, "Aucun fichier sélectionné.")
            return render(request, "cantine_web/restore.html")

        # Valider le fichier
        is_valid, error_msg = validate_file_upload(
            file, allowed_extensions=[".sqlite3"]
        )
        if not is_valid:
            messages.error(request, error_msg)
            return render(request, "cantine_web/restore.html")

        try:
            db_path = settings.DATABASES["default"]["NAME"]
            backup_dir = Path(settings.BASE_DIR) / "backups"
            backup_dir.mkdir(exist_ok=True)

            # Sauvegarder la base actuelle avant restauration
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            current_backup = backup_dir / f"pre_restore_{timestamp}.sqlite3"
            shutil.copy2(db_path, current_backup)

            # Restaurer
            with open(db_path, "wb") as f:
                for chunk in file.chunks():
                    f.write(chunk)

            messages.success(request, "Base de données restaurée avec succès.")
            log_action(request.user, "IMPORT", "Database", f"Restore effectué")

            return redirect("cantine_web:dashboard")

        except Exception as e:
            messages.error(request, f"Erreur lors de la restauration: {str(e)}")

    return render(request, "cantine_web/restore.html")
