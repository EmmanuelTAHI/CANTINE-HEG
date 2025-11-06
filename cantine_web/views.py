from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from decimal import Decimal
from calendar import monthrange

from .models import (
    Eleve,
    Classe,
    Menu,
    Repas,
    InscriptionMensuelle,
    Facture,
    ProfilPrestataire,
)
from .forms import (
    EleveForm,
    ClasseForm,
    MenuForm,
    RepasForm,
    InscriptionMensuelleForm,
    FactureForm,
    ProfilPrestataireForm,
    ReportFilterForm,
)
from .mixins import (
    AdminRequiredMixin,
    PrestataireRequiredMixin,
    AdminOrPrestataireMixin,
)
from .decorators import (
    admin_required,
    prestataire_required,
    admin_or_prestataire_required,
)
from .reports import generate_pdf_report, generate_excel_report
from .utils import log_action, get_cached_stats


@login_required
@admin_or_prestataire_required
def dashboard(request):
    """Tableau de bord principal"""
    today = timezone.now().date()
    premier_jour_mois = today.replace(day=1)

    # Vérifier si l'utilisateur est admin ou prestataire
    is_admin = hasattr(request.user, "profil") and request.user.profil.is_admin
    is_prestataire = (
        hasattr(request.user, "profil") and request.user.profil.is_prestataire
    )

    # Statistiques avec cache
    def compute_stats():
        stats = {
            "total_eleves": Eleve.objects.filter(actif=True).count(),
            "repas_aujourd_hui": Repas.objects.filter(date=today).count(),
            "repas_ce_mois": Repas.objects.filter(
                date__gte=premier_jour_mois, date__lte=today
            ).count(),
        }

        if is_admin:
            stats["eleves_inscrits_mois"] = InscriptionMensuelle.objects.filter(
                annee=today.year, mois=today.month, inscrit=True
            ).count()
            stats["factures_en_attente"] = Facture.objects.filter(
                statut="ENVOYEE"
            ).count()
            stats["montant_factures_mois"] = Facture.objects.filter(
                annee=today.year, mois=today.month
            ).aggregate(Sum("montant_total"))["montant_total__sum"] or Decimal("0.00")

        return stats

    stats = get_cached_stats(f"dashboard_stats_{today}", compute_stats, timeout=300)

    # Repas par jour (30 derniers jours) pour graphique
    import json

    repas_par_jour_data = []
    for i in range(29, -1, -1):  # Du plus ancien au plus récent
        date_jour = today - timedelta(days=i)
        count = Repas.objects.filter(date=date_jour).count()
        repas_par_jour_data.append(
            {"date": date_jour.strftime("%d/%m"), "count": count}
        )
    repas_par_jour_data_json = json.dumps(repas_par_jour_data)

    # Repas récents
    repas_recents = Repas.objects.select_related("eleve", "menu").order_by(
        "-date", "-created_at"
    )[:10]

    # Menu du jour
    menu_du_jour = Menu.objects.filter(date=today).first()

    # Alertes
    alertes = []
    if not menu_du_jour:
        alertes.append(
            {"type": "warning", "message": "Aucun menu défini pour aujourd'hui"}
        )

    if is_admin:
        factures_pending = Facture.objects.filter(statut="ENVOYEE").count()
        if factures_pending > 0:
            alertes.append(
                {
                    "type": "info",
                    "message": f"{factures_pending} facture(s) en attente de paiement",
                }
            )

    context = {
        "stats": stats,
        "repas_recents": repas_recents,
        "menu_du_jour": menu_du_jour,
        "is_admin": is_admin,
        "is_prestataire": is_prestataire,
        "repas_par_jour_data": repas_par_jour_data_json,
        "alertes": alertes,
    }

    log_action(request.user, "VIEW", "Dashboard", "Consultation du dashboard")

    return render(request, "cantine_web/dashboard.html", context)


# ============ GESTION DES ÉLÈVES (Admin uniquement) ============


