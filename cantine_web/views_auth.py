"""
Vues pour l'authentification (login, logout, password reset, password change, profile)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.models import User
from .forms import UserProfileForm


def login_view(request):
    """Vue de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect("cantine_web:dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not hasattr(user, "profil"):
                messages.error(
                    request,
                    "Votre compte n'a pas de profil associé. Contactez l'administrateur.",
                )
                return render(request, "cantine_web/login.html", {"form": form})

            if not user.profil.actif:
                messages.error(
                    request, "Votre compte est désactivé. Contactez l'administrateur."
                )
                return render(request, "cantine_web/login.html", {"form": form})

            login(request, user)
            role_display = user.profil.get_role_display()
            messages.success(
                request,
                f"Bienvenue {user.get_full_name() or user.username} ! Vous êtes connecté en tant que {role_display}.",
            )

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("cantine_web:dashboard")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, "cantine_web/login.html", {"form": form})


@login_required
def profile_view(request):
    """Vue pour afficher et modifier le profil utilisateur"""
    user = request.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect("cantine_web:profile")
    else:
        form = UserProfileForm(instance=user)

    context = {
        "form": form,
        "user": user,
    }

    return render(request, "cantine_web/profile.html", context)


@login_required
def password_change_view(request):
    """Vue pour changer le mot de passe"""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Votre mot de passe a été modifié avec succès.")
            login(
                request, user
            )  # Reconnecter l'utilisateur avec le nouveau mot de passe
            return redirect("cantine_web:profile")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "cantine_web/password_change.html", {"form": form})


# Vues de réinitialisation de mot de passe
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = "cantine_web/password_reset.html"
    email_template_name = "cantine_web/password_reset_email.html"
    subject_template_name = "cantine_web/password_reset_subject.txt"
    form_class = PasswordResetForm
    success_url = reverse_lazy("cantine_web:password_reset_done")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Si un compte existe avec cet email, vous recevrez un email avec les instructions.",
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "cantine_web/password_reset_done.html"


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "cantine_web/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("cantine_web:password_reset_complete")

    def form_valid(self, form):
        messages.success(
            self.request, "Votre mot de passe a été réinitialisé avec succès."
        )
        return super().form_valid(form)


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "cantine_web/password_reset_complete.html"
