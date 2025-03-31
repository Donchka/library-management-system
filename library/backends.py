from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from .models import Member

class MemberBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
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