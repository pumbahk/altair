# -*- coding: utf-8 -*-

class BasePermission(object):
    """All permission class should inherit this class."""

    message = None

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True