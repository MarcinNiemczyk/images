from rest_framework.permissions import BasePermission


class GenerateLinksAllowed(BasePermission):
    message = "You are not allowed to generate link that expire"

    def has_permission(self, request, view):
        if request.user.tier.generate_links:
            return True
        return False
