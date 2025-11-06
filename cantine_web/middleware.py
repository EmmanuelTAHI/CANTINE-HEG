"""
Middleware pour logging automatique des actions
"""
from .utils import log_action
from .models import ActionLog


class ActionLoggingMiddleware:
    """Middleware pour logger automatiquement les actions importantes"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Logger certaines actions importantes
        if request.user.is_authenticated and hasattr(request.user, "profil"):
            # Logger les créations, modifications, suppressions
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                # Ne logger que les actions importantes, pas les requêtes AJAX
                if not request.path.startswith(
                    "/static/"
                ) and not request.path.startswith("/media/"):
                    # Le logging détaillé sera fait dans les vues
                    pass

        return response
