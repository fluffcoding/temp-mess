from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.apps import apps


class User(AbstractUser):
    # pass
    username = None
    erp = models.IntegerField(unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["erp"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def subscribe(self, dinner=False, lunch=False, breakfast=False):
        if sum([dinner, lunch, breakfast]) == 0:
            raise ValueError(
                "Empty subscription! You need to add at least one ")
        subscription_model = apps.get_model("subscription", "Subscription")
        subscription_model.objects.create(
            user=self, dinner=dinner, lunch=lunch, breakfast=breakfast
        )
        self.subscription_set.get(is_active=True, user=self)
