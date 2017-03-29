# -*- coding: utf-8 -*-

import rest_framework.permissions

from .models import User


class ObjectPermissionAuthBackend:
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            return False

        if obj is None:
            return False

        # Defer this to the object itself.
        try:
            if perm == 'view':
                perms = ['view', 'change']
            else:
                perms = [perm]
            return obj.user_has_perm_in(user_obj, perms)
        except AttributeError:
            return False

    def authenticate(self, not_ever_to_be_called):
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class ObjectPermisssionRestBackend(rest_framework.permissions.DjangoObjectPermissions):
    perms_map = {
        'GET': ['view'],
        'OPTIONS': ['view'],
        'HEAD': ['view'],
        'POST': ['change'],
        'PUT': ['change'],
        'PATCH': ['change'],
        'DELETE': ['delete'],
        # 'GET': ['%(app_label)s.view'],
        # 'OPTIONS': ['%(app_label)s.view'],
        # 'HEAD': ['%(app_label)s.view'],
        # 'POST': ['%(app_label)s.change'],
        # 'PUT': ['%(app_label)s.change'],
        # 'PATCH': ['%(app_label)s.change'],
        # 'DELETE': ['%(app_label)s.delete'],
    }

    def has_permission(self, request, view):
        from rest_framework.compat import is_authenticated
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        return (
            request.user and
            (is_authenticated(request.user) or not self.authenticated_users_only)
        )

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
