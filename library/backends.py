"""
This module contains the custom authentication backend for library members.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser, User

from .models import Member


class MemberBackend(BaseBackend):
    """
    Custom authentication backend for library members.
    This backend handles authentication for library members using their email and password.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticates a member using their email and password.
        """
        try:
            member = Member.objects.get(email=email, credential=password)
            # Create a temporary User object to integrate with Django's auth system
            user = User(
                id=member.member_id,
                username=member.first_name+" "+member.last_name,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
            )
            user.is_authenticated = True
            return user
        except Member.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Retrieves a user by their ID.
        """
        try:
            member = Member.objects.get(member_id=user_id)
            user = User(
                id=member.member_id,
                username=member.first_name+" "+member.last_name,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
            )
            user.is_authenticated = True
            return user
        except Member.DoesNotExist:
            return AnonymousUser()