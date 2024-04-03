from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as BaseGroup


class User(AbstractUser):
    pass


class Group(BaseGroup):
    pass
