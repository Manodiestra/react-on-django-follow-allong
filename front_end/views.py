import posixpath
import os
from pathlib import Path
from django.http import Http404, HttpResponseServerError
from django.utils._os import safe_join
from django.views.static import serve as static_serve
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.timezone import now

from .models import JournalEntry
from .serializers import JournalEntrySerializer

def serve_react(request, path='', document_root=None):
    if not document_root or not os.path.isdir(document_root):
        return HttpResponseServerError("Server configuration error.")

    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))

    if fullpath.is_file():
        return static_serve(request, path, document_root=document_root)
    else:
        index_path = Path(safe_join(document_root, "index.html"))
        if not index_path.is_file():
            return Http404("index.html not found.")

        return static_serve(request, "index.html", document_root=document_root)


class TokenPresent(BasePermission):
    # Allows access only if a token is present in the headers.
    def has_permission(self, request, view):
        return 'Authorization' in request.headers


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]  # Apply the permission class to all actions

    def get_queryset(self):
        # Filter the queryset by the authenticated user's Cognito User ID
        user_id = self.request.user.username  # Cognito User ID stored in `username`
        return JournalEntry.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        # Automatically save the user_id when creating a new Journal Entry
        serializer.save(user_id=self.request.user.username)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.user_id != request.user.username:
            return Response({"detail": "You do not have permission to update this entry."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

