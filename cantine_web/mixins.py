from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est un admin"""

    def test_func(self):
        if not hasattr(self.request.user, "profil"):
            return False
        return self.request.user.profil.is_admin

    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect

        messages.error(
            self.request,
            "Vous n'avez pas les permissions nécessaires pour accéder à cette page.",
        )
        return redirect("cantine_web:dashboard")


class PrestataireRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est un prestataire ou admin"""

    def test_func(self):
        if not hasattr(self.request.user, "profil"):
            return False
        return (
            self.request.user.profil.is_prestataire or self.request.user.profil.is_admin
        )

    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect

        messages.error(
            self.request,
            "Vous n'avez pas les permissions nécessaires pour accéder à cette page.",
        )
        return redirect("cantine_web:dashboard")


class AdminOrPrestataireMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur a un profil (admin ou prestataire)"""

    def test_func(self):
        return hasattr(self.request.user, "profil")

    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect

        messages.error(self.request, "Votre compte n'a pas de profil associé.")
        return redirect("cantine_web:dashboard")
