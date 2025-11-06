from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est un admin"""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "profil") or not request.user.profil.is_admin:
            messages.error(
                request,
                "Vous n'avez pas les permissions nécessaires pour accéder à cette page.",
            )
            return redirect("cantine_web:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


def prestataire_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est un prestataire ou admin"""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "profil"):
            messages.error(request, "Votre compte n'a pas de profil associé.")
            return redirect("cantine_web:dashboard")
        if not (request.user.profil.is_prestataire or request.user.profil.is_admin):
            messages.error(
                request,
                "Vous n'avez pas les permissions nécessaires pour accéder à cette page.",
            )
            return redirect("cantine_web:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_or_prestataire_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est admin ou prestataire"""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "profil"):
            messages.error(request, "Votre compte n'a pas de profil associé.")
            return redirect("cantine_web:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper
