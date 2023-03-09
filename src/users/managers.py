from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from .validators import email_validation
from django.apps import apps


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        wallet_model = apps.get_model("accounts", "Wallet")
        is_student = extra_fields.setdefault("is_student", True)
        if is_student:
            email_validation(email)
            if extra_fields.get("erp") == None:
                raise ValueError(_("As a student you need to provide an erp"))
        else:
            extra_fields["erp"] = None

        if not email:
            raise ValueError(_("The Email must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        wallet_model.objects.create(user=user)

        return user

    def create_superuser(self, email, password, **extra_fields):

        is_staff = extra_fields.setdefault("is_staff", True)
        is_superuser = extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if is_staff is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if is_superuser is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)
