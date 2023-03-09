from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def email_validation(email):
    validate_email(email)
    if not email.endswith("iba.edu.pk"):
        raise ValidationError(
            "enter a valid IBA email only"
        )
