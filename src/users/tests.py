from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.apps import apps
import datetime

Wallet = apps.get_model("accounts", "Wallet")


class UserManagerTesting(TestCase):
    User = get_user_model()

    def setUp(self):

        price_model = apps.get_model("accounts", "Price")
        price = price_model.objects.create(
            dinner=210,
            lunch=190,
            breakfast=180,
            surcharge=500
        )

        period_model = apps.get_model("subscription", "Period")
        period_model.objects.create(
            end_date=datetime.date(2023, 3, 20)
        )

        # signing up a normal student
        self.assertRaises(ValueError, self.User.objects.create_user,
                          *["normaluser@khi.iba.edu.pk", "fooooooo"])

        try:
            self.User.objects.create_user(
                "normaluser@khi.iba.edu.pk", "fooooooo", erp=19334)
        except ValidationError as e:
            self.fail("normal user not created")

        # create user with wrong email ending
        self.assertRaises(ValidationError, self.User.objects.create_user,
                          *["normaluser@gmail.com", "fooooooo"], **{"erp": 19039})

        try:
            self.User.objects.create_user(
                "notadaminnotstudent@gmail.com", "fooooooo", is_student=False)
        except ValidationError as e:
            self.fail("non admin non student user creation failed")

        # signing up with is_student=False and non zero erp
        try:
            self.User.objects.create_user(
                "notstudentwitherp@gmail.com", "fooooooo", is_student=False, erp=19340)
        except ValidationError as e:
            self.fail("non admin non student user creation failed")

        # create

    def test_user_attributes(self):
        user = self.User.objects.get(email="normaluser@khi.iba.edu.pk")
        self.assertEqual(user.email, "normaluser@khi.iba.edu.pk",
                         "Email for normal student signup not equal")
        self.assertEqual(
            user.erp, 19334, "ERP for normalstudent signup not set")

        user_not_admin = self.User.objects.get(
            email="notadaminnotstudent@gmail.com")
        self.assertEqual(user_not_admin.erp, None,
                         "The erp for users that are not admin or students is set to null")

        not_student_with_erp = self.User.objects.get(
            email="notstudentwitherp@gmail.com")
        self.assertEqual(not_student_with_erp.erp, None,
                         "Non student users can set erp")

    def test_super_user_creation(self):
        pass

    def test_user_wallet(self):
        user2 = self.User.objects.get(email="normaluser@khi.iba.edu.pk")
        user = self.User.objects.get(email="notadaminnotstudent@gmail.com")
        wallet = Wallet.objects.filter(user=user).exists()
        wallet2 = Wallet.objects.filter(user=user2)
        self.assertTrue(wallet, "wallet for the user was not created")
        self.assertTrue(wallet2, "wallet for the user was not created")

    def test_user_subscription(self):
        user2 = self.User.objects.get(email="normaluser@khi.iba.edu.pk")
        user2.subscribe(dinner=True)
        user2.subscribe(lunch=True)