class EleveListView(AdminRequiredMixin, ListView):
    model = Eleve
    template_name = "cantine_web/eleve_list.html"
    context_object_name = "eleves"
    paginate_by = 20

    def get_queryset(self):
        queryset = Eleve.objects.select_related("classe").all()
        search = self.request.GET.get("search")
        classe_id = self.request.GET.get("classe")
        actif = self.request.GET.get("actif")

        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) | Q(prenom__icontains=search)
            )
        if classe_id:
            queryset = queryset.filter(classe_id=classe_id)
        if actif is not None:
            queryset = queryset.filter(actif=actif == "1")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["classes"] = Classe.objects.all()
        context["search"] = self.request.GET.get("search", "")
        context["classe_selected"] = self.request.GET.get("classe", "")
        context["actif_selected"] = self.request.GET.get("actif", "")
        return context


class EleveCreateView(AdminRequiredMixin, CreateView):
    model = Eleve
    form_class = EleveForm
    template_name = "cantine_web/eleve_form.html"
    success_url = reverse_lazy("cantine_web:eleve_list")

    def form_valid(self, form):
        messages.success(self.request, f"Élève {form.instance} ajouté avec succès.")
        log_action(
            self.request.user, "CREATE", "Eleve", f"Création élève {form.instance}"
        )
        return super().form_valid(form)


class EleveUpdateView(AdminRequiredMixin, UpdateView):
    model = Eleve
    form_class = EleveForm
    template_name = "cantine_web/eleve_form.html"
    success_url = reverse_lazy("cantine_web:eleve_list")

    def form_valid(self, form):
        messages.success(self.request, f"Élève {form.instance} modifié avec succès.")
        log_action(
            self.request.user,
            "UPDATE",
            "Eleve",
            f"Modification élève {form.instance}",
            self.object.pk,
        )
        return super().form_valid(form)


class EleveDetailView(AdminRequiredMixin, DetailView):
    model = Eleve
    template_name = "cantine_web/eleve_detail.html"
    context_object_name = "eleve"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eleve = self.get_object()

        # Repas récents
        context["repas_recents"] = (
            Repas.objects.filter(eleve=eleve)
            .select_related("menu")
            .order_by("-date")[:20]
        )

        # Statistiques
        today = timezone.now().date()
        premier_jour_mois = today.replace(day=1)
        context["repas_ce_mois"] = Repas.objects.filter(
            eleve=eleve, date__gte=premier_jour_mois
        ).count()

        # Inscriptions mensuelles
        context["inscriptions"] = InscriptionMensuelle.objects.filter(
            eleve=eleve
        ).order_by("-annee", "-mois")[:12]

        return context


class EleveDeleteView(AdminRequiredMixin, DeleteView):
    model = Eleve
    template_name = "cantine_web/eleve_confirm_delete.html"
    success_url = reverse_lazy("cantine_web:eleve_list")

    def form_valid(self, form):
        messages.success(self.request, f"Élève {self.object} supprimé avec succès.")
        log_action(
            self.request.user,
            "DELETE",
            "Eleve",
            f"Suppression élève {self.object}",
            self.object.pk,
        )
        return super().form_valid(form)


# ============ GESTION DES INSCRIPTIONS MENSUELLES (Admin uniquement) ============


class InscriptionMensuelleListView(AdminRequiredMixin, ListView):
    model = InscriptionMensuelle
    template_name = "cantine_web/inscription_mensuelle_list.html"
    context_object_name = "inscriptions"
    paginate_by = 50

    def get_queryset(self):
        queryset = InscriptionMensuelle.objects.select_related(
            "eleve", "created_by"
        ).all()
        annee = self.request.GET.get("annee")
        mois = self.request.GET.get("mois")
        eleve_id = self.request.GET.get("eleve")

        if annee:
            queryset = queryset.filter(annee=annee)
        if mois:
            queryset = queryset.filter(mois=mois)
        if eleve_id:
            queryset = queryset.filter(eleve_id=eleve_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["annee_selected"] = self.request.GET.get("annee", today.year)
        context["mois_selected"] = self.request.GET.get("mois", today.month)
        context["eleves"] = Eleve.objects.filter(actif=True).order_by("nom", "prenom")
        return context


class InscriptionMensuelleCreateView(AdminRequiredMixin, CreateView):
    model = InscriptionMensuelle
    form_class = InscriptionMensuelleForm
    template_name = "cantine_web/inscription_mensuelle_form.html"
    success_url = reverse_lazy("cantine_web:inscription_mensuelle_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request, f"Inscription mensuelle enregistrée avec succès."
        )
        log_action(
            self.request.user,
            "CREATE",
            "InscriptionMensuelle",
            f"Création inscription {form.instance}",
        )
        return super().form_valid(form)


class InscriptionMensuelleUpdateView(AdminRequiredMixin, UpdateView):
    model = InscriptionMensuelle
    form_class = InscriptionMensuelleForm
    template_name = "cantine_web/inscription_mensuelle_form.html"
    success_url = reverse_lazy("cantine_web:inscription_mensuelle_list")

    def form_valid(self, form):
        messages.success(self.request, f"Inscription mensuelle modifiée avec succès.")
        return super().form_valid(form)


class InscriptionMensuelleDeleteView(AdminRequiredMixin, DeleteView):
    model = InscriptionMensuelle
    template_name = "cantine_web/inscription_mensuelle_confirm_delete.html"
    success_url = reverse_lazy("cantine_web:inscription_mensuelle_list")

    def form_valid(self, form):
        messages.success(self.request, "Inscription mensuelle supprimée avec succès.")
        return super().form_valid(form)


# ============ GESTION DES MENUS (Admin et Prestataire) ============


class MenuListView(AdminOrPrestataireMixin, ListView):
    model = Menu
    template_name = "cantine_web/menu_list.html"
    context_object_name = "menus"
    paginate_by = 20

    def get_queryset(self):
        queryset = Menu.objects.all()
        mois = self.request.GET.get("mois")
        annee = self.request.GET.get("annee")

        if mois and annee:
            queryset = queryset.filter(date__year=annee, date__month=mois)
        elif annee:
            queryset = queryset.filter(date__year=annee)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["menu_du_jour"] = Menu.objects.filter(date=today).first()
        context["menu_actuel"] = Menu.objects.filter(
            date__year=today.year, date__month=today.month
        ).order_by("date")

        # Menu précédent
        prev_month = today.replace(day=1) - timedelta(days=1)
        context["menu_precedent"] = Menu.objects.filter(
            date__year=prev_month.year, date__month=prev_month.month
        ).order_by("date")

        # Menu à venir
        next_month = today.replace(day=28) + timedelta(days=4)
        next_month = next_month.replace(day=1)
        context["menu_avenir"] = Menu.objects.filter(
            date__year=next_month.year, date__month=next_month.month
        ).order_by("date")

        return context


class MenuCreateView(AdminOrPrestataireMixin, CreateView):
    model = Menu
    form_class = MenuForm
    template_name = "cantine_web/menu_form.html"
    success_url = reverse_lazy("cantine_web:menu_list")

    def form_valid(self, form):
        messages.success(
            self.request, f"Menu du {form.instance.date} ajouté avec succès."
        )
        log_action(
            self.request.user, "CREATE", "Menu", f"Création menu {form.instance.date}"
        )
        return super().form_valid(form)


class MenuUpdateView(AdminOrPrestataireMixin, UpdateView):
    model = Menu
    form_class = MenuForm
    template_name = "cantine_web/menu_form.html"
    success_url = reverse_lazy("cantine_web:menu_list")

    def form_valid(self, form):
        messages.success(
            self.request, f"Menu du {form.instance.date} modifié avec succès."
        )
        log_action(
            self.request.user,
            "UPDATE",
            "Menu",
            f"Modification menu {form.instance.date}",
            self.object.pk,
        )
        return super().form_valid(form)


class MenuDeleteView(AdminOrPrestataireMixin, DeleteView):
    model = Menu
    template_name = "cantine_web/menu_confirm_delete.html"
    success_url = reverse_lazy("cantine_web:menu_list")


# ============ GESTION DES REPAS (Admin et Prestataire) ============


class RepasListView(AdminOrPrestataireMixin, ListView):
    model = Repas
    template_name = "cantine_web/repas_list.html"
    context_object_name = "repas"
    paginate_by = 50

    def get_queryset(self):
        queryset = Repas.objects.select_related("eleve", "menu", "created_by").all()
        date = self.request.GET.get("date")
        eleve_id = self.request.GET.get("eleve")

        if date:
            queryset = queryset.filter(date=date)
        if eleve_id:
            queryset = queryset.filter(eleve_id=eleve_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["date_selected"] = self.request.GET.get("date", today.isoformat())
        context["eleves"] = Eleve.objects.filter(actif=True).order_by("nom", "prenom")
        return context


@login_required
@admin_or_prestataire_required
def repas_marquer_multiples(request):
    """Marquer plusieurs élèves comme ayant mangé aujourd'hui"""
    if request.method == "POST":
        eleve_ids = request.POST.getlist("eleves")
        date_str = request.POST.get("date", timezone.now().date().isoformat())
        date_repas = datetime.strptime(date_str, "%Y-%m-%d").date()
        menu = Menu.objects.filter(date=date_repas).first()

        if not menu:
            messages.warning(
                request,
                "Aucun menu défini pour cette date. Les repas seront enregistrés sans menu associé.",
            )

        if not eleve_ids:
            messages.warning(request, "Aucun élève sélectionné.")
            return redirect("cantine_web:repas_marquer")

        repas_crees = 0
        for eleve_id in eleve_ids:
            eleve = get_object_or_404(Eleve, id=eleve_id, actif=True)
            # Vérifier si le repas n'existe pas déjà
            if not Repas.objects.filter(eleve=eleve, date=date_repas).exists():
                Repas.objects.create(
                    eleve=eleve,
                    menu=menu,  # Peut être None si pas de menu
                    date=date_repas,
                    created_by=request.user,
                )
                repas_crees += 1

        messages.success(request, f"{repas_crees} repas enregistré(s) avec succès.")
        log_action(
            request.user,
            "CREATE",
            "Repas",
            f"Création de {repas_crees} repas pour {date_repas}",
        )
        return redirect("cantine_web:repas_list")

    today = timezone.now().date()
    date_str = request.GET.get("date", today.isoformat())
    date_repas = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Récupérer les élèves actifs pour le mois
    # D'abord, essayer de récupérer ceux avec inscription mensuelle
    eleves_inscrits = (
        Eleve.objects.filter(
            actif=True,
            inscriptions_mensuelles__annee=date_repas.year,
            inscriptions_mensuelles__mois=date_repas.month,
            inscriptions_mensuelles__inscrit=True,
        )
        .select_related("classe")
        .distinct()
    )

    # Si aucun élève avec inscription mensuelle, afficher tous les élèves actifs
    if not eleves_inscrits.exists():
        eleves_inscrits = Eleve.objects.filter(actif=True).select_related("classe")

    eleves_inscrits = eleves_inscrits.order_by("classe", "nom", "prenom")

    menu_du_jour = Menu.objects.filter(date=date_repas).first()

    # Élèves qui ont déjà mangé
    eleves_ayant_mange = Repas.objects.filter(date=date_repas).values_list(
        "eleve_id", flat=True
    )

    context = {
        "eleves": eleves_inscrits,
        "menu_du_jour": menu_du_jour,
        "date": date_repas,
        "eleves_ayant_mange": eleves_ayant_mange,
    }
    return render(request, "cantine_web/repas_marquer.html", context)


# ============ GESTION DES FACTURES (Prestataire principalement, Admin peut consulter) ============


class FactureListView(AdminOrPrestataireMixin, ListView):
    model = Facture
    template_name = "cantine_web/facture_list.html"
    context_object_name = "factures"
    paginate_by = 20

    def get_queryset(self):
        queryset = Facture.objects.select_related("created_by").all()
        annee = self.request.GET.get("annee")
        mois = self.request.GET.get("mois")
        statut = self.request.GET.get("statut")

        if annee:
            queryset = queryset.filter(annee=annee)
        if mois:
            queryset = queryset.filter(mois=mois)
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset


class FactureCreateView(PrestataireRequiredMixin, CreateView):
    model = Facture
    form_class = FactureForm
    template_name = "cantine_web/facture_form.html"
    success_url = reverse_lazy("cantine_web:facture_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Générer un numéro de facture si non fourni
        if not form.instance.numero:
            last_facture = Facture.objects.order_by("-id").first()
            if last_facture:
                last_num = (
                    int(last_facture.numero.split("-")[-1])
                    if "-" in last_facture.numero
                    else 0
                )
            else:
                last_num = 0
            form.instance.numero = (
                f"FAC-{form.instance.annee}-{form.instance.mois:02d}-{last_num + 1:04d}"
            )

        # Calculer le montant total
        form.instance.montant_total = (
            form.instance.nombre_repas_servis * form.instance.prix_unitaire_repas
        )

        messages.success(
            self.request, f"Facture {form.instance.numero} créée avec succès."
        )
        return super().form_valid(form)


class FactureUpdateView(PrestataireRequiredMixin, UpdateView):
    model = Facture
    form_class = FactureForm
    template_name = "cantine_web/facture_form.html"
    success_url = reverse_lazy("cantine_web:facture_list")

    def form_valid(self, form):
        # Recalculer le montant total
        form.instance.montant_total = (
            form.instance.nombre_repas_servis * form.instance.prix_unitaire_repas
        )
        messages.success(
            self.request, f"Facture {form.instance.numero} modifiée avec succès."
        )
        return super().form_valid(form)


class FactureDetailView(AdminOrPrestataireMixin, DetailView):
    model = Facture
    template_name = "cantine_web/facture_detail.html"
    context_object_name = "facture"


class FactureDeleteView(PrestataireRequiredMixin, DeleteView):
    model = Facture
    template_name = "cantine_web/facture_confirm_delete.html"
    success_url = reverse_lazy("cantine_web:facture_list")

    def form_valid(self, form):
        messages.success(
            self.request, f"Facture {self.object.numero} supprimée avec succès."
        )
        return super().form_valid(form)


# ============ STATISTIQUES ============


@login_required
@admin_or_prestataire_required
def statistiques(request):
    """Page de statistiques"""
    today = timezone.now().date()
    premier_jour_mois = today.replace(day=1)

    is_admin = hasattr(request.user, "profil") and request.user.profil.is_admin

    # Statistiques globales
    stats = {
        "total_eleves": Eleve.objects.filter(actif=True).count(),
        "repas_aujourd_hui": Repas.objects.filter(date=today).count(),
        "repas_ce_mois": Repas.objects.filter(
            date__gte=premier_jour_mois, date__lte=today
        ).count(),
        "repas_total": Repas.objects.count(),
    }

    if is_admin:
        stats["montant_factures_total"] = Facture.objects.aggregate(
            Sum("montant_total")
        )["montant_total__sum"] or Decimal("0.00")
        stats["factures_payees"] = Facture.objects.filter(statut="PAYEE").count()

    # Repas par jour (derniers 30 jours)
    repas_par_jour = []
    for i in range(30):
        date_jour = today - timedelta(days=i)
        count = Repas.objects.filter(date=date_jour).count()
        repas_par_jour.append({"date": date_jour, "count": count})
    repas_par_jour.reverse()

    # Top élèves (ce mois)
    top_eleves = (
        Eleve.objects.filter(repas__date__gte=premier_jour_mois, repas__date__lte=today)
        .annotate(nb_repas=Count("repas"))
        .order_by("-nb_repas")[:10]
    )

    context = {
        "stats": stats,
        "repas_par_jour": repas_par_jour,
        "top_eleves": top_eleves,
        "is_admin": is_admin,
    }

    return render(request, "cantine_web/statistiques.html", context)


# ============ RAPPORTS PDF/EXCEL ============


@login_required
@admin_or_prestataire_required
def generer_rapport(request):
    """Générer un rapport PDF ou Excel"""
    if request.method == "POST":
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            type_rapport = form.cleaned_data["type_rapport"]
            format_export = form.cleaned_data["format_export"]
            date_debut = form.cleaned_data.get("date_debut")
            date_fin = form.cleaned_data.get("date_fin")
            annee = form.cleaned_data.get("annee")
            mois = form.cleaned_data.get("mois")

            today = timezone.now().date()

            # Déterminer les dates
            if type_rapport == "JOURNALIER":
                if not date_debut:
                    date_debut = today
                date_fin = date_debut
                date_debut_filter = date_debut
                date_fin_filter = date_debut
            elif type_rapport == "HEBDOMADAIRE":
                if not date_debut:
                    date_debut = today - timedelta(days=today.weekday())
                if not date_fin:
                    date_fin = date_debut + timedelta(days=6)
                date_debut_filter = date_debut
                date_fin_filter = date_fin
            else:  # MENSUEL
                if not annee:
                    annee = today.year
                if not mois:
                    mois = today.month
                premier_jour = date(annee, mois, 1)
                dernier_jour = date(annee, mois, monthrange(annee, mois)[1])
                date_debut_filter = premier_jour
                date_fin_filter = dernier_jour

            # Récupérer les données
            repas = (
                Repas.objects.filter(
                    date__gte=date_debut_filter, date__lte=date_fin_filter
                )
                .select_related("eleve", "menu")
                .order_by("date", "eleve")
            )

            # Préparer les données pour le rapport
            data = []
            for repas_obj in repas:
                data.append(
                    {
                        "Date": repas_obj.date.strftime("%d/%m/%Y"),
                        "Élève": str(repas_obj.eleve),
                        "Classe": str(repas_obj.eleve.classe)
                        if repas_obj.eleve.classe
                        else "",
                        "Plat principal": repas_obj.menu.plat_principal
                        if repas_obj.menu
                        else "",
                        "Menu complet": f"{repas_obj.menu.plat_principal} - {repas_obj.menu.accompagnement}"
                        if repas_obj.menu
                        else "",
                    }
                )

            # Statistiques
            stats_data = [
                {"Statistique": "Nombre total de repas", "Valeur": repas.count()}
            ]

            if type_rapport == "MENSUEL":
                stats_data.append(
                    {
                        "Statistique": "Nombre d'élèves servis",
                        "Valeur": repas.values("eleve").distinct().count(),
                    }
                )

            # Générer le rapport
            if type_rapport == "JOURNALIER":
                title = f"Rapport Journalier - {date_debut.strftime('%d/%m/%Y')}"
                filename = f"rapport_journalier_{date_debut.strftime('%Y%m%d')}"
            elif type_rapport == "HEBDOMADAIRE":
                title = f"Rapport Hebdomadaire - {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"
                filename = f"rapport_hebdomadaire_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}"
            else:
                title = f"Rapport Mensuel - {mois}/{annee}"
                filename = f"rapport_mensuel_{annee}_{mois:02d}"

            if format_export == "PDF":
                filename += ".pdf"
                return generate_pdf_report(title, data, filename)
            else:
                filename += ".xlsx"
                return generate_excel_report(title, data, filename)
    else:
        form = ReportFilterForm()
        today = timezone.now().date()
        form.fields["annee"].initial = today.year
        form.fields["mois"].initial = today.month
        form.fields["date_debut"].initial = today

    return render(request, "cantine_web/generer_rapport.html", {"form": form})


# ============ GESTION DES PRESTATAIRES (Admin uniquement) ============


class PrestataireListView(AdminRequiredMixin, ListView):
    model = ProfilPrestataire
    template_name = "cantine_web/prestataire_list.html"
    context_object_name = "prestataires"
    paginate_by = 20

    def get_queryset(self):
        queryset = ProfilPrestataire.objects.select_related("user").all()
        role = self.request.GET.get("role")
        actif = self.request.GET.get("actif")

        if role:
            queryset = queryset.filter(role=role)
        if actif is not None:
            queryset = queryset.filter(actif=actif == "1")

        return queryset


class PrestataireCreateView(AdminRequiredMixin, CreateView):
    model = ProfilPrestataire
    form_class = ProfilPrestataireForm
    template_name = "cantine_web/prestataire_form.html"
    success_url = reverse_lazy("cantine_web:prestataire_list")

    def form_valid(self, form):
        profil = form.save()
        messages.success(
            self.request, f"Compte prestataire créé pour {profil.user.username}."
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["data"] = self.request.POST
        return kwargs


class PrestataireUpdateView(AdminRequiredMixin, UpdateView):
    model = ProfilPrestataire
    form_class = ProfilPrestataireForm
    template_name = "cantine_web/prestataire_form.html"
    success_url = reverse_lazy("cantine_web:prestataire_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Compte prestataire {form.instance.user.username} modifié avec succès.",
        )
        return super().form_valid(form)


class PrestataireDeleteView(AdminRequiredMixin, DeleteView):
    model = ProfilPrestataire
    template_name = "cantine_web/prestataire_confirm_delete.html"
    success_url = reverse_lazy("cantine_web:prestataire_list")

    def form_valid(self, form):
        username = self.object.user.username
        messages.success(self.request, f"Prestataire {username} supprimé avec succès.")
        return super().form_valid(form)


# ============ DÉCOMPTE JOURNALIER ET MENSUEL ============


@login_required
@prestataire_required
def decompte_journalier(request):
    """Décompte journalier des repas servis"""
    date_str = request.GET.get("date", timezone.now().date().isoformat())
    date_repas = datetime.strptime(date_str, "%Y-%m-%d").date()

    repas = Repas.objects.filter(date=date_repas).select_related("eleve", "menu")
    menu = Menu.objects.filter(date=date_repas).first()

    context = {
        "date": date_repas,
        "repas": repas,
        "nombre_repas": repas.count(),
        "menu": menu,
        "eleves_servis": repas.values("eleve").distinct().count(),
    }

    return render(request, "cantine_web/decompte_journalier.html", context)


@login_required
@prestataire_required
def decompte_mensuel(request):
    """Décompte mensuel des repas servis"""
    today = timezone.now().date()
    annee = int(request.GET.get("annee", today.year))
    mois = int(request.GET.get("mois", today.month))

    premier_jour = date(annee, mois, 1)
    dernier_jour = date(annee, mois, monthrange(annee, mois)[1])

    repas = (
        Repas.objects.filter(date__gte=premier_jour, date__lte=dernier_jour)
        .select_related("eleve", "menu")
        .order_by("date")
    )

    # Statistiques
    nombre_repas = repas.count()
    nombre_jours_travail = repas.values("date").distinct().count()
    eleves_servis = repas.values("eleve").distinct().count()

    # Repas par jour
    repas_par_jour = {}
    for repas_obj in repas:
        jour = repas_obj.date.strftime("%d/%m/%Y")
        if jour not in repas_par_jour:
            repas_par_jour[jour] = 0
        repas_par_jour[jour] += 1

    context = {
        "annee": annee,
        "mois": mois,
        "premier_jour": premier_jour,
        "dernier_jour": dernier_jour,
        "repas": repas,
        "nombre_repas": nombre_repas,
        "nombre_jours_travail": nombre_jours_travail,
        "eleves_servis": eleves_servis,
        "repas_par_jour": repas_par_jour,
    }

    return render(request, "cantine_web/decompte_mensuel.html", context)


# ============ LISTE DES ÉLÈVES INSCRITS (Prestataire) ============


@login_required
@prestataire_required
def eleves_inscrits(request):
    """Voir la liste des élèves inscrits (envoyée par l'admin)"""
    today = timezone.now().date()
    annee = int(request.GET.get("annee", today.year))
    mois = int(request.GET.get("mois", today.month))

    eleves = (
        Eleve.objects.filter(
            actif=True,
            inscriptions_mensuelles__annee=annee,
            inscriptions_mensuelles__mois=mois,
            inscriptions_mensuelles__inscrit=True,
        )
        .select_related("classe")
        .distinct()
        .order_by("classe", "nom", "prenom")
    )

    context = {
        "eleves": eleves,
        "annee": annee,
        "mois": mois,
    }

    return render(request, "cantine_web/eleves_inscrits.html", context)


# ============ DÉTAIL DES PLATS SERVIS ============


@login_required
@admin_or_prestataire_required
def detail_plats_servis(request):
    """Détail des plats servis par élève, par jour, semaine ou mois"""
    eleve_id = request.GET.get("eleve")
    date_debut_str = request.GET.get("date_debut")
    date_fin_str = request.GET.get("date_fin")

    queryset = Repas.objects.select_related("eleve", "menu").all()

    if eleve_id:
        queryset = queryset.filter(eleve_id=eleve_id)

    if date_debut_str:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
        queryset = queryset.filter(date__gte=date_debut)

    if date_fin_str:
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
        queryset = queryset.filter(date__lte=date_fin)

    repas = queryset.order_by("-date", "eleve")

    context = {
        "repas": repas,
        "eleves": Eleve.objects.filter(actif=True).order_by("nom", "prenom"),
        "eleve_selected": int(eleve_id) if eleve_id else None,
        "date_debut": date_debut_str or "",
        "date_fin": date_fin_str or "",
    }

    return render(request, "cantine_web/detail_plats_servis.html", context)


# ============ HANDLERS D'ERREURS ============


def handler404(request, exception):
    """Handler personnalisé pour les erreurs 404"""
    return render(request, "404.html", status=404)


def handler500(request):
    """Handler personnalisé pour les erreurs 500"""
    return render(request, "500.html", status=500)
